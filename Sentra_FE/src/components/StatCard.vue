<template>
  <div class="bg-white p-5 rounded-2xl shadow-sm border border-transparent dark:bg-slate-900 dark:border-transparent border-l-4 border-amber-500 transition-all duration-200 hover:shadow-md">
    <div class="flex items-start justify-between gap-2">
      
      <div class="space-y-1">
        <p class="text-sm font-medium text-slate-500 dark:text-yellow-300 tracking-wide transition-colors duration-200">
          {{ title }}
        </p>
        
        <h3 class="text-3xl font-bold text-slate-800 dark:text-yellow-400 font-mono transition-colors duration-200">
          {{ value }}
        </h3>
      </div>

      <div class="text-xl text-amber-500 dark:text-yellow-400 bg-amber-50 dark:bg-yellow-950/40 p-2.5 rounded-xl shrink-0 border border-amber-100/50 dark:border-yellow-900/40 flex items-center justify-center w-11 h-11">
        <i :class="icon"></i>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
    default: 'Statistik'
  },
  value: {
    type: [String, Number],
    required: true,
    default: '0'
  },
  icon: {
    type: String,
    required: true,
    default: 'fas fa-chart-bar'
  }
})
</script>