<!-- src/components/InfoRow.vue -->
<template>
  <div v-if="value" class="flex items-center gap-2 text-sm">
    <span>{{ icon }}</span>
    <span class="text-gray-400 w-14 shrink-0">{{ label }}</span>
    <span class="text-gray-700 truncate">{{ value }}</span>
  </div>
</template>
<script setup>
defineProps({ icon: String, label: String, value: [String, Number] })
</script>