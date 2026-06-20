<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Violation;
use App\Models\Alert;
use App\Models\Camera;
use Illuminate\Http\JsonResponse;

class DashboardController extends Controller
{
    public function index(): JsonResponse
    {
        $totalViolations = Violation::count();

        $helmetMissing = Violation::where(
            'violation_type',
            'helmet_missing'
        )->count();

        $vestMissing = Violation::where(
            'violation_type',
            'vest_missing'
        )->count();

        $dangerZone = Violation::where(
            'violation_type',
            'danger_zone'
        )->count();

        return response()->json([
            'success' => true,
            'message' => 'Dashboard data retrieved successfully',

            'data' => [
                'stats' => [
                    'total_violations' => $totalViolations,
                    'helmet_missing' => $helmetMissing,
                    'vest_missing' => $vestMissing,
                    'danger_zone' => $dangerZone,
                    'active_alerts' => Alert::where('status', 'active')->count(),
                    'online_cameras' => Camera::where('status', true)->count(),
                ],
                'alerts' => Alert::with('violation.camera')->latest()->limit(8)->get(),
                'violations' => Violation::with('camera')->latest('detected_at')->limit(10)->get(),
                'cameras' => Camera::orderBy('code')->get(),
            ]
        ], 200);
    }
}
