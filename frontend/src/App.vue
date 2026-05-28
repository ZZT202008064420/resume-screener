<!-- src/App.vue -->
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="max-w-4xl mx-auto flex items-center gap-3">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <span class="text-white text-sm font-bold">AI</span>
        </div>
        <h1 class="text-lg font-semibold text-gray-800">简历智能筛选系统</h1>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-6 py-8">

      <!-- 步骤一：上传简历 -->
      <StepUpload
        v-if="step === 1"
        @uploaded="onUploaded"
      />

      <!-- 步骤二：输入JD + 查看提取信息 -->
      <StepJD
        v-if="step === 2"
        :resume-data="resumeData"
        @scored="onScored"
        @reset="reset"
      />

      <!-- 步骤三：评分结果 -->
      <StepResult
        v-if="step === 3"
        :score-data="scoreData"
        :resume-data="resumeData"
        @reset="reset"
        @rescore="step = 2"
      />

    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StepUpload from './components/StepUpload.vue'
import StepJD from './components/StepJD.vue'
import StepResult from './components/StepResult.vue'

const step = ref(1)
const resumeData = ref(null)
const scoreData = ref(null)

const onUploaded = (data) => {
  resumeData.value = data
  step.value = 2
}

const onScored = (data) => {
  scoreData.value = data
  step.value = 3
}

const reset = () => {
  step.value = 1
  resumeData.value = null
  scoreData.value = null
}
</script>