<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Alert;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class AlertController extends Controller
{
    public function index()
    {
        return response()->json([
            'success' => true,
            'data' => Alert::with('violation')->latest()->get()
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'violation_id' => ['nullable', 'integer', 'exists:violations,id'],
            'message' => ['required', 'string'],
            'status' => ['nullable', Rule::in(['active', 'resolved'])],
        ]);

        $alert = Alert::create([
            'violation_id' => $validated['violation_id'] ?? null,
            'message' => $validated['message'],
            'status' => $validated['status'] ?? 'active'
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Alert berhasil dibuat',
            'data' => $alert
        ], 201);
    }

    public function update(Request $request, $id)
    {
        $validated = $request->validate([
            'status' => ['required', Rule::in(['active', 'resolved'])],
        ]);

        $alert = Alert::findOrFail($id);

        $alert->update([
            'status' => $validated['status']
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Status alert berhasil diubah',
            'data' => $alert
        ]);
    }
}
