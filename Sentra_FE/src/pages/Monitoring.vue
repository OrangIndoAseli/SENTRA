<template>
  <div class="space-y-6 p-6 bg-slate-50 dark:bg-slate-950 min-h-screen transition-colors duration-300">
    
    <AlertPopup 
      v-if="notification" 
      :key="notification.id" 
      :type="notification.type" 
      title="Pelanggaran terkonfirmasi" 
      :message="notification.message" 
      :location="cameraCode" 
    />
    
    <div>
      <h1 class="text-3xl font-bold text-slate-800 dark:text-slate-100 tracking-tight">Live Monitoring</h1>
      <p class="text-slate-500 dark:text-slate-400 font-medium">Video berjalan terus. Database hanya menerima bukti saat pelanggaran dikonfirmasi.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6">
      
      <section class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 p-5 space-y-4 shadow-sm transition-colors duration-300">
        
        <div class="space-y-2">
          <label class="block text-sm font-semibold text-slate-700 dark:text-slate-200">Kode kamera</label>
          <select v-model="cameraCode" :disabled="cameraActive" class="w-full border border-slate-200 dark:border-slate-700 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-hidden focus:border-amber-500">
            <option value="CAM-01">CAM-01</option>
            <option v-for="camera in cameras" :key="camera.id" :value="camera.code">{{ camera.code }} — {{ camera.location }}</option>
          </select>
        </div>

        <details class="rounded-xl border border-slate-200 dark:border-slate-700 p-3 text-sm text-slate-700 dark:text-slate-200">
          <summary class="cursor-pointer font-bold select-none text-slate-800 dark:text-slate-200">Tambah kamera</summary>
          <div class="mt-3 space-y-2">
            <input v-model.trim="newCamera.code" placeholder="Kode, contoh CAM-02" class="input dark:text-slate-100" />
            <input v-model.trim="newCamera.name" placeholder="Nama kamera" class="input dark:text-slate-100" />
            <input v-model.trim="newCamera.location" placeholder="Lokasi" class="input dark:text-slate-100" />
            <input v-model.trim="newCamera.stream_url" placeholder="RTSP URL (untuk integrasi CCTV server)" class="input dark:text-slate-100" />
            <button @click="addCamera" :disabled="cameraSaving" class="w-full border border-amber-500 hover:bg-amber-500 hover:text-slate-950 text-amber-600 font-bold py-2 rounded-xl transition duration-150 disabled:opacity-50 cursor-pointer">
              {{ cameraSaving ? 'Menyimpan…' : 'Simpan kamera' }}
            </button>
          </div>
        </details>

        <div class="rounded-xl border border-slate-200 dark:border-slate-700 p-4 space-y-3">
          <div>
            <p class="text-sm font-bold text-slate-800 dark:text-slate-200">Kamera browser</p>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Untuk uji webcam. Tidak ada frame normal yang disimpan ke database.</p>
          </div>
          
          <button v-if="!cameraActive" @click="startWebcam" class="w-full border border-emerald-500 hover:bg-emerald-500 hover:text-white text-emerald-600 dark:text-emerald-400 font-bold py-2.5 rounded-xl transition cursor-pointer">Nyalakan webcam</button>
          <button v-else @click="stopWebcam" class="w-full border border-rose-500 hover:bg-rose-500 hover:text-white text-rose-600 font-bold py-2.5 rounded-xl transition cursor-pointer">Matikan webcam</button>
          
          <template v-if="cameraActive">
            <div class="flex gap-2">
              <button @click="toggleMonitoring" class="flex-1 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold py-2.5 rounded-xl transition cursor-pointer">
                {{ monitoring ? 'Hentikan pemantauan' : 'Mulai pemantauan AI' }}
              </button>
              <!-- <select v-model.number="intervalMs" :disabled="monitoring" class="border border-slate-200 dark:border-slate-700 dark:bg-slate-800 rounded-xl px-2 text-sm text-slate-700 dark:text-slate-200">
                <option :value="1000">1 dtk</option>
                <option :value="2000">2 dtk</option>
                <option :value="3000">3 dtk</option>
              </select> -->
            </div>
            
            <div class="grid grid-cols-2 text-xs text-slate-500 dark:text-slate-400 gap-2 font-medium">
              <span>AI Engine: <b :class="loading ? 'text-amber-500' : 'text-emerald-500 dark:text-emerald-400'">{{ loading ? 'analisis' : 'siap' }}</b></span>
              <span class="text-right font-mono">{{ lastLatencyMs ? `${lastLatencyMs} ms` : 'menunggu frame' }}</span>
            </div>
          </template>
        </div>
        
        <!-- <div class="rounded-xl bg-slate-100 dark:bg-slate-800/60 border dark:border-slate-800 p-3 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
          <strong class="text-slate-800 dark:text-slate-200 font-bold block mb-0.5">⚠️ Aturan Event K3:</strong> 
          Pelanggaran harus terlihat pada 3 analisis berturut-turut. Satu insiden menyimpan bukti awal dan hanya mengganti bukti terbaik saat frame baru minimal 15% lebih jelas.
        </div> -->
        <p v-if="error" class="text-sm text-rose-600 bg-rose-50 dark:bg-rose-950/20 border dark:border-rose-900/30 p-3 rounded-xl font-medium">{{ error }}</p>
      </section>

      <section class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 p-5 space-y-4 shadow-sm transition-colors duration-300">
        
        <div class="aspect-video bg-slate-950 rounded-xl overflow-hidden flex items-center justify-center relative border dark:border-slate-800">
          <video ref="video" v-show="cameraActive" autoplay playsinline muted class="w-full h-full object-contain"></video>
          <canvas ref="overlayCanvas" class="absolute inset-0 w-full h-full pointer-events-none"></canvas>
          
          <p v-if="!cameraActive" class="text-slate-500 dark:text-slate-600 font-medium">Nyalakan webcam browser di panel kiri untuk memulai pemantauan</p>
          <span v-if="monitoring" class="absolute top-3 right-3 bg-rose-600 text-white text-xs font-black px-3 py-1.5 rounded-full shadow-md animate-pulse">LIVE AI</span>
        </div>
        
        <canvas ref="canvas" class="hidden"></canvas>

        <div v-if="result" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="metric border dark:border-slate-800">
            <b class="dark:text-yellow-400">{{ stats.total_violations || 0 }}</b>
            <span class="dark:text-yellow-300">Total Pelanggaran</span>
          </div>
          <div class="metric border dark:border-slate-800">
            <b class="dark:text-yellow-400">{{ stats.helmet_missing || 0 }}</b>
            <span class="dark:text-yellow-300">Helmet Missing</span>
          </div>
          <div class="metric border dark:border-slate-800">
            <b class="dark:text-yellow-400">{{ lastDetectionAt || '-' }}</b>
            <span class="dark:text-yellow-300">Deteksi Terakhir</span>
          </div>
        </div>

        <div v-for="worker in result?.detections || []" :key="worker.worker_id" class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800 border dark:border-slate-700/50 flex flex-wrap justify-between items-center gap-2 text-sm transition hover:bg-slate-100 dark:hover:bg-slate-800/80">
          <div class="flex items-center gap-2">
            <i class="fas fa-user text-xs text-slate-400"></i>
            <b class="font-bold text-slate-700 dark:text-slate-200">{{ worker.worker_id }}</b>
          </div>
          <div class="flex gap-4 text-xs text-slate-600 dark:text-slate-300">
            <span>Helmet: <strong :class="worker.helmet ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-500 font-bold'">{{ worker.helmet ? 'OK' : 'Tidak' }}</strong></span>
            <span>Vest: <strong :class="worker.vest ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-500 font-bold'">{{ worker.vest ? 'OK' : 'Tidak' }}</strong></span>
          </div>
          <span class="text-xs font-black tracking-wide font-mono px-2 py-0.5 rounded-md" :class="worker.violations.length ? 'text-rose-600 bg-rose-50 dark:bg-rose-950/30 dark:text-rose-400' : 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/30 dark:text-emerald-400'">
            {{ worker.violations.join(', ') || 'AMAN' }}
          </span>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { storeToRefs } from 'pinia'
