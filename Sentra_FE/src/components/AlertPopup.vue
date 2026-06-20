<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    leave-active-class="transition duration-200 ease-in"
    enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:translate-x-4"
    leave-to-class="opacity-0 translate-y-2 sm:translate-x-4"
  >
    <div
      v-if="show"
      class="fixed top-20 right-4 sm:right-6 w-full max-w-[380px] z-50 p-1"
    >
      <div
        :class="alertConfig.bgClass"
        class="rounded-2xl border p-4.5 border-l-4 bg-white dark:bg-slate-900 dark:border-transparent dark:border-800/80 backdrop-blur-sm transition-all duration-300"
      >
        <div class="flex justify-between items-start gap-3">
          
          <div class="flex gap-3 min-w-0">
            <span class="text-xl shrink-0 mt-0.5">
              {{ alertConfig.icon }}
            </span>
            
            <div class="min-w-0">
              <h3 
                :class="alertConfig.textClass" 
                class="font-bold tracking-tight text-sm sm:text-base leading-5 dark:text-white transition-colors duration-200"
              >
                {{ title }}
              </h3>

              <p class="text-xs text-slate-600 dark:text-slate-300 mt-1 font-medium leading-relaxed">
                {{ message }}
              </p>

              <div class="flex items-center gap-1.5 mt-2.5 text-[11px] font-semibold text-slate-500 dark:text-slate-400 font-mono bg-slate-900/5 dark:bg-slate-950 px-2 py-0.5 rounded-md w-fit border dark:border-slate-800">
                <span class="truncate">{{ location }}</span>
              </div>
            </div>
          </div>

          <button
            @click="show = false"
            class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-lg hover:bg-slate-900/5 dark:hover:bg-slate-800 transition shrink-0 cursor-pointer"
            aria-label="Tutup Peringatan"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>

        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed } from 'vue'

const show = ref(true)

const props = defineProps({
  type: {
    type: String,
    default: 'danger' 
  },
  title: {
    type: String,
    default: 'Alert Keselamatan'
  },
  message: {
    type: String,
    default: ''
  },
  location: {
    type: String,
    default: 'Area Lapangan'
  }
})

// Semua properti shadow- telah dibersihkan total dari konfigurasi
const alertConfig = computed(() => {
  switch (props.type) {
    case 'danger':
      return {
        bgClass: 'border-rose-600',
        textClass: 'text-rose-700',
        icon: '🚨'
      }
    case 'warning':
      return {
        bgClass: 'border-transparent',
        textClass: 'text-amber-700',
        icon: '⚠️'
      }
    case 'success':
      return {
        bgClass: 'border-emerald-500',
        textClass: 'text-emerald-700',
        icon: '✓'
      }
    default:
      return {
        bgClass: 'border-blue-500',
        textClass: 'text-blue-700',
        icon: 'ℹ️'
      }
  }
})
</script>