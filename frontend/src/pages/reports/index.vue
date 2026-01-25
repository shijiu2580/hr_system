<template>
  <div class="page-grid reports-page">
    <div class="page-hero">
      <div class="hero-info">
        <div class="hero-icon">
          <img src="/icons/reports.svg" alt="" style="width:100%;height:100%;" />
        </div>
        <div>
          <h2>数据报表</h2>
          <p class="hero-subtitle">组织运行数据统计</p>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn outline icon-btn" @click="reloadAll" :disabled="loadingAll">
          <img src="/icons/refresh.svg" alt="" class="btn-icon" />
          <span>{{ loadingAll ? '刷新中...' : '刷新' }}</span>
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">
      <img src="/icons/error.svg" alt="" class="alert-icon" />
      <div>
        <strong>加载失败</strong>
        <p>{{ error }}</p>
      </div>
    </div>

    <!-- 顶部总览指标 -->
    <section class="section-grid metrics-section" v-if="overview">
      <div class="section-header">
        <div class="section-title">
          <h3>核心指标总览</h3>
        </div>
        <span class="section-hint">最近一个自然月的核心经营指标快照。</span>
      </div>
      <div class="metrics-grid">
        <div class="metric-card">
          <p class="metric-label">在职员工</p>
          <p class="metric-value">{{ overview.employees.active }}</p>
          <p class="metric-desc">总人数 {{ overview.employees.total }}，待入职 {{ overview.employees.pending || 0 }}，本月新入职 {{ overview.employees.new_this_month }}</p>
        </div>
        <div class="metric-card">
          <p class="metric-label">本月薪资支出</p>
          <p class="metric-value">￥{{ formatNumber(overview.salary.this_month) }}</p>
          <p class="metric-desc">较上月 {{ overview.salary.change >= 0 ? '增加' : '减少' }} ￥{{ formatNumber(Math.abs(overview.salary.change)) }}</p>
        </div>
        <div class="metric-card">
          <p class="metric-label">本月出勤率</p>
          <p class="metric-value">{{ overview.attendance.rate }}%</p>
          <p class="metric-desc">打卡 {{ overview.attendance.this_month }} 次，迟到 {{ overview.attendance.late_this_month }} 次</p>
        </div>
        <div class="metric-card">
          <p class="metric-label">本月请假</p>
          <p class="metric-value">{{ overview.leaves.this_month }}</p>
          <p class="metric-desc">待审批 {{ overview.leaves.pending }} 条</p>
        </div>
      </div>
    </section>

    <!-- 图表区域 -->
    <section class="section-grid charts-section">
      <div class="chart-card">
        <div class="chart-header">
          <h3>部门人员分布</h3>
          <span class="section-hint">展示各部门在职员工数量占比。</span>
        </div>
        <div class="chart-container-sm">
          <canvas ref="deptChartRef"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>考勤结构</h3>
          <span class="section-hint">统计最近 30 天不同考勤类型占比。</span>
        </div>
        <div class="chart-container-sm">
          <canvas ref="attendanceChartRef"></canvas>
        </div>
      </div>

      <div class="chart-card large">
        <div class="chart-header">
          <h3>月度薪资支出趋势</h3>
          <span class="section-hint">观察近 12 个月的薪资支出变化趋势。</span>
        </div>
        <div class="chart-container-line">
          <canvas ref="salaryChartRef"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>请假类型分析</h3>
          <span class="section-hint">近 90 天不同请假类型数量。</span>
        </div>
        <canvas ref="leaveChartRef"></canvas>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>职位分布 Top 15</h3>
          <span class="section-hint">在职人数最多的职位。</span>
        </div>
        <canvas ref="positionChartRef"></canvas>
      </div>

      <div class="chart-card large">
        <div class="chart-header">
          <h3>员工规模变化</h3>
          <span class="section-hint">近 12 个月员工总数与在职人数。</span>
        </div>
        <div class="chart-container-line">
          <canvas ref="empGrowthChartRef"></canvas>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import api from '../../utils/api';
import Chart from 'chart.js/auto';

