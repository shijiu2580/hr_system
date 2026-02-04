<template>
  <div class="page-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <img src="/icons/salaries.svg" alt="" />
        </div>
        <span class="header-title">差旅报销</span>
      </div>
      <div class="header-right">
        <button class="btn-approval" @click="$router.push('/salaries/expense-approval')">报销审批</button>
        <button class="btn-apply" @click="showCreateModal = true">申请报销</button>
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
        v-model="filterDate"
        :options="[
          { value: '', label: '申请日期' },
          { value: 'today', label: '今天' },
          { value: 'week', label: '本周' },
          { value: 'month', label: '本月' }
        ]"
        placeholder="申请日期"
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
            <th class="col-type">
              <span class="th-text">报销类型</span>
            </th>
            <th class="col-amount">报销金额</th>
            <th class="col-trip">关联出差</th>
            <th class="col-date sortable" @click="toggleSort('created_at')">
              <span class="th-text">申请时间</span>
              <span class="sort-icon" :class="{ active: sortField === 'created_at', desc: sortField === 'created_at' && sortOrder === 'desc' }">
                <img src="/icons/up_down.svg" />
              </span>
            </th>
            <th class="col-reason">报销事由</th>
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
            <td class="col-type">
              <a href="javascript:;" class="type-link">{{ getTypeLabel(item.expense_type) }}</a>
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
              <a href="javascript:;" class="action-link" v-if="item.status === 'pending'" @click="openEdit(item)">编辑</a>
              <a href="javascript:;" class="action-link" @click="showDetail(item)">详情</a>
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
        暂无报销记录
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

    <!-- 新建/编辑弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editItem ? '编辑报销' : '申请报销' }}</h3>
          <button class="modal-close" @click="closeCreateModal">×</button>
        </div>
        <form @submit.prevent="submitForm" class="modal-body">
          <div class="form-row">
            <label class="form-label required">报销类型</label>
            <CustomSelect
              v-model="form.expense_type"
              :options="[
                { value: 'travel', label: '差旅费' },
                { value: 'transport', label: '交通费' },
                { value: 'accommodation', label: '住宿费' },
                { value: 'meal', label: '餐饮费' },
                { value: 'other', label: '其他' }
              ]"
              placeholder="请选择报销类型"
              class="form-select"
            />
          </div>
          <div class="form-row">
            <label class="form-label required">报销金额</label>
            <input type="number" step="0.01" min="0" v-model="form.amount" class="form-input" placeholder="请输入金额" required />
          </div>
          <div class="form-row">
            <label class="form-label">关联出差</label>
            <CustomSelect
              v-model="form.business_trip_id"
              :options="businessTripOptions"
              placeholder="选择关联的出差申请（可选）"
              class="form-select"
            />
          </div>
          <div class="form-row">
            <label class="form-label required">报销事由</label>
            <textarea v-model="form.description" class="form-textarea" rows="3" placeholder="请输入报销事由" required></textarea>
          </div>
          <div class="form-row">
            <label class="form-label">发票附件</label>
            <div class="file-upload-wrapper">
              <input
                type="file"
                ref="invoiceInput"
                @change="handleInvoiceChange"
                accept=".pdf,.jpg,.jpeg,.png"
                class="file-input"
              />
              <div class="file-upload-box" @click="triggerFileInput">
                <span v-if="!form.invoice && !editItem?.invoice" class="upload-placeholder">
                  <span class="upload-icon">📎</span>
                  点击上传发票（支持PDF、JPG、PNG，最大10MB）
                </span>
                <span v-else-if="form.invoice" class="upload-filename">
                  {{ form.invoice.name }}
                  <button type="button" class="btn-remove-file" @click.stop="removeInvoice">×</button>
                </span>
                <span v-else-if="editItem?.invoice" class="upload-filename">
                  已上传发票
                  <a :href="editItem.invoice" target="_blank" class="btn-view-file" @click.stop>查看</a>
                </span>
              </div>
            </div>
          </div>
          <div class="form-row">
            <label class="form-label">备注</label>
            <textarea v-model="form.remarks" class="form-textarea" rows="2" placeholder="备注信息（可选）"></textarea>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="closeCreateModal">取消</button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? '提交中...' : '提交' }}
            </button>
          </div>
        </form>
      </div>
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
              <a :href="detailItem.invoice" target="_blank" class="invoice-link">点击查看/下载发票</a>
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
          <div class="detail-row" v-if="detailItem.remarks">
            <span class="detail-label">备注</span>
            <span class="detail-value">{{ detailItem.remarks }}</span>
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
const businessTrips = ref([]);
const message = ref(null);
const detailItem = ref(null);
const showCreateModal = ref(false);
const editItem = ref(null);
const submitting = ref(false);

// 表单
const form = ref({
  expense_type: 'travel',
  amount: '',
  business_trip_id: '',
  description: '',
  remarks: '',
  invoice: null
});
const invoiceInput = ref(null);

// 筛选
const filterType = ref('');
const filterDate = ref('');
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

// 出差选项
const businessTripOptions = computed(() => {
  const options = [{ value: '', label: '无' }];
  businessTrips.value.forEach(trip => {
    options.push({
      value: trip.id,
      label: `${trip.destination} (${trip.start_date} ~ ${trip.end_date})`
    });
  });
  return options;
});

