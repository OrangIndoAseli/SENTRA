<template>
  <aside class="h-full bg-slate-950 text-white flex flex-col justify-between border-r border-slate-800 select-none transition-all duration-300">
    
    <div class="flex flex-col min-h-0">
      
      <div class="p-5 border-b border-slate-800/60 bg-slate-900/40 shrink-0">
        <div class="flex items-center gap-3" :class="{ 'justify-center': isCollapsed }">
          
          <div class="bg-slate-900 w-9 h-9 rounded-full flex items-center justify-center overflow-hidden shrink-0 border border-slate-800 shadow-inner">
            <img src="../assets/logo_sentra.png" alt="SENTRA Logo" class="w-full h-full object-cover" />
          </div>

          <div v-if="!isCollapsed" class="min-w-0 transition-opacity duration-200">
            <h1 class="text-base font-bold tracking-wider text-slate-100 truncate">SENTRA</h1>
            <p class="text-[10px] text-amber-500 font-bold uppercase tracking-widest -mt-0.5 truncate">Mining Safety AI</p>
          </div>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
        
        <div>
          <p v-if="!isCollapsed" class="text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-3 mb-2">Utama</p>
          <nav class="space-y-1">
            <router-link to="/" exact-active-class="bg-amber-500 text-slate-950 font-bold shadow-lg shadow-amber-500/10" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:bg-slate-900 hover:text-slate-100 transition duration-150 group" :class="{ 'justify-center px-0': isCollapsed }">
              <i class="fas fa-tachometer-alt text-base w-5 text-center group-hover:scale-110 transition duration-150 shrink-0"></i>
              <span v-if="!isCollapsed" class="truncate">Beranda</span>
            </router-link>

            <router-link to="/monitoring" active-class="bg-amber-500 text-slate-950 font-bold shadow-lg shadow-amber-500/10" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:bg-slate-900 hover:text-slate-100 transition duration-150 group" :class="{ 'justify-center px-0': isCollapsed }">
              <i class="fas fa-video text-base w-5 text-center group-hover:scale-110 transition duration-150 shrink-0"></i>
              <span v-if="!isCollapsed" class="truncate">Monitoring</span>
            </router-link>
          </nav>
        </div>

        <div>
          <p v-if="!isCollapsed" class="text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-3 mb-2">Inspeksi & Risiko</p>
          <nav class="space-y-1">
            <router-link to="/violations" active-class="bg-amber-500 text-slate-950 font-bold shadow-lg shadow-amber-500/10" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:bg-slate-900 hover:text-slate-100 transition duration-150 group" :class="{ 'justify-center px-0': isCollapsed }">
              <i class="fas fa-hard-hat text-base w-5 text-center group-hover:scale-110 transition duration-150 shrink-0"></i>
              <span v-if="!isCollapsed" class="truncate">Pelanggaran APD</span>
            </router-link>

            <!-- <router-link to="/danger-zone" active-class="bg-amber-500 text-slate-950 font-bold shadow-lg shadow-amber-500/10" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:bg-slate-900 hover:text-slate-100 transition duration-150 group" :class="{ 'justify-center px-0': isCollapsed }">
              <i class="fas fa-exclamation-triangle text-base w-5 text-center group-hover:scale-110 transition duration-150 shrink-0"></i>
              <span v-if="!isCollapsed" class="truncate">Geofencing Zona Merah</span>
            </router-link> -->
          </nav>
        </div>

      </div>
    </div>

    <div class="p-4 border-t border-slate-900 bg-slate-900/20 shrink-0">
      <div class="flex items-center gap-3 bg-slate-900/50 p-2.5 rounded-xl border border-slate-800/50" :class="{ 'justify-center p-2': isCollapsed }">
        <div class="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-500 flex items-center justify-center shrink-0">
          <i class="fas fa-sign-out-alt text-xs"></i>
        </div>
        <div v-if="!isCollapsed" class="min-w-0">
        <button class="text-sm font-bold text-slate-100 truncate" @click="store.logout()">Logout</button>
        </div>
      </div>
    </div>

  </aside>
</template>

<script setup>
// Menangkap properti isCollapsed kiriman dari DashboardLayout.vue
defineProps({
  isCollapsed: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
</style>