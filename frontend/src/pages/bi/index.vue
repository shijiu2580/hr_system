<template>
  <div class="page-grid bi-page">
    <div class="page-hero">
      <div class="hero-info">
        <div class="hero-icon">
          <img src="/icons/bi.svg" alt="" style="width:100%;height:100%;" />
        </div>
        <div>
          <h2>BI 报表</h2>
          <p class="hero-subtitle">深度经营分析与趋势洞察</p>
        </div>
      </div>
      <div class="hero-actions">
        <div class="filters">
          <div class="filter-group">
            <label>考勤周期</label>
            <select v-model="daysRange">
              <option :value="30">近 30 天</option>
              <option :value="60">近 60 天</option>
              <option :value="90">近 90 天</option>
            </select>
          </div>
          <div class="filter-group">
            <label>请假周期</label>
            <select v-model="leaveDaysRange">
              <option :value="90">近 3 个月</option>
              <option :value="180">近 6 个月</option>
              <option :value="365">近 1 年</option>
            </select>
          </div>
          <div class="filter-group">
            <label>流动趋势</label>
            <select v-model="turnoverMonths">
              <option :value="6">近 6 个月</option>
              <option :value="12">近 1 年</option>
              <option :value="24">近 2 年</option>
            </select>
          </div>
        </div>
        <button class="btn outline icon-btn" @click="reloadAll" :disabled="loadingAll">
          <img src="/icons/refresh.svg" alt="" class="btn-icon" />
          <span>{{ loadingAll ? '刷新中...' : '刷新' }}</span>
        </button>
      </div>
    </div>

    <div v-if="lastUpdated" class="update-hint">更新于 {{ lastUpdated }}</div>

    <div v-if="error" class="alert alert-error">
      <img src="/icons/error.svg" alt="" class="alert-icon" />
      <div>
        <strong>加载失败</strong>
        <p>{{ error }}</p>
      </div>
    </div>

    <!-- KPI 指标 -->
    <section class="section-grid metrics-section" v-if="kpi">
      <div class="section-header">
        <div class="section-title">
          <h3>核心经营指标</h3>
        </div>
        <span class="section-hint">滚动窗口统计（近 30~90 天）</span>
      </div>
      <div class="metrics-grid">
        <div class="metric-card">
          <p class="metric-label">本月人均薪资</p>
          <p class="metric-value">￥{{ formatNumber(kpi.avgSalary) }}</p>
          <p class="metric-desc">统计区间 {{ kpi.salaryPeriod }}</p>
        </div>
        <div class="metric-card">
          <p class="metric-label">月度流动率</p>
          <p class="metric-value">{{ kpi.turnoverRate }}%</p>
          <p class="metric-desc">当月离职 / 月末在职</p>
        </div>
        <div class="metric-card">
          <p class="metric-label">近 {{ daysRange }} 天迟到</p>
          <p class="metric-value">{{ kpi.late30 }} 次</p>
          <p class="metric-desc">异常打卡次数</p>
        </div>
        <div class="metric-card">
          <p class="metric-label">近 {{ leaveDaysRange }} 天请假天数</p>
          <p class="metric-value">{{ kpi.leaveDays90 }}</p>
          <p class="metric-desc">部门累计请假天数</p>
        </div>
      </div>
    </section>

    <!-- 图表区域 -->
    <section class="section-grid charts-section">
      <div class="chart-card">
        <div class="chart-header">
          <h3>部门人力成本</h3>
          <span class="section-hint">上月薪资总额与占比</span>
        </div>
        <div class="chart-container-line">
          <canvas ref="deptCostChartRef"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>薪资区间分布</h3>
          <span class="section-hint">上月净薪分布</span>
        </div>
        <div class="chart-container-line">
          <canvas ref="salaryRangeChartRef"></canvas>
        </div>
      </div>

      <div class="chart-card large">
        <div class="chart-header">
          <h3>员工流动趋势</h3>
          <span class="section-hint">近 12 个月入职/离职/净增长</span>
        </div>
        <div class="chart-container-line">
          <canvas ref="turnoverChartRef"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>每日出勤率</h3>
          <span class="section-hint">近 30 天出勤率趋势</span>
        </div>
        <div class="chart-container-line">
          <canvas ref="dailyAttendanceChartRef"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>考勤热力矩阵</h3>
          <span class="section-hint">近 30 天考勤结构</span>
        </div>
        <div class="chart-container-line">
          <canvas ref="attendanceHeatmapRef"></canvas>
        </div>
      </div>

      <div class="chart-card large">
        <div class="chart-header">
          <h3>部门请假负荷</h3>
          <span class="section-hint">近 90 天请假天数</span>
        </div>
        <div class="chart-container-line">
          <canvas ref="leaveDeptChartRef"></canvas>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import api from '../../utils/api';
