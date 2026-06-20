<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\DetectionController;
use App\Http\Controllers\Api\DashboardController;
use App\Http\Controllers\Api\CameraController;
use App\Http\Controllers\Api\DangerZoneController;
use App\Http\Controllers\Api\AlertController;

Route::get('/detections', [DetectionController::class, 'index']);
Route::post('/detections', [DetectionController::class, 'store']);
Route::post('/detections/resolve', [DetectionController::class, 'resolve']);
Route::post('/detections/evidence', [DetectionController::class, 'updateEvidence']);
Route::post('/detect-image', [DetectionController::class, 'detectImage']);
Route::get('/health', [DetectionController::class, 'health']);

Route::get('/dashboard', [DashboardController::class, 'index']);

Route::get('/cameras', [CameraController::class, 'index']);
Route::post('/cameras', [CameraController::class, 'store']);

Route::get('/danger-zones', [DangerZoneController::class, 'index']);
Route::post('/danger-zones', [DangerZoneController::class, 'store']);

Route::get('/alerts', [AlertController::class, 'index']);
Route::post('/alerts', [AlertController::class, 'store']);
Route::put('/alerts/{id}', [AlertController::class, 'update']);

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});
