<template>
  <div class="space-y-6 p-6 bg-slate-50 dark:bg-slate-950 min-h-screen transition-colors duration-300">
    
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-slate-800 dark:text-slate-100 tracking-tight">
          Beranda SENTRA
        </h1>
        <p class="text-slate-500 dark:text-slate-400 font-medium">
          Monitoring keselamatan berbasis AI — <span class="text-amber-600 dark:text-yellow-400 font-semibold">Sektor Pertambangan</span>
        </p>
      </div>
      
      <div class="flex gap-2 text-xs font-bold">
        <span 
          :class="health?.ml === 'healthy' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400' : 'bg-rose-100 text-rose-700 dark:bg-rose-950/30 dark:text-rose-400'" 
          class="px-3 py-2 rounded-xl shadow-sm border dark:border-slate-800"
        >
          AI {{ health?.ml || 'checking' }}
        </span>
        <span class="bg-blue-100 text-blue-700 dark:bg-blue-950/30 dark:text-blue-400 px-3 py-2 rounded-xl shadow-sm border dark:border-slate-800">
          {{ stats.online_cameras || 0 }} kamera aktif
        </span>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 xl:grid-cols-3 gap-4">
      <StatCard title="Total Pelanggaran" :value="stats.total_violations || 0" icon="fas fa-chart-bar" />
      <StatCard title="Helmet Tidak Dipakai" :value="stats.helmet_missing || 0" icon="fas fa-hard-hat" />
      <StatCard title="Vest Tidak Dipakai" :value="stats.vest_missing || 0" icon="fas fa-vest" />
    </div>

    <div class="grid lg:grid-cols-2 gap-6">
      
      <section class="panel">
        <h2 class="title text-slate-800 dark:text-yellow-300 transition-colors duration-200">
          Alert Aktif
        </h2>
        <p v-if="!activeAlerts.length" class="empty dark:text-slate-500">
          Belum ada alert aktif.
        </p>
        
        <div 
          v-for="alert in activeAlerts" 
          :key="alert.id" 
          class="flex items-start justify-between gap-3 border-l-4 border-rose-500 bg-rose-50 dark:bg-rose-950/20 p-3.5 rounded-r-xl mb-3 transition hover:bg-rose-100/40 dark:hover:bg-rose-950/30"
        >
          <div class="min-w-0">
            <p class="font-semibold text-rose-700 dark:text-rose-400 text-sm truncate">
              {{ alert.message }}
            </p>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-mono">
              📍 {{ alert.violation?.camera?.code || 'Kamera' }} · {{ formatDate(alert.created_at) }}
            </p>
          </div>
          <button 
            @click="store.resolveAlert(alert.id)" 
            class="text-xs bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 px-2.5 py-1.5 rounded-xl shadow-sm transition shrink-0 font-bold"
          >
            Selesaikan
          </button>
        </div>
      </section>

      <section class="panel">
        <h2 class="title text-slate-800 dark:text-yellow-300 transition-colors duration-200">
          Deteksi Terbaru
        </h2>
        <p v-if="!violations.length" class="empty dark:text-slate-500">
          Belum ada hasil deteksi.
        </p>
        
        <div 
          v-for="item in violations.slice(0, 8)" 
          :key="item.id" 
          class="flex justify-between items-center gap-3 py-3 border-b border-slate-100 dark:border-slate-800 last:border-0 transition hover:bg-slate-50/30 dark:hover:bg-slate-800/10 px-1 rounded-lg"
        >
          <div class="min-w-0">
            <p class="font-semibold text-slate-800 dark:text-slate-200 text-sm truncate">
              {{ labels[item.violation_type] }}
            </p>
            <p class="text-xs text-slate-500 dark:text-slate-400 font-mono mt-0.5">
              {{ item.camera?.code }} · ID Worker: {{ item.worker_id }}
            </p>
          </div>
          <span 
            class="text-xs font-black font-mono tracking-wider shrink-0 px-2 py-0.5 rounded" 
            :class="item.risk_level === 'CRITICAL' ? 'text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/20' : 'text-amber-600 dark:text-yellow-400 bg-amber-50 dark:bg-amber-950/20'"
          >
            {{ item.risk_level }}
          </span>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import StatCard from '../components/StatCard.vue'
import { useSentraStore } from '../stores/sentraStore'

const store = useSentraStore()
const { stats, alerts, violations, health } = storeToRefs(store)

const activeAlerts = computed(() => alerts.value.filter(a => a.status === 'active'))
const labels = { 
  helmet_missing: 'Helmet tidak dipakai', 
  vest_missing: 'Safety vest tidak dipakai', 
  danger_zone: 'Memasuki zona bahaya' 
}

const formatDate = value => new Date(value).toLocaleString('id-ID')

onMounted(async () => { 
  await Promise.allSettled([store.fetchDashboard(), store.checkHealth()]) 
})
</script>

<style scoped>
/* PANEL UTAMA: Menggunakan sistem class bawaan untuk transisi warna */
.panel {
  background: white;
  border-radius: 1rem;
  padding: 1.25rem;
  border: 1px solid rgb(226 232 240);
  transition: all 0.3s ease;
}
.title {
  font-weight: 700;
  font-size: 1.125rem;
  margin-bottom: 1rem;
}
.empty {
  color: rgb(255, 255, 255);
  font-size: .875rem;
}

/* INTEGRASI DENGAN KLAS UTAMA BLACK MODE */
:deep(.dark) .panel,
.dark .panel {
  background: rgb(15 23 42) !important;
  border-color: rgb(30 41 59) !important;
}
</style>