<template>
  <div class="page-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <img src="/icons/salaries.svg" alt="" />
        </div>
        <span class="header-title">报销审批</span>
      </div>
      <div class="header-right">
        <button class="btn-back" @click="$router.push('/salaries/travel-expense')">返回报销</button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filters-bar">
      <CustomSelect
        v-model="filterType"
        :options="[
          { value: '', label: '报销类型' },
          { value: 'travel', label: '差旅费' },
          { value: 'transport', label: '交通费' },
          { value: 'accommodation', label: '住宿费' },
          { value: 'meal', label: '餐饮费' },
          { value: 'other', label: '其他' }
        ]"
        placeholder="报销类型"
        class="filter-dropdown"
      />
      <CustomSelect
        v-model="filterStatus"
        :options="[
          { value: '', label: '审批状态' },
          { value: 'pending', label: '待审批' },
          { value: 'approved', label: '已批准' },
          { value: 'rejected', label: '已拒绝' },
          { value: 'paid', label: '已报销' }
        ]"
        placeholder="审批状态"
        class="filter-dropdown"
      />
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-employee">申请人</th>
            <th class="col-type">报销类型</th>
            <th class="col-amount">报销金额</th>
            <th class="col-trip">关联出差</th>
            <th class="col-date sortable" @click="toggleSort('created_at')">
              <span class="th-text">申请时间</span>
              <span class="sort-icon" :class="{ active: sortField === 'created_at' }">
                {{ sortField === 'created_at' ? (sortOrder === 'asc' ? '↑' : '↓') : '⇅' }}
              </span>
            </th>
            <th class="col-reason">报销事由</th>
            <th class="col-status">状态</th>
            <th class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody v-if="!loading && paged.length">
          <tr v-for="item in paged" :key="item.id" class="data-row">
            <td class="col-employee">{{ item.employee?.name || '--' }}</td>
            <td class="col-type">
              <span class="type-text">{{ getTypeLabel(item.expense_type) }}</span>
            </td>
            <td class="col-amount">
              <span class="amount-value">¥{{ formatMoney(item.amount) }}</span>
            </td>
            <td class="col-trip">{{ item.business_trip?.destination || '--' }}</td>
            <td class="col-date">{{ formatDateTime(item.created_at) }}</td>
            <td class="col-reason">
              <span class="reason-ellipsis" :title="item.description">{{ item.description || '--' }}</span>
            </td>
            <td class="col-status">
              <span class="status-badge" :class="'status-' + item.status">{{ getStatusLabel(item.status) }}</span>
            </td>
            <td class="col-actions">
              <template v-if="item.status === 'pending'">
                <a href="javascript:;" class="action-link approve" @click="handleApprove(item)" :class="{ disabled: processing === item.id }">批准</a>
                <a href="javascript:;" class="action-link reject" @click="handleReject(item)" :class="{ disabled: processing === item.id }">拒绝</a>
              </template>
              <template v-else-if="item.status === 'approved'">
                <a href="javascript:;" class="action-link pay" @click="handlePay(item)" :class="{ disabled: processing === item.id }">发放</a>
              </template>
              <a href="javascript:;" class="action-link" @click="showDetail(item)">详情</a>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="progress-bar">
          <div class="progress-fill"></div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && !paged.length" class="empty-state">
        暂无报销申请
      </div>
    </div>

    <!-- 底部 -->
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

    <!-- 提示消息 -->
    <div v-if="message" class="message" :class="'message-' + message.type">
      {{ message.text }}
      <button class="close-btn" @click="message = null">×</button>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="detailItem" class="modal-overlay" @click.self="detailItem = null">
      <div class="modal-content">
        <div class="modal-header">
          <h3>报销详情</h3>
          <button class="modal-close" @click="detailItem = null">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <span class="detail-label">申请人</span>
            <span class="detail-value">{{ detailItem.employee?.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">部门</span>
            <span class="detail-value">{{ detailItem.employee?.department?.name || '--' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">报销类型</span>
            <span class="detail-value">{{ getTypeLabel(detailItem.expense_type) }}</span>
          </div>
          <div class="detail-row highlight">
            <span class="detail-label">报销金额</span>
            <span class="detail-value amount">¥{{ formatMoney(detailItem.amount) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">关联出差</span>
            <span class="detail-value">{{ detailItem.business_trip?.destination || '无' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">报销事由</span>
            <span class="detail-value">{{ detailItem.description }}</span>
          </div>
          <div class="detail-row" v-if="detailItem.invoice">
            <span class="detail-label">发票附件</span>
            <span class="detail-value">
              <a :href="detailItem.invoice" target="_blank" class="invoice-link">📄 点击查看/下载发票</a>
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">状态</span>
            <span class="detail-value">
              <span class="status-badge" :class="'status-' + detailItem.status">{{ getStatusLabel(detailItem.status) }}</span>
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">申请时间</span>
            <span class="detail-value">{{ formatDateTime(detailItem.created_at) }}</span>
          </div>
          <div class="detail-row" v-if="detailItem.approved_by">
            <span class="detail-label">审批人</span>
            <span class="detail-value">{{ detailItem.approved_by?.username }}</span>
          </div>
          <div class="detail-row" v-if="detailItem.approved_at">
            <span class="detail-label">审批时间</span>
            <span class="detail-value">{{ formatDateTime(detailItem.approved_at) }}</span>
          </div>
          <div class="detail-row" v-if="detailItem.comments">
            <span class="detail-label">审批意见</span>
            <span class="detail-value">{{ detailItem.comments }}</span>
          </div>
          <div class="detail-row" v-if="detailItem.remarks">
            <span class="detail-label">备注</span>
            <span class="detail-value">{{ detailItem.remarks }}</span>
          </div>
          
          <!-- 审批操作区 -->
          <div v-if="detailItem.status === 'pending'" class="approval-section">
            <div class="form-row">
              <label class="form-label">审批意见</label>
              <textarea v-model="approvalComment" class="form-textarea" rows="2" placeholder="可填写审批意见（可选）"></textarea>
            </div>
            <div class="approval-actions">
              <button class="btn-approve" @click="approveFromModal" :disabled="processing">批准</button>
              <button class="btn-reject" @click="rejectFromModal" :disabled="processing">拒绝</button>
            </div>
          </div>
          <div v-else-if="detailItem.status === 'approved'" class="approval-section">
            <div class="approval-actions">
              <button class="btn-pay" @click="payFromModal" :disabled="processing">确认发放报销</button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="detailItem = null">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import CustomSelect from '../../components/CustomSelect.vue';
import api from '../../utils/api';

// 数据状态
const loading = ref(false);
const records = ref([]);
const message = ref(null);
const detailItem = ref(null);
const processing = ref(null);
const approvalComment = ref('');

// 筛选
const filterType = ref('');
const filterStatus = ref('');

// 排序
const sortField = ref('created_at');
const sortOrder = ref('desc');

// 分页
const currentPage = ref(1);
const pageSize = ref(20);
const pageSizeSelectOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' }
];

// 类型标签映射
const typeLabels = {
  travel: '差旅费',
  transport: '交通费',
  accommodation: '住宿费',
  meal: '餐饮费',
  other: '其他'
};

// 状态标签映射
const statusLabels = {
  pending: '待审批',
  approved: '已批准',
  rejected: '已拒绝',
  paid: '已报销'
};

function getTypeLabel(type) {
  return typeLabels[type] || type;
}

function getStatusLabel(status) {
  return statusLabels[status] || status;
}

// 筛选后的数据
const filtered = computed(() => {
  let result = [...records.value];
  
  if (filterType.value) {
    result = result.filter(r => r.expense_type === filterType.value);
  }
  
  if (filterStatus.value) {
    result = result.filter(r => r.status === filterStatus.value);
  }
  
  // 排序
  if (sortField.value) {
    result.sort((a, b) => {
      let aVal = a[sortField.value];
      let bVal = b[sortField.value];
      if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1;
      return 0;
    });
  }
  
  return result;
});

// 总页数
const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filtered.value.length / pageSize.value));
});

// 分页后的数据
const paged = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filtered.value.slice(start, start + pageSize.value);
});

// 排序切换
function toggleSort(field) {
  if (sortField.value === field) {
    if (sortOrder.value === 'desc') {
      sortOrder.value = 'asc';
    } else if (sortOrder.value === 'asc') {
      sortField.value = '';
      sortOrder.value = 'desc';
    }
  } else {
    sortField.value = field;
    sortOrder.value = 'desc';
  }
}

// 翻页
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
}

