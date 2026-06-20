<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Alert;
use App\Models\Camera;
use App\Models\DangerZone;
use App\Models\Violation;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class DetectionController extends Controller
{
    public function index(): JsonResponse
    {
        return response()->json([
            'success' => true,
            'data' => Violation::with(['alert', 'camera'])->latest('detected_at')->limit(200)->get(),
        ]);
    }

    public function health(): JsonResponse
    {
        try {
            $ml = Http::timeout(5)->get(config('services.sentra_ml.url').'/health');
        } catch (ConnectionException) {
            $ml = null;
        }

        return response()->json([
            'success' => true,
            'backend' => 'healthy',
            'ml' => $ml?->successful() ? 'healthy' : 'unavailable',
        ]);
    }

    public function detectImage(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'image' => ['required', 'image', 'max:10240'],
            'camera_code' => ['nullable', 'string', 'max:100'],
            'persist' => ['nullable', 'boolean'],
        ]);
        $image = $request->file('image');
        $cameraCode = $validated['camera_code'] ?? 'CAM-01';
        $query = $this->detectionQuery($cameraCode);

        try {
            $response = Http::timeout(config('services.sentra_ml.timeout'))
                ->attach('file', file_get_contents($image->getRealPath()), $image->getClientOriginalName())
                ->post(config('services.sentra_ml.url').'/detect-image?'.http_build_query($query));
        } catch (ConnectionException $exception) {
            return response()->json([
                'success' => false,
                'message' => 'Layanan AI tidak dapat dihubungi. Pastikan SENTRA-ML berjalan di port 8001.',
                'detail' => $exception->getMessage(),
            ], 503);
        }

        if (! $response->successful()) {
            return response()->json([
                'success' => false,
                'message' => 'Layanan AI gagal memproses gambar.',
                'detail' => $response->json() ?? $response->body(),
            ], 502);
        }

        if (! ($validated['persist'] ?? true)) {
            return response()->json([
                'success' => true,
                'data' => ['result' => $response->json()],
            ]);
        }

        return $this->persistMlPayload($response->json());
    }

    public function store(Request $request): JsonResponse
    {
        $payload = $request->validate([
            'camera_code' => ['required', 'string', 'max:100'],
            'worker_count' => ['required', 'integer', 'min:0'],
            'detections' => ['required', 'array'],
            'detections.*.worker_id' => ['required', 'string'],
            'detections.*.helmet' => ['required', 'boolean'],
            'detections.*.vest' => ['required', 'boolean'],
            'detections.*.in_danger_zone' => ['required', 'boolean'],
            'detections.*.violations' => ['required', 'array'],
            'detections.*.risk_score' => ['required', 'integer'],
            'detections.*.risk_level' => ['required', 'string'],
            'detections.*.box' => ['required', 'array', 'size:4'],
            'detections.*.evidence_score' => ['nullable', 'numeric', 'min:0'],
            'summary' => ['required', 'array'],
            'annotated_image_base64' => ['nullable', 'string'],
        ]);

        return $this->persistMlPayload($payload);
    }

    public function resolve(Request $request): JsonResponse
    {
        $payload = $request->validate([
            'camera_code' => ['required', 'string', 'max:100'],
            'worker_ids' => ['required', 'array', 'min:1'],
            'worker_ids.*' => ['required', 'string'],
        ]);
        $cameraId = $this->cameraId($payload['camera_code']);
        if (! $cameraId) {
            return response()->json(['success' => true, 'resolved' => 0]);
        }

        $violations = Violation::where('camera_id', $cameraId)
            ->whereIn('worker_id', $payload['worker_ids'])
            ->whereNull('resolved_at')
            ->get();
        foreach ($violations as $violation) {
            $violation->update(['resolved_at' => now(), 'last_detected_at' => now()]);
            $violation->alert?->update(['status' => 'resolved']);
        }

        return response()->json(['success' => true, 'resolved' => $violations->count()]);
    }

    public function updateEvidence(Request $request): JsonResponse
    {
        $payload = $request->validate([
            'camera_code' => ['required', 'string', 'max:100'],
            'worker_id' => ['required', 'string'],
            'evidence_score' => ['required', 'numeric', 'min:0'],
            'annotated_image_base64' => ['required', 'string'],
        ]);
        $cameraId = $this->cameraId($payload['camera_code']);
        if (! $cameraId) {
            return response()->json(['success' => true, 'updated' => 0]);
        }

        $violations = Violation::where('camera_id', $cameraId)
            ->where('worker_id', $payload['worker_id'])
            ->whereNull('resolved_at')
            ->get()
            ->filter(fn (Violation $violation) => $violation->best_evidence_score === null
                || (float) $payload['evidence_score'] >= (float) $violation->best_evidence_score * 1.15);
        if ($violations->isEmpty()) {
            return response()->json(['success' => true, 'updated' => 0]);
        }

        $path = $this->storeScreenshot($payload['annotated_image_base64']);
        $replacedPaths = [];
        foreach ($violations as $violation) {
            if ($violation->best_screenshot && $violation->best_screenshot !== $violation->screenshot) {
                $replacedPaths[] = $violation->best_screenshot;
            }
            $violation->update(['best_screenshot' => $path, 'best_evidence_score' => $payload['evidence_score'], 'last_detected_at' => now()]);
        }
        foreach (array_unique($replacedPaths) as $replacedPath) {
            Storage::disk('public')->delete($replacedPath);
        }
        return response()->json(['success' => true, 'updated' => $violations->count()]);
    }

    private function persistMlPayload(array $payload): JsonResponse
    {
        $camera = Camera::firstOrCreate(
            ['code' => $payload['camera_code']],
            ['name' => $payload['camera_code'], 'location' => 'Belum diatur', 'status' => true]
        );

        $created = DB::transaction(function () use ($payload, $camera) {
            $violations = collect();
            $alerts = collect();
            $suppressed = 0;
            $screenshot = null;

            foreach ($payload['detections'] as $worker) {
                foreach ($worker['violations'] as $code) {
                    $type = $this->mapViolationType($code);
                    if (! $type) {
                        continue;
                    }
                    $openViolation = Violation::where('camera_id', $camera->id)
                        ->where('worker_id', $worker['worker_id'])
                        ->where('violation_type', $type)
                        ->whereNull('resolved_at')
                        ->latest('detected_at')
                        ->first();
                    if ($openViolation) {
                        $openViolation->update([
                            'last_detected_at' => now(),
                            'occurrence_count' => $openViolation->occurrence_count + 1,
                            'risk_score' => $worker['risk_score'],
                            'risk_level' => $worker['risk_level'],
                        ]);
                        $suppressed++;
                        continue;
                    }
                    $screenshot ??= $this->storeScreenshot($payload['annotated_image_base64'] ?? null);
                    $violation = Violation::create([
                        'camera_id' => $camera->id,
                        'worker_id' => $worker['worker_id'],
                        'violation_type' => $type,
                        'risk_score' => $worker['risk_score'],
                        'risk_level' => $worker['risk_level'],
                        'screenshot' => $screenshot,
                        'best_screenshot' => $screenshot,
                        'best_evidence_score' => $worker['evidence_score'] ?? null,
                        'detection_data' => $worker,
                        'detected_at' => now(),
                        'last_detected_at' => now(),
                    ]);
                    $alert = Alert::create([
                        'violation_id' => $violation->id,
                        'message' => $this->alertMessage($type),
                        'status' => 'active',
                    ]);
                    $violations->push($violation->load('camera'));
                    $alerts->push($alert);
                }
            }

            return compact('violations', 'alerts', 'suppressed', 'screenshot');
        });

        unset($payload['annotated_image_base64']);
        $payload['annotated_image_url'] = $created['screenshot'] ? asset('storage/'.$created['screenshot']) : null;

        return response()->json([
            'success' => true,
            'message' => $created['violations']->isEmpty()
                ? ($created['suppressed'] ? 'Deteksi selesai; alert duplikat masih dalam cooldown.' : 'Deteksi selesai, tidak ada pelanggaran.')
                : 'Deteksi selesai dan pelanggaran tersimpan.',
            'data' => [
                'result' => $payload,
                'violations' => $created['violations'],
                'alerts' => $created['alerts'],
                'suppressed_alerts' => $created['suppressed'],
            ],
        ], $created['violations']->isEmpty() ? 200 : 201);
    }

    private function cameraId(string $code): ?int
    {
        return Camera::where('code', $code)->value('id');
    }

    private function detectionQuery(string $cameraCode): array
    {
        $cameraId = $this->cameraId($cameraCode);
        $zone = $cameraId
            ? DangerZone::where('status', true)->where('camera_id', $cameraId)->latest()->first()
            : null;

        $zone ??= DangerZone::where('status', true)->whereNull('camera_id')->latest()->first();
        $query = ['camera_code' => $cameraCode];

        if (! is_array($zone?->coordinates)) {
            return $query;
        }

        foreach (['x1', 'y1', 'x2', 'y2'] as $key) {
            if (isset($zone->coordinates[$key]) && is_numeric($zone->coordinates[$key])) {
                $query['zone_'.$key] = (int) $zone->coordinates[$key];
            }
        }

        return $query;
    }

    private function storeScreenshot(?string $base64): ?string
    {
        if (! $base64) {
            return null;
        }
        $content = base64_decode(preg_replace('#^data:image/\w+;base64,#i', '', $base64), true);
        if ($content === false) {
            return null;
        }
        $path = 'detections/'.now()->format('Y/m/d').'/'.Str::uuid().'.jpg';
        Storage::disk('public')->put($path, $content);
        return $path;
    }

    private function mapViolationType(string $code): ?string
    {
        return match ($code) {
            'NO_HELMET' => 'helmet_missing',
            'NO_VEST' => 'vest_missing',
            'DANGER_ZONE_ENTRY' => 'danger_zone',
            default => null,
        };
    }

    private function alertMessage(string $type): string
    {
        return match ($type) {
            'helmet_missing' => 'Pelanggaran APD: helmet tidak dipakai',
            'vest_missing' => 'Pelanggaran APD: safety vest tidak dipakai',
            'danger_zone' => 'Pelanggaran zona: pekerja berada di zona bahaya',
            default => 'Pelanggaran terdeteksi',
        };
    }
}
