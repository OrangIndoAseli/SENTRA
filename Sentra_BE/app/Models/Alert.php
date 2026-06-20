<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Alert extends Model
{
    protected $fillable = [
        'violation_id',
        'message',
        'status',
    ];

    public function violation(): BelongsTo
    {
        return $this->belongsTo(Violation::class);
    }
}