// 筛选后的数据
const filtered = computed(() => {
  let result = [...records.value];

  if (filterType.value) {
    result = result.filter(r => r.expense_type === filterType.value);
  }

  if (filterDate.value) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    result = result.filter(r => {
      const d = new Date(r.created_at);
      if (filterDate.value === 'today') {
        return d >= today;
      } else if (filterDate.value === 'week') {
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - today.getDay());
        return d >= weekStart;
      } else if (filterDate.value === 'month') {
        const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
        return d >= monthStart;
      }
      return true;
    });
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
}

// 打开编辑
function openEdit(item) {
  editItem.value = item;
  form.value = {
    expense_type: item.expense_type,
    amount: item.amount,
    business_trip_id: item.business_trip?.id || '',
    description: item.description,
    remarks: item.remarks || '',
    invoice: null
  };
  showCreateModal.value = true;
}

// 关闭创建弹窗
function closeCreateModal() {
  showCreateModal.value = false;
  editItem.value = null;
  form.value = {
    expense_type: 'travel',
    amount: '',
    business_trip_id: '',
    description: '',
    remarks: '',
    invoice: null
  };
  // 清除文件输入
  if (invoiceInput.value) {
    invoiceInput.value.value = '';
  }
}

// 提交表单
async function submitForm() {
  if (submitting.value) return;

  submitting.value = true;
  try {
    const formData = new FormData();
    formData.append('expense_type', form.value.expense_type);
    formData.append('amount', form.value.amount);
    formData.append('description', form.value.description);
    if (form.value.remarks) {
      formData.append('remarks', form.value.remarks);
    }
    if (form.value.business_trip_id) {
      formData.append('business_trip_id', form.value.business_trip_id);
    }
    if (form.value.invoice) {
      formData.append('invoice', form.value.invoice);
    }

    if (editItem.value) {
      await api.patch(`/travel-expenses/${editItem.value.id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      showMessage('success', '修改成功');
    } else {
      await api.post('/travel-expenses/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      showMessage('success', '提交成功');
    }
    closeCreateModal();
    await load();
  } catch (err) {
    showMessage('error', err.response?.data?.detail || '操作失败');
  } finally {
    submitting.value = false;
  }
}

// 文件选择处理
function triggerFileInput() {
  if (invoiceInput.value) {
    invoiceInput.value.click();
  }
}

function handleInvoiceChange(event) {
  const file = event.target.files[0];
  if (file) {
    // 验证文件类型
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
      showMessage('error', '只支持PDF和图片格式(JPG/PNG)');
      event.target.value = '';
      return;
    }
    // 验证文件大小 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      showMessage('error', '文件大小不能超过10MB');
      event.target.value = '';
      return;
    }
    form.value.invoice = file;
  }
}

function removeInvoice() {
  form.value.invoice = null;
  if (invoiceInput.value) {
    invoiceInput.value.value = '';
  }
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
    const [expenseRes, tripRes] = await Promise.all([
      api.get('/travel-expenses/', { params: { page_size: 9999 } }),
      // 只获取自己的已批准出差申请用于关联
      api.get('/business-trips/', { params: { page_size: 9999, status: 'approved', my_only: 'true' } })
    ]);
    records.value = expenseRes.data.results || expenseRes.data || [];
    businessTrips.value = tripRes.data.results || tripRes.data || [];
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

.btn-approval {
  padding: 0.5rem 1.25rem;
  background: white;
  color: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-approval:hover {
  background: #eff6ff;
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
.col-type { width: 100px; }
.col-amount { width: 120px; }
.col-trip { width: 150px; }
.col-date { width: 150px; }
.col-reason { max-width: 200px; }
.col-status { width: 90px; }
.col-actions { width: 100px; }

.type-link {
  color: #2563eb;
  text-decoration: none;
}

.type-link:hover {
  text-decoration: underline;
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
  max-width: 200px;
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

/* 表单 */
.form-row {
  margin-bottom: 1rem;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-label.required::after {
  content: '*';
  color: #dc2626;
  margin-left: 0.25rem;
}

.form-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #1f2937;
  transition: border-color 0.2s;
  box-sizing: border-box;
  appearance: textfield;
  -moz-appearance: textfield;
}

.form-input::-webkit-outer-spin-button,
.form-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: none;
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

/* 文件上传样式 */
.file-upload-wrapper {
  width: 100%;
  position: relative;
}

.file-input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

.file-upload-box {
  width: 100%;
  min-height: 60px;
  border: 2px dashed #d1d5db;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #f9fafb;
  box-sizing: border-box;
  padding: 12px;
}

.file-upload-box:hover {
  border-color: #2563eb;
  background: #eff6ff;
}

.upload-placeholder {
  color: #6b7280;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-icon {
  font-size: 18px;
}

.upload-filename {
  color: #1f2937;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-remove-file {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.btn-remove-file:hover {
  background: #dc2626;
}

.btn-view-file {
  color: #2563eb;
  text-decoration: none;
  font-size: 12px;
  margin-left: 4px;
}

.btn-view-file:hover {
  text-decoration: underline;
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

.form-select {
  width: 100%;
}

.form-select :deep(.select-trigger) {
  padding: 0.625rem 0.75rem;
  padding-right: 2rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #fff;
  min-height: auto;
  font-size: 14px;
}

.form-select :deep(.select-trigger:hover) {
  border-color: #9ca3af;
}

.form-select :deep(.custom-select.open .select-trigger) {
  border-color: #2563eb;
  box-shadow: none;
}

.form-select :deep(.select-option.selected) {
  background: #2563eb;
  color: #fff;
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

.btn-primary {
  padding: 0.5rem 1rem;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
