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
        <h1>{{ isEdit ? '编辑部门' : '新建部门' }}</h1>
        <p class="subtitle">{{ isEdit ? '修改部门信息' : '添加新部门' }}</p>
      </div>
    </header>

    <div v-if="error" class="alert alert-error">
      <span>{{ error }}</span>
      <button @click="error = ''" class="alert-close">×</button>
    </div>

    <section class="card form-card">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <span>加载数据...</span>
      </div>
      <form v-else @submit.prevent="handleSubmit" class="department-form">
        <div class="form-field">
          <label class="form-label">部门名称 *</label>
          <input v-model.trim="form.name" class="form-control" required />
        </div>
        
        <div class="form-field">
          <label class="form-label">部门描述</label>
          <textarea v-model.trim="form.description" rows="4" class="form-control" placeholder="可选填写部门说明"></textarea>
        </div>
        
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
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

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)

const loading = ref(false)
const saving = ref(false)
const error = ref('')

const form = ref({
  name: '',
  description: ''
})

onMounted(async () => {
  if (isEdit.value) {
    loading.value = true
    try {
      const res = await api.get(`/departments/${route.params.id}/`)
      form.value = {
        name: res.data.name,
        description: res.data.description || ''
      }
    } catch (e) {
      error.value = '加载失败：' + (e.response?.data?.detail || e.message)
    } finally {
      loading.value = false
    }
  }
})

function goBack() {
  router.push('/departments')
}

async function handleSubmit() {
  if (!form.value.name.trim()) {
    error.value = '请填写部门名称'
    return
  }
  
  saving.value = true
  error.value = ''
  try {
    if (isEdit.value) {
      await api.put(`/departments/${route.params.id}/`, form.value)
    } else {
      await api.post('/departments/', form.value)
    }
    router.push('/departments')
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.error?.message || '保存失败'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 1.5rem;
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
  border-radius: 16px;
  border: 1px solid var(--color-border, #e2e8f0);
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
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

.department-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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
</style>