const loadingAll = ref(false);
const error = ref('');
const overview = ref(null);

const deptChartRef = ref(null);
const salaryChartRef = ref(null);
const attendanceChartRef = ref(null);
const leaveChartRef = ref(null);
const empGrowthChartRef = ref(null);
const positionChartRef = ref(null);

let deptChart, salaryChart, attendanceChart, leaveChart, empGrowthChart, positionChart;

function formatNumber(n) {
  if (n === null || n === undefined) return '0';
  return Number(n).toLocaleString('zh-CN', { maximumFractionDigits: 2 });
}

function destroyCharts() {
  [deptChart, salaryChart, attendanceChart, leaveChart, empGrowthChart, positionChart].forEach(c => {
    if (c) c.destroy();
  });
}

async function loadOverview() {
  const res = await api.get('/reports/overview/');
  if (!res.success) throw new Error(res.error?.message || '加载概览失败');
  overview.value = res.data;
}

async function loadDeptChart() {
  const res = await api.get('/reports/department_distribution/');
  if (!res.success) throw new Error(res.error?.message || '加载部门分布失败');
  const data = res.data;
  if (!deptChartRef.value) return;
  if (deptChart) deptChart.destroy();
  deptChart = new Chart(deptChartRef.value.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values,
        backgroundColor: data.colors || [
          '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
          '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'
        ]
      }]
    },
    options: {
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}

async function loadSalaryChart() {
  const res = await api.get('/reports/monthly_salary/?months=12');
  if (!res.success) throw new Error(res.error?.message || '加载薪资趋势失败');
  const data = res.data;
  if (!salaryChartRef.value) return;
  if (salaryChart) salaryChart.destroy();
  salaryChart = new Chart(salaryChartRef.value.getContext('2d'), {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        label: '薪资支出 (￥)',
        data: data.totals,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59,130,246,0.15)',
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

async function loadAttendanceChart() {
  const res = await api.get('/reports/attendance_rate/?days=30');
  if (!res.success) throw new Error(res.error?.message || '加载考勤统计失败');
  const data = res.data;
  if (!attendanceChartRef.value) return;
  if (attendanceChart) attendanceChart.destroy();
  attendanceChart = new Chart(attendanceChartRef.value.getContext('2d'), {
    type: 'pie',
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values,
        backgroundColor: [
          '#22c55e', '#f97316', '#ef4444', '#e5e7eb', '#a855f7'
        ]
      }]
    },
    options: {
      plugins: { legend: { position: 'bottom' } }
    }
  });
}

async function loadLeaveChart() {
  const res = await api.get('/reports/leave_analysis/?days=90');
  if (!res.success) throw new Error(res.error?.message || '加载请假分析失败');
  const data = res.data;
  if (!leaveChartRef.value) return;
  if (leaveChart) leaveChart.destroy();
  const labels = Object.values(data.type_stats).map(i => i.label);
  const values = Object.values(data.type_stats).map(i => i.count);
  leaveChart = new Chart(leaveChartRef.value.getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: '请假次数',
        data: values,
        backgroundColor: '#3b82f6'
      }]
    },
    options: {
      indexAxis: 'y',
      scales: { x: { beginAtZero: true } }
    }
  });
}

async function loadEmpGrowthChart() {
  const res = await api.get('/reports/employee_growth/?months=12');
  if (!res.success) throw new Error(res.error?.message || '加载员工增长失败');
  const data = res.data;
  if (!empGrowthChartRef.value) return;
  if (empGrowthChart) empGrowthChart.destroy();
  empGrowthChart = new Chart(empGrowthChartRef.value.getContext('2d'), {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [
        {
          label: '员工总数',
          data: data.total_series,
          borderColor: '#3b82f6',
          tension: 0.3
        },
        {
          label: '在职人数',
          data: data.active_series,
          borderColor: '#10b981',
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } }
    }
  });
}

