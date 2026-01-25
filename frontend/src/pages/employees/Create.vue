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
        <h1>新增员工</h1>
        <p class="subtitle">填写员工基本信息</p>
      </div>
    </header>

    <div v-if="error" class="alert alert-error">
      <span>{{ error }}</span>
      <button @click="error = ''" class="alert-close">×</button>
    </div>

    <section class="card form-card">
      <div v-if="loadingOptions" class="loading-state">
        <div class="spinner"></div>
        <span>加载选项数据...</span>
      </div>
      <EmployeeForm
        v-else
        :value="null"
        :users="users"
        :departments="departments"
        :positions="positions"
        :checkin-locations="checkinLocations"
        :loading="saving"
        @save="handleSave"
        @cancel="goBack"
      />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'
import EmployeeForm from './components/EmployeeForm.vue'

const router = useRouter()

const users = ref([])
const departments = ref([])
const positions = ref([])
const checkinLocations = ref([])
const loadingOptions = ref(true)
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    const [usersRes, deptsRes, posRes, locRes] = await Promise.all([
      api.get('/users/manage/'),
      api.get('/departments/'),
      api.get('/positions/'),
      api.get('/checkin-locations/')
    ])
    users.value = usersRes.data.results || usersRes.data || []
    departments.value = deptsRes.data.results || deptsRes.data || []
    positions.value = posRes.data.results || posRes.data || []
    checkinLocations.value = locRes.data.results || locRes.data || []
  } catch (e) {
    error.value = '加载选项失败：' + (e.response?.data?.detail || e.message)
  } finally {
    loadingOptions.value = false
  }
})

function goBack() {
  router.push('/employees/manage')
}

async function handleSave(payload) {
  saving.value = true
  error.value = ''
  try {
    await api.post('/employees/', payload)
    router.push('/employees/manage')
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.error?.message || '创建失败'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page-container {
  max-width: 900px;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
