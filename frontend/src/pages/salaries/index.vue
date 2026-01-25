<template>
  <div class="salary-page">
    <section class="hero-panel">
      <div class="hero-info">
        <div class="hero-icon">
          <img src="/icons/salaries.svg" alt="" style="width:100%;height:100%;" />
        </div>
        <div>
          <h1>薪资管理</h1>
          <p class="hero-text">管理员工薪资记录与差旅报销</p>
        </div>
      </div>
    </section>

    <div class="toast-stack" aria-live="polite" aria-atomic="true">
      <transition name="fade">
        <div v-if="message" class="alert toast" :class="`alert-${message.type}`">
          <div class="alert-icon">
            <img v-if="message.type === 'success'" src="/icons/success.svg" alt="" />
            <img v-else src="/icons/error.svg" alt="" />
          </div>
          <div class="alert-text">{{ message.text }}</div>
          <button type="button" class="alert-close" @click="message = null" aria-label="关闭">×</button>
        </div>
      </transition>
    </div>

    <!-- 功能入口卡片 -->
    <section class="section-block">
      <div class="section-header">
        <div class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" />
            <rect x="14" y="3" width="7" height="7" />
            <rect x="14" y="14" width="7" height="7" />
            <rect x="3" y="14" width="7" height="7" />
          </svg>
          <h2>功能模块</h2>
        </div>
        <span class="section-hint">选择要进入的功能模块</span>
      </div>

      <div class="feature-grid">
        <div class="feature-card" @click="router.push('/salaries/records')">
          <div class="feature-icon records-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
          </div>
          <div class="feature-content">
            <h3>薪资记录</h3>
            <p>查看和管理员工的薪资发放记录</p>
          </div>
          <div class="feature-stats" v-if="stats.salaryCount !== null">
            <span class="stat-value">{{ stats.salaryCount }}</span>
            <span class="stat-label">条记录</span>
          </div>
          <div class="feature-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6" />
            </svg>
          </div>
        </div>

        <div class="feature-card" @click="router.push('/salaries/travel-expense')">
          <div class="feature-icon expense-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
              <line x1="1" y1="10" x2="23" y2="10" />
            </svg>
          </div>
          <div class="feature-content">
            <h3>差旅报销</h3>
            <p>提交和管理差旅费用报销申请</p>
          </div>
          <div class="feature-stats" v-if="stats.expenseCount !== null">
            <span class="stat-value">{{ stats.expenseCount }}</span>
            <span class="stat-label">条申请</span>
          </div>
          <div class="feature-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6" />
            </svg>
          </div>
        </div>

        <div class="feature-card" @click="router.push('/salaries/expense-approval')" v-if="isStaff">
          <div class="feature-icon approval-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
          </div>
          <div class="feature-content">
            <h3>报销审批</h3>
            <p>审批员工提交的差旅报销申请</p>
          </div>
          <div class="feature-stats" v-if="stats.pendingExpense !== null">
            <span class="stat-value highlight">{{ stats.pendingExpense }}</span>
            <span class="stat-label">待审批</span>
          </div>
          <div class="feature-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6" />
            </svg>
          </div>
        </div>

        <div class="feature-card" @click="router.push('/salaries/create')" v-if="isStaff">
          <div class="feature-icon create-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="16" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
          </div>
          <div class="feature-content">
            <h3>新建薪资</h3>
            <p>为员工创建新的薪资发放记录</p>
          </div>
          <div class="feature-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6" />
            </svg>
          </div>
        </div>
      </div>
    </section>

    <!-- 汇总概览 -->
    <section class="section-block" v-if="isStaff">
      <div class="section-header">
        <div class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12h18" />
            <path d="M3 6h18" />
            <path d="M3 18h18" />
          </svg>
          <h2>数据概览</h2>
        </div>
        <span class="section-hint">本月薪资与报销数据汇总</span>
      </div>

      <div class="summary-grid">
        <div class="summary-card">
          <span class="summary-label">本月薪资</span>
          <span class="summary-value">{{ formatCurrency(stats.monthSalaryTotal) }}</span>
          <span class="summary-desc">{{ stats.monthSalaryCount }} 条发放记录</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">本月报销</span>
          <span class="summary-value">{{ formatCurrency(stats.monthExpenseTotal) }}</span>
          <span class="summary-desc">{{ stats.monthExpenseCount }} 条已批准</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">待审批报销</span>
          <span class="summary-value">{{ stats.pendingExpense }}</span>
          <span class="summary-desc">条待处理</span>
        </div>
        <div class="summary-card highlight-card">
          <span class="summary-label">员工总数</span>
          <span class="summary-value">{{ stats.employeeCount }}</span>
          <span class="summary-desc">在职员工</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const message = ref(null)

const auth = useAuthStore()
const isStaff = computed(() => auth.user?.is_staff || auth.user?.is_superuser || auth.roles?.some(r=>r.code==='admin'))

const stats = reactive({
  salaryCount: null,
  expenseCount: null,
  pendingExpense: null,
  monthSalaryTotal: 0,
  monthSalaryCount: 0,
  monthExpenseTotal: 0,
  monthExpenseCount: 0,
  employeeCount: 0
})

function formatCurrency(value) {
  const num = Number(value)
  return Number.isFinite(num) ? `¥${num.toFixed(2)}` : '¥0.00'
}