async function loadPositionChart() {
  const res = await api.get('/reports/position_distribution/');
  if (!res.success) throw new Error(res.error?.message || '加载职位分布失败');
  const data = res.data;
  if (!positionChartRef.value) return;
  if (positionChart) positionChart.destroy();
  positionChart = new Chart(positionChartRef.value.getContext('2d'), {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [{
        label: '在职人数',
        data: data.values,
        backgroundColor: '#6366f1'
      }]
    },
    options: {
      indexAxis: 'y',
      scales: { x: { beginAtZero: true } }
    }
  });
}

async function reloadAll() {
  loadingAll.value = true;
  error.value = '';
  try {
    await Promise.all([
      loadOverview(),
      loadDeptChart(),
      loadSalaryChart(),
      loadAttendanceChart(),
      loadLeaveChart(),
      loadEmpGrowthChart(),
      loadPositionChart()
    ]);
  } catch (e) {
    console.error(e);
    error.value = e?.response?.data?.detail || e.message || '加载失败';
  } finally {
    loadingAll.value = false;
  }
}

onMounted(() => {
  reloadAll();
});

onBeforeUnmount(() => {
  destroyCharts();
});
</script>

<style scoped>
.reports-page {
  gap: 1.25rem;
}

.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  margin-bottom: .5rem;
}

.hero-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.hero-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-icon svg {
  width: 24px;
  height: 24px;
}

.hero-info h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 .25rem;
}

.hero-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.hero-actions {
  display: flex;
  gap: .5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  padding: .5rem 1rem;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all .2s;
}

.btn.outline {
  background: #fff;
  border: 1px solid #e2e8f0;
  color: #334155;
}

.btn.outline:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn.outline:disabled {
  opacity: .6;
  cursor: not-allowed;
}

.icon-btn svg {
  width: 16px;
  height: 16px;
}

.alert {
  display: flex;
  align-items: flex-start;
  gap: .75rem;
  padding: .85rem 1rem;
  border-radius: 8px;
  font-size: 14px;
}

.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.alert-error svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  stroke: #dc2626;
}

.metrics-section {
  margin-bottom: .25rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: .75rem;
}

.section-title h3 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.alert-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: .9rem;
}

.metric-card {
  background: #fff;
  border-radius: 10px;
  padding: .85rem 1rem;
  border: 1px solid #e5e7eb;
}

.metric-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: .25rem;
}

.metric-value {
  font-size: 22px;
  font-weight: 600;
  color: #111827;
  margin-bottom: .15rem;
}

.metric-desc {
  font-size: 12px;
  color: #9ca3af;
}

.section-grid {
  background: transparent;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.chart-card {
  background: #fff;
  border-radius: 10px;
  padding: .85rem 1rem 1rem;
  border: 1px solid #e5e7eb;
}

.chart-card.large {
  grid-column: span 2 / span 2;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: .6rem;
}

.chart-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
}

.section-hint {
  font-size: 12px;
  color: #9ca3af;
}

.chart-container-sm {
  max-width: 280px;
  max-height: 280px;
  margin: 0 auto;
}

.chart-container-line {
  position: relative;
  height: 280px;
  width: 100%;
}

canvas {
  max-width: 100%;
}

@media (max-width: 1024px) {
  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .charts-section {
    grid-template-columns: minmax(0, 1fr);
  }
  .chart-card.large {
    grid-column: auto;
  }
}

[data-theme="dark"] .metric-card,
[data-theme="dark"] .chart-card {
  background: #18181b;
  border-color: #27272a;
}

[data-theme="dark"] .metric-label,
[data-theme="dark"] .section-hint {
  color: #9ca3af;
}

[data-theme="dark"] .metric-value,
[data-theme="dark"] .chart-header h3 {
  color: #e5e7eb;
}

[data-theme="dark"] .page-hero {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

[data-theme="dark"] .hero-info h2 {
  color: #f1f5f9;
}

[data-theme="dark"] .hero-subtitle {
  color: #94a3b8;
}

[data-theme="dark"] .btn.outline {
  background: #1e293b;
  border-color: #334155;
  color: #e2e8f0;
}

[data-theme="dark"] .btn.outline:hover {
  background: #334155;
}

[data-theme="dark"] .section-title h3 {
  color: #f1f5f9;
}
</style>
