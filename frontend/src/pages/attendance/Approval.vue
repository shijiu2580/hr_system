<template>
  <div class="page-grid attendance-page">
    <div class="card attendance-card">
      <!-- 顶部标签栏 -->
      <div class="tab-header">
        <div class="tab-left">
          <div class="tab-icon">
            <img src="/icons/attendance.svg" alt="" />
          </div>
          <div class="tab-nav">
            <button class="tab-btn active">
              补签审批
            </button>
          </div>
        </div>
        <button class="btn-refresh" @click="load" :disabled="loading">
          <img src="/icons/refresh.svg" alt="" style="width: 16px; height: 16px;" />
          刷新
        </button>
      </div>

      <!-- 筛选栏 -->
      <div class="filters-bar">
        <div class="filter-item filter-date-group">
          <span class="filter-label">申请日期：</span>
          <input type="date" v-model="dateFrom" class="filter-date" />
          <span class="filter-sep">~</span>
          <input type="date" v-model="dateTo" class="filter-date" />
        </div>
        <div class="filter-item">
          <span class="filter-label">审批状态</span>
          <CustomSelect 
            v-model="statusFilter" 
            :options="approvalStatusOptions" 
            placeholder="全部"
            class="filter-custom-select"
          />
        </div>
        <button class="batch-approve-btn" :disabled="selected.length === 0 || batchApproving" @click="handleBatchApprove">
          <span v-if="batchApproving">处理中...</span>
          <span v-else>批量通过{{ selected.length > 0 ? `(${selected.length})` : '' }}</span>
        </button>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-check"><input type="checkbox" class="checkbox" v-model="selectAll" @change="toggleSelectAll" /></th>
              <th class="col-employee">员工</th>
              <th class="col-date">补签日期</th>
              <th class="col-time">补签时间</th>
              <th class="col-type">补签类型</th>
              <th class="col-reason">补签原因</th>
              <th class="col-status">审批状态</th>
              <th class="col-time">申请时间</th>
              <th class="col-action">操作</th>
            </tr>
          </thead>
          <tbody v-if="!loading && paginatedData.length">
            <tr v-for="item in paginatedData" :key="item.id" class="data-row" :class="{ 'row-selected': selected.includes(item.id) }">
              <td class="col-check"><input type="checkbox" class="checkbox" v-model="selected" :value="item.id" /></td>
              <td class="col-employee">{{ item.employee_name || item.employee_id }}</td>
              <td class="col-date">{{ item.date }}</td>
              <td class="col-time">{{ item.time }}</td>
              <td class="col-type">{{ item.type === 'check_in' ? '补签到' : '补签退' }}</td>
              <td class="col-reason">{{ item.reason || '--' }}</td>
              <td class="col-status">
                <span class="status-text" :class="'status-' + item.status">{{ getStatusLabel(item.status) }}</span>
              </td>
              <td class="col-time">{{ formatCreatedAt(item.created_at) }}</td>
              <td class="col-action">
                <template v-if="item.status === 'pending'">
                  <button class="btn-approve" @click="handleApprove(item.id, 'approve')" :disabled="approvingId === item.id">通过</button>
                  <button class="btn-reject" @click="handleApprove(item.id, 'reject')" :disabled="approvingId === item.id">拒绝</button>
                </template>
                <span v-else class="action-done">{{ item.status === 'approved' ? '已通过' : '已拒绝' }}</span>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && !paginatedData.length" class="empty-state">
          暂无补签申请记录
        </div>
      </div>

      <!-- 底部统计和分页 -->
      <div class="table-footer">
        <span class="total-count">共{{ filtered.length }}条</span>
        <div class="pagination">
          <span class="page-size-label">每页</span>
          <CustomSelect 
            v-model="pageSize" 
            :options="pageSizeSelectOptions" 
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

      <!-- 消息提示 -->
      <transition name="fade">
        <div v-if="message" class="message-toast" :class="message.type">
          {{ message.text }}
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../utils/api';
import { useAuthStore } from '../../stores/auth';
import CustomSelect from '../../components/CustomSelect.vue';

const auth = useAuthStore();

const loading = ref(false);
const items = ref([]);
const dateFrom = ref('');
const dateTo = ref('');
const statusFilter = ref('');
const selected = ref([]);
const selectAll = ref(false);
const message = ref(null);
const approvingId = ref(null);
const batchApproving = ref(false);

// 下拉选项
const approvalStatusOptions = [
  { value: '', label: '全部' },
  { value: 'pending', label: '待审批' },
  { value: 'approved', label: '已批准' },
  { value: 'rejected', label: '已拒绝' }
];

