<template>
  <div class="flex h-screen w-full bg-slate-100 dark:bg-slate-950 antialiased overflow-hidden transition-colors duration-300">

    <Sidebar 
      :isCollapsed="isCollapsed" 
      class="h-full shrink-0 transition-all duration-300"
      :class="isCollapsed ? 'w-20' : 'w-64'"
    />

    <div class="flex-1 flex flex-col min-w-0 h-full overflow-hidden bg-slate-100 dark:bg-slate-950 transition-colors duration-300">
      
      <Navbar 
        :isCollapsed="isCollapsed" 
        @toggle-sidebar="toggleSidebar"
        class="shrink-0" 
      />

      <div class="flex-1 flex flex-col w-full max-w-[1600px] mx-auto min-h-0 overflow-hidden bg-slate-100 dark:bg-slate-950 transition-colors duration-300">
        <main class="flex-1 overflow-y-auto p-4 sm:p-6 w-full min-h-0 bg-slate-100 dark:bg-slate-950 transition-colors duration-300">
          <router-view />
        </main>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import Navbar from '../components/Navbar.vue'

const isCollapsed = ref(false)

// Fungsi untuk dipanggil dari Navbar
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>