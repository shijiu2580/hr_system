<template>
  <div class="page-grid approval-page">
    <div class="card approval-card">
      <h2 style="margin: 0 0 1.25rem 0; font-size: 18px; font-weight: 600; color: #1e293b;">审批流程</h2>
      <!-- 筛选栏 -->
      <div class="filters-bar">
        <CustomSelect
          v-model="filterDocType"
          :options="[
            { value: '', label: '单据类型' },
            { value: 'leave', label: '请假' },
            { value: 'business_trip', label: '出差' }
          ]"
          placeholder="单据类型"
          class="filter-dropdown"
        />
        <CustomSelect
          v-if="filterDocType !== 'business_trip'"
          v-model="filterType"
          :options="[
            { value: '', label: '休假项目' },
            { value: 'sick', label: '病假' },
            { value: 'personal', label: '事假' },
            { value: 'annual', label: '年假' },
            { value: 'maternity', label: '产假' }
          ]"
          placeholder="休假项目"
          class="filter-dropdown"
        />
        <CustomSelect
          v-if="filterDocType === 'business_trip'"
          v-model="filterTripType"
          :options="[
            { value: '', label: '出差类型' },
            { value: 'domestic', label: '国内出差' },
            { value: 'overseas', label: '海外出差' }
          ]"
          placeholder="出差类型"
          class="filter-dropdown"
        />
        <CustomSelect
          v-model="filterStatus"
          :options="[
            { value: '', label: '审批状态' },
            { value: 'pending', label: '待审批' },
            { value: 'approved', label: '已批准' },
            { value: 'rejected', label: '已拒绝' }
          ]"
          placeholder="审批状态"
          class="filter-dropdown"
        />
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-employee">申请人</th>
              <th class="col-type">项目类型</th>
              <th class="col-time sortable" @click="toggleSort('start_date')">
                开始时间
                <span class="sort-icon" :class="{ active: sortField === 'start_date', desc: sortField === 'start_date' && sortOrder === 'desc' }">
                  <img src="/icons/up_down.svg" />
                </span>
              </th>
              <th class="col-time sortable" @click="toggleSort('end_date')">
                结束时间
                <span class="sort-icon" :class="{ active: sortField === 'end_date', desc: sortField === 'end_date' && sortOrder === 'desc' }">
                  <img src="/icons/up_down.svg" />
                </span>
              </th>
              <th class="col-days">时长</th>
              <th class="col-doc">单据类型</th>
              <th class="col-reason">事由</th>
              <th class="col-status">状态</th>
              <th class="col-actions">操作</th>
            </tr>
          </thead>
          <tbody v-if="!loading && paged.length">
            <tr v-for="item in paged" :key="item._key" class="data-row">
              <td class="col-employee">
                <span class="employee-name">{{ item.employee?.name || '-' }}</span>
              </td>
              <td class="col-type">
                <a href="javascript:;" class="type-link">{{ getTypeLabel(item) }}</a>
              </td>
              <td class="col-time">{{ formatDateTime(item.start_date) }}</td>
              <td class="col-time">{{ formatDateTime(item.end_date) }}</td>
              <td class="col-days">{{ item.days }}天</td>
              <td class="col-doc">
                <span class="doc-badge" :class="item._docType">{{ item._docType === 'leave' ? '请假' : '出差' }}</span>
              </td>
              <td class="col-reason">
                <span class="reason-text" :title="item.reason || item.destination">
                  {{ item._docType === 'business_trip' ? item.destination : item.reason || '-' }}
                </span>
              </td>
              <td class="col-status">
                <span class="status-badge" :class="'status-' + item.status">{{ getStatusLabel(item.status) }}</span>
              </td>
              <td class="col-actions">
                <div class="action-links">
                  <a
                    v-if="item.status === 'pending'"
                    href="javascript:;"
                    class="action-link approve"
                    @click="handleApprove(item)"
                    :class="{ disabled: processing === item._key }"
                  >批准</a>
                  <a
                    v-if="item.status === 'pending'"
                    href="javascript:;"
                    class="action-link reject"
                    @click="handleReject(item)"
                    :class="{ disabled: processing === item._key }"
                  >拒绝</a>
                  <a href="javascript:;" class="action-link" @click="showDetail(item)">详情</a>
                </div>
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
        <div v-if="!loading && !paged.length" class="empty-state">
          暂无数据
        </div>

        <!-- 进度条（装饰） -->
        <div class="progress-bar" v-if="loading">
          <div class="progress-fill"></div>
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
            :dropUp="true"
          />
          <span class="page-size-label">条</span>
          <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(1)">«</button>
          <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">‹</button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">›</button>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(totalPages)">»</button>
        </div>
      </div>

      <!-- 详情弹窗 -->
      <div v-if="detailItem" class="modal-overlay" @click.self="detailItem = null">
        <div class="modal-content">
          <div class="modal-header">
            <h3>{{ detailItem._docType === 'leave' ? '请假详情' : '出差详情' }}</h3>
            <button class="modal-close" @click="detailItem = null">×</button>
          </div>
          <div class="modal-body">
            <div class="detail-row">
              <span class="detail-label">申请人</span>
              <span class="detail-value">{{ detailItem.employee?.name }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">部门</span>
              <span class="detail-value">{{ detailItem.employee?.department?.name || '-' }}</span>
            </div>
            <div class="detail-row" v-if="detailItem._docType === 'leave'">
              <span class="detail-label">休假类型</span>
              <span class="detail-value">{{ getLeaveTypeLabel(detailItem.leave_type) }}</span>
            </div>
            <div class="detail-row" v-if="detailItem._docType === 'business_trip'">
              <span class="detail-label">出差地点</span>
              <span class="detail-value">{{ detailItem.destination }}</span>
            </div>
            <div class="detail-row" v-if="detailItem._docType === 'business_trip'">
              <span class="detail-label">出差类型</span>
              <span class="detail-value">{{ getTripTypeLabel(detailItem.trip_type) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">开始时间</span>
              <span class="detail-value">{{ formatDateTime(detailItem.start_date) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">结束时间</span>
              <span class="detail-value">{{ formatDateTime(detailItem.end_date) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">时长</span>
              <span class="detail-value">{{ detailItem.days }}天</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">事由</span>
              <span class="detail-value">{{ detailItem.reason || '-' }}</span>
            </div>
            <div class="detail-row" v-if="detailItem._docType === 'business_trip' && detailItem.remarks">
              <span class="detail-label">备注</span>
              <span class="detail-value">{{ detailItem.remarks }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">状态</span>
              <span class="detail-value status-text" :class="'status-' + detailItem.status">
                {{ getStatusLabel(detailItem.status) }}
              </span>
            </div>
            <div v-if="detailItem.comments" class="detail-row">
              <span class="detail-label">审批备注</span>
              <span class="detail-value">{{ detailItem.comments }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">申请时间</span>
              <span class="detail-value">{{ formatCreatedAt(detailItem.created_at) }}</span>
            </div>
          </div>
          <div class="modal-footer" v-if="detailItem.status === 'pending'">
            <input
              type="text"
              v-model="modalComment"
              placeholder="审批备注（可选）"
              class="modal-input"
            />
            <div class="modal-actions">
              <button class="btn-modal approve" @click="approveFromModal" :disabled="processing">批准</button>
              <button class="btn-modal reject" @click="rejectFromModal" :disabled="processing">拒绝</button>
            </div>
          </div>
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
import CustomSelect from '../../components/CustomSelect.vue';

const loading = ref(false);
const items = ref([]);
const filterType = ref('');
const filterTripType = ref('');
const filterDocType = ref('');
const filterStatus = ref('');
const sortField = ref('');
const sortOrder = ref('asc');
const processing = ref(null);
const message = ref(null);
const detailItem = ref(null);
const modalComment = ref('');
const currentPage = ref(1);
const pageSize = ref(20);
const pageSizeSelectOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' }
];

const filtered = computed(() => {
  let result = items.value;

  // 按单据类型筛选
  if (filterDocType.value) {
    result = result.filter(i => i._docType === filterDocType.value);
  }

  // 按请假类型筛选（仅请假）
  if (filterType.value && filterDocType.value !== 'business_trip') {
    result = result.filter(i => i._docType === 'leave' && i.leave_type === filterType.value);
  }

  // 按出差类型筛选（仅出差）
  if (filterTripType.value && filterDocType.value === 'business_trip') {
    result = result.filter(i => i._docType === 'business_trip' && i.trip_type === filterTripType.value);
  }

  // 按状态筛选
  if (filterStatus.value) {
    result = result.filter(i => i.status === filterStatus.value);
  }

  // 排序：先按状态排序（待审批在前），再按其他字段排序
  result = [...result].sort((a, b) => {
    // 待审批状态优先
    const statusOrder = { pending: 0 };
    const aStatusOrder = statusOrder[a.status] ?? 1;
    const bStatusOrder = statusOrder[b.status] ?? 1;

    if (aStatusOrder !== bStatusOrder) {
      return aStatusOrder - bStatusOrder;
    }

    // 如果状态相同，按其他字段排序
    if (sortField.value) {
      const aVal = a[sortField.value] || '';
      const bVal = b[sortField.value] || '';
      return sortOrder.value === 'asc'
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal);
    }

    // 默认按创建时间倒序
    return (b.created_at || '').localeCompare(a.created_at || '');
  });

  return result;
});

const totalPages = computed(() => Math.ceil(filtered.value.length / pageSize.value) || 1);

const paged = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filtered.value.slice(start, start + pageSize.value);
});

// 分页方法
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
}

function getLeaveTypeLabel(type) {
  const map = { sick: '病假', personal: '事假', annual: '年假', maternity: '产假', paternity: '陪产假', other: '其他' };
  return map[type] || type;
}

function getTripTypeLabel(type) {
  const map = { domestic: '国内出差', overseas: '海外出差' };
  return map[type] || type;
}

function getTypeLabel(item) {
  if (item._docType === 'leave') {
    return getLeaveTypeLabel(item.leave_type);
  } else {
    return item.destination || '出差';
  }
}

function getStatusLabel(status) {
  const map = { pending: '待审批', approved: '已批准', rejected: '已拒绝', cancelled: '已取消' };
  return map[status] || status;
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-';
  return `${dateStr} 09:00`;
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

function toggleSort(field) {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortField.value = field;
    sortOrder.value = 'asc';
  }
}

function showDetail(item) {
  detailItem.value = item;
  modalComment.value = '';
}

function showMessage(type, text) {
  message.value = { type, text };
  setTimeout(() => { message.value = null; }, 3000);
}

async function load() {
  loading.value = true;

  // 并行加载请假和出差数据
  const [leavesResp, tripsResp] = await Promise.all([
    api.get('/leaves/', { params: { page_size: 9999 } }),
    api.get('/business-trips/', { params: { page_size: 9999 } })
  ]);

  const allItems = [];

  // 处理请假数据
  if (leavesResp.success) {
    const raw = leavesResp.data;
    const leaves = Array.isArray(raw) ? raw : (raw?.results || []);
    leaves.forEach(item => {
      allItems.push({
        ...item,
        _docType: 'leave',
        _key: `leave_${item.id}`
      });
    });
  }

  // 处理出差数据
  if (tripsResp.success) {
    const raw = tripsResp.data;
    const trips = Array.isArray(raw) ? raw : (raw?.results || []);
    trips.forEach(item => {
      allItems.push({
        ...item,
        _docType: 'business_trip',
        _key: `trip_${item.id}`
      });
    });
  }

  // 按创建时间排序（最新的在前）
  allItems.sort((a, b) => {
    const dateA = a.created_at || '';
    const dateB = b.created_at || '';
    return dateB.localeCompare(dateA);
  });

  items.value = allItems;
  loading.value = false;
}

async function doApprove(item, comments = '') {
  const apiPath = item._docType === 'leave'
    ? `/leaves/${item.id}/approve/`
    : `/business-trips/${item.id}/approve/`;

  const resp = await api.post(apiPath, {
    action: 'approve',
    comments: comments
  });

  return resp;
}

async function doReject(item, comments = '') {
  const apiPath = item._docType === 'leave'
    ? `/leaves/${item.id}/approve/`
    : `/business-trips/${item.id}/approve/`;

  const resp = await api.post(apiPath, {
    action: 'reject',
    comments: comments
  });

  return resp;
}

async function handleApprove(item) {
  if (processing.value) return;
  processing.value = item._key;

  const resp = await doApprove(item);
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
  processing.value = item._key;

  const resp = await doReject(item);
  if (resp.success) {
    showMessage('success', '已拒绝');
    await load();
  } else {
    showMessage('error', resp.error?.message || '操作失败');
  }
  processing.value = null;
}

async function approveFromModal() {
  if (!detailItem.value || processing.value) return;
  processing.value = detailItem.value._key;

  const resp = await doApprove(detailItem.value, modalComment.value);
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
  processing.value = detailItem.value._key;

  const resp = await doReject(detailItem.value, modalComment.value);
  if (resp.success) {
    showMessage('success', '已拒绝');
    detailItem.value = null;
    await load();
  } else {
    showMessage('error', resp.error?.message || '操作失败');
  }
  processing.value = null;
}

onMounted(() => {
  load();
});
</script>

<style scoped>
.approval-page {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.approval-card {
  background: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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

/* 表格 */
.table-wrapper {
  position: relative;
  min-height: 200px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  /* 使用全局样式 */
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background: #eff6ff;
}

.sort-icon {
  display: inline-flex;
  width: 12px;
  height: 12px;
  margin-left: 0.25rem;
  transition: transform 0.2s;
}

.sort-icon img {
  width: 100%;
  height: 100%;
}

.sort-icon.desc {
  transform: rotate(180deg);
}

.data-table td {
  padding: 0.625rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
  vertical-align: middle;
}

.data-row:hover {
  background: #fafafa;
}

.col-employee { width: 100px; }
.col-type { width: 120px; }
.col-time { width: 150px; }
.col-days { width: 70px; }
.col-doc { width: 80px; }
.col-reason { max-width: 150px; }
.col-status { width: 80px; }
.col-actions { width: 140px; }

.employee-name {
  font-weight: 500;
  color: #1f2937;
}

.type-link {
  color: #2563eb;
  text-decoration: none;
}

.type-link:hover {
  text-decoration: underline;
}

.doc-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.doc-badge.leave {
  background: #fef3c7;
  color: #d97706;
}

.doc-badge.business_trip {
  background: #dbeafe;
  color: #2563eb;
}

.reason-text {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 150px;
}

.status-badge {
  font-size: 13px;
  font-weight: 500;
}

.status-badge.status-pending {
  color: #d97706;
}

.status-badge.status-approved {
  color: #059669;
}

.status-badge.status-rejected {
  color: #dc2626;
}

.status-badge.status-cancelled {
  color: #6b7280;
}

.action-links {
  display: flex;
  gap: 0.75rem;
}

.action-link {
  color: #2563eb;
  text-decoration: none;
  font-size: 14px;
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

.action-link.disabled {
  color: #9ca3af;
  pointer-events: none;
}

/* 加载状态 */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
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
  color: #9ca3af;
  font-size: 14px;
}

/* 进度条 */
.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #e5e7eb;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24, #84cc16);
  animation: progress 1.5s ease-in-out infinite;
}

@keyframes progress {
  0% { width: 0; margin-left: 0; }
  50% { width: 60%; margin-left: 20%; }
  100% { width: 0; margin-left: 100%; }
}

/* 底部 */
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #fafafa;
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
  background: #2563eb;
  color: #fff;
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

/* 详情弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 450px;
  max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
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
  color: #1e293b;
}

.modal-close {
  border: none;
  background: none;
  font-size: 24px;
  color: #9ca3af;
  cursor: pointer;
  line-height: 1;
}

.modal-close:hover {
  color: #374151;
}

.modal-body {
  padding: 1.25rem;
  max-height: 60vh;
  overflow-y: auto;
}

.detail-row {
  display: flex;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  width: 80px;
  flex-shrink: 0;
  font-size: 13px;
  color: #6b7280;
}

.detail-value {
  flex: 1;
  font-size: 14px;
  color: #1e293b;
}

.status-text.status-pending { color: #d97706; }
.status-text.status-approved { color: #059669; }
.status-text.status-rejected { color: #dc2626; }

.modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #e5e7eb;
  background: #f8fafc;
  border-radius: 0 0 8px 8px;
}

.modal-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  margin-bottom: 0.75rem;
  box-sizing: border-box;
}

.modal-input:focus {
  outline: none;
  border-color: #2563eb;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-modal {
  flex: 1;
  padding: 0.625rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-modal.approve {
  background: #059669;
  color: white;
}

.btn-modal.approve:hover:not(:disabled) {
  background: #047857;
}

.btn-modal.reject {
  background: #dc2626;
  color: white;
}

.btn-modal.reject:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-modal:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
