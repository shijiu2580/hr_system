<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="show" class="import-modal-overlay" @click.self="close">
        <div class="import-modal" @click.stop>
          <header class="modal-header">
            <h3>{{ title }}</h3>
            <button class="close-btn" @click="close" :disabled="uploading">×</button>
          </header>
          
          <div class="modal-body">
            <!-- 步骤指示器 -->
            <div class="steps">
              <div class="step" :class="{ active: step >= 1, done: step > 1 }">
                <span class="step-num">1</span>
                <span class="step-text">下载模板</span>
              </div>
              <div class="step-line" :class="{ active: step > 1 }"></div>
              <div class="step" :class="{ active: step >= 2, done: step > 2 }">
                <span class="step-num">2</span>
                <span class="step-text">上传文件</span>
              </div>
              <div class="step-line" :class="{ active: step > 2 }"></div>
              <div class="step" :class="{ active: step >= 3 }">
                <span class="step-num">3</span>
                <span class="step-text">完成导入</span>
              </div>
            </div>
            
            <!-- 下载模板 -->
            <div v-if="step === 1" class="step-content">
              <div class="template-info">
                <div class="info-icon">📄</div>
                <div class="info-text">
                  <p><strong>请先下载导入模板</strong></p>
                  <p>模板包含所有可导入的字段和示例数据，请按照模板格式填写数据</p>
                </div>
              </div>
              <div class="template-actions">
                <button class="btn-primary" @click="downloadTemplate">
                  <span>📥</span> 下载模板
                </button>
                <button class="btn-ghost" @click="step = 2">
                  已有文件，跳过
                </button>
              </div>
            </div>
            
            <!-- 上传文件 -->
            <div v-if="step === 2" class="step-content">
              <div 
                class="upload-zone"
                :class="{ dragging: isDragging, 'has-file': selectedFile }"
                @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input 
                  ref="fileInput" 
                  type="file" 
                  accept=".xlsx,.xls" 
                  @change="handleFileChange"
                  style="display:none"
                />
                <template v-if="!selectedFile">
                  <div class="upload-icon">📁</div>
                  <p class="upload-text">拖拽文件到此处，或点击选择文件</p>
                  <p class="upload-hint">支持 .xlsx, .xls 格式</p>
                </template>
                <template v-else>
                  <div class="file-info">
                    <span class="file-icon">📄</span>
                    <span class="file-name">{{ selectedFile.name }}</span>
                    <span class="file-size">{{ formatSize(selectedFile.size) }}</span>
                    <button class="remove-btn" @click.stop="selectedFile = null">×</button>
                  </div>
                </template>
              </div>
              
              <div class="upload-actions">
                <button class="btn-ghost" @click="step = 1">上一步</button>
                <button 
                  class="btn-primary" 
                  @click="upload" 
                  :disabled="!selectedFile || uploading"
                >
                  {{ uploading ? '导入中...' : '开始导入' }}
                </button>
              </div>
            </div>
            
            <!-- 导入结果 -->
            <div v-if="step === 3" class="step-content">
              <div class="result-summary" :class="{ success: result.failed === 0, warning: result.failed > 0 }">
                <div class="result-icon">{{ result.failed === 0 ? '✅' : '⚠️' }}</div>
                <div class="result-stats">
                  <p class="result-title">{{ result.failed === 0 ? '导入完成' : '部分导入失败' }}</p>
                  <p class="result-detail">
                    成功: <strong>{{ result.success }}</strong> 条，
                    失败: <strong>{{ result.failed }}</strong> 条
                  </p>
                </div>
              </div>
              
              <div v-if="result.errors && result.errors.length" class="error-list">
                <p class="error-title">错误详情:</p>
                <ul>
                  <li v-for="(err, idx) in result.errors" :key="idx">{{ err }}</li>
                </ul>
              </div>
              
              <div class="result-actions">
                <button class="btn-ghost" @click="reset">继续导入</button>
                <button class="btn-primary" @click="close">完成</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import api from '../utils/api'

const props = defineProps({
  show: Boolean,
  title: { type: String, default: '批量导入' },
  importUrl: { type: String, required: true },
  templateType: { type: String, required: true }
})

const emit = defineEmits(['close', 'success'])

const step = ref(1)
const isDragging = ref(false)
const selectedFile = ref(null)
const fileInput = ref(null)
const uploading = ref(false)
const result = ref({ success: 0, failed: 0, errors: [] })

function close() {
  if (uploading.value) return
  emit('close')
  setTimeout(reset, 300)
}

function reset() {
  step.value = 1
  selectedFile.value = null
  result.value = { success: 0, failed: 0, errors: [] }
}

