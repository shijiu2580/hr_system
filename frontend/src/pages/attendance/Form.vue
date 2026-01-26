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
        <h1>{{ isEdit ? '编辑考勤' : '新增考勤' }}</h1>
        <p class="subtitle">{{ isEdit ? '修改考勤记录' : '添加考勤记录' }}</p>
      </div>
    </header>

    <div v-if="error" class="alert alert-error">
      <span>{{ error }}</span>
      <button @click="error = ''" class="alert-close">×</button>
    </div>

    <div v-if="success" class="alert alert-success">
      <span>{{ success }}</span>
      <button @click="success = ''" class="alert-close">×</button>
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
      <form v-else @submit.prevent="handleSubmit" class="attendance-form">
        <div class="form-grid">
          <div v-if="isStaff" class="form-field span-2">
            <label class="form-label">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" stroke="currentColor" stroke-width="2"/>
                <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
              </svg>
              选择员工
            </label>
            <CustomSelect
              v-model="form.employee_id"
              :options="employees.map(e => ({ value: e.id, label: e.employee_id + ' - ' + e.name }))"
              placeholder="请选择员工"
            />
          </div>
          <div class="form-field">
            <label class="form-label">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M16 2v4M8 2v4M3 10h18" stroke="currentColor" stroke-width="2"/>
              </svg>
              日期
            </label>
            <input type="date" v-model="form.date" class="form-control" required />
          </div>
          <div class="form-field">
            <label class="form-label">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="currentColor" stroke-width="2"/>
              </svg>
              考勤类型
            </label>
            <CustomSelect
              v-model="form.attendance_type"
              :options="typeOptions"
              placeholder="请选择类型"
            />
          </div>
          <div class="form-field span-2">
            <label class="form-label">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="2"/>
              </svg>
              备注说明
            </label>
            <textarea v-model.trim="form.notes" rows="3" placeholder="选填，可记录异常情况说明..." class="form-control"></textarea>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn btn-primary" type="submit" :disabled="saving">
            {{ saving ? '保存中...' : '保存记录' }}
          </button>
          <button class="btn btn-secondary" type="button" @click="goBack">取消</button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isEdit = computed(() => !!route.params.id)
const isStaff = computed(() => authStore.user?.is_staff)

const employees = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')

const form = ref({
  employee_id: '',
  date: new Date().toISOString().slice(0, 10),
  attendance_type: 'normal',
  notes: ''
})

const typeOptions = [
  { value: 'normal', label: '正常出勤' },
  { value: 'late', label: '迟到' },
  { value: 'early', label: '早退' },
  { value: 'absent', label: '缺勤' },
  { value: 'leave', label: '请假' },
  { value: 'overtime', label: '加班' },
  { value: 'remote', label: '远程办公' },
  { value: 'business', label: '出差' }
]

onMounted(async () => {
  try {
    // 加载员工列表（管理员需要）
    if (isStaff.value) {
      const res = await api.get('/employees/')
      employees.value = res.data.results || res.data || []
    }

    // 如果是编辑模式，加载现有记录
    if (isEdit.value) {
      const res = await api.get(`/attendance/${route.params.id}/`)
      const record = res.data
      form.value = {
        employee_id: record.employee?.id || '',
        date: record.date,
        attendance_type: record.attendance_type,
        notes: record.notes || ''
      }
    } else if (!isStaff.value) {
      // 普通员工自动设置自己
      form.value.employee_id = authStore.user?.id
    }
  } catch (e) {
    error.value = '加载失败：' + (e.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.push('/attendance')
}

async function handleSubmit() {
  saving.value = true
  error.value = ''
  try {
    const payload = { ...form.value }
    if (isEdit.value) {
      await api.put(`/attendance/${route.params.id}/`, payload)
    } else {
      await api.post('/attendance/', payload)
    }
    router.push('/attendance')
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

.alert-success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
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

.attendance-form {
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
}

.form-label svg {
  color: var(--color-primary, #3b82f6);
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
  min-height: 80px;
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
  .form-grid,
  .form-row {
    grid-template-columns: 1fr;
  }
  .form-field.span-2 {
    grid-column: span 1;
  }
}
</style>
