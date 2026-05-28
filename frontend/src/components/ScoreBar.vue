<!-- src/components/ScoreBar.vue -->
<template>
  <div>
    <div class="flex justify-between text-sm mb-1">
      <span class="text-gray-600">{{ label }}</span>
      <span class="font-medium text-gray-800">{{ score }} / {{ max }}</span>
    </div>
    <div class="w-full bg-gray-100 rounded-full h-2">
      <div
        class="h-2 rounded-full transition-all duration-700"
        :class="`bg-${color}-500`"
        :style="{ width: (score / max * 100) + '%' }"
      />
    </div>
  </div>
</template>
<script setup>
defineProps({ label: String, score: Number, max: Number, color: String })
</script>