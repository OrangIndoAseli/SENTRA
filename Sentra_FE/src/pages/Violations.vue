<template>
  <div class="space-y-6 p-6 bg-slate-50 dark:bg-slate-950 min-h-screen">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-slate-800 dark:text-white">Pelanggaran</h1>
        <p class="text-slate-500">Riwayat insiden aktif dan selesai yang tersimpan di backend.</p>
      </div>
      <button @click="exportCsv" class="bg-slate-900 text-white px-4 py-2 h-fit rounded-lg text-sm">
        Export CSV
      </button>
    </div>

    <div class="bg-white dark:bg-slate-900 rounded-lg border dark:border-slate-800 overflow-x-auto">
      <table class="w-full text-sm text-left">
        <thead class="bg-slate-100 dark:bg-slate-800 text-slate-500">
          <tr>
            <th class="p-4">Mulai</th>
            <th class="p-4">Pelanggaran</th>
            <th class="p-4">Kamera</th>
            <th class="p-4">Status insiden</th>
            <th class="p-4">Bukti</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!violations.length">
            <td colspan="5" class="p-8 text-center text-slate-500">Belum ada pelanggaran.</td>
          </tr>
          <tr v-for="item in violations" :key="item.id" class="border-t dark:border-slate-800">
            <td class="p-4 whitespace-nowrap">{{ formatDate(item.detected_at) }}</td>
            <td class="p-4 font-semibold">
              {{ labels[item.violation_type] || item.violation_type }}
              <small class="block text-slate-500">
                {{ item.worker_id || '-' }} - {{ item.occurrence_count || 1 }} kali terpantau
              </small>
            </td>
            <td class="p-4">
              {{ item.camera?.code || '-' }}
              <small class="block text-slate-500">{{ item.camera?.location || '-' }}</small>
            </td>
            <td class="p-4">
              <span v-if="item.resolved_at" class="font-bold text-emerald-600">Selesai</span>
              <span v-else class="font-bold text-rose-600">Aktif</span>
              <small class="block text-slate-500">
                {{ item.resolved_at ? `Selesai: ${formatDate(item.resolved_at)}` : `Terakhir: ${formatDate(item.last_detected_at || item.detected_at)}` }}
              </small>
            </td>
            <td class="p-4">
              <template v-if="evidenceLinks(item).length">
                <a
                  v-for="link in evidenceLinks(item)"
                  :key="link.label"
                  :href="screenshotUrl(link.path)"
                  target="_blank"
                  class="block underline"
                  :class="link.primary ? 'text-blue-600' : 'text-xs text-slate-500 mt-1'"
                >
                  {{ link.label }}
                </a>
              </template>
              <span v-else>-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSentraStore } from '../stores/sentraStore'

const store = useSentraStore()
const { violations } = storeToRefs(store)
const labels = {
  helmet_missing: 'Helmet tidak dipakai',
  vest_missing: 'Safety vest tidak dipakai',
  danger_zone: 'Memasuki zona bahaya',
}
const apiBase = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

function formatDate(value) {
  return value ? new Date(value).toLocaleString('id-ID') : '-'
}

function screenshotUrl(path) {
  return `${apiBase.replace(/\/api$/, '')}/storage/${path}`
}

function evidenceLinks(item) {
  if (!item.best_screenshot && !item.screenshot) return []
  if (!item.best_screenshot || item.best_screenshot === item.screenshot) {
    return [{ label: 'Bukti awal & terbaik', path: item.screenshot || item.best_screenshot, primary: true }]
  }

  return [
    { label: 'Bukti terbaik', path: item.best_screenshot, primary: true },
    { label: 'Bukti awal', path: item.screenshot, primary: false },
  ]
}

function exportCsv() {
  const rows = [
    ['Mulai', 'Selesai', 'Status', 'Jenis', 'Kamera', 'Pekerja', 'Kemunculan', 'Risiko', 'Bukti terbaik', 'Bukti awal'],
    ...violations.value.map((item) => [
      item.detected_at,
      item.resolved_at || '',
      item.resolved_at ? 'Selesai' : 'Aktif',
      item.violation_type,
      item.camera?.code || '',
      item.worker_id || '',
      item.occurrence_count || 1,
      item.risk_level || '',
      item.best_screenshot || '',
      item.screenshot || '',
    ]),
  ]
  const csv = rows.map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\n')
  const anchor = document.createElement('a')
  anchor.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
  anchor.download = 'sentra-pelanggaran.csv'
  anchor.click()
}

onMounted(() => store.fetchViolations())
</script>
