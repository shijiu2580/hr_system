<template>
  <div class="page-grid alerts-page">
    <div class="card alerts-card">
      <!-- 顶部标签栏 -->
      <div class="tab-header">
        <div class="tab-left">
          <div class="tab-icon">
            <img src="/icons/attendance.svg" alt="" />
          </div>
          <div class="tab-nav">
            <button class="tab-btn" :class="{ active: typeFilter === 'all' }" @click="typeFilter = 'all'; loadData()">
              全部异常
            </button>
            <button class="tab-btn" :class="{ active: typeFilter === 'absent' }" @click="typeFilter = 'absent'; loadData()">
              缺勤
            </button>
            <button class="tab-btn" :class="{ active: typeFilter === 'late' }" @click="typeFilter = 'late'; loadData()">
              迟到
            </button>
            <button class="tab-btn" :class="{ active: typeFilter === 'early_leave' }" @click="typeFilter = 'early_leave'; loadData()">
              早退
            </button>
          </div>
        </div>
        <div class="stat-badges">
          <span class="stat-badge alert" v-if="summary.absent > 0">
            <span class="stat-value">{{ summary.absent }}</span>
            <span class="stat-label">缺勤</span>
          </span>
          <span class="stat-badge warning" v-if="summary.late > 0">
            <span class="stat-value">{{ summary.late }}</span>
            <span class="stat-label">迟到</span>
          </span>
          <span class="stat-badge warning" v-if="summary.early > 0">
            <span class="stat-value">{{ summary.early }}</span>
            <span class="stat-label">早退</span>
          </span>
        </div>
      </div>

      <!-- 筛选栏 -->
      <div class="filters-bar">
        <div class="filter-item">
          <span class="filter-label">时间范围</span>
          <CustomSelect
            v-model="daysFilter"
            :options="daysOptions"
            class="filter-custom-select"
            @change="loadData"
          />
        </div>
        <button class="refresh-btn" @click="loadData" :disabled="loading">
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-name">员工</th>
              <th class="col-dept">部门</th>
              <th class="col-date">考勤日期</th>
              <th class="col-time">签到时间</th>
              <th class="col-time">签退时间</th>
              <th class="col-status">异常类型</th>
              <th class="col-reason">备注</th>
              <th class="col-action">操作</th>
            </tr>
          </thead>
          <tbody v-if="!loading && paginatedData.length">
            <tr v-for="item in paginatedData" :key="item.id" class="data-row">
              <td class="col-name">
                <div class="employee-cell">
                  <div class="avatar" :style="{ background: getAvatarColor(item.employee?.id || 0) }">
                    {{ item.employee?.name?.charAt(0) || '?' }}
                  </div>
                  <span class="name-text">{{ item.employee?.name || '-' }}</span>
                </div>
              </td>
              <td class="col-dept">{{ item.employee?.department?.name || '未分配' }}</td>
              <td class="col-date">
                <span class="date-link">{{ item.date }}</span>
                <span class="weekday">{{ getWeekday(item.date) }}</span>
              </td>
              <td class="col-time">{{ formatTime(item.check_in) }}</td>
              <td class="col-time">{{ formatTime(item.check_out) }}</td>
              <td class="col-status">
                <span class="status-text" :class="'status-' + item.attendance_type">
                  {{ getTypeText(item.attendance_type) }}
                </span>
              </td>
              <td class="col-reason">
                <template v-if="item.late_reason || item.early_leave_reason || item.notes">
                  <div v-if="item.late_reason" class="reason-line">迟到：{{ item.late_reason }}</div>
                  <div v-if="item.early_leave_reason" class="reason-line">早退：{{ item.early_leave_reason }}</div>
                  <div v-if="item.notes && !item.late_reason && !item.early_leave_reason" class="reason-line">{{ item.notes }}</div>
                </template>
                <template v-else>--</template>
              </td>
              <td class="col-action">
                <router-link :to="`/employees/${item.employee?.id}`" class="action-link">查看员工</router-link>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && !paginatedData.length" class="empty-state">
          <img src="/icons/success.svg" alt="success" class="empty-icon" />
          <p>太棒了！暂无{{ emptyStateText }}记录</p>
        </div>
      </div>

      <!-- 底部分页 -->
      <div class="table-footer">
        <span class="total-count">共{{ alerts.length }}条</span>
        <div class="pagination">
          <span class="page-size-label">每页</span>
          <CustomSelect
            v-model="pageSize"
            :options="pageSizeOptions"
            class="page-size-custom-select"
            @change="currentPage = 1"
          />
          <span class="page-size-label">条</span>
          <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(1)">«</button>
          <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">‹</button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">›</button>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(totalPages)">»</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'
