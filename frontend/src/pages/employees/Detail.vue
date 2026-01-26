<template>
  <div class="employee-detail">
    <header class="page-header">
      <div>
        <h1>
          <img src="/icons/employees.svg" alt="" class="header-icon" />
          员工详情
        </h1>
        <p class="muted">查看员工的基础信息与历史薪资记录。</p>
      </div>
      <router-link to="/employees/list" class="btn-secondary">返回员工列表</router-link>
    </header>

    <div v-if="loading" class="loading-dots-text">
      <div class="dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
      <span>正在加载...</span>
    </div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>

    <section v-else class="card">
      <header class="card-header">
        <h2>{{ emp?.name }} <span class="emp-id">{{ emp?.employee_id }}</span></h2>
      </header>
      <div class="grid">
        <div class="field"><span class="label">部门</span><span class="value">{{ emp?.department?.name || '未填写' }}</span></div>
        <div class="field"><span class="label">职位</span><span class="value">{{ emp?.position?.name || '未填写' }}</span></div>
        <div class="field"><span class="label">基本工资</span><span class="value">{{ formatCurrency(emp?.salary) }}</span></div>
        <div class="field"><span class="label">入职日期</span><span class="value">{{ formatDate(emp?.hire_date) }}</span></div>
        <div class="field"><span class="label">在职状态</span><span class="value">{{ emp?.is_active ? '在职' : '离职' }}</span></div>
      </div>
    </section>

    <section class="card" v-if="!loading">
      <header class="card-header">
        <h2>历史薪资记录 <span class="record-count">(共{{ salaries.length }}条)</span></h2>
      </header>
      <div v-if="salaries.length">
        <table class="salary-table">
          <thead>
            <tr>
              <th>年份</th>
              <th>月份</th>
              <th>基本工资</th>
              <th>奖金</th>
              <th>加班费</th>
              <th>津贴</th>
              <th>实发工资</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in pagedSalaries" :key="item.id">
              <td>{{ item.year }}</td>
              <td>{{ String(item.month).padStart(2,'0') }}</td>
              <td>{{ formatCurrency(item.basic_salary) }}</td>
              <td>{{ formatCurrency(item.bonus) }}</td>
              <td>{{ formatCurrency(item.overtime_pay) }}</td>
              <td>{{ formatCurrency(item.allowance) }}</td>
              <td class="highlight">{{ formatCurrency(item.net_salary) }}</td>
              <td>
                <span class="status-badge" :class="item.paid ? 'paid' : 'unpaid'">
                  {{ item.paid ? '已发放' : '未发放' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <!-- 分页 -->
        <div class="table-footer" v-if="totalPages > 1">
          <span class="total-count">共{{ salaries.length }}条记录</span>
          <div class="pagination">
            <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage = 1">«</button>
            <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage--">‹</button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage++">›</button>
            <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage = totalPages">»</button>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">暂无薪资记录</div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../utils/api'

const route = useRoute()
const id = route.params.id
const loading = ref(true)
const error = ref('')
const emp = ref(null)
const salaries = ref([])

// 分页
const pageSize = 10
const currentPage = ref(1)

const totalPages = computed(() => Math.ceil(salaries.value.length / pageSize) || 1)

const pagedSalaries = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return salaries.value.slice(start, start + pageSize)
})

function formatCurrency(value) {
  const num = Number(value || 0)
  return `¥${num.toFixed(2)}`
}

function formatDate(d) {
  if (!d) return ''
  try {
    const dt = new Date(d)
    return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
  } catch {
    return d
  }
}

onMounted(async () => {
  try {
    const { data: empRes } = await api.get(`/employees/${id}/`)
    emp.value = empRes.data || empRes
    // 获取该员工的所有薪资记录，不限制数量
    const { data: salRes } = await api.get('/salaries/', { params: { employee: id, page_size: 1000 } })
    const raw = salRes.results || salRes.data || salRes || []
    // 按年份月份倒序排列（最新的在前）
    salaries.value = (Array.isArray(raw) ? raw : []).sort((a, b) => {
      if (a.year !== b.year) return b.year - a.year
      return b.month - a.month
    })
  } catch (e) {
    error.value = e.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.page-header h1 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.header-icon {
  width: 24px;
  height: 24px;
  color: #4f46e5;
}
.muted { color: #64748b; font-size: 13px; }
.btn-secondary { padding: .5rem .8rem; background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; color: #334155; text-decoration: none; }
.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: .75rem; }
.emp-id { margin-left: .5rem; color: #64748b; font-size: 14px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: .75rem 1rem; }
.field { display: flex; justify-content: space-between; background: #f8fafc; border: 1px solid #eef2f7; border-radius: 8px; padding: .5rem .75rem; }
.label { color: #64748b; }
.value { color: #334155; font-weight: 500; }
.salary-table { width: 100%; border-collapse: collapse; }
.salary-table th, .salary-table td { padding: .5rem .6rem; border-bottom: 1px solid #eef2f7; font-size: 13px; }
.salary-table .highlight { color: #4f46e5; font-weight: 600; }
.loading { padding: 1rem; }
.alert { padding: .75rem; border-radius: 8px; }
.alert-error { background: #fee2e2; color: #7f1d1d; border: 1px solid #fecaca; }
.record-count { font-size: 14px; color: #64748b; font-weight: 400; }
.empty-state { padding: 2rem; text-align: center; color: #94a3b8; }

/* 状态徽章 */
.status-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}
.status-badge.paid { background: #dcfce7; color: #16a34a; }
.status-badge.unpaid { background: #fef3c7; color: #d97706; }

/* 分页 */
.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  margin-top: 0.5rem;
  border-top: 1px solid #f1f5f9;
}

.total-count {
  font-size: 13px;
  color: #64748b;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #64748b;
}

.page-btn:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #475569;
  min-width: 60px;
  text-align: center;
}
</style>
