<template>
  <div class="dashboard-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <h1>公司动态</h1>
        <p class="header-desc">组织运行数据概览</p>
      </div>
      <button class="refresh-btn" @click="reload" :disabled="loading">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ spinning: loading }">
          <path d="M23 4v6h-6" />
          <path d="M1 20v-6h6" />
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
        </svg>
        {{ loading ? '刷新中' : '刷新数据' }}
      </button>
    </header>

    <!-- 错误提示 -->
    <div v-if="error" class="error-banner">
      <strong>加载失败：</strong>{{ error }}
    </div>

    <!-- 快捷导航 -->
    <nav v-if="visibleQuickActions.length > 0" class="quick-nav">
      <router-link 
        v-for="action in visibleQuickActions" 
        :key="action.to" 
        :to="action.to" 
        class="nav-link"
      >
        {{ action.title }}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7" />
        </svg>
      </router-link>
    </nav>

    <!-- 核心数据 -->
    <section class="metrics-section">
      <h2 class="section-label">核心指标</h2>
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">员工总数</span>
          </div>
          <div class="metric-value">{{ loading ? '--' : data.employees.total }}</div>
          <div class="metric-detail">在职 {{ data.employees.active }} / 离职 {{ data.employees.inactive }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">组织架构</span>
          </div>
          <div class="metric-value">{{ loading ? '--' : data.org.departments }}</div>
          <div class="metric-detail">部门数，含 {{ data.org.positions }} 个职位</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">近7天考勤</span>
          </div>
          <div class="metric-value">{{ loading ? '--' : data.attendance.last7d }}</div>
          <div class="metric-detail">打卡记录数</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">待审批</span>
          </div>
          <div class="metric-value">{{ loading ? '--' : data.leaves.pending }}</div>
          <div class="metric-detail">请假申请，近7天新增 {{ data.leaves.recent7d }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">我的待办</span>
          </div>
          <div class="metric-value">{{ todosLoading ? '--' : todos.total }}</div>
          <div class="metric-detail">{{ todosSub }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">{{ data.salary.year }}年薪资</span>
          </div>
          <div class="metric-value">{{ loading ? '--' : data.salary.records }}</div>
          <div class="metric-detail">发放记录</div>
        </div>
      </div>
    </section>

    <!-- 数据图表 -->
    <section class="charts-section">
      <h2 class="section-label">趋势分析</h2>
      <div v-if="loading" class="charts-skeleton">
        <div v-for="n in 4" :key="n" class="skeleton-card">
          <div class="skeleton-bar"></div>
          <div class="skeleton-area"></div>
        </div>
      </div>
      <div v-else class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">最近30天考勤趋势</span>
            <button class="chart-refresh" @click="loadTrend" :disabled="trendLoading">
              {{ trendLoading ? '加载中...' : '刷新' }}
            </button>
          </div>
          <div v-if="trendError" class="chart-error">{{ trendError }}</div>
          <ChartLine v-else :labels="trend.labels" :series="trend.series" />
        </div>
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">最近30天请假类型分布</span>
            <button class="chart-refresh" @click="loadLeavePie" :disabled="leaveLoading">
              {{ leaveLoading ? '加载中...' : '刷新' }}
            </button>
          </div>
          <div v-if="leaveError" class="chart-error">{{ leaveError }}</div>
          <ChartBar v-else :labels="leaveType.labels" :values="leaveType.values" :colors="leaveType.colors" :height="240" x-title="请假类型" y-title="次数" />
        </div>
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">{{ logCalendar.year }}年{{ logCalendar.month }}月日志热力</span>
            <button class="chart-refresh" @click="loadLogCalendar" :disabled="logCalLoading">
              {{ logCalLoading ? '加载中...' : '刷新' }}
            </button>
          </div>
          <div v-if="logCalError" class="chart-error">{{ logCalError }}</div>
          <CalendarLogHeat v-else :year="logCalendar.year" :month="logCalendar.month" :today="logCalendar.today" :days="logCalendar.days" />
        </div>
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">员工流失率（近{{ churn.days }}天）</span>
            <button class="chart-refresh" @click="loadChurn" :disabled="churnLoading">
              {{ churnLoading ? '加载中...' : '刷新' }}
            </button>
          </div>
          <div v-if="churnError" class="chart-error">{{ churnError }}</div>
          <div v-else class="churn-content">
            <div class="churn-main">
              <span class="churn-value">{{ churn.churnRate }}%</span>
              <span class="churn-label">流失率</span>
            </div>
            <div class="churn-stats">
              <span>当前在职 {{ churn.currentActive }}</span>
              <span>近期离职 {{ churn.recentlyInactive }}</span>
              <span>估算期初 {{ churn.startActiveEst }}</span>
            </div>
            <p class="churn-note">流失率 = 近期离职 ÷ 估算期初在职 × 100%</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import api from '../../utils/api';
import { useAuthStore } from '../../stores/auth';
import ChartLine from './components/ChartLine.vue';
import ChartBar from './components/ChartBar.vue';
import CalendarLogHeat from './components/CalendarLogHeat.vue';

const auth = useAuthStore();

function canAccess(permissionKeys) {
  if (auth.user?.is_staff || auth.user?.is_superuser) return true;
  return permissionKeys.some(k => auth.permissions.includes(k));
}

const quickActions = [
  { to: '/employees', title: '员工管理', permissions: ['employee.view', 'manage_employees'] },
  { to: '/departments', title: '组织架构', permissions: ['department.view', 'position.view'] },
  { to: '/attendance', title: '考勤管理', permissions: ['attendance.view', 'attendance.add'] },
  { to: '/salaries', title: '薪资管理', permissions: ['manage_salaries'], staffOnly: true },
  { to: '/leaves', title: '请假管理', permissions: ['leave.view', 'leave.add'] },
  { to: '/documents', title: '文档中心', permissions: ['document.view'] },
  { to: '/system', title: '系统维护', permissions: ['manage_backups', 'manage_system_logs'], staffOnly: true },
];

const visibleQuickActions = computed(() => {
  return quickActions.filter(action => {
    if (action.staffOnly && !auth.user?.is_staff && !auth.user?.is_superuser) {
      return false;
    }
    return canAccess(action.permissions);
  });
});

const loading = ref(false);
const error = ref('');
// 图表状态
const trendLoading = ref(false); const trendError = ref('');
const leaveLoading = ref(false); const leaveError = ref('');
const logCalLoading = ref(false); const logCalError = ref('');
const churnLoading = ref(false); const churnError = ref('');
const data = reactive({
  employees:{ total:0, active:0, inactive:0 },
  org:{ departments:0, positions:0 },
  attendance:{ last7d:0 },
  leaves:{ pending:0, recent7d:0 },
  salary:{ year:0, records:0 },
  logs:{ last24h:0 },
  security:{ permissions:0, roles:0 }
});

const todosLoading = ref(false);
const todosError = ref('');
const todos = reactive({ total: 0, manager_pending: 0, hr_pending: 0 });
const todosSub = computed(() => {
  if (!todos.total) return '暂无待处理审批';
  const parts = [];
  if (todos.manager_pending) parts.push(`直属上级 ${todos.manager_pending}`);
  if (todos.hr_pending) parts.push(`人事 ${todos.hr_pending}`);
  return parts.length ? parts.join(' / ') : '待处理审批';
});

function cardError(section){ return error.value ? error.value : ''; }

async function load() {
  loading.value = true
  error.value = ''
  const resp = await api.get('/summary/')
  if (resp.success && resp.data) {
    Object.keys(data).forEach(k => {
      if (resp.data[k]) Object.assign(data[k], resp.data[k])
    })
  } else {
    error.value = resp.error?.message || '加载失败'
  }
  loading.value = false
}

async function loadTodos() {
  todosLoading.value = true;
  todosError.value = '';
  const resp = await api.get('/todos/');
  if (resp.success && resp.data?.todos) {
    Object.assign(todos, resp.data.todos);
  } else {
    todosError.value = resp.error?.message || '待办加载失败';
    Object.assign(todos, { total: 0, manager_pending: 0, hr_pending: 0 });
  }
  todosLoading.value = false;
}
function reload() { load() }
// 折线图数据
const trend = reactive({ labels: [], series: { total: [], late: [], absent: [] } })
async function loadTrend() {
  trendLoading.value = true
  trendError.value = ''
  const resp = await api.get('/stats/attendance_trend/?days=30')
  if (resp.success && resp.data) {
    const d = resp.data
    trend.labels = d.labels || []
    trend.series.total = d.series?.total || []
    trend.series.late = d.series?.late || []
    trend.series.absent = d.series?.absent || []
  } else {
    trendError.value = resp.error?.message || '趋势加载失败'
  }
  trendLoading.value = false
}
// 请假类型柱状图数据
const leaveType = reactive({ labels: [], values: [], colors: [] })
const palette = ['#4e79a7','#f28e2b','#e15759','#76b7b2','#59a14f','#edc948','#b07aa1','#ff9da7','#9c755f','#bab0ab']
async function loadLeavePie() {
  leaveLoading.value = true
  leaveError.value = ''
  const resp = await api.get('/stats/leave_type/?recent_days=60')
  if (resp.success && resp.data) {
    leaveType.labels = resp.data.labels || []
    leaveType.values = resp.data.values || []
    leaveType.colors = leaveType.labels.map((_, i) => palette[i % palette.length])
  } else {
    leaveError.value = resp.error?.message || '请假统计加载失败'
  }
  leaveLoading.value = false
}
// 日志当月日历数据
const logCalendar = reactive({ year: 0, month: 0, today: '', days: [] })
async function loadLogCalendar() {
  logCalLoading.value = true
  logCalError.value = ''
  const resp = await api.get('/stats/log_calendar/')
  if (resp.success && resp.data) {
    logCalendar.year = resp.data.year
    logCalendar.month = resp.data.month
    logCalendar.today = resp.data.today
    logCalendar.days = resp.data.days || []
  } else {
    logCalError.value = resp.error?.message || '日志月历加载失败'
  }
  logCalLoading.value = false
}
// 员工流失率（近 N 天估算）
const churn = reactive({ churnRate: 0, currentActive: 0, recentlyInactive: 0, startActiveEst: 0, days: 60 })
async function loadChurn() {
  churnLoading.value = true
  churnError.value = ''
  const resp = await api.get(`/stats/employee_churn/?days=${churn.days}`)
  if (resp.success && resp.data) {
    churn.churnRate = resp.data.churn_rate_pct
    churn.currentActive = resp.data.current_active
    churn.recentlyInactive = resp.data.recently_inactive
    churn.startActiveEst = resp.data.start_active_est
  } else {
    churnError.value = resp.error?.message || '流失率加载失败'
  }
  churnLoading.value = false
}
onMounted(() => { load(); loadTodos(); loadTrend(); loadLeavePie(); loadLogCalendar(); loadChurn() })
</script>
<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.header-content h1 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: #0f172a;
}

.header-desc {
  margin: 0;
  font-size: 0.875rem;
  color: #64748b;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  font-size: 0.8125rem;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #f8fafc;
  border-color: rgba(148, 163, 184, 0.6);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn svg {
  width: 16px;
  height: 16px;
}

.refresh-btn svg.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 错误提示 */
.error-banner {
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  font-size: 0.8125rem;
  color: #991b1b;
}

.error-banner strong {
  margin-right: 0.25rem;
}

/* 快捷导航 */
.quick-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 0.875rem;
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #334155;
  text-decoration: none;
  transition: all 0.15s ease;
}

.nav-link:hover {
  background: #f8fafc;
  border-color: rgba(148, 163, 184, 0.6);
  color: #0f172a;
}

.nav-link svg {
  width: 14px;
  height: 14px;
  opacity: 0.5;
}

/* 核心指标 */
.metrics-section,
.charts-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-label {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
}

.metric-card {
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  padding: 1rem 1.125rem;
  transition: border-color 0.15s ease;
}

.metric-card:hover {
  border-color: rgba(148, 163, 184, 0.6);
}

.metric-header {
  margin-bottom: 0.5rem;
}

.metric-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #64748b;
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.2;
  margin-bottom: 0.25rem;
}

.metric-detail {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* 图表区域 */
.charts-skeleton {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.skeleton-card {
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.skeleton-bar {
  height: 14px;
  width: 40%;
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-area {
  height: 140px;
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
}

.chart-card {
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  padding: 1rem 1.125rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: border-color 0.15s ease;
}

.chart-card:hover {
  border-color: rgba(148, 163, 184, 0.6);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.chart-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #374151;
}

.chart-refresh {
  padding: 0.25rem 0.625rem;
  background: transparent;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 5px;
  font-size: 0.75rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
}

.chart-refresh:hover:not(:disabled) {
  background: #f8fafc;
  border-color: rgba(148, 163, 184, 0.6);
}

.chart-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chart-error {
  font-size: 0.75rem;
  color: #dc2626;
}

/* 流失率 */
.churn-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.churn-main {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.churn-value {
  font-size: 2rem;
  font-weight: 600;
  color: #0f172a;
}

.churn-label {
  font-size: 0.8125rem;
  color: #64748b;
}

.churn-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.8125rem;
  color: #475569;
}

.churn-note {
  margin: 0;
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.4;
}

/* 响应式 */
@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .refresh-btn {
    justify-content: center;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .metric-value {
    font-size: 1.5rem;
  }

  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .chart-refresh {
    align-self: stretch;
    text-align: center;
  }
}
</style>