// 格式化金额
function formatMoney(val) {
  if (val == null) return '0.00';
  return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// 格式化日期时间
function formatDateTime(dt) {
  if (!dt) return '';
  const d = new Date(dt);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const h = String(d.getHours()).padStart(2, '0');
  const min = String(d.getMinutes()).padStart(2, '0');
  const s = String(d.getSeconds()).padStart(2, '0');
  return `${y}-${m}-${day} ${h}:${min}:${s}`;
}

// 显示详情
function showDetail(item) {
  detailItem.value = item;
  approvalComment.value = '';
}

// 审批操作
async function handleApprove(item) {
  if (processing.value) return;
  processing.value = item.id;
  
  const resp = await api.post(`/travel-expenses/${item.id}/approve/`, {
    action: 'approve',
    comments: ''
  });
  
  if (resp.success) {
    showMessage('success', '已批准');
    await load();
  } else {
    showMessage('error', resp.error?.message || '操作失败');
  }
  processing.value = null;
}

async function handleReject(item) {
  if (processing.value) return;
  processing.value = item.id;
  
  const resp = await api.post(`/travel-expenses/${item.id}/approve/`, {
    action: 'reject',
    comments: ''
  });
  
  if (resp.success) {
    showMessage('success', '已拒绝');
    await load();
  } else {
    showMessage('error', resp.error?.message || '操作失败');
  }
  processing.value = null;
}

async function handlePay(item) {
  if (processing.value) return;
  processing.value = item.id;
  
  const resp = await api.post(`/travel-expenses/${item.id}/pay/`);
  
  if (resp.success) {
    showMessage('success', '已发放');
    await load();
  } else {
    showMessage('error', resp.error?.message || '操作失败');
  }
  processing.value = null;
}

async function approveFromModal() {
  if (!detailItem.value || processing.value) return;
  processing.value = detailItem.value.id;
  
  const resp = await api.post(`/travel-expenses/${detailItem.value.id}/approve/`, {
    action: 'approve',
    comments: approvalComment.value
  });
  
  if (resp.success) {
    showMessage('success', '已批准');
    detailItem.value = null;
    await load();
  } else {
    showMessage('error', resp.error?.message || '操作失败');
  }
  processing.value = null;
}

async function rejectFromModal() {
  if (!detailItem.value || processing.value) return;
  processing.value = detailItem.value.id;
  
  const resp = await api.post(`/travel-expenses/${detailItem.value.id}/approve/`, {
    action: 'reject',
    comments: approvalComment.value
  });
  
  if (resp.success) {
    showMessage('success', '已拒绝');
    detailItem.value = null;
    await load();
  } else {
    showMessage('error', resp.error?.message || '操作失败');
  }
  processing.value = null;
}

async function payFromModal() {
  if (!detailItem.value || processing.value) return;
  processing.value = detailItem.value.id;
  
  const resp = await api.post(`/travel-expenses/${detailItem.value.id}/pay/`);
  
  if (resp.success) {
    showMessage('success', '已发放');
    detailItem.value = null;
    await load();
  } else {
    showMessage('error', resp.error?.message || '操作失败');
  }
  processing.value = null;
}

// 显示消息
function showMessage(type, text) {
  message.value = { type, text };
  setTimeout(() => {
    if (message.value?.text === text) {
      message.value = null;
    }
  }, 3000);
}

// 加载数据
async function load() {
  loading.value = true;
  try {
    // 获取所有报销申请（管理员可看到所有）
    const resp = await api.get('/travel-expenses/', { params: { page_size: 9999 } });
    records.value = resp.data.results || resp.data || [];
  } catch (err) {
    showMessage('error', '加载失败');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  load();
});
</script>

<style scoped>
.page-container {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

/* 顶部标题栏 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon img {
  width: 24px;
  height: 24px;
}

.header-title {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
}

.header-right {
  display: flex;
  gap: 10px;
}

.btn-back {
  padding: 0.5rem 1.25rem;
  background: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

/* 筛选栏 */
.filters-bar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.filter-dropdown {
  width: 120px;
  flex-shrink: 0;
}

.filter-dropdown :deep(.select-trigger) {
  padding: 0.5rem 0.75rem;
  padding-right: 2rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 4px;
  background: #fff;
  min-height: auto;
  font-size: 14px;
  color: #374151;
}

.filter-dropdown :deep(.select-trigger:hover) {
  background: #f8fafc;
}

.filter-dropdown :deep(.custom-select.open .select-trigger) {
  border-color: rgba(148, 163, 184, 0.6);
}

.filter-dropdown :deep(.select-value) {
  font-size: 14px;
  color: #374151;
}

.filter-dropdown :deep(.select-arrow) {
  color: #6b7280;
}

.filter-dropdown :deep(.select-dropdown) {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  padding: 4px;
}

.filter-dropdown :deep(.select-option) {
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 14px;
  color: #374151;
}

.filter-dropdown :deep(.select-option:hover),
.filter-dropdown :deep(.select-option.highlighted) {
  background: #f3f4f6;
}

.filter-dropdown :deep(.select-option.selected) {
  background: #2563eb;
  color: #fff;
}

/* 表格容器 */
.table-container {
  position: relative;
  min-height: 200px;
  flex: 1;
}

/* 表格 */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  padding: 0.875rem 1rem;
  text-align: left;
  font-weight: 500;
  color: #2563eb;
  border-bottom: 2px solid #2563eb;
  background: #fff;
  white-space: nowrap;
}

.data-table th.sortable {
  cursor: pointer;
}

.data-table th .th-text {
  margin-right: 0.25rem;
}

.data-table th .sort-icon {
  font-size: 12px;
  color: #9ca3af;
  transition: color 0.2s;
}

.data-table th .sort-icon.active {
  color: #2563eb;
}

.data-table th.sortable:hover .sort-icon {
  color: #6b7280;
}

.data-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
  vertical-align: middle;
}

