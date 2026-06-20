<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class DangerZone extends Model
{
    protected $fillable = [
        'camera_id',
        'zone_name',
        'description',
        'coordinates',
        'status'
    ];

    protected function casts(): array
    {
        return ['coordinates' => 'array', 'status' => 'boolean'];
    }

    public function camera(): BelongsTo
    {
        return $this->belongsTo(Camera::class);
    }
}