async function loadStats() {
  try {
    // 薪资记录数量
    const salaryRes = await api.get('/salaries/')
    if (salaryRes.success) {
      const data = salaryRes.data
      const records = data.results || data.data || data || []
      stats.salaryCount = records.length
      
      // 本月薪资统计
      const now = new Date()
      const currentYear = now.getFullYear()
      const currentMonth = now.getMonth() + 1
      const monthRecords = records.filter(r => r.year === currentYear && r.month === currentMonth)
      stats.monthSalaryCount = monthRecords.length
      stats.monthSalaryTotal = monthRecords.reduce((sum, r) => {
        return sum + (Number(r.basic_salary) || 0) + (Number(r.bonus) || 0) + (Number(r.allowance) || 0)
      }, 0)
    }

    // 差旅报销数量
    const expenseRes = await api.get('/travel-expenses/')
    if (expenseRes.success) {
      const data = expenseRes.data
      const records = data.results || data.data || data || []
      stats.expenseCount = records.length
      stats.pendingExpense = records.filter(r => r.status === 'pending').length
      
      // 本月已批准报销统计
      const now = new Date()
      const currentYear = now.getFullYear()
      const currentMonth = now.getMonth() + 1
      const approvedThisMonth = records.filter(r => {
        if (r.status !== 'approved' && r.status !== 'paid') return false
        const date = new Date(r.created_at)
        return date.getFullYear() === currentYear && date.getMonth() + 1 === currentMonth
      })
      stats.monthExpenseCount = approvedThisMonth.length
      stats.monthExpenseTotal = approvedThisMonth.reduce((sum, r) => sum + (Number(r.amount) || 0), 0)
    }

    // 员工数量
    if (isStaff.value) {
      const empRes = await api.get('/employees/', { params: { page_size: 1 } })
      if (empRes.success) {
        stats.employeeCount = empRes.data.count || 0
      }
    }
  } catch (error) {
    console.error('加载统计数据失败', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.salary-page {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  padding: 2.25rem;
  min-height: 100vh;
  box-sizing: border-box;
  background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.08), transparent 55%), #f5f7fb;
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
  flex-wrap: wrap;
  padding: 1.8rem;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.85), rgba(255, 255, 255, 0.95));
  box-shadow: 0 26px 45px rgba(15, 23, 42, 0.08);
}

.hero-info {
  display: flex;
  align-items: center;
  gap: 1.1rem;
}

.hero-icon {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
}

.hero-panel h1 {
  margin: 0 0 0.35rem;
  font-size: 26px;
  color: #0f172a;
}

.hero-text {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  max-width: 520px;
}

.toast-stack {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  z-index: 2000;
  max-width: min(420px, calc(100vw - 2.5rem));
}

.toast {
  width: 100%;
}

.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.95rem;
  border-radius: 12px;
  font-size: 14px;
  box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
}

.alert-icon {
  flex: 0 0 auto;
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
}

.alert-icon img {
  width: 22px;
  height: 22px;
  display: block;
}

.alert-text {
  flex: 1;
}

.alert-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  padding: 0 0.2rem;
}

.alert-success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.section-block {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.96));
  border-radius: 18px;
  box-shadow: 0 22px 40px rgba(15, 23, 42, 0.08);
  border: 1px solid rgba(226, 232, 240, 0.8);
  padding: 1.6rem;
  gap: 1.1rem;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.section-title {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 16px;
  color: #0f172a;
  font-weight: 600;
}

.section-title h2 {
  margin: 0;
  font-size: inherit;
  font-weight: inherit;
  line-height: 1;
}

.section-title svg {
  width: 18px;
  height: 18px;
  color: #4338ca;
  flex-shrink: 0;
}

.section-hint {
  font-size: 12px;
  color: #94a3b8;
}

/* 功能入口卡片 */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.4rem;
  border: 1px solid rgba(226, 232, 240, 0.85);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.98);
  cursor: pointer;
  transition: all 0.25s ease;
}

.feature-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 35px rgba(79, 70, 229, 0.15);
  border-color: rgba(99, 102, 241, 0.35);
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.feature-icon svg {
  width: 24px;
  height: 24px;
}

.records-icon {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
  color: #6366f1;
}

.expense-icon {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(52, 211, 153, 0.1));
  color: #10b981;
}

.approval-icon {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(251, 191, 36, 0.1));
  color: #f59e0b;
}

.create-icon {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(96, 165, 250, 0.1));
  color: #3b82f6;
}

.feature-content {
  flex: 1;
  min-width: 0;
}

.feature-content h3 {
  margin: 0 0 0.35rem;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.feature-content p {
  margin: 0;
  font-size: 13px;
  color: #64748b;
  line-height: 1.4;
}

.feature-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.15rem;
  flex-shrink: 0;
}

.feature-stats .stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #4338ca;
}

.feature-stats .stat-value.highlight {
  color: #f59e0b;
}

.feature-stats .stat-label {
  font-size: 11px;
  color: #94a3b8;
}

.feature-arrow {
  width: 24px;
  height: 24px;
  color: #cbd5e1;
  flex-shrink: 0;
  transition: transform 0.2s ease, color 0.2s ease;
}

.feature-card:hover .feature-arrow {
  transform: translateX(4px);
  color: #6366f1;
}

.feature-arrow svg {
  width: 100%;
  height: 100%;
}

/* 汇总卡片 */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-card {
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 16px;
  padding: 1.3rem 1.4rem;
  background: rgba(255, 255, 255, 0.96);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.summary-card.highlight-card {
  border-color: rgba(99, 102, 241, 0.4);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.14), rgba(139, 92, 246, 0.1));
  box-shadow: 0 20px 38px rgba(79, 70, 229, 0.12);
}

.summary-label {
  font-size: 12px;
  color: #94a3b8;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.summary-desc {
  font-size: 13px;
  color: #64748b;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 900px) {
  .hero-panel {
    padding: 1.4rem;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .salary-page {
    padding: 1.4rem;
  }

  .feature-card {
    flex-wrap: wrap;
  }

  .feature-stats {
    flex-direction: row;
    gap: 0.5rem;
    align-items: baseline;
  }
}
</style>
