<template>
  <div class="p-6 bg-slate-50 dark:bg-slate-950 min-h-screen space-y-6">
    <div><h1 class="text-3xl font-bold text-slate-800 dark:text-white">Zona Bahaya</h1><p class="text-slate-500">Zona aktif dikirim ke AI berdasarkan kamera yang dipilih saat deteksi.</p></div>
    <div class="bg-amber-50 border border-amber-200 text-amber-900 rounded-xl p-4 text-sm"><b>Format koordinat:</b> x1/y1 adalah sudut kiri atas dan x2/y2 sudut kanan bawah dalam piksel gambar kamera.</div>
    <form @submit.prevent="addZone" class="bg-white dark:bg-slate-900 border dark:border-slate-800 rounded-2xl p-5 grid md:grid-cols-2 xl:grid-cols-3 gap-3">
      <input v-model.trim="form.zone_name" required placeholder="Nama zona" class="input" />
      <select v-model="form.camera_id" class="input"><option value="">Semua kamera</option><option v-for="camera in cameras" :key="camera.id" :value="camera.id">{{ camera.code }} — {{ camera.location }}</option></select>
      <input v-model.trim="form.description" placeholder="Deskripsi (opsional)" class="input" />
      <input v-model.number="form.x1" required min="0" type="number" placeholder="x1" class="input" />
      <input v-model.number="form.y1" required min="0" type="number" placeholder="y1" class="input" />
      <input v-model.number="form.x2" required min="0" type="number" placeholder="x2" class="input" />
      <input v-model.number="form.y2" required min="0" type="number" placeholder="y2" class="input" />
      <label class="flex items-center gap-2 text-sm dark:text-slate-200"><input v-model="form.status" type="checkbox" /> Aktif</label>
      <button :disabled="saving" class="bg-amber-500 text-slate-950 font-bold py-2 rounded-xl disabled:opacity-50">{{ saving ? 'Menyimpan…' : 'Tambah zona' }}</button>
      <p v-if="error" class="text-sm text-rose-600 xl:col-span-3">{{ error }}</p>
    </form>
    <div class="grid md:grid-cols-2 xl:grid-cols-3 gap-4"><div v-if="!zones.length" class="text-slate-500">Belum ada zona bahaya.</div><article v-for="z in zones" :key="z.id" class="bg-white dark:bg-slate-900 border dark:border-slate-800 rounded-2xl p-5"><div class="flex justify-between"><h2 class="font-bold text-lg dark:text-white">{{ z.zone_name }}</h2><span :class="z.status?'text-emerald-600':'text-slate-500'" class="text-xs font-bold">{{ z.status?'AKTIF':'NONAKTIF' }}</span></div><p class="text-sm text-slate-500 mt-1">{{ z.camera?.code || 'Semua kamera' }}</p><p class="text-sm text-slate-600 dark:text-slate-300 my-3">{{ z.description || 'Tanpa deskripsi' }}</p><code class="text-xs bg-slate-100 dark:bg-slate-800 dark:text-slate-300 p-2 rounded block">{{ z.coordinates || 'Tanpa koordinat' }}</code></article></div>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useSentraStore } from '../stores/sentraStore'
const store = useSentraStore(); const { zones, cameras } = storeToRefs(store)
const saving = ref(false), error = ref('')
const emptyForm = () => ({ zone_name: '', camera_id: '', description: '', x1: null, y1: null, x2: null, y2: null, status: true })
const form = ref(emptyForm())
async function addZone() {
  if (form.value.x2 <= form.value.x1 || form.value.y2 <= form.value.y1) { error.value = 'x2 dan y2 harus lebih besar dari x1 dan y1.'; return }
  saving.value = true; error.value = ''
  try { await store.addZone({ camera_id: form.value.camera_id || null, zone_name: form.value.zone_name, description: form.value.description || null, coordinates: { x1: form.value.x1, y1: form.value.y1, x2: form.value.x2, y2: form.value.y2 }, status: form.value.status }); form.value = emptyForm() }
  catch (e) { error.value = e.response?.data?.message || e.message } finally { saving.value = false }
}
onMounted(() => Promise.all([store.fetchZones(), store.fetchDashboard()]))
</script>
<style scoped>.input{width:100%;border:1px solid rgb(203 213 225);border-radius:.75rem;padding:.5rem .75rem;background:transparent}</style>