// 分页相关
const currentPage = ref(1);
const pageSize = ref(20);
const pageSizeOptions = [20, 50, 100];
const pageSizeSelectOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' }
];

// 初始化日期范围为本月
onMounted(() => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  dateFrom.value = `${year}-${String(month).padStart(2, '0')}-01`;
  const lastDay = new Date(year, month, 0).getDate();
  dateTo.value = `${year}-${String(month).padStart(2, '0')}-${lastDay}`;
  load();
});

const filtered = computed(() => {
  let result = items.value;
  
  if (dateFrom.value) {
    result = result.filter(i => i.date >= dateFrom.value);
  }
  if (dateTo.value) {
    result = result.filter(i => i.date <= dateTo.value);
  }
  if (statusFilter.value) {
    result = result.filter(i => i.status === statusFilter.value);
  }
  
  // 按申请时间倒序排列
  return result.sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''));
});

// 分页后的数据
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filtered.value.slice(start, end);
});

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filtered.value.length / pageSize.value) || 1;
});

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
}

function getStatusLabel(status) {
  const map = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝'
  };
  return map[status] || status;
}

// 格式化申请时间（去除秒后的数字）
function formatCreatedAt(dateTimeStr) {
  if (!dateTimeStr) return '-';
  // 截取到秒，格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM:SS
  const match = dateTimeStr.match(/^(\d{4}-\d{2}-\d{2})[T\s](\d{2}:\d{2}:\d{2})/);
  if (match) {
    return `${match[1]} ${match[2]}`;
  }
  return dateTimeStr.substring(0, 19).replace('T', ' ');
}

function toggleSelectAll() {
  if (selectAll.value) {
    selected.value = paginatedData.value.filter(i => i.status === 'pending').map(i => i.id);
  } else {
    selected.value = [];
  }
}

function showMessage(type, text) {
  message.value = { type, text };
  setTimeout(() => { message.value = null; }, 3000);
}

async function load() {
  loading.value = true;
  try {
    // 获取所有补签申请（管理员接口）
    const resp = await api.get('/attendance/supplement/pending/?status=all');
    if (resp.success) {
      items.value = Array.isArray(resp.data) ? resp.data : [];
    } else {
      console.error('加载补签申请失败:', resp.error?.message);
    }
  } catch (e) {
    console.error('加载补签申请出错:', e);
  }
  loading.value = false;
}

async function handleBatchApprove() {
  if (selected.value.length === 0) return;
  
  if (!window.confirm(`确定要批量通过 ${selected.value.length} 条补签申请吗？`)) {
    return;
  }
  
  batchApproving.value = true;
  let successCount = 0;
  let failCount = 0;
  
  for (const id of selected.value) {
    try {
      const resp = await api.post(`/attendance/supplement/${id}/approve/`, { action: 'approve', comments: '' });
      if (resp.success) {
        successCount++;
      } else {
        failCount++;
      }
    } catch (e) {
      failCount++;
    }
  }
  
  batchApproving.value = false;
  selected.value = [];
  
  if (failCount === 0) {
    showMessage('success', `成功通过 ${successCount} 条补签申请`);
  } else {
    showMessage('warning', `成功 ${successCount} 条，失败 ${failCount} 条`);
  }
  
  await load();
}

async function handleApprove(id, action) {
  const actionText = action === 'approve' ? '通过' : '拒绝';
  let comments = '';
  if (action === 'reject') {
    comments = window.prompt('请输入拒绝原因：', '');
    if (comments === null) return;
  }
  
  approvingId.value = id;
  try {
    const resp = await api.post(`/attendance/supplement/${id}/approve/`, { action, comments });
    if (resp.success) {
      showMessage('success', `已${actionText}补签申请`);
      await load();
    } else {
      showMessage('error', resp.error?.message || `${actionText}失败`);
    }
  } catch (e) {
    showMessage('error', `${actionText}失败，请重试`);
  }
  approvingId.value = null;
}
</script>

