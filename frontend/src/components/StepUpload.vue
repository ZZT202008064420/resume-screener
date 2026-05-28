<!-- src/components/StepUpload.vue -->
<template>
  <div class="max-w-xl mx-auto mt-12">
    <h2 class="text-2xl font-bold text-gray-800 mb-2">上传简历</h2>
    <p class="text-gray-500 mb-8">支持 PDF 格式，最大 10MB</p>

    <!-- 拖拽上传区 -->
    <div
      class="border-2 border-dashed rounded-2xl p-12 text-center transition-all cursor-pointer"
      :class="isDragging
        ? 'border-blue-500 bg-blue-50'
        : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
      @click="fileInput.click()"
    >
      <div v-if="!file">
        <div class="text-5xl mb-4">📄</div>
        <p class="text-gray-600 font-medium">点击或拖拽 PDF 文件到此处</p>
        <p class="text-gray-400 text-sm mt-1">支持多页简历</p>
      </div>
      <div v-else class="text-gray-700">
        <div class="text-4xl mb-3">✅</div>
        <p class="font-medium">{{ file.name }}</p>
        <p class="text-sm text-gray-400 mt-1">{{ (file.size / 1024).toFixed(1) }} KB</p>
      </div>
    </div>

    <input ref="fileInput" type="file" accept=".pdf" class="hidden" @change="handleFileChange" />

    <!-- 上传进度 -->
    <div v-if="uploading" class="mt-6">
      <div class="flex justify-between text-sm text-gray-600 mb-1">
        <span>{{ statusText }}</span>
        <span>{{ progress }}%</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div
          class="bg-blue-600 h-2 rounded-full transition-all duration-300"
          :style="{ width: progress + '%' }"
        />
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
      {{ errorMsg }}
    </div>

    <!-- 操作按钮 -->
    <div class="mt-6 flex gap-3">
      <button
        v-if="file && !uploading"
        class="flex-1 bg-blue-600 text-white py-3 rounded-xl font-medium hover:bg-blue-700 transition-colors"
        @click="upload"
      >
        开始解析
      </button>
      <button
        v-if="file && !uploading"
        class="px-6 py-3 border border-gray-300 rounded-xl text-gray-600 hover:bg-gray-50"
        @click="file = null"
      >
        重选
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { uploadResume } from '../api/index.js'

const emit = defineEmits(['uploaded'])

const file = ref(null)
const fileInput = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const progress = ref(0)
const statusText = ref('上传中...')
const errorMsg = ref('')

const handleFileChange = (e) => {
  file.value = e.target.files[0] || null
  errorMsg.value = ''
}

const handleDrop = (e) => {
  isDragging.value = false
  const f = e.dataTransfer.files[0]
  if (f?.type === 'application/pdf') {
    file.value = f
    errorMsg.value = ''
  } else {
    errorMsg.value = '请上传 PDF 格式文件'
  }
}

const upload = async () => {
  if (!file.value) return
  uploading.value = true
  errorMsg.value = ''
  progress.value = 0
  statusText.value = '上传中...'

  try {
    const res = await uploadResume(file.value, (p) => {
      progress.value = p < 100 ? p : 99  // 留1%给AI解析
    })

    statusText.value = 'AI 解析中...'
    progress.value = 100

    if (res.code === 0) {
      emit('uploaded', res.data)
    } else {
      errorMsg.value = res.message || '解析失败'
    }
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    uploading.value = false
  }
}
</script>