<template>
  <div class="page-container">
    <header class="page-header">
      <button class="btn-back" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        返回
      </button>
      <div class="header-info">
        <h1>{{ isEdit ? '编辑文档' : '上传文档' }}</h1>
        <p class="subtitle">{{ isEdit ? '修改文档信息' : '上传新文档' }}</p>
      </div>
    </header>

    <div v-if="error" class="alert alert-error">
      <span>{{ error }}</span>
      <button @click="error = ''" class="alert-close">×</button>
    </div>

    <section class="card form-card">
      <div v-if="loading" class="loading-dots-text">
        <div class="dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
        <span>加载数据...</span>
      </div>
      <form v-else @submit.prevent="handleSubmit" class="document-form">
        <div class="form-grid">
          <div class="form-field span-2">
            <label class="form-label">标题 *</label>
            <input v-model.trim="form.title" class="form-control" required />
          </div>

          <div class="form-field">
            <label class="form-label">文档类型 *</label>
            <CustomSelect
              v-model="form.document_type"
              :options="typeOptions"
              placeholder="请选择文档类型"
            />
          </div>

          <div class="form-field">
            <label class="form-label">版本号 *</label>
            <input v-model.trim="form.version" class="form-control" required placeholder="例如：1.0" />
          </div>

          <div class="form-field span-2">
            <label class="form-label">描述</label>
            <textarea
              v-model.trim="form.description"
              rows="4"
              class="form-control"
              placeholder="补充文档适用范围、更新亮点或必读提示"
            ></textarea>
          </div>

          <div class="form-field span-2">
            <label class="form-label">附件 {{ isEdit ? '(留空则不更换)' : '*' }}</label>
            <div class="file-upload">
              <input
                type="file"
                ref="fileInput"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.rar"
                @change="handleFileChange"
                :required="!isEdit"
                class="file-input"
              />
              <div class="file-display" @click="$refs.fileInput.click()">
                <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <span v-if="selectedFileName">{{ selectedFileName }}</span>
                <span v-else class="placeholder">点击选择文件 (PDF, Word, Excel, PPT, ZIP)</span>
              </div>
            </div>
            <p v-if="isEdit && originalFileName" class="file-hint">
              当前文件：{{ originalFileName }}
            </p>
          </div>

          <div class="form-field span-2">
            <label class="toggle-label">
              <input type="checkbox" v-model="form.is_active" class="toggle-input" />
              <span class="toggle-switch"></span>
              <span>启用该文档</span>
            </label>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? '保存中...' : isEdit ? '保存更改' : '上传' }}
          </button>
          <button type="button" class="btn btn-secondary" @click="goBack">取消</button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const selectedFileName = ref('')
const originalFileName = ref('')

const typeOptions = [
  { value: 'policy', label: '政策文件' },
  { value: 'procedure', label: '流程文件' },
  { value: 'template', label: '模板文件' },
  { value: 'announcement', label: '公告通知' },
  { value: 'training', label: '培训资料' },
  { value: 'other', label: '其他' }
]

const form = ref({
  title: '',
  document_type: 'policy',
  version: '1.0',
  description: '',
  is_active: true,
  file: null
})

onMounted(async () => {
  if (isEdit.value) {
    loading.value = true
    try {
      const res = await api.get(`/documents/${route.params.id}/`)
      const doc = res.data
      form.value = {
        title: doc.title,
        document_type: doc.document_type,
        version: doc.version,
        description: doc.description || '',
        is_active: doc.is_active,
        file: null
      }
      // 提取原始文件名并解码
      if (doc.file_url) {
        const rawName = doc.file_url.split('/').pop()
        try {
          originalFileName.value = decodeURIComponent(rawName)
        } catch {
          originalFileName.value = rawName
        }
      }
    } catch (e) {
      error.value = '加载失败：' + (e.response?.data?.detail || e.message)
    } finally {
      loading.value = false
    }
  }
})