import Chart from 'chart.js/auto';

const loadingAll = ref(false);
const error = ref('');
const kpi = ref(null);
const lastUpdated = ref('');

const daysRange = ref(30);
const leaveDaysRange = ref(90);
const turnoverMonths = ref(12);

const deptCostChartRef = ref(null);
const salaryRangeChartRef = ref(null);
const turnoverChartRef = ref(null);
const dailyAttendanceChartRef = ref(null);
const attendanceHeatmapRef = ref(null);
const leaveDeptChartRef = ref(null);

let deptCostChart, salaryRangeChart, turnoverChart, dailyAttendanceChart, attendanceHeatmapChart, leaveDeptChart;

function formatNumber(n) {
  if (n === null || n === undefined) return '0';
  return Number(n).toLocaleString('zh-CN', { maximumFractionDigits: 2 });
}

function destroyCharts() {
  [deptCostChart, salaryRangeChart, turnoverChart, dailyAttendanceChart, attendanceHeatmapChart, leaveDeptChart].forEach(c => {
    if (c) c.destroy();
  });
}

async function loadDepartmentCost() {
  const res = await api.get('/bi/department-cost/');
  if (!res.success) throw new Error(res.error?.message || '加载部门成本失败');
  const data = res.data;
  if (!deptCostChartRef.value) return;
  if (deptCostChart) deptCostChart.destroy();
  deptCostChart = new Chart(deptCostChartRef.value.getContext('2d'), {
    type: 'bar',
    data: {
      labels: data.items.map(i => i.department),
      datasets: [{
        label: '薪资总额 (￥)',
        data: data.items.map(i => i.total_salary),
        backgroundColor: '#3b82f6'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: { x: { beginAtZero: true } }
    }
  });
  return data;
}

async function loadSalaryRange() {
  const res = await api.get('/bi/salary-range/');
  if (!res.success) throw new Error(res.error?.message || '加载薪资分布失败');
  const data = res.data;
  if (!salaryRangeChartRef.value) return;
  if (salaryRangeChart) salaryRangeChart.destroy();
  salaryRangeChart = new Chart(salaryRangeChartRef.value.getContext('2d'), {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [{
        label: '人数',
        data: data.values,
        backgroundColor: '#10b981'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } }
    }
  });
  return data;
}

async function loadTurnover() {
  const res = await api.get(`/bi/turnover/?months=${turnoverMonths.value}`);
  if (!res.success) throw new Error(res.error?.message || '加载流动趋势失败');
  const data = res.data;
  if (!turnoverChartRef.value) return;
  if (turnoverChart) turnoverChart.destroy();
  turnoverChart = new Chart(turnoverChartRef.value.getContext('2d'), {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [
        { label: '入职', data: data.joined, borderColor: '#3b82f6', tension: 0.3 },
        { label: '离职', data: data.left, borderColor: '#ef4444', tension: 0.3 },
        { label: '净增长', data: data.net, borderColor: '#10b981', tension: 0.3 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } }
    }
  });
  return data;
}

