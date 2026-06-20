<template>
  <header class="h-16 bg-slate-950 border-b border-slate-800 flex items-center justify-between px-6 shadow-md sticky top-0 z-50 shrink-0 w-full">
    
    <div class="flex items-center gap-4">
      
      <button 
        @click="$emit('toggle-sidebar')" 
        class="w-10 h-10 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-amber-500 border border-slate-800 flex items-center justify-center transition cursor-pointer active:scale-95 shrink-0"
        title="Buka/Tutup Sidebar"
      >
        <i :class="isCollapsed ? 'fas fa-bars text-base' : 'fas fa-outdent text-base'"></i>
      </button>

      <h2 class="font-bold text-slate-100 tracking-tight text-sm sm:text-base">
        SENTRA Control Center
      </h2>
    </div>

    <div class="flex items-center gap-6">
      <div class="hidden md:flex items-center gap-4 border-r border-slate-800 pr-6 text-xs text-slate-400 font-medium">
        <!-- <div class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50"></span>
          <span>AI Inference: <strong class="text-slate-200 font-mono">98.4%</strong></span>
        </div> -->
        <div class="flex items-center gap-1.5 font-mono bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-lg text-slate-300 font-bold">
          {{ formatDateTime }} WIB
        </div>
      </div>

      <div class="flex items-center gap-4">
        <button @click="toggleDarkMode" class="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800 transition">
          <i :class="isDark ? 'fas fa-sun text-amber-500' : 'fas fa-moon'" class="text-sm"></i>
        </button>

        <div class="flex items-center gap-3">
          <div class="text-right hidden sm:block">
            <span class="block text-xs font-bold text-slate-200 leading-3">Operator On-Duty</span>
            <span class="text-[11px] text-slate-500 font-medium">Control Room</span>
          </div>
          <div class="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-500 flex items-center justify-center font-bold text-xs">
            OP
          </div>
        </div>
      </div>
    </div>

  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

// Definisikan props & emit untuk komunikasi ke DashboardLayout
defineProps({
  isCollapsed: Boolean
})
defineEmits(['toggle-sidebar'])

// --- Sisa skrip logika jam & dark mode di bawah tetap sama seperti sebelumnya ---
const currentDateTime = ref(new Date())
let timerId = null
onMounted(() => { timerId = setInterval(() => { currentDateTime.value = new Date() }, 1000) })
onBeforeUnmount(() => { clearInterval(timerId) })
const formatDateTime = computed(() => {
  const date = currentDateTime.value
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
})

const isDark = ref(false)
onMounted(() => {
  if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
})
const toggleDarkMode = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}
</script>