function goBack() {
  router.push('/documents')
}

function handleFileChange(event) {
  const file = event.target.files?.[0]
  form.value.file = file || null
  selectedFileName.value = file?.name || ''
}

async function handleSubmit() {
  if (!form.value.title.trim()) {
    error.value = '请填写标题'
    return
  }
  if (!isEdit.value && !form.value.file) {
    error.value = '请选择文件'
    return
  }

  saving.value = true
  error.value = ''

  try {
    const fd = new FormData()
    fd.append('title', form.value.title)
    fd.append('document_type', form.value.document_type)
    fd.append('version', form.value.version)
    fd.append('description', form.value.description || '')
    fd.append('is_active', form.value.is_active ? 'true' : 'false')
    if (form.value.file) {
      fd.append('file', form.value.file)
    }

    const headers = { headers: { 'Content-Type': 'multipart/form-data' } }

    if (isEdit.value) {
      await api.patch(`/documents/${route.params.id}/`, fd, headers)
    } else {
      await api.post('/documents/', fd, headers)
    }
    router.push('/documents')
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.error?.message || '保存失败'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page-container {
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
  box-sizing: border-box;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  background: var(--color-bg-primary, #fff);
  color: var(--color-text-secondary, #64748b);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-back svg {
  width: 16px;
  height: 16px;
}

.btn-back:hover {
  background: var(--color-bg-secondary, #f1f5f9);
  color: var(--color-text-primary, #1e293b);
  border-color: var(--color-primary, #3b82f6);
}

.header-info h1 {
  margin: 0;
  font-size: 24px;
  color: var(--color-text-primary, #0f172a);
}

.subtitle {
  margin: 0.25rem 0 0;
  font-size: 13px;
  color: var(--color-text-secondary, #64748b);
}

.alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.alert-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: inherit;
}

.card {
  background: var(--color-bg-primary, #fff);
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.4);
  padding: 28px 32px;
  box-sizing: border-box;
  width: 100%;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem;
  color: var(--color-text-secondary, #64748b);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border, #e2e8f0);
  border-top-color: var(--color-primary, #3b82f6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.document-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field.span-2 {
  grid-column: span 2;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
}

.form-control {
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  font-size: 14px;
  background: var(--color-bg-primary, #fff);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: none;
}

textarea.form-control {
  resize: vertical;
  min-height: 100px;
}

.file-upload {
  position: relative;
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.file-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px dashed var(--color-border, #e2e8f0);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--color-bg-secondary, #f8fafc);
}

.file-display:hover {
  border-color: var(--color-primary, #3b82f6);
  background: rgba(59, 130, 246, 0.05);
}

.upload-icon {
  width: 24px;
  height: 24px;
  color: var(--color-text-secondary, #64748b);
}

.file-display .placeholder {
  color: var(--color-text-secondary, #64748b);
  font-size: 14px;
}

.file-hint {
  margin: 0.5rem 0 0;
  font-size: 12px;
  color: var(--color-text-secondary, #64748b);
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text-primary, #1e293b);
}

.toggle-input {
  display: none;
}

.toggle-switch {
  position: relative;
  width: 44px;
  height: 24px;
  background: var(--color-border, #e2e8f0);
  border-radius: 12px;
  transition: background 0.2s;
}

.toggle-switch::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toggle-input:checked + .toggle-switch {
  background: var(--color-primary, #3b82f6);
}

.toggle-input:checked + .toggle-switch::after {
  transform: translateX(20px);
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--color-primary, #3b82f6);
  color: #fff;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--color-bg-secondary, #f1f5f9);
  color: var(--color-text-primary, #1e293b);
  border: 1px solid var(--color-border, #e2e8f0);
}

.btn-secondary:hover {
  background: var(--color-bg-tertiary, #e2e8f0);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .form-field.span-2 {
    grid-column: span 1;
  }
}
</style>