import { useSentraStore } from '../stores/sentraStore'
import AlertPopup from '../components/AlertPopup.vue'

const store = useSentraStore()
const { cameras, loading, error, detectionResult: result, stats } = storeToRefs(store)

const cameraCode = ref('CAM-01')
const newCamera = ref({ code: '', name: '', location: '', stream_url: '' })
const cameraSaving = ref(false)

const video = ref(null)
const canvas = ref(null)
const overlayCanvas = ref(null)
const cameraActive = ref(false)
const monitoring = ref(false)
const intervalMs = ref(1000)
const lastLatencyMs = ref(null)
const lastDetectionAt = ref('')
const notification = ref(null)

let mediaStream = null
let detectionTimer = null
let socket = null
let frameSentAt = 0

async function addCamera(){ 
  if(!newCamera.value.code || !newCamera.value.name || !newCamera.value.location) return
  cameraSaving.value = true
  try { 
    const camera = await store.addCamera(newCamera.value)
    cameraCode.value = camera.code
    newCamera.value = { code: '', name: '', location: '', stream_url: '' } 
  } catch(e) { 
    store.error = e.response?.data?.message || e.message 
  } finally { 
    cameraSaving.value = false 
  } 
}

async function startWebcam(){ 
  try { 
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false })
    cameraActive.value = true
    await new Promise(resolve => requestAnimationFrame(resolve))
    video.value.srcObject = mediaStream
    await video.value.play() 
  } catch(e) { 
    store.error = 'Webcam tidak dapat diakses. Izinkan kamera pada browser lalu coba lagi.' 
  } 
}