async function loadDailyAttendance() {
  const res = await api.get(`/bi/daily-attendance/?days=${daysRange.value}`);
  if (!res.success) throw new Error(res.error?.message || '加载出勤率失败');
  const data = res.data;
  if (!dailyAttendanceChartRef.value) return;
  if (dailyAttendanceChart) dailyAttendanceChart.destroy();
  dailyAttendanceChart = new Chart(dailyAttendanceChartRef.value.getContext('2d'), {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        label: '出勤率 %',
        data: data.rates,
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99,102,241,0.15)',
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true, max: 100 } }
    }
  });
  return data;
}

async function loadAttendanceHeatmap() {
  const res = await api.get(`/bi/attendance-heatmap/?days=${daysRange.value}`);
  if (!res.success) throw new Error(res.error?.message || '加载考勤热力失败');
  const data = res.data;
  if (!attendanceHeatmapRef.value) return;
  if (attendanceHeatmapChart) attendanceHeatmapChart.destroy();

  // 简化：使用堆叠条形图模拟热力矩阵
  const datasets = data.types.map((t, idx) => ({
    label: t,
    data: data.matrix.map(row => row[idx]),
    backgroundColor: ['#22c55e', '#f97316', '#eab308', '#ef4444'][idx] || '#94a3b8'
  }));

  attendanceHeatmapChart = new Chart(attendanceHeatmapRef.value.getContext('2d'), {
    type: 'bar',
    data: {
      labels: data.weekdays,
      datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } }
    }
  });
  return data;
}

async function loadLeaveDept() {
  const res = await api.get(`/bi/leave-balance/?days=${leaveDaysRange.value}`);
  if (!res.success) throw new Error(res.error?.message || '加载请假负荷失败');
  const data = res.data;
  if (!leaveDeptChartRef.value) return;
  if (leaveDeptChart) leaveDeptChart.destroy();
  leaveDeptChart = new Chart(leaveDeptChartRef.value.getContext('2d'), {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [{
        label: '请假天数',
        data: data.values,
        backgroundColor: '#f59e0b'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: { x: { beginAtZero: true } }
    }
  });
  return data;
}

async function reloadAll() {
  loadingAll.value = true;
  error.value = '';
  try {
    const [deptCost, salaryRange, turnover, dailyAtt, heatmap, leaveDept] = await Promise.all([
      loadDepartmentCost(),
      loadSalaryRange(),
      loadTurnover(),
      loadDailyAttendance(),
      loadAttendanceHeatmap(),
      loadLeaveDept(),
    ]);

    kpi.value = {
      avgSalary: salaryRange?.total ? Math.round((deptCost?.grand_total || 0) / salaryRange.total) : 0,
      salaryPeriod: deptCost?.period || '-',
      turnoverRate: turnover?.turnover_rate?.slice(-1)[0] || 0,
      late30: dailyAtt?.lates?.reduce((a, b) => a + b, 0) || 0,
      leaveDays90: leaveDept?.values?.reduce((a, b) => a + b, 0) || 0,
    };
    lastUpdated.value = new Date().toLocaleString('zh-CN');
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

watch([daysRange, leaveDaysRange, turnoverMonths], () => {
  if (!loadingAll.value) {
    reloadAll();
  }
});

onBeforeUnmount(() => {
  destroyCharts();
});
</script>

<style scoped>
.bi-page {
  gap: 1.25rem;
}

.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
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
  align-items: center;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 14px;
  color: #64748b;
  white-space: nowrap;
  font-weight: 500;
}

.filter-group select {
  width: 130px;
  background-color: #fff;
}

[data-theme="dark"] .filter-group label {
  color: #94a3b8;
}

[data-theme="dark"] .filter-group select {
  background-color: #1e293b;
  border-color: #334155;
  color: #e2e8f0;
}

.update-hint {
  font-size: 12px;
  color: #94a3b8;
  margin-top: -0.5rem;
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

.btn-icon {
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

.alert-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
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

.section-hint {
  font-size: 12px;
  color: #9ca3af;
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
