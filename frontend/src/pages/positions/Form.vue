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
        <h1>{{ isEdit ? '编辑职位' : '新建职位' }}</h1>
        <p class="subtitle">{{ isEdit ? '修改职位信息' : '添加新职位' }}</p>
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
      <form v-else @submit.prevent="handleSubmit" class="position-form">
        <div class="form-grid">
          <div class="form-field">
            <label class="form-label">职位名称 *</label>
            <input v-model.trim="form.name" class="form-control" required />
          </div>

          <div class="form-field">
            <label class="form-label">所属部门</label>
            <DeptTreeSelect
              v-model="form.department_id"
              :departments="departments"
              placeholder="请选择部门"
              empty-label="不指定部门"
            />
          </div>

          <div class="form-field span-2">
            <label class="form-label">职位描述</label>
            <textarea v-model.trim="form.description" rows="3" class="form-control" placeholder="可选填写职位说明"></textarea>
          </div>

          <div class="form-field">
            <label class="form-label">最低薪资</label>
            <input type="number" step="0.01" v-model.number="form.salary_range_min" class="form-control" placeholder="可选" />
          </div>
          <div class="form-field">
            <label class="form-label">最高薪资</label>
            <input type="number" step="0.01" v-model.number="form.salary_range_max" class="form-control" placeholder="可选" />
          </div>

          <div class="form-field span-2">
            <label class="form-label">任职要求</label>
            <textarea v-model.trim="form.requirements" rows="3" class="form-control" placeholder="可选填写任职要求"></textarea>
          </div>

          <div class="form-field span-2">
            <label class="form-label">默认角色</label>
            <p class="field-hint">新员工入职该职位时将自动获得这些角色的权限</p>
            <div class="checkbox-group">
              <label v-for="role in roles" :key="role.id" class="checkbox-item">
                <input type="checkbox" :value="role.id" v-model="form.default_role_ids" />
                <span class="checkbox-label">{{ role.name }}</span>
                <span v-if="role.description" class="checkbox-desc">{{ role.description }}</span>
              </label>
              <span v-if="!roles.length" class="muted">暂无可用角色</span>
            </div>
          </div>
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
import DeptTreeSelect from '../../components/DeptTreeSelect.vue'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)

const departments = ref([])
const roles = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const form = ref({
  name: '',
  department_id: '',
  description: '',
  salary_range_min: null,
  salary_range_max: null,
  requirements: '',
  default_role_ids: []
})

onMounted(async () => {
  try {
    // 并行加载部门和角色列表
    const [deptRes, roleRes] = await Promise.all([
      api.get('/departments/', { params: { page_size: 9999 } }),
      api.get('/rbac/roles/', { params: { page_size: 9999 } })
    ])
    departments.value = deptRes.data.results || deptRes.data || []
    roles.value = roleRes.data.results || roleRes.data || []

    // 如果是编辑模式，加载职位数据
    if (isEdit.value) {
      const res = await api.get(`/positions/${route.params.id}/`)
      const data = res.data
      form.value = {
        name: data.name,
        department_id: data.department?.id || '',
        description: data.description || '',
        salary_range_min: data.salary_range_min,
        salary_range_max: data.salary_range_max,
        requirements: data.requirements || '',
        default_role_ids: data.default_role_ids || []
      }
    }
  } catch (e) {
    error.value = '加载失败：' + (e.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.push('/positions')
}

async function handleSubmit() {
  if (!form.value.name.trim()) {
    error.value = '请填写职位名称'
    return
  }

  saving.value = true
  error.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.department_id) payload.department_id = null

    if (isEdit.value) {
      await api.put(`/positions/${route.params.id}/`, payload)
    } else {
      await api.post('/positions/', payload)
    }
    router.push('/positions')
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

.position-form {
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

.field-hint {
  margin: 0 0 0.5rem;
  font-size: 12px;
  color: var(--color-text-secondary, #94a3b8);
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  background: var(--color-bg-secondary, #f8fafc);
  max-height: 200px;
  overflow-y: auto;
}

.checkbox-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.checkbox-item:hover {
  background: var(--color-bg-tertiary, #e2e8f0);
}

.checkbox-item input[type="checkbox"] {
  margin-top: 2px;
  accent-color: var(--color-primary, #3b82f6);
}

.checkbox-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary, #1e293b);
}

.checkbox-desc {
  font-size: 12px;
  color: var(--color-text-secondary, #64748b);
  margin-left: auto;
}

.muted {
  color: var(--color-text-secondary, #94a3b8);
  font-size: 13px;
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
