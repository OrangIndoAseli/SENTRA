<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\DangerZone;
use Illuminate\Http\Request;

class DangerZoneController extends Controller
{
    public function index()
    {
        return response()->json([
            'success' => true,
            'data' => DangerZone::with('camera')->get()
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'camera_id' => ['nullable', 'exists:cameras,id'],
            'zone_name' => ['required', 'string', 'max:255'],
            'description' => ['nullable', 'string'],
            'coordinates' => ['nullable', 'array'],
            'status' => ['nullable', 'boolean'],
        ]);
        $dangerZone = DangerZone::create($validated + ['status' => true]);

        return response()->json([
            'success' => true,
            'message' => 'Danger Zone berhasil ditambahkan',
            'data' => $dangerZone
        ]);
    }
}
