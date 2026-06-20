<template>
  <div class="p-6 bg-slate-50 dark:bg-slate-950 min-h-screen transition-colors duration-300">
    <h1 class="text-3xl font-bold text-slate-800 dark:text-yellow-400 tracking-tight">
      Log Sistem
    </h1>
    <p class="text-slate-500 dark:text-yellow-300/70 mb-6 font-medium">
      Timeline aktivitas deteksi dan alert.
    </p>

    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 p-6 shadow-sm">
      <p v-if="!alerts.length" class="text-slate-500 dark:text-yellow-300/60 font-medium py-4">
        Belum ada log.
      </p>

      <div v-else class="space-y-1">
        <div 
          v-for="a in alerts" 
          :key="a.id" 
          class="relative border-l-2 border-slate-200 dark:border-slate-700 pl-5 pb-6 last:pb-0"
        >
          <span 
            class="absolute -left-[8px] top-1.5 w-3.5 h-3.5 rounded-full border-2 border-white dark:border-slate-900" 
            :class="a.status === 'active' ? 'bg-rose-500' : 'bg-emerald-500'"
          ></span>

          <div class="flex justify-between items-start gap-4">
            <div class="space-y-1">
              <p class="font-semibold text-slate-800 dark:text-yellow-400 tracking-tight">
                {{ a.message }}
              </p>
              
              <p class="text-xs text-slate-500 dark:text-yellow-300/80 font-medium font-mono">
                {{ a.violation?.camera?.code || '-' }} · {{ a.violation?.worker_id || '-' }}
              </p>
            </div>

            <span class="text-xs text-slate-400 dark:text-yellow-300/60 whitespace-nowrap font-mono pt-0.5">
              {{ new Date(a.created_at).toLocaleString('id-ID', { dateStyle: 'short', timeStyle: 'short' }) }}
            </span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSentraStore } from '../stores/sentraStore'

const store = useSentraStore()
const { alerts } = storeToRefs(store)

onMounted(() => {
  store.fetchDashboard()
})
</script>