import CustomSelect from '@/components/CustomSelect.vue'

const loading = ref(false)
const alerts = ref([])
const typeFilter = ref('all')
const daysFilter = ref('7')
const currentPage = ref(1)
const pageSize = ref(20)

// 下拉选项
const daysOptions = [
  { value: '7', label: '最近7天' },
  { value: '14', label: '最近14天' },
  { value: '30', label: '最近30天' },
  { value: '90', label: '最近90天' }
]

const pageSizeOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' }
]

const summary = computed(() => {
  const absent = alerts.value.filter(a => a.attendance_type === 'absent').length
  const late = alerts.value.filter(a => a.attendance_type === 'late').length
  const early = alerts.value.filter(a => a.attendance_type === 'early_leave').length
  return { absent, late, early }
})

const emptyStateText = computed(() => {
  const textMap = {
    'all': '考勤异常',
    'absent': '缺勤',
    'late': '迟到',
    'early_leave': '早退'
  }
  return textMap[typeFilter.value] || '考勤异常'
})

const totalPages = computed(() => {
  return Math.ceil(alerts.value.length / pageSize.value) || 1
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return alerts.value.slice(start, end)
})

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const avatarColors = [
  'linear-gradient(135deg, #38bdf8, #0ea5e9)',
  'linear-gradient(135deg, #a78bfa, #8b5cf6)',
  'linear-gradient(135deg, #34d399, #10b981)',
  'linear-gradient(135deg, #fbbf24, #f59e0b)',
  'linear-gradient(135deg, #f87171, #ef4444)',
  'linear-gradient(135deg, #60a5fa, #3b82f6)',
]

function getAvatarColor(id) {
  return avatarColors[id % avatarColors.length]
}

function getTypeText(type) {
  const map = {
    'absent': '缺勤',
    'late': '迟到',
    'early_leave': '早退',
    'normal': '正常',
  }
  return map[type] || type
}

function getWeekday(dateStr) {
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const d = new Date(dateStr)
  return days[d.getDay()]
}

function formatTime(timeStr) {
  if (!timeStr) return '--'
  // 格式: 2026-01-20T16:19:05 或 16:19:05
  if (timeStr.includes('T')) {
    return timeStr.split('T')[1].slice(0, 8)
  }
  return timeStr.slice(0, 8)
}

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  currentPage.value = 1
  try {
    const params = { days: daysFilter.value }
    if (typeFilter.value !== 'all') {
      params.type = typeFilter.value
    }
    const res = await api.get('/attendance/alerts/', { params })
    if (res.data.success !== false) {
      alerts.value = res.data.data || res.data.results || res.data || []
    }
  } catch (e) {
    console.error('Load alerts error:', e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.alerts-page {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.alerts-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}

/* 顶部标签栏 */
.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f8fafc;
}

.tab-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.tab-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ef4444;
  border-radius: 8px;
}

.tab-icon img {
  width: 20px;
  height: 20px;
  filter: brightness(0) invert(1);
}

.tab-nav {
  display: flex;
  gap: 0.25rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  font-size: 15px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  position: relative;
}

.tab-btn.active {
  color: #ef4444;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1rem;
  left: 0;
  right: 0;
  height: 2px;
  background: #ef4444;
}

.stat-badges {
  display: flex;
  gap: 12px;
}

.stat-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 14px;
  border-radius: 8px;
  min-width: 50px;
}

.stat-badge.alert {
  background: #fef2f2;
  color: #dc2626;
}

.stat-badge.warning {
  background: #fffbeb;
  color: #d97706;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
}

.stat-label {
  font-size: 11px;
  opacity: 0.8;
}

/* 筛选栏 */
.filters-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: white;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 14px;
  color: #374151;
  white-space: nowrap;
}

/* 自定义下拉框样式 */
.filter-custom-select {
  min-width: 110px;
}

.filter-custom-select :deep(.select-trigger) {
  padding: 0.45rem 0.75rem;
  padding-right: 2rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 6px;
  background: #fff;
  min-height: auto;
}

.filter-custom-select :deep(.select-trigger:hover) {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}

.filter-custom-select :deep(.select-trigger:focus),
.filter-custom-select :deep(.custom-select.open .select-trigger) {
  border-color: rgba(148, 163, 184, 0.6);
  box-shadow: none;
}

