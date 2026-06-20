<template>
  <div class="bg-white rounded-2xl shadow-sm overflow-hidden">

    <div
      class="flex justify-between items-center p-4 border-b"
    >
      <div>
        <h3 class="font-semibold text-slate-800">
          {{ title }}
        </h3>

        <p class="text-sm text-slate-500">
          {{ location }}
        </p>
      </div>

      <span
        :class="
          isOnline
            ? 'bg-green-100 text-green-700'
            : 'bg-red-100 text-red-700'
        "
        class="px-3 py-1 rounded-full text-xs font-medium"
      >
        {{ isOnline ? 'ONLINE' : 'OFFLINE' }}
      </span>
    </div>

    <img
      :src="image"
      :alt="title"
      class="w-full h-64 object-cover"
    />

    <div class="p-4">

      <div class="flex justify-between text-sm">

        <span class="text-slate-500">
          Deteksi
        </span>

        <span class="font-medium">
          {{ detection }}
        </span>

      </div>

    </div>

  </div>
</template>

<script setup>
defineProps({
  title: String,
  location: String,
  image: String,
  detection: String,
  isOnline: {
    type: Boolean,
    default: true
  }
})
</script>