function stopMonitoring(){ 
  if(detectionTimer) clearTimeout(detectionTimer)
  detectionTimer = null
  monitoring.value = false
  if(socket){ socket.close(); socket = null } 
}

function clearOverlay(){
  const context = overlayCanvas.value?.getContext('2d')
  if(context) context.clearRect(0, 0, overlayCanvas.value.width, overlayCanvas.value.height)
}

function stopWebcam(){ 
  stopMonitoring()
  if(mediaStream){ mediaStream.getTracks().forEach(track => track.stop()); mediaStream = null } 
  if(video.value) video.value.srcObject = null
  cameraActive.value = false
  clearOverlay() 
}

function scheduleNext(){ 
  if(monitoring.value) detectionTimer = setTimeout(sendVideoFrame, intervalMs.value) 
}

function drawBoxes(detections){
  if(!overlayCanvas.value || !video.value) return
  const output = overlayCanvas.value, context = output.getContext('2d'), width = video.value.clientWidth, height = video.value.clientHeight, dpr = window.devicePixelRatio || 1
  output.width = width * dpr
  output.height = height * dpr
  context.scale(dpr, dpr)
  context.clearRect(0, 0, width, height)
  
  if(!canvas.value.width) return
  const sourceRatio = canvas.value.width / canvas.value.height, viewRatio = width / height, contentWidth = viewRatio > sourceRatio ? height * sourceRatio : width, contentHeight = viewRatio > sourceRatio ? height : width / sourceRatio, offsetX = (width - contentWidth) / 2, offsetY = (height - contentHeight) / 2
  
  const renderBox = (box, label, color) => {
    if(!box) return
    const [x1, y1, x2, y2] = box, x = offsetX + (x1 / canvas.value.width) * contentWidth, y = offsetY + (y1 / canvas.value.height) * contentHeight, w = ((x2 - x1) / canvas.value.width) * contentWidth, h = ((y2 - y1) / canvas.value.height) * contentHeight
    context.strokeStyle = color
    context.lineWidth = 3
    context.strokeRect(x, y, w, h)
    context.font = 'bold 13px sans-serif'
    context.fillStyle = color
    context.fillRect(x, Math.max(0, y - 22), context.measureText(label).width + 10, 22)
    context.fillStyle = '#fff'
    context.fillText(label, x + 5, Math.max(15, y - 7))
  }
  
  for(const worker of detections){
    if(worker.violations.length) renderBox(worker.box, worker.violations.join(', '), '#ef4444')
    renderBox(worker.helmet_box, 'HELMET', '#22c55e')
    renderBox(worker.vest_box, 'VEST', '#22c55e')
  }
}

