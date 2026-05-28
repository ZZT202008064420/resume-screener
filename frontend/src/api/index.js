// src/api/index.js
import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 60000,
})

// 统一错误处理
http.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.message || '网络错误，请稍后重试'
    return Promise.reject(new Error(msg))
  }
)

export const uploadResume = (file, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  return http.post('/api/resume/upload', form, {
    onUploadProgress: e => {
      onProgress?.(Math.round(e.loaded / e.total * 100))
    }
  })
}

export const scoreResume = (fileHash, jobDescription) =>
  http.post('/api/resume/score', { file_hash: fileHash, job_description: jobDescription })