function downloadTemplate() {
  window.open(`/api/import/template/${props.templateType}/`, '_blank')
  step.value = 2
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(e) {
  const file = e.target.files?.[0]
  if (file) {
    selectedFile.value = file
  }
}

function handleDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files?.[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
    selectedFile.value = file
  }
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function upload() {
  if (!selectedFile.value || uploading.value) return
  
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const res = await api.post(props.importUrl, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    result.value = res.data?.data || { success: 0, failed: 0, errors: [] }
    step.value = 3
    
    if (result.value.success > 0) {
      emit('success')
    }
  } catch (err) {
    result.value = {
      success: 0,
      failed: 1,
      errors: [err.response?.data?.detail || err.message || '导入失败']
    }
    step.value = 3
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.import-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.import-modal {
  background: var(--color-bg-primary, #fff);
  border-radius: 16px;
  width: 90%;
  max-width: 520px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary, #111);
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--color-bg-secondary, #f3f4f6);
  border-radius: 8px;
  font-size: 20px;
  color: var(--color-text-secondary, #6b7280);
  cursor: pointer;
  transition: all 0.15s;
}

.close-btn:hover {
  background: var(--color-bg-tertiary, #e5e7eb);
  color: var(--color-text-primary, #111);
}

.modal-body {
  padding: 24px;
}

/* Steps */
.steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 32px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.step-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-secondary, #9ca3af);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
}

.step.active .step-num {
  background: var(--color-primary, #3b82f6);
  color: #fff;
}

.step.done .step-num {
  background: var(--color-success, #10b981);
  color: #fff;
}

.step-text {
  font-size: 12px;
  color: var(--color-text-secondary, #9ca3af);
}

.step.active .step-text {
  color: var(--color-text-primary, #111);
  font-weight: 500;
}

.step-line {
  width: 40px;
  height: 2px;
  background: var(--color-border, #e5e7eb);
  transition: background 0.2s;
}

.step-line.active {
  background: var(--color-success, #10b981);
}

/* Step Content */
.step-content {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Template Info */
.template-info {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--color-bg-secondary, #f3f4f6);
  border-radius: 12px;
  margin-bottom: 24px;
}

.info-icon {
  font-size: 32px;
}

.info-text p {
  margin: 0;
  color: var(--color-text-secondary, #6b7280);
  font-size: 14px;
  line-height: 1.6;
}

.info-text p:first-child {
  color: var(--color-text-primary, #111);
  margin-bottom: 4px;
}

.template-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Upload Zone */
.upload-zone {
  border: 2px dashed var(--color-border, #d1d5db);
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 24px;
}

.upload-zone:hover,
.upload-zone.dragging {
  border-color: var(--color-primary, #3b82f6);
  background: var(--color-primary-bg, #eff6ff);
}

.upload-zone.has-file {
  padding: 16px 20px;
  background: var(--color-bg-secondary, #f3f4f6);
  border-style: solid;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.upload-text {
  font-size: 15px;
  color: var(--color-text-primary, #111);
  margin: 0 0 4px;
}

.upload-hint {
  font-size: 13px;
  color: var(--color-text-secondary, #9ca3af);
  margin: 0;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-icon {
  font-size: 24px;
}

.file-name {
  flex: 1;
  font-weight: 500;
  color: var(--color-text-primary, #111);
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 13px;
  color: var(--color-text-secondary, #9ca3af);
}

.remove-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: var(--color-error-bg, #fee2e2);
  color: var(--color-error, #ef4444);
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.upload-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Result */
.result-summary {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.result-summary.success {
  background: var(--color-success-bg, #d1fae5);
}

.result-summary.warning {
  background: var(--color-warning-bg, #fef3c7);
}

.result-icon {
  font-size: 36px;
}

.result-title {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary, #111);
}

.result-detail {
  margin: 0;
  font-size: 14px;
  color: var(--color-text-secondary, #6b7280);
}

.result-detail strong {
  color: var(--color-text-primary, #111);
}

.error-list {
  background: var(--color-error-bg, #fee2e2);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
  max-height: 160px;
  overflow-y: auto;
}

.error-title {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-error, #ef4444);
}

.error-list ul {
  margin: 0;
  padding-left: 20px;
}

.error-list li {
  font-size: 13px;
  color: var(--color-error, #dc2626);
  line-height: 1.6;
}

.result-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Buttons */
.btn-primary,
.btn-ghost {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: var(--color-primary, #3b82f6);
  color: #fff;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover, #2563eb);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary, #6b7280);
  border: 1px solid var(--color-border, #d1d5db);
}

.btn-ghost:hover {
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-primary, #111);
}

/* Modal Animation */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-active .import-modal,
.modal-fade-leave-active .import-modal {
  transition: transform 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .import-modal,
.modal-fade-leave-to .import-modal {
  transform: scale(0.95);
}
</style>