async function sendVideoFrame(){ 
  if(!monitoring.value || !video.value?.videoWidth || socket?.readyState !== WebSocket.OPEN){ scheduleNext(); return } 
  const maxWidth = 1280, scale = Math.min(1, maxWidth / video.value.videoWidth)
  canvas.value.width = Math.round(video.value.videoWidth * scale)
  canvas.value.height = Math.round(video.value.videoHeight* scale)
  canvas.value.getContext('2d').drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height)
  const blob = await new Promise(resolve => canvas.value.toBlob(resolve, 'image/jpeg', 0.92))
  if(!blob){ scheduleNext(); return } 
  frameSentAt = performance.now()
  socket.send(await blob.arrayBuffer()) 
}

function startMonitoring(){ 
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
  socket = new WebSocket(`${protocol}://127.0.0.1:8001/ws/detect?camera_code=${encodeURIComponent(cameraCode.value)}`)
  
  socket.onopen = () => { monitoring.value = true; sendVideoFrame() }
  
  socket.onmessage = async event => {
    const data = JSON.parse(event.data)
    if(data.error){ store.error = data.error; scheduleNext(); return } 
    store.detectionResult = data.result
    drawBoxes(data.result.detections)
    lastLatencyMs.value = Math.round(performance.now() - frameSentAt)
    lastDetectionAt.value = new Date().toLocaleTimeString('id-ID')
    
    if(data.event_saved){
      await store.fetchDashboard()
      const workers = data.result.detections.filter(worker => data.event_workers.includes(worker.worker_id))
      const codes = [...new Set(workers.flatMap(worker => worker.violations))]
      notification.value = { 
        id: Date.now(), 
        type: workers.some(worker => worker.risk_level === 'CRITICAL') ? 'danger' : 'warning', 
        message: `${workers.map(worker => worker.worker_id).join(', ')}: ${codes.join(', ')}` 
      }
      setTimeout(() => notification.value = null, 7000)
    }
    scheduleNext()
  }
  
  socket.onerror = () => { store.error = 'Koneksi live AI terputus.' }
  socket.onclose = () => { if(monitoring.value){ monitoring.value = false; store.error = 'Live AI dihentikan. Coba mulai kembali.' } } 
}

function toggleMonitoring(){ if(monitoring.value){ stopMonitoring(); return }; startMonitoring() }

onMounted(() => store.fetchDashboard())
onBeforeUnmount(stopWebcam)
</script>

<style scoped>
.input {
  width: 100%;
  border: 1px solid rgb(203 213 225);
  border-radius: .75rem;
  padding: .5rem .75rem;
  background: transparent;
  transition: all 0.2s ease;
}
.input:focus {
  border-color: rgb(245 158 11);
  outline: none;
}
:deep(.dark) .input,
.dark .input {
  border-color: rgb(51 65 85);
}

/* Base style untuk metric (Mode Terang) */
.metric {
  display: flex;
  flex-direction: column;
  background: rgb(248 250 252);
  padding: .75rem;
  border-radius: .75rem;
  transition: all 0.2s ease;
}
.metric b {
  font-size: 1.25rem;
  color: rgb(30 41 59);
}
.metric span {
  font-size: .75rem;
  color: rgb(100 116 139);
}

/* --- PAKSA WARNA KUNING DI MODE GELAP (DARK MODE) --- */
:deep(.dark) .metric,
.dark .metric {
  background: rgb(30 41 59) !important;
}

/* Override teks 'b' menjadi kuning cerah */
:deep(.dark) .metric b,
.dark .metric b {
  font-size: 1.25rem;
  color: #facc15 !important; /* Setara text-yellow-400 */
}

/* Override teks 'span' menjadi kuning soft */
:deep(.dark) .metric span,
.dark .metric span {
  font-size: .75rem;
  color: #fde047 !important; /* Setara text-yellow-300 */
}
</style>