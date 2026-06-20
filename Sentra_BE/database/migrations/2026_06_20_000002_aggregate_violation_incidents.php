<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('violations', function (Blueprint $table) {
            $table->timestamp('last_detected_at')->nullable()->after('detected_at');
            $table->timestamp('resolved_at')->nullable()->after('last_detected_at');
            $table->unsignedInteger('occurrence_count')->default(1)->after('resolved_at');
            $table->index(['camera_id', 'worker_id', 'violation_type', 'resolved_at']);
        });
    }

    public function down(): void
    {
        Schema::table('violations', function (Blueprint $table) {
            $table->dropIndex(['camera_id', 'worker_id', 'violation_type', 'resolved_at']);
            $table->dropColumn(['last_detected_at', 'resolved_at', 'occurrence_count']);
        });
    }
};
