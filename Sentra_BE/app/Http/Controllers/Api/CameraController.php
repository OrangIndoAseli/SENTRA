<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Camera;
use Illuminate\Http\Request;

class CameraController extends Controller
{
    public function index()
    {
        return response()->json([
            'success' => true,
            'data' => Camera::all()
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'code' => ['required', 'string', 'max:100', 'unique:cameras,code'],
            'name' => ['required', 'string', 'max:255'],
            'location' => ['required', 'string', 'max:255'],
            'stream_url' => ['nullable', 'string'],
            'status' => ['nullable', 'boolean'],
        ]);
        $camera = Camera::create($validated + ['status' => true]);

        return response()->json([
            'success' => true,
            'message' => 'Camera berhasil ditambahkan',
            'data' => $camera
        ]);
    }
}