.data-row:hover {
  background: #fafafa;
}

/* 列宽 */
.col-employee { width: 100px; }
.col-type { width: 80px; }
.col-amount { width: 100px; }
.col-trip { width: 120px; }
.col-date { width: 150px; }
.col-reason { max-width: 180px; }
.col-status { width: 80px; }
.col-actions { width: 140px; }

.type-text {
  color: #374151;
}

.amount-value {
  font-weight: 600;
  color: #059669;
}

.reason-ellipsis {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

.status-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.status-pending {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.status-approved {
  background: #dbeafe;
  color: #2563eb;
}

.status-badge.status-rejected {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.status-paid {
  background: #d1fae5;
  color: #059669;
}

.action-link {
  color: #2563eb;
  text-decoration: none;
  font-size: 14px;
  margin-right: 0.75rem;
}

.action-link:last-child {
  margin-right: 0;
}

.action-link:hover {
  text-decoration: underline;
}

.action-link.approve {
  color: #059669;
}

.action-link.reject {
  color: #dc2626;
}

.action-link.pay {
  color: #7c3aed;
}

.action-link.disabled {
  opacity: 0.5;
  pointer-events: none;
}

/* 加载状态 */
.loading-state {
  padding: 3rem;
}

.progress-bar {
  height: 3px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
  width: 200px;
  margin: 0 auto;
}

.progress-fill {
  height: 100%;
  background: #2563eb;
  animation: progress 1.5s ease-in-out infinite;
}

@keyframes progress {
  0% { width: 0; margin-left: 0; }
  50% { width: 60%; margin-left: 20%; }
  100% { width: 0; margin-left: 100%; }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-size: 14px;
}

/* 底部 */
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.total-count {
  font-size: 13px;
  color: #6b7280;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-size-label {
  font-size: 13px;
  color: #6b7280;
}

.page-size-custom-select {
  width: 70px;
}

.page-size-custom-select :deep(.select-trigger) {
  padding: 0.25rem 0.5rem;
  padding-right: 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #fff;
  min-height: auto;
  font-size: 13px;
}

.page-size-custom-select :deep(.select-value) {
  font-size: 13px;
}

.page-size-custom-select :deep(.select-dropdown) {
  min-width: 70px;
}

.page-size-custom-select :deep(.select-option) {
  padding: 0.375rem 0.5rem;
  font-size: 13px;
}

.page-size-custom-select :deep(.select-option.selected) {
  background: #2563eb;
  color: #fff;
}

.page-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d1d5db;
  background: #fff;
  border-radius: 4px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #374151;
  min-width: 60px;
  text-align: center;
}

/* 消息提示 */
.message {
  position: fixed;
  top: 80px;
  right: 24px;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.message-success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #6ee7b7;
}

.message-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.6;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  opacity: 1;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-close:hover {
  color: #1f2937;
}

.modal-body {
  padding: 1.25rem;
}

/* 详情行 */
.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.625rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row.highlight {
  background: #f0fdf4;
  margin: 0.5rem -1.25rem;
  padding: 0.75rem 1.25rem;
  border-bottom: none;
}

.detail-label {
  font-size: 14px;
  color: #6b7280;
  flex-shrink: 0;
}

.detail-value {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
  text-align: right;
  word-break: break-word;
}

.detail-value.amount {
  font-size: 18px;
  color: #059669;
  font-weight: 600;
}

.invoice-link {
  color: #2563eb;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.invoice-link:hover {
  text-decoration: underline;
}

/* 审批区域 */
.approval-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.form-row {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-textarea {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #1f2937;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: none;
}

.approval-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-approve {
  padding: 0.5rem 1.25rem;
  background: #059669;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-approve:hover {
  background: #047857;
}

.btn-approve:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-reject {
  padding: 0.5rem 1.25rem;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-reject:hover {
  background: #b91c1c;
}

.btn-reject:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-pay {
  padding: 0.5rem 1.25rem;
  background: #7c3aed;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-pay:hover {
  background: #6d28d9;
}

.btn-pay:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e5e7eb;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #e5e7eb;
}
</style>
