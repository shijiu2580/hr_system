<template>
  <div class="page-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <img src="/icons/leaves.svg" alt="" />
        </div>
        <span class="header-title">出差申请</span>
      </div>
      <button class="btn-apply" @click="router.push('/leaves/business/create')">申请出差</button>
    </div>

    <!-- 筛选栏 -->
    <div class="filters-bar">
      <CustomSelect
        v-model="filterDestination"
        :options="[
          { value: '', label: '出差地点' },
          { value: 'domestic', label: '国内出差' },
          { value: 'overseas', label: '海外出差' }
        ]"
        placeholder="出差地点"
        class="filter-dropdown"
      />
      <CustomSelect
        v-model="filterDate"
        :options="[
          { value: '', label: '出差日期' },
          { value: 'today', label: '今天' },
          { value: 'week', label: '本周' },
          { value: 'month', label: '本月' }
        ]"
        placeholder="出差日期"
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
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-dest">
              <span class="th-text">出差地点</span>
            </th>
            <th class="col-time sortable" @click="toggleSort('start_date')">
              <span class="th-text">开始时间</span>
              <span class="sort-icon" :class="{ active: sortField === 'start_date', desc: sortField === 'start_date' && sortOrder === 'desc' }">
                <img src="/icons/up_down.svg" />
              </span>
            </th>
            <th class="col-time sortable" @click="toggleSort('end_date')">
              <span class="th-text">结束时间</span>
              <span class="sort-icon" :class="{ active: sortField === 'end_date', desc: sortField === 'end_date' && sortOrder === 'desc' }">
                <img src="/icons/up_down.svg" />
              </span>
            </th>
            <th class="col-duration">时长</th>
            <th class="col-reason">出差事由</th>
            <th class="col-status">状态</th>
            <th class="col-actions">
              <div class="action-header">
                <span>操作</span>
                <img src="/icons/setting.svg" class="settings-icon" alt="设置" />
              </div>
            </th>
          </tr>
        </thead>
        <tbody v-if="!loading && paged.length">
          <tr v-for="item in paged" :key="item.id" class="data-row">
            <td class="col-dest">
              <a href="javascript:;" class="type-link">{{ item.destination }}</a>
            </td>
            <td class="col-time">{{ formatDateTime(item.start_date) }}</td>
            <td class="col-time">{{ formatDateTime(item.end_date) }}</td>
            <td class="col-duration">{{ item.days }}天</td>
            <td class="col-reason">
              <span class="reason-ellipsis" :title="item.reason">{{ item.reason || '--' }}</span>
            </td>
            <td class="col-status">
              <span class="status-badge" :class="'status-' + item.status">{{ getStatusLabel(item.status) }}</span>
            </td>
            <td class="col-actions">
              <a href="javascript:;" class="action-link" v-if="canEdit(item)" @click="openEdit(item)">变更</a>
              <a href="javascript:;" class="action-link" v-if="item.status === 'approved'" @click="openCancel(item)">取消</a>
              <a href="javascript:;" class="action-link" @click="showLog(item)">日志</a>
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
        暂无出差记录
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

    <!-- 提示消息 -->
    <div v-if="message" class="message" :class="'message-' + message.type">
      {{ message.text }}
      <button class="close-btn" @click="message = null">×</button>
    </div>

    <!-- 日志详情弹窗 -->
    <div v-if="logItem" class="modal-overlay" @click.self="logItem = null">
      <div class="modal-content">
        <div class="modal-header">
          <h3>出差详情</h3>
          <button class="modal-close" @click="logItem = null">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <span class="detail-label">出差地点</span>
            <span class="detail-value">{{ logItem.destination }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">开始时间</span>
            <span class="detail-value">{{ formatDateTime(logItem.start_date) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">结束时间</span>
            <span class="detail-value">{{ formatDateTime(logItem.end_date) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">时长</span>
            <span class="detail-value">{{ logItem.days }}天</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">事由</span>
            <span class="detail-value">{{ logItem.reason || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">状态</span>
            <span class="detail-value status-text" :class="'status-' + logItem.status">
              {{ getStatusLabel(logItem.status) }}
            </span>
          </div>
          <div v-if="logItem.comments" class="detail-row">
            <span class="detail-label">审批备注</span>
            <span class="detail-value">{{ logItem.comments }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">申请时间</span>
            <span class="detail-value">{{ formatCreatedAt(logItem.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 变更弹窗 -->
    <div v-if="editItem" class="modal-overlay" @click.self="editItem = null">
      <div class="modal-content">
        <div class="modal-header">
          <h3>变更申请</h3>
          <button class="modal-close" @click="editItem = null">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">出差地点</label>
            <input type="text" v-model="editForm.destination" class="form-input" placeholder="请输入出差地点" />
          </div>
          <div class="form-group">
            <label class="form-label">开始日期</label>
            <CustomDateInput v-model="editForm.start_date" placeholder="选择日期" />
          </div>
          <div class="form-group">
            <label class="form-label">结束日期</label>
            <CustomDateInput v-model="editForm.end_date" placeholder="选择日期" />
          </div>
          <div class="form-group">
            <label class="form-label">出差事由</label>
            <textarea v-model="editForm.reason" class="form-textarea" rows="4" placeholder="请填写出差事由"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="editItem = null">取消</button>
          <button class="btn-submit" @click="submitEdit" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交变更' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 取消确认弹窗 -->
    <div v-if="cancelItem" class="modal-overlay" @click.self="cancelItem = null">
      <div class="modal-content modal-confirm">
        <div class="modal-header">
          <h3>确认取消</h3>
          <button class="modal-close" @click="cancelItem = null">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-message">
            <p>确定要取消此出差申请吗？</p>
            <p class="confirm-detail">
              {{ cancelItem.destination }}：{{ cancelItem.start_date }} 至 {{ cancelItem.end_date }}
            </p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="cancelItem = null">取消</button>
          <button class="btn-submit btn-danger" @click="submitCancel" :disabled="submitting">
            {{ submitting ? '处理中...' : '确认取消' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'
import CustomDateInput from '../../components/CustomDateInput.vue'

const router = useRouter()
const auth = useAuthStore()

// 状态
const items = ref([])
const loading = ref(false)
const submitting = ref(false)
const filterStatus = ref('')
const filterDestination = ref('')
const sortField = ref('')
const sortOrder = ref('desc')
const filterDate = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const pageSizeSelectOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' }
]
const message = ref(null)

// 弹窗状态
const logItem = ref(null)
const editItem = ref(null)
const cancelItem = ref(null)
const editForm = ref({
  start_date: '',
  end_date: '',
  destination: '',
  reason: ''
})

// 日期时间格式化
function formatDateTime(dateStr) {
  if (!dateStr) return ''
  return `${dateStr} 09:00`
}

// 格式化申请时间（去除秒后的数字）
function formatCreatedAt(dateTimeStr) {
  if (!dateTimeStr) return '-'
  // 截取到秒，格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM:SS
  const match = dateTimeStr.match(/^(\d{4}-\d{2}-\d{2})[T\s](\d{2}:\d{2}:\d{2})/)
  if (match) {
    return `${match[1]} ${match[2]}`
  }
  return dateTimeStr.substring(0, 19).replace('T', ' ')
}

// 计算属性
const filtered = computed(() => {
  let result = items.value.filter(item => {
    if (filterStatus.value && item.status !== filterStatus.value) return false
    return true
  })

  // 排序
  if (sortField.value) {
    result = [...result].sort((a, b) => {
      const aVal = a[sortField.value] || ''
      const bVal = b[sortField.value] || ''
      if (sortOrder.value === 'asc') {
        return aVal.localeCompare(bVal)
      } else {
        return bVal.localeCompare(aVal)
      }
    })
  }

  return result
})

const totalPages = computed(() => Math.ceil(filtered.value.length / pageSize.value) || 1)

const paged = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filtered.value.slice(start, start + pageSize.value)
})

// 分页方法
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 方法
function getStatusLabel(status) {
  const map = { pending: '待审批', approved: '已批准', rejected: '已拒绝', cancelled: '已取消' }
  return map[status] || status
}

function showLog(item) {
  logItem.value = item
}

function toggleSort(field) {
  if (sortField.value === field) {
    if (sortOrder.value === 'desc') {
      sortOrder.value = 'asc'
    } else {
      sortField.value = ''
      sortOrder.value = 'desc'
    }
  } else {
    sortField.value = field
    sortOrder.value = 'desc'
  }
}

// 判断是否在开始日期前
function isBeforeStartDate(item) {
  if (!item.start_date) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const startDate = new Date(item.start_date)
  startDate.setHours(0, 0, 0, 0)
  return today < startDate
}

// 判断是否可以变更：待审批且在开始日期前
function canEdit(item) {
  return item.status === 'pending' && isBeforeStartDate(item)
}

function openEdit(item) {
  editItem.value = item
  editForm.value = {
    start_date: item.start_date,
    end_date: item.end_date,
    destination: item.destination,
    reason: item.reason || ''
  }
}

function openCancel(item) {
  if (!isBeforeStartDate(item)) {
    message.value = { type: 'error', text: '出差已经开始，无法取消' }
    setTimeout(() => { message.value = null }, 3000)
    return
  }
  cancelItem.value = item
}

async function submitEdit() {
  if (!editForm.value.start_date || !editForm.value.end_date || !editForm.value.destination) {
    message.value = { type: 'error', text: '请填写完整信息' }
    return
  }

  submitting.value = true
  try {
    const resp = await api.put(`/business-trips/${editItem.value.id}/`, editForm.value)
    if (resp.success) {
      message.value = { type: 'success', text: '变更申请已提交' }
      editItem.value = null
      load()
    } else {
      message.value = { type: 'error', text: resp.error?.message || '变更失败' }
    }
  } catch (e) {
    message.value = { type: 'error', text: '操作失败' }
  } finally {
    submitting.value = false
  }
}

async function submitCancel() {
  submitting.value = true
  try {
    const resp = await api.post(`/business-trips/${cancelItem.value.id}/cancel/`)
    if (resp.success) {
      message.value = { type: 'success', text: '取消成功' }
      cancelItem.value = null
      load()
    } else {
      message.value = { type: 'error', text: resp.error?.message || '取消失败' }
    }
  } catch (e) {
    message.value = { type: 'error', text: '操作失败' }
  } finally {
    submitting.value = false
  }
}

async function load() {
  loading.value = true
  const resp = await api.get('/business-trips/', { params: { page_size: 9999 } })
  if (resp.success) {
    const d = resp.data
    if (Array.isArray(d)) {
      items.value = d
    } else if (d?.results && Array.isArray(d.results)) {
      items.value = d.results
    } else if (d?.data && Array.isArray(d.data)) {
      items.value = d.data
    } else {
      items.value = []
    }
    currentPage.value = 1
  } else {
    console.error('加载出差数据失败:', resp.error)
    message.value = {
      type: 'error',
      text: resp.error?.message || '加载失败，请检查网络连接'
    }
    items.value = []
  }
  loading.value = false
}

onMounted(() => load())
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.page-container {
  background: #fff;
  min-height: 100vh;
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
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon img {
  width: 24px;
  height: 24px;
  filter: invert(39%) sepia(90%) saturate(1352%) hue-rotate(196deg) brightness(96%) contrast(101%);
}

.header-title {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
}

.btn-apply {
  padding: 0.5rem 1.25rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-apply:hover {
  background: #1d4ed8;
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
}

/* 表格 */
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
}

.data-table th .th-text {
  margin-right: 0.25rem;
}

.data-table th .sort-icon {
  display: inline-flex;
  width: 12px;
  height: 12px;
  transition: transform 0.2s;
}

.data-table th .sort-icon img {
  width: 100%;
  height: 100%;
}

.data-table th .sort-icon.desc {
  transform: rotate(180deg);
}

.data-table th .settings-icon {
  width: 18px;
  height: 18px;
  color: #9ca3af;
  cursor: pointer;
}

.action-header {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
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
.col-dest {
  min-width: 120px;
}

.col-time {
  min-width: 150px;
}

.col-duration {
  min-width: 80px;
}

.col-reason {
  min-width: 150px;
  max-width: 200px;
}

.col-status {
  min-width: 80px;
}

.col-actions {
  min-width: 150px;
}

/* 状态标签 */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.status-pending {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.status-approved {
  background: #d1fae5;
  color: #059669;
}

.status-badge.status-rejected {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.status-cancelled {
  background: #e5e7eb;
  color: #6b7280;
}

/* 链接样式 */
.type-link {
  color: #2563eb;
  text-decoration: none;
}

.type-link:hover {
  text-decoration: underline;
}

.reason-ellipsis {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 操作链接 */
.action-link {
  color: #2563eb;
  text-decoration: none;
  margin-right: 1rem;
  font-size: 14px;
}

.action-link:hover {
  text-decoration: underline;
}

/* 加载状态 */
.loading-state {
  padding: 2rem;
}


/* 空状态 */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
  font-size: 14px;
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

/* 消息提示 */
.message {
  position: fixed;
  top: 1rem;
  right: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 2000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.message-success {
  background: #22c55e;
}

.message-error {
  background: #ef4444;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.8;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  opacity: 1;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 8px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-content.modal-confirm {
  max-width: 400px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.modal-close {
  width: 28px;
  height: 28px;
  border: none;
  background: none;
  font-size: 20px;
  color: #9ca3af;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #6b7280;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.modal-body::-webkit-scrollbar {
  display: none;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

/* 详情行 */
.detail-row {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  width: 90px;
  flex-shrink: 0;
  color: #6b7280;
  font-size: 14px;
}

.detail-value {
  flex: 1;
  color: #1f2937;
  font-size: 14px;
}

.status-text.status-pending {
  color: #f59e0b;
}

.status-text.status-approved {
  color: #22c55e;
}

.status-text.status-rejected {
  color: #ef4444;
}

/* 表单组 */
.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #1f2937;
  background: #fff;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: none;
}

.form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #1f2937;
  background: #fff;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: none;
}

.form-textarea::placeholder {
  color: #9ca3af;
}

/* 确认弹窗 */
.confirm-message {
  text-align: center;
  padding: 10px 0;
}

.confirm-message p {
  margin: 0 0 10px;
  font-size: 15px;
  color: #1f2937;
}

.confirm-detail {
  color: #6b7280 !important;
  font-size: 14px !important;
}

/* 按钮 */
.btn-cancel {
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-cancel:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-submit {
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: #3b82f6;
  color: #fff;
  border: none;
}

.btn-submit:hover:not(:disabled) {
  background: #2563eb;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-submit.btn-danger {
  background: #ef4444;
}

.btn-submit.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

/* 响应式 */
@media (max-width: 768px) {
  .filters-bar {
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .data-table {
    font-size: 12px;
  }

  .data-table th,
  .data-table td {
    padding: 0.625rem 0.5rem;
  }

  .action-link {
    margin-right: 0.5rem;
  }
}
</style>
