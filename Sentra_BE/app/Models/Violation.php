<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasOne;

class Violation extends Model
{
    protected $fillable = [
        'camera_id',
        'worker_id',
        'violation_type',
        'risk_score',
        'risk_level',
        'screenshot',
        'best_screenshot',
        'best_evidence_score',
        'detection_data',
        'detected_at',
        'last_detected_at',
        'resolved_at',
        'occurrence_count',
    ];

    protected function casts(): array
    {
        return [
            'detection_data' => 'array',
            'detected_at' => 'datetime',
            'last_detected_at' => 'datetime',
            'resolved_at' => 'datetime',
        ];
    }

    public function alert(): HasOne
    {
        return $this->hasOne(Alert::class);
    }

    public function camera(): BelongsTo
    {
        return $this->belongsTo(Camera::class);
    }
}
