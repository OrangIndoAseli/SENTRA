<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('cameras', function (Blueprint $table) {
            $table->string('code')->nullable()->unique()->after('id');
            $table->text('stream_url')->nullable()->after('location');
        });

        Schema::table('violations', function (Blueprint $table) {
            $table->string('worker_id')->nullable()->after('camera_id');
            $table->unsignedInteger('risk_score')->default(0)->after('violation_type');
            $table->string('risk_level')->default('WARNING')->after('risk_score');
            $table->json('detection_data')->nullable()->after('screenshot');
        });

        Schema::table('danger_zones', function (Blueprint $table) {
            $table->foreignId('camera_id')->nullable()->after('id')->constrained()->nullOnDelete();
            $table->json('coordinates')->nullable()->after('description');
        });
    }

    public function down(): void
    {
        Schema::table('danger_zones', function (Blueprint $table) {
            $table->dropConstrainedForeignId('camera_id');
            $table->dropColumn('coordinates');
        });
        Schema::table('violations', function (Blueprint $table) {
            $table->dropColumn(['worker_id', 'risk_score', 'risk_level', 'detection_data']);
        });
        Schema::table('cameras', function (Blueprint $table) {
            $table->dropUnique(['code']);
            $table->dropColumn(['code', 'stream_url']);
        });
    }
};
