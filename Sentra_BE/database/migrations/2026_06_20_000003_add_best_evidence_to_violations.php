<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('violations', function (Blueprint $table) {
            $table->string('best_screenshot')->nullable()->after('screenshot');
            $table->decimal('best_evidence_score', 10, 6)->nullable()->after('best_screenshot');
        });
    }

    public function down(): void
    {
        Schema::table('violations', function (Blueprint $table) {
            $table->dropColumn(['best_screenshot', 'best_evidence_score']);
        });
    }
};
