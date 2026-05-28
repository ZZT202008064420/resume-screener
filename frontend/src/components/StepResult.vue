<!-- src/components/StepResult.vue -->
<template>
  <div class="space-y-6">

    <!-- 顶部总分卡片 -->
    <div class="bg-white rounded-2xl p-8 border border-gray-200 flex items-center justify-between">
      <div>
        <p class="text-gray-500 text-sm mb-1">综合匹配评分</p>
        <div class="flex items-end gap-3">
          <span class="text-6xl font-bold" :class="scoreColor">{{ totalScore }}</span>
          <span class="text-gray-400 text-xl mb-2">/ 100</span>
        </div>
        <p class="text-gray-600 mt-2">{{ candidateName }} · {{ hireAdvice }}</p>
      </div>

      <!-- 雷达图 -->
      <div class="w-56 h-56">
        <v-chart :option="radarOption" autoresize />
      </div>
    </div>

    <!-- 推荐意见 -->
    <div class="bg-blue-50 border border-blue-100 rounded-2xl p-5">
      <p class="text-xs text-blue-400 font-medium mb-1">AI 推荐意见</p>
      <p class="text-gray-700 text-sm leading-relaxed">{{ recommendation }}</p>
    </div>

    <!-- 关键词匹配 -->
    <div class="grid grid-cols-2 gap-4">
      <div class="bg-white rounded-2xl p-5 border border-gray-200">
        <p class="text-xs text-gray-400 font-medium mb-3">✅ 命中关键词</p>
        <div class="flex flex-wrap gap-1.5">
          <span
            v-for="kw in matchedKeywords"
            :key="kw"
            class="px-2.5 py-1 bg-green-50 text-green-700 text-xs rounded-full"
          >{{ kw }}</span>
          <span v-if="!matchedKeywords.length" class="text-gray-400 text-sm">暂无命中</span>
        </div>
      </div>
      <div class="bg-white rounded-2xl p-5 border border-gray-200">
        <p class="text-xs text-gray-400 font-medium mb-3">❌ 缺失关键词</p>
        <div class="flex flex-wrap gap-1.5">
          <span
            v-for="kw in missingKeywords"
            :key="kw"
            class="px-2.5 py-1 bg-red-50 text-red-500 text-xs rounded-full"
          >{{ kw }}</span>
          <span v-if="!missingKeywords.length" class="text-gray-400 text-sm">全部命中</span>
        </div>
      </div>
    </div>

    <!-- 分维度评分 -->
    <div class="bg-white rounded-2xl p-6 border border-gray-200">
      <p class="text-sm font-medium text-gray-700 mb-4">分维度得分</p>
      <div class="space-y-4">
        <ScoreBar label="技能匹配" :score="aiScore.skill_match" :max="40" color="blue" />
        <ScoreBar label="经验匹配" :score="aiScore.experience_match" :max="30" color="purple" />
        <ScoreBar label="学历匹配" :score="aiScore.education_match" :max="15" color="green" />
        <ScoreBar label="综合评估" :score="aiScore.overall_fit" :max="15" color="orange" />
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex gap-3">
      <button
        class="flex-1 bg-blue-600 text-white py-3 rounded-xl font-medium hover:bg-blue-700"
        @click="emit('rescore')"
      >
        换个岗位重新评分
      </button>
      <button
        class="flex-1 border border-gray-300 text-gray-600 py-3 rounded-xl font-medium hover:bg-gray-50"
        @click="emit('reset')"
      >
        上传新简历
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { RadarChart } from 'echarts/charts'
import { RadarComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import ScoreBar from './ScoreBar.vue'

use([RadarChart, RadarComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({ scoreData: Object, resumeData: Object })
const emit = defineEmits(['reset', 'rescore'])

const aiScore = computed(() => props.scoreData?.score_detail?.ai_score || {})
const totalScore = computed(() => props.scoreData?.total_score || 0)
const hireAdvice = computed(() => props.scoreData?.hire_advice || '')
const candidateName = computed(() => props.scoreData?.candidate_name || '候选人')
const recommendation = computed(() => aiScore.value.recommendation || '')
const matchedKeywords = computed(() => aiScore.value.matched_keywords || [])
const missingKeywords = computed(() => aiScore.value.missing_keywords || [])

const scoreColor = computed(() => {
  const s = totalScore.value
  if (s >= 80) return 'text-green-500'
  if (s >= 60) return 'text-blue-500'
  if (s >= 40) return 'text-yellow-500'
  return 'text-red-500'
})

// ECharts 雷达图配置
const radarOption = computed(() => ({
  radar: {
    indicator: [
      { name: '技能', max: 40 },
      { name: '经验', max: 30 },
      { name: '学历', max: 15 },
      { name: '综合', max: 15 },
    ],
    radius: 80,
    axisName: { color: '#9ca3af', fontSize: 11 }
  },
  series: [{
    type: 'radar',
    data: [{
      value: [
        aiScore.value.skill_match || 0,
        aiScore.value.experience_match || 0,
        aiScore.value.education_match || 0,
        aiScore.value.overall_fit || 0,
      ],
      areaStyle: { color: 'rgba(59,130,246,0.15)' },
      lineStyle: { color: '#3b82f6' },
      itemStyle: { color: '#3b82f6' }
    }]
  }]
}))
</script>