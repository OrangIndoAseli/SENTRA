<?php

namespace Database\Seeders;

use App\Models\User;
use App\Models\Camera;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // User::factory(10)->create();

        User::factory()->create([
            'name' => 'Test User',
            'email' => 'test@example.com',
        ]);

        Camera::firstOrCreate(
            ['code' => 'CAM-01'],
            ['name' => 'Kamera Utama', 'location' => 'Area Operasional', 'status' => true]
        );
    }
}
