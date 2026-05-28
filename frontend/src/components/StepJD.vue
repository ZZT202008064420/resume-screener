<!-- src/components/StepJD.vue -->
<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

    <!-- 左：提取的简历信息 -->
    <div class="bg-white rounded-2xl p-6 border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-gray-800">📋 提取信息</h3>
        <span v-if="props.resumeData.from_cache"
          class="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded-full">
          缓存命中
        </span>
      </div>

      <!-- 基本信息 -->
      <div class="mb-5">
        <p class="text-xs text-gray-400 font-medium uppercase tracking-wide mb-2">基本信息</p>
        <div class="space-y-1.5">
          <InfoRow icon="👤" label="姓名" :value="basic.name" />
          <InfoRow icon="📱" label="电话" :value="basic.phone" />
          <InfoRow icon="📧" label="邮箱" :value="basic.email" />
          <InfoRow icon="📍" label="地址" :value="basic.address" />
        </div>
      </div>

      <!-- 求职意向 -->
      <div class="mb-5" v-if="intention.position || intention.expected_salary">
        <p class="text-xs text-gray-400 font-medium uppercase tracking-wide mb-2">求职意向</p>
        <div class="space-y-1.5">
          <InfoRow icon="💼" label="意向" :value="intention.position" />
          <InfoRow icon="💰" label="期望薪资" :value="intention.expected_salary" />
        </div>
      </div>

      <!-- 背景 -->
      <div class="mb-5">
        <p class="text-xs text-gray-400 font-medium uppercase tracking-wide mb-2">背景</p>
        <div class="space-y-1.5">
          <InfoRow icon="🎓" label="学历" :value="background.education" />
          <InfoRow icon="🏫" label="院校" :value="background.school" />
          <InfoRow icon="⏱️" label="工作年限" :value="background.work_years ? background.work_years + ' 年' : null" />
        </div>
      </div>

      <!-- 技能标签 -->
      <div v-if="background.skills?.length">
        <p class="text-xs text-gray-400 font-medium uppercase tracking-wide mb-2">技能</p>
        <div class="flex flex-wrap gap-1.5">
          <span
            v-for="skill in background.skills"
            :key="skill"
            class="px-2.5 py-1 bg-blue-50 text-blue-700 text-xs rounded-full font-medium"
          >
            {{ skill }}
          </span>
        </div>
      </div>
    </div>

    <!-- 右：输入JD + 评分按钮 -->
    <div class="bg-white rounded-2xl p-6 border border-gray-200 flex flex-col">
      <h3 class="font-semibold text-gray-800 mb-1">🎯 输入岗位需求</h3>
      <p class="text-sm text-gray-400 mb-4">粘贴招聘JD，AI将自动提取关键词并评分</p>

      <textarea
        v-model="jd"
        placeholder="例：招聘Python后端工程师，要求3年以上经验，熟悉Django/FastAPI，了解Redis、MySQL、Docker，有微服务架构经验优先..."
        class="flex-1 min-h-48 w-full border border-gray-200 rounded-xl p-4 text-sm resize-none focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100"
      />

      <div v-if="errorMsg" class="mt-3 text-sm text-red-500">{{ errorMsg }}</div>

      <div class="mt-4 flex gap-3">
        <button
          class="flex-1 bg-blue-600 text-white py-3 rounded-xl font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          :disabled="scoring || !jd.trim()"
          @click="score"
        >
          <span v-if="scoring" class="animate-spin">⏳</span>
          {{ scoring ? 'AI 评分中...' : '开始匹配评分' }}
        </button>
        <button
          class="px-4 py-3 border border-gray-300 rounded-xl text-gray-500 hover:bg-gray-50 text-sm"
          @click="emit('reset')"
        >
          重新上传
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { scoreResume } from '../api/index.js'
import InfoRow from './InfoRow.vue'

const props = defineProps({ resumeData: Object })
const emit = defineEmits(['scored', 'reset'])

const jd = ref('')
const scoring = ref(false)
const errorMsg = ref('')

const info = computed(() => props.resumeData?.extracted_info || {})
const basic = computed(() => info.value.basic_info || {})
const intention = computed(() => info.value.job_intention || {})
const background = computed(() => info.value.background || {})

const score = async () => {
  if (!jd.value.trim()) return
  scoring.value = true
  errorMsg.value = ''
  try {
    const res = await scoreResume(props.resumeData.file_hash, jd.value)
    if (res.code === 0) {
      emit('scored', res.data)
    } else {
      errorMsg.value = res.message
    }
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    scoring.value = false
  }
}
</script>