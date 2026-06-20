<?php

namespace Tests\Feature;

use App\Models\Camera;
use App\Models\DangerZone;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

class DetectionIntegrationTest extends TestCase
{
    use RefreshDatabase;

    public function test_health_reports_ml_status(): void
    {
        Http::fake(['*/health' => Http::response(['status' => 'healthy'])]);

        $this->getJson('/api/health')
            ->assertOk()
            ->assertJsonPath('backend', 'healthy')
            ->assertJsonPath('ml', 'healthy');
    }

    public function test_detection_forwards_selected_camera_zone_to_ml_and_persists_result(): void
    {
        $camera = Camera::create(['code' => 'CAM-02', 'name' => 'Area Tambang', 'location' => 'Pit A', 'status' => true]);
        DangerZone::create([
            'camera_id' => $camera->id,
            'zone_name' => 'Crusher',
            'coordinates' => ['x1' => 10, 'y1' => 20, 'x2' => 300, 'y2' => 400],
            'status' => true,
        ]);
        Http::fake(['*/detect-image*' => Http::response([
            'camera_code' => 'CAM-02',
            'worker_count' => 1,
            'detections' => [[
                'worker_id' => 'W-001', 'helmet' => false, 'vest' => true,
                'in_danger_zone' => true, 'violations' => ['NO_HELMET', 'DANGER_ZONE_ENTRY'],
                'risk_score' => 90, 'risk_level' => 'CRITICAL', 'box' => [1, 2, 3, 4],
            ]],
            'summary' => ['total_violation' => 2, 'highest_risk' => 'CRITICAL', 'screenshot_saved' => false],
        ])]);

        $this->post('/api/detect-image', ['camera_code' => 'CAM-02', 'image' => UploadedFile::fake()->image('frame.jpg')])
            ->assertCreated()
            ->assertJsonPath('data.violations.0.violation_type', 'helmet_missing');

        Http::assertSent(fn ($request) => str_contains($request->url(), 'camera_code=CAM-02')
            && str_contains($request->url(), 'zone_x1=10')
            && str_contains($request->url(), 'zone_y2=400'));
        $this->assertDatabaseCount('violations', 2);
        $this->assertDatabaseCount('alerts', 2);
    }

    public function test_repeated_live_violation_is_suppressed_during_alert_cooldown(): void
    {
        $payload = [
            'camera_code' => 'CAM-03', 'worker_count' => 1,
            'detections' => [[
                'worker_id' => 'W-001', 'helmet' => false, 'vest' => true,
                'in_danger_zone' => false, 'violations' => ['NO_HELMET'],
                'risk_score' => 40, 'risk_level' => 'WARNING', 'box' => [1, 2, 100, 200],
            ]],
            'summary' => ['total_violation' => 1, 'highest_risk' => 'WARNING'],
        ];

        $this->postJson('/api/detections', $payload)->assertCreated();
        $this->postJson('/api/detections', $payload)
            ->assertOk()
            ->assertJsonPath('data.suppressed_alerts', 1);

        $this->assertDatabaseCount('violations', 1);
        $this->assertDatabaseCount('alerts', 1);
    }

    public function test_live_analysis_does_not_persist_frames_until_an_incident_is_reported(): void
    {
        Http::fake(['*/detect-image*' => Http::response([
            'camera_code' => 'CAM-04', 'worker_count' => 1,
            'detections' => [[
                'worker_id' => 'W-001', 'helmet' => false, 'vest' => true,
                'in_danger_zone' => false, 'violations' => ['NO_HELMET'],
                'risk_score' => 40, 'risk_level' => 'WARNING', 'box' => [1, 2, 3, 4],
            ]],
            'summary' => ['total_violation' => 1, 'highest_risk' => 'WARNING', 'screenshot_saved' => false],
        ])]);

        $this->post('/api/detect-image', [
            'camera_code' => 'CAM-04', 'persist' => false,
            'image' => UploadedFile::fake()->image('live-frame.jpg'),
        ])->assertOk()->assertJsonPath('data.result.camera_code', 'CAM-04');

        $this->assertDatabaseCount('violations', 0);
        $this->assertDatabaseCount('alerts', 0);
    }

    public function test_best_evidence_updates_only_when_score_improves_by_at_least_fifteen_percent(): void
    {
        Storage::fake('public');
        $payload = [
            'camera_code' => 'CAM-05', 'worker_count' => 1,
            'detections' => [[
                'worker_id' => 'W-001', 'helmet' => false, 'vest' => true,
                'in_danger_zone' => false, 'violations' => ['NO_HELMET'],
                'risk_score' => 40, 'risk_level' => 'WARNING', 'box' => [1, 2, 100, 200],
                'evidence_score' => 1,
            ]],
            'summary' => ['total_violation' => 1, 'highest_risk' => 'WARNING'],
            'annotated_image_base64' => base64_encode('initial-frame'),
        ];

        $this->postJson('/api/detections', $payload)->assertCreated();
        $initial = \App\Models\Violation::first();

        $this->postJson('/api/detections/evidence', [
            'camera_code' => 'CAM-05',
            'worker_id' => 'W-001',
            'evidence_score' => 1.14,
            'annotated_image_base64' => base64_encode('almost-better-frame'),
        ])->assertOk()->assertJsonPath('updated', 0);
        $this->assertSame($initial->best_screenshot, $initial->fresh()->best_screenshot);

        $this->postJson('/api/detections/evidence', [
            'camera_code' => 'CAM-05',
            'worker_id' => 'W-001',
            'evidence_score' => 1.15,
            'annotated_image_base64' => base64_encode('better-frame'),
        ])->assertOk()->assertJsonPath('updated', 1);

        $updated = $initial->fresh();
        $this->assertNotSame($initial->best_screenshot, $updated->best_screenshot);
        $this->assertEqualsWithDelta(1.15, (float) $updated->best_evidence_score, 0.000001);
    }

    public function test_suppressed_incident_does_not_store_extra_screenshot(): void
    {
        Storage::fake('public');
        $payload = [
            'camera_code' => 'CAM-06', 'worker_count' => 1,
            'detections' => [[
                'worker_id' => 'W-001', 'helmet' => false, 'vest' => true,
                'in_danger_zone' => false, 'violations' => ['NO_HELMET'],
                'risk_score' => 40, 'risk_level' => 'WARNING', 'box' => [1, 2, 100, 200],
                'evidence_score' => 1,
            ]],
            'summary' => ['total_violation' => 1, 'highest_risk' => 'WARNING'],
            'annotated_image_base64' => base64_encode('initial-frame'),
        ];

        $this->postJson('/api/detections', $payload)->assertCreated();
        $this->postJson('/api/detections', [
            ...$payload,
            'annotated_image_base64' => base64_encode('duplicate-frame'),
        ])->assertOk()->assertJsonPath('data.suppressed_alerts', 1);

        Storage::disk('public')->assertCount('detections/'.now()->format('Y/m/d'), 1);
    }
}