<style scoped>
.attendance-page {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.attendance-card {
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
  background: #2563eb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-icon img {
  width: 20px;
  height: 20px;
  filter: brightness(0) invert(1);
}

.tab-nav {
  display: flex;
  gap: 0.5rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #1e293b;
}

.tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
  font-weight: 500;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 筛选栏 */
.filters-bar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 1.25rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: nowrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.filter-date-group {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.filter-label {
  font-size: 14px;
  color: #374151;
  white-space: nowrap;
}

.filter-date {
  padding: 0.5rem 0.5rem;
  padding-right: 1.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
  background: white url("/icons/calendar.svg") no-repeat right 0.5rem center;
  background-size: 14px;
  outline: none;
  width: 130px;
  position: relative;
}

.filter-date::-webkit-calendar-picker-indicator {
  cursor: pointer;
  opacity: 0;
  position: absolute;
  right: 0;
  top: 0;
  width: 1.5rem;
  height: 100%;
  margin: 0;
  padding: 0;
}

.filter-date:focus {
  border-color: #2563eb;
  box-shadow: none;
}

.filter-sep {
  color: #9ca3af;
  margin: 0 0.25rem;
}

.filter-select {
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  outline: none;
  background: white url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23374151' d='M2.5 4.5l3.5 3.5 3.5-3.5'/%3E%3C/svg%3E") no-repeat right 0.5rem center;
  background-size: 12px;
  appearance: none;
  -webkit-appearance: none;
  min-width: 90px;
}

.filter-select:focus {
  border-color: #2563eb;
  box-shadow: none;
}

.filter-select:hover {
  border-color: #9ca3af;
}

/* 自定义下拉框样式 */
.filter-custom-select {
  min-width: 100px;
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
  background: #2563eb;
  color: #fff;
}

.filter-custom-select :deep(.select-option.selected::before) {
  display: none;
}

.batch-approve-btn {
  margin-left: auto;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 6px;
  font-size: 13px;
  color: #1e293b;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  white-space: nowrap;
}

.batch-approve-btn:hover:not(:disabled) {
  background: #f1f5f9;
}

.batch-approve-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #94a3b8;
  color: #94a3b8;
}

/* 表格 */
.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th,
.data-table td {
  padding: 0.75rem 0.5rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
  font-size: 12px;
  white-space: nowrap;
}

.data-row:hover {
  background: #f8fafc;
}

.data-row.row-selected {
  background: #eff6ff;
}

.data-row.row-selected:hover {
  background: #dbeafe;
}

.col-check {
  width: 40px;
  text-align: center;
}

.col-employee {
  min-width: 100px;
}

.col-date {
  min-width: 100px;
}

.col-time {
  min-width: 80px;
}

.col-type {
  min-width: 80px;
}

.col-reason {
  min-width: 150px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-status {
  min-width: 80px;
}

.col-action {
  min-width: 120px;
  white-space: nowrap;
}

/* 复选框样式 */
.checkbox {
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
  width: 15px !important;
  height: 15px !important;
  min-width: 15px !important;
  min-height: 15px !important;
  max-width: 15px !important;
  max-height: 15px !important;
  border: 1px solid #d1d5db !important;
  border-radius: 2px !important;
  background: #fff !important;
  cursor: pointer;
  position: relative;
  vertical-align: middle;
  transition: all 0.15s ease;
  flex-shrink: 0;
  margin: 0;
  padding: 0;
}

.checkbox:hover {
  border-color: #9ca3af !important;
}

.checkbox:checked {
  background: #9ca3af !important;
  border-color: #9ca3af !important;
}

.checkbox:checked::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 45%;
  width: 5px;
  height: 8px;
  border: solid #fff;
  border-width: 0 2px 2px 0;
  transform: translate(-50%, -50%) rotate(45deg);
}

.checkbox:indeterminate {
  background: #9ca3af !important;
  border-color: #9ca3af !important;
}

.checkbox:indeterminate::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  width: 8px;
  height: 2px;
  background: #fff;
  transform: translate(-50%, -50%);
}

/* 状态文字 */
.status-text {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: #fef3c7;
  color: #d97706;
}

.status-approved {
  background: #d1fae5;
  color: #059669;
}

.status-rejected {
  background: #fee2e2;
  color: #dc2626;
}

/* 操作按钮 */
.btn-approve {
  padding: 0.375rem 0.75rem;
  font-size: 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  background: #10b981;
  color: white;
  margin-right: 0.25rem;
}

.btn-approve:hover:not(:disabled) {
  background: #059669;
}

.btn-reject {
  padding: 0.375rem 0.75rem;
  font-size: 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  background: #ef4444;
  color: white;
}

.btn-reject:hover:not(:disabled) {
  background: #dc2626;
}

.btn-approve:disabled,
.btn-reject:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-done {
  color: #94a3b8;
  font-size: 12px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #94a3b8;
  font-size: 14px;
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
  color: #64748b;
}

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

.page-size-select {
  width: 60px;
  padding: 0.25rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
  color: #374151;
  background: white;
  cursor: pointer;
  outline: none;
}

.page-size-select:focus {
  border-color: #2563eb;
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
  background: #2563eb;
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

/* 消息提示 */
.message-toast {
  position: fixed;
  top: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.625rem 1.25rem;
  border-radius: 6px;
  font-size: 14px;
  z-index: 1001;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.message-toast.success {
  background: #059669;
  color: white;
}

.message-toast.error {
  background: #dc2626;
  color: white;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}
</style>