.filter-custom-select :deep(.select-value) {
  font-size: 14px;
  color: #1e293b;
}

.filter-custom-select :deep(.select-arrow) {
  color: #1e293b;
}

.filter-custom-select :deep(.select-dropdown) {
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 4px;
}

.filter-custom-select :deep(.select-option) {
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
}

.filter-custom-select :deep(.select-option:hover),
.filter-custom-select :deep(.select-option.highlighted) {
  background: #f1f5f9;
  color: #1e293b;
}

.filter-custom-select :deep(.select-option.selected) {
  background: #ef4444;
  color: #fff;
}

.filter-custom-select :deep(.select-option.selected::before) {
  display: none;
}

.refresh-btn {
  margin-left: auto;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 6px;
  font-size: 13px;
  color: #1e293b;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #f1f5f9;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 表格 */
.table-wrapper {
  position: relative;
  min-height: 300px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 500;
  color: #ef4444;
  border-bottom: 2px solid #ef4444;
  background: #f8fafc;
  white-space: nowrap;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
  vertical-align: middle;
}

.data-row:hover {
  background: #fafafa;
}

.col-name {
  min-width: 140px;
}

.col-dept {
  min-width: 100px;
}

.col-date {
  min-width: 150px;
}

.col-time {
  min-width: 100px;
}

.col-status {
  min-width: 80px;
}

.col-reason {
  min-width: 150px;
  color: #9ca3af;
}

.col-action {
  min-width: 80px;
}

.employee-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.name-text {
  font-weight: 500;
  color: #1e293b;
}

.date-link {
  color: #ef4444;
}

.weekday {
  margin-left: 8px;
  color: #9ca3af;
  font-size: 13px;
}

.status-text {
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
}

.status-text.status-absent {
  color: #dc2626;
  background: #fef2f2;
}

.status-text.status-late {
  color: #d97706;
  background: #fffbeb;
}

.status-text.status-early_leave {
  color: #d97706;
  background: #fffbeb;
}

.reason-line {
  line-height: 1.5;
  font-size: 13px;
}

.reason-line + .reason-line {
  margin-top: 4px;
}

.action-link {
  color: #ef4444;
  text-decoration: none;
  font-size: 13px;
}

.action-link:hover {
  text-decoration: underline;
}

/* 加载和空状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #f3f4f6;
  border-top-color: #ef4444;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #9ca3af;
}

.empty-icon {
  width: 60px;
  height: 60px;
  margin-bottom: 16px;
}

/* 底部分页 */
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-top: 1px solid #e5e7eb;
  font-size: 13px;
  color: #6b7280;
}

.total-count {
  font-size: 13px;
  color: #6b7280;
}

/* 分页 */
.pagination {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: nowrap;
}

.page-size-label {
  color: #6b7280;
  font-size: 13px;
  white-space: nowrap;
}

/* 分页下拉框样式 */
.page-size-custom-select {
  width: 70px;
}

.page-size-custom-select :deep(.select-trigger) {
  padding: 0.3rem 0.5rem;
  padding-right: 1.5rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 6px;
  background: #fff;
  min-height: auto;
}

.page-size-custom-select :deep(.select-trigger:hover) {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}

.page-size-custom-select :deep(.select-trigger:focus),
.page-size-custom-select :deep(.custom-select.open .select-trigger) {
  border-color: rgba(148, 163, 184, 0.6);
  box-shadow: none;
}

.page-size-custom-select :deep(.select-value) {
  font-size: 13px;
  color: #1e293b;
}

.page-size-custom-select :deep(.select-arrow) {
  color: #1e293b;
  width: 12px;
  height: 12px;
  right: 0.4rem;
}

.page-size-custom-select :deep(.select-dropdown) {
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 4px;
  min-width: 70px;
  top: auto;
  bottom: calc(100% + 4px);
}

.page-size-custom-select :deep(.select-option) {
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  text-align: center;
}

.page-size-custom-select :deep(.select-option:hover),
.page-size-custom-select :deep(.select-option.highlighted) {
  background: #f1f5f9;
  color: #1e293b;
}

.page-size-custom-select :deep(.select-option.selected) {
  background: #ef4444;
  color: #fff;
}

.page-size-custom-select :deep(.select-option.selected::before) {
  display: none;
}

.page-btn {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}

.page-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  padding: 0 0.5rem;
  font-size: 13px;
  color: #374151;
  white-space: nowrap;
}
</style>
