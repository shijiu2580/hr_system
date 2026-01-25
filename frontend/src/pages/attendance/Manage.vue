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
            <button class="tab-btn" :class="{ active: activeTab === 'records' }" @click="activeTab = 'records'">
              我的考勤
            </button>
            <button class="tab-btn" :class="{ active: activeTab === 'supplement' }" @click="activeTab = 'supplement'">
              我的补签
            </button>
          </div>
        </div>
        <button class="btn-supplement" @click="showSupplementModal = true">
          补签
        </button>
      </div>

      <!-- 我的考勤 -->
      <div v-if="activeTab === 'records'" class="tab-content">
        <!-- 筛选栏 -->
        <div class="filters-bar">
          <div class="filter-item filter-date-group">
            <span class="filter-label">考勤日期：</span>
            <input type="date" v-model="dateFrom" class="filter-date" />
            <span class="filter-sep">~</span>
            <input type="date" v-model="dateTo" class="filter-date" />
          </div>
          <div class="filter-item">
            <span class="filter-label">考勤状态</span>
            <CustomSelect 
              v-model="statusFilter" 
              :options="statusOptions" 
              placeholder="全部"
              class="filter-custom-select"
            />
          </div>
          <div class="filter-item">
            <span class="filter-label">审批状态</span>
            <CustomSelect 
              v-model="approvalFilter" 
              :options="approvalOptions" 
              placeholder="全部"
              class="filter-custom-select"
            />
          </div>
          <button class="export-btn" :disabled="selected.length === 0 || exporting" @click="handleExport">
            <span v-if="exporting">导出中...</span>
            <span v-else>导出Excel{{ selected.length > 0 ? `(${selected.length})` : '' }}</span>
          </button>
        </div>

        <!-- 表格 -->
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-check"><input type="checkbox" class="checkbox" v-model="selectAll" @change="toggleSelectAll" /></th>
                <th class="col-date">考勤日期</th>
                <th class="col-time">首打卡</th>
                <th class="col-time">末打卡</th>
                <th class="col-absent">缺勤时长</th>
                <th class="col-status">考勤状态</th>
                <th class="col-reason">异常原因</th>
                <th class="col-settings"><img src="/icons/setting.svg" class="settings-icon" alt="设置" /></th>
              </tr>
            </thead>
            <tbody v-if="!loading && paginatedData.length">
              <tr v-for="item in paginatedData" :key="item.id" class="data-row" :class="{ 'row-selected': selected.includes(item.id) }">
                <td class="col-check"><input type="checkbox" class="checkbox" v-model="selected" :value="item.id" /></td>
                <td class="col-date">
                  <a href="javascript:;" class="date-link">{{ formatDateWithWeek(item.date) }}</a>
                  <span v-if="isWeekend(item.date)" class="weekend-icon">🏖️</span>
                </td>
                <td class="col-time">{{ item.check_in_time ? formatDateTime(item.date, item.check_in_time) : '--' }}</td>
                <td class="col-time">{{ item.check_out_time ? formatDateTime(item.date, item.check_out_time) : '--' }}</td>
                <td class="col-absent">{{ getAbsentDuration(item) }}</td>
                <td class="col-status">
                  <span class="status-text" :class="'status-' + getStatus(item)">{{ getStatusLabel(item) }}</span>
                </td>
                <td class="col-reason">
                  <template v-if="item.notes && formatReasonLines(item.notes).length">
                    <div v-for="(line, idx) in formatReasonLines(item.notes)" :key="idx" class="reason-line">{{ line }}</div>
                  </template>
                  <template v-else>--</template>
                </td>
                <td class="col-settings"></td>
              </tr>
            </tbody>
          </table>

          <!-- 加载状态 -->
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
          </div>

          <!-- 空状态 -->
          <div v-if="!loading && !paginatedData.length" class="empty-state">
            暂无考勤记录
          </div>

          <!-- 进度条 -->
          <div class="progress-bar" v-if="loading">
            <div class="progress-fill"></div>
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
      </div>

      <!-- 我的补签 -->
      <div v-if="activeTab === 'supplement'" class="tab-content">
        <!-- 异常考勤记录（迟到/早退） -->
        <div class="section-title">异常考勤记录</div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-date">考勤日期</th>
                <th class="col-time">签到时间</th>
                <th class="col-time">签退时间</th>
                <th class="col-status">异常类型</th>
                <th class="col-reason">异常原因</th>
              </tr>
            </thead>
            <tbody v-if="abnormalRecords.length">
              <tr v-for="item in paginatedAbnormalRecords" :key="item.id" class="data-row">
                <td class="col-date">{{ formatDateWithWeek(item.date) }}</td>
                <td class="col-time">{{ item.check_in_time ? formatTime(item.check_in_time) : '--' }}</td>
                <td class="col-time">{{ item.check_out_time ? formatTime(item.check_out_time) : '--' }}</td>
                <td class="col-status">
                  <span class="status-text" :class="'status-' + getStatus(item)">{{ getStatusLabel(item) }}</span>
                </td>
                <td class="col-reason">
                  <template v-if="item.notes && formatReasonLines(item.notes).length">
                    <div v-for="(line, idx) in formatReasonLines(item.notes)" :key="idx" class="reason-line">{{ line }}</div>
                  </template>
                  <template v-else>--</template>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="!abnormalRecords.length" class="empty-state">
            暂无异常考勤记录
          </div>
        </div>
        <!-- 异常考勤记录分页 -->
        <div v-if="abnormalRecords.length" class="table-footer">
          <span class="total-count">共{{ abnormalRecords.length }}条</span>
          <div class="pagination">
            <span class="page-size-label">每页</span>
            <CustomSelect 
              v-model="abnormalPageSize" 
              :options="pageSizeSelectOptions" 
              class="page-size-custom-select"
              @change="abnormalCurrentPage = 1"
            />
            <span class="page-size-label">条</span>
            <button class="page-btn" :disabled="abnormalCurrentPage <= 1" @click="abnormalGoToPage(1)">«</button>
            <button class="page-btn" :disabled="abnormalCurrentPage <= 1" @click="abnormalGoToPage(abnormalCurrentPage - 1)">‹</button>
            <span class="page-info">{{ abnormalCurrentPage }} / {{ abnormalTotalPages }}</span>
            <button class="page-btn" :disabled="abnormalCurrentPage >= abnormalTotalPages" @click="abnormalGoToPage(abnormalCurrentPage + 1)">›</button>
            <button class="page-btn" :disabled="abnormalCurrentPage >= abnormalTotalPages" @click="abnormalGoToPage(abnormalTotalPages)">»</button>
          </div>
        </div>

        <!-- 补签申请记录 -->
        <div class="section-title" style="margin-top: 1.5rem;">补签申请记录</div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-date">补签日期</th>
                <th class="col-time">补签时间</th>
                <th class="col-type">补签类型</th>
                <th class="col-reason">补签原因</th>
                <th class="col-status">审批状态</th>
                <th class="col-time">申请时间</th>
              </tr>
            </thead>
            <tbody v-if="supplements.length">
              <tr v-for="item in paginatedSupplements" :key="item.id" class="data-row">
                <td class="col-date">{{ item.date }}</td>
                <td class="col-time">{{ item.time }}</td>
                <td class="col-type">{{ item.type === 'check_in' ? '补签到' : '补签退' }}</td>
                <td class="col-reason">{{ item.reason || '-' }}</td>
                <td class="col-status">
                  <span class="status-text" :class="'status-' + item.status">{{ getApprovalLabel(item.status) }}</span>
                </td>
                <td class="col-time">{{ formatCreatedAt(item.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="!supplements.length" class="empty-state">
            暂无补签记录
          </div>
        </div>
        <!-- 补签申请记录分页 -->
        <div v-if="supplements.length" class="table-footer">
          <span class="total-count">共{{ supplements.length }}条</span>
          <div class="pagination">
            <span class="page-size-label">每页</span>
            <CustomSelect 
              v-model="supplementPageSize" 
              :options="pageSizeSelectOptions" 
              class="page-size-custom-select"
              @change="supplementCurrentPage = 1"
            />
            <span class="page-size-label">条</span>
            <button class="page-btn" :disabled="supplementCurrentPage <= 1" @click="supplementGoToPage(1)">«</button>
            <button class="page-btn" :disabled="supplementCurrentPage <= 1" @click="supplementGoToPage(supplementCurrentPage - 1)">‹</button>
            <span class="page-info">{{ supplementCurrentPage }} / {{ supplementTotalPages }}</span>
            <button class="page-btn" :disabled="supplementCurrentPage >= supplementTotalPages" @click="supplementGoToPage(supplementCurrentPage + 1)">›</button>
            <button class="page-btn" :disabled="supplementCurrentPage >= supplementTotalPages" @click="supplementGoToPage(supplementTotalPages)">»</button>
          </div>
        </div>
      </div>

      <!-- 补签弹窗 -->
      <div v-if="showSupplementModal" class="modal-overlay" @click.self="showSupplementModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>申请补签</h3>
            <button class="modal-close" @click="showSupplementModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-row">
              <label class="form-label">补签日期</label>
              <CustomDateInput v-model="supplementForm.date" placeholder="选择日期" />
            </div>
            <div class="form-row">
              <label class="form-label">补签时间</label>
              <input type="text" v-model="supplementForm.time" class="form-input" placeholder="例如：09:00" />
            </div>
            <div class="form-row">
              <label class="form-label">补签类型</label>
              <CustomSelect
                v-model="supplementForm.type"
                :options="supplementTypeOptions"
                placeholder="选择补签类型"
              />
            </div>
            <div class="form-row">
              <label class="form-label">补签原因</label>
              <textarea v-model="supplementForm.reason" class="form-textarea" placeholder="请填写补签原因"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showSupplementModal = false">取消</button>
            <button class="btn-submit" @click="submitSupplement" :disabled="submitting">
              {{ submitting ? '提交中...' : '提交申请' }}
            </button>
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
import { ref, computed, onMounted, watch } from 'vue';
import api from '../../utils/api';
import { useAuthStore } from '../../stores/auth';
import CustomSelect from '../../components/CustomSelect.vue';
import CustomDateInput from '../../components/CustomDateInput.vue';

const auth = useAuthStore();

const activeTab = ref('records');
const loading = ref(false);
const items = ref([]);
const supplements = ref([]);
const dateFrom = ref('');
const dateTo = ref('');
const statusFilter = ref('');
const approvalFilter = ref('');
const selected = ref([]);
const selectAll = ref(false);
const showSupplementModal = ref(false);
const submitting = ref(false);
const exporting = ref(false);
const message = ref(null);

// 下拉选项
const statusOptions = [
  { value: '', label: '全部' },
  { value: 'normal', label: '正常' },
  { value: 'late', label: '迟到' },
  { value: 'early_leave', label: '早退' },
  { value: 'absent', label: '缺勤' }
];

const approvalOptions = [
  { value: '', label: '全部' },
  { value: 'pending', label: '待审批' },
  { value: 'approved', label: '已批准' },
  { value: 'rejected', label: '已拒绝' }
];

const supplementTypeOptions = [
  { value: 'check_in', label: '补签到' },
  { value: 'check_out', label: '补签退' }
];

// 分页相关（我的考勤）
const currentPage = ref(1);
const pageSize = ref(20);
const pageSizeSelectOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' }
];

// 分页相关（异常考勤记录）
const abnormalCurrentPage = ref(1);
const abnormalPageSize = ref(20);

// 分页相关（补签申请记录）
const supplementCurrentPage = ref(1);
const supplementPageSize = ref(20);

// 管理员审批相关
const isAdmin = computed(() => auth.user?.is_staff || auth.user?.is_superuser);
const pendingSupplements = ref([]);
const approvingId = ref(null);

const supplementForm = ref({
  date: '',
  time: '',
  type: 'check_in',
  reason: ''
});

// 初始化日期范围为本月
onMounted(() => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  dateFrom.value = `${year}-${String(month).padStart(2, '0')}-01`;
  const lastDay = new Date(year, month, 0).getDate();
  dateTo.value = `${year}-${String(month).padStart(2, '0')}-${lastDay}`;
  load();
  loadPendingSupplements(); // 加载待审批补签
});

// 监听日期变化自动刷新
watch([dateFrom, dateTo], () => {
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
    result = result.filter(i => getStatus(i) === statusFilter.value);
  }
  
  // 按日期倒序排列
  return result.sort((a, b) => b.date.localeCompare(a.date));
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

// 异常考勤记录（迟到、早退、迟到/早退）
const abnormalRecords = computed(() => {
  return items.value.filter(item => {
    const status = getStatus(item);
    return status === 'late' || status === 'early_leave' || status === 'late_and_early';
  }).sort((a, b) => b.date.localeCompare(a.date));
});

// 异常考勤记录分页后的数据
const paginatedAbnormalRecords = computed(() => {
  const start = (abnormalCurrentPage.value - 1) * abnormalPageSize.value;
  const end = start + abnormalPageSize.value;
  return abnormalRecords.value.slice(start, end);
});

// 异常考勤记录总页数
const abnormalTotalPages = computed(() => {
  return Math.ceil(abnormalRecords.value.length / abnormalPageSize.value) || 1;
});

// 异常考勤记录切换页码
function abnormalGoToPage(page) {
  if (page >= 1 && page <= abnormalTotalPages.value) {
    abnormalCurrentPage.value = page;
  }
}

// 补签申请记录分页后的数据
const paginatedSupplements = computed(() => {
  const start = (supplementCurrentPage.value - 1) * supplementPageSize.value;
  const end = start + supplementPageSize.value;
  return supplements.value.slice(start, end);
});

// 补签申请记录总页数
const supplementTotalPages = computed(() => {
  return Math.ceil(supplements.value.length / supplementPageSize.value) || 1;
});

// 补签申请记录切换页码
function supplementGoToPage(page) {
  if (page >= 1 && page <= supplementTotalPages.value) {
    supplementCurrentPage.value = page;
  }
}

// 切换页码
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
}

// 格式化时间（只显示时分秒）
function formatTime(timeStr) {
  if (!timeStr) return '--';
  if (timeStr.includes('T') || timeStr.includes(' ')) {
    const d = new Date(timeStr);
    const pad = n => String(n).padStart(2, '0');
    return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }
  const parts = timeStr.split(':');
  const hh = String(parts[0]).padStart(2, '0');
  const mm = String(parts[1]).padStart(2, '0');
  const ss = parts[2] ? String(Math.floor(parseFloat(parts[2]))).padStart(2, '0') : '00';
  return `${hh}:${mm}:${ss}`;
}

const weekDays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];

function formatDateWithWeek(dateStr) {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  const weekDay = weekDays[d.getDay()];
  return `${dateStr} ${weekDay}`;
}

// 格式化异常原因（迟到/早退原因分行显示）
function formatReasonLines(notes) {
  if (!notes) return [];
  const lines = [];
  const lateMatch = notes.match(/迟到原因[：:]\s*([^\s早]+)/);
  const earlyMatch = notes.match(/早退原因[：:]\s*(.+?)(?:\s*迟到|$)/);
  if (lateMatch) lines.push(`迟到原因：${lateMatch[1]}`);
  if (earlyMatch) lines.push(`早退原因：${earlyMatch[1].trim()}`);
  if (lines.length === 0 && notes.trim()) lines.push(notes);
  return lines;
}

function isWeekend(dateStr) {
  if (!dateStr) return false;
  const d = new Date(dateStr);
  return d.getDay() === 0 || d.getDay() === 6;
}

function formatDateTime(dateStr, timeStr) {
  if (!timeStr) return '--';
  // 如果timeStr已经包含日期，则解析完整时间
  if (timeStr.includes('T') || timeStr.includes(' ')) {
    const d = new Date(timeStr);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }
  // 如果只有时间部分
  const parts = timeStr.split(':');
  const hh = String(parts[0]).padStart(2, '0');
  const mm = String(parts[1]).padStart(2, '0');
  const ss = parts[2] ? String(Math.floor(parseFloat(parts[2]))).padStart(2, '0') : '00';
  return `${dateStr} ${hh}:${mm}:${ss}`;
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

function getAbsentDuration(item) {
  // 简化处理，假设正常情况返回0
  return '0 分钟';
}

function getStatus(item) {
  if (!item.check_in_time && !item.check_out_time) {
    return isWeekend(item.date) ? 'normal' : 'absent';
  }
  if (item.attendance_type === 'late') return 'late';
  if (item.attendance_type === 'early_leave') return 'early_leave';
  if (item.attendance_type === 'absent') return 'absent';
  return 'normal';
}

function getStatusLabel(item) {
  const status = getStatus(item);
  const map = {
    normal: '正常',
    late: '迟到',
    early_leave: '早退',
    absent: '缺勤'
  };
  return map[status] || '正常';
}

function getApprovalLabel(status) {
  const map = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝'
  };
  return map[status] || status;
}

function toggleSelectAll() {
  if (selectAll.value) {
    selected.value = filtered.value.map(i => i.id);
  } else {
    selected.value = [];
  }
}

function showMessage(type, text) {
  message.value = { type, text };
  setTimeout(() => { message.value = null; }, 3000);
}

// 导出Excel
async function handleExport() {
  if (selected.value.length === 0) {
    showMessage('error', '请先勾选要导出的记录');
    return;
  }
  
  exporting.value = true;
  try {
    // 获取选中的记录
    const selectedRecords = items.value.filter(item => selected.value.includes(item.id));
    
    // 构建CSV内容
    const headers = ['考勤日期', '星期', '首打卡', '末打卡', '缺勤时长', '考勤状态', '异常原因'];
    const rows = selectedRecords.map(item => {
      const d = new Date(item.date);
      const weekDay = weekDays[d.getDay()];
      const status = getStatus(item);
      const statusMap = { normal: '正常', late: '迟到', early_leave: '早退', late_and_early: '迟到/早退', absent: '缺勤' };
      return [
        item.date,
        weekDay,
        item.check_in_time || '--',
        item.check_out_time || '--',
        getAbsentDuration(item),
        statusMap[status] || status,
        item.late_reason || item.early_leave_reason || '--'
      ];
    });
    
    // 添加BOM以支持中文
    let csvContent = '\uFEFF';
    csvContent += headers.join(',') + '\n';
    rows.forEach(row => {
      csvContent += row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',') + '\n';
    });
    
    // 下载文件
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `考勤记录_${dateFrom.value}_${dateTo.value}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
    
    showMessage('success', `成功导出 ${selectedRecords.length} 条记录`);
    selected.value = [];
    selectAll.value = false;
  } catch (e) {
    console.error('导出失败:', e);
    showMessage('error', '导出失败，请重试');
  }
  exporting.value = false;
}

async function load() {
  loading.value = true;
  try {
    let url = '/attendance/';
    const queryParams = [];
    if (dateFrom.value) queryParams.push(`date_from=${dateFrom.value}`);
    if (dateTo.value) queryParams.push(`date_to=${dateTo.value}`);
    if (queryParams.length) url += '?' + queryParams.join('&');
    
    const resp = await api.get(url);
    if (resp.success) {
      const raw = resp.data;
      items.value = Array.isArray(raw) ? raw : (raw?.results || []);
    } else {
      console.error('加载考勤记录失败:', resp.error?.message);
    }
  } catch (e) {
    console.error('加载考勤记录出错:', e);
  }
  
  // 加载补签申请记录
  await loadSupplements();
  
  loading.value = false;
}

async function loadSupplements() {
  try {
    const resp = await api.get('/attendance/supplement/');
    if (resp.success) {
      supplements.value = Array.isArray(resp.data) ? resp.data : [];
    }
  } catch (e) {
    console.error('加载补签记录出错:', e);
  }
}

async function submitSupplement() {
  if (!supplementForm.value.date || !supplementForm.value.time || !supplementForm.value.reason) {
    showMessage('error', '请填写完整信息');
    return;
  }
  submitting.value = true;
  try {
    const resp = await api.post('/attendance/supplement/', supplementForm.value);
    if (resp.success) {
      showMessage('success', '补签申请已提交');
      showSupplementModal.value = false;
      supplementForm.value = { date: '', time: '', type: 'check_in', reason: '' };
      // 重新加载补签记录
      await loadSupplements();
    } else {
      showMessage('error', resp.error?.message || '提交失败');
    }
  } catch (e) {
    showMessage('error', '提交失败，请重试');
    console.error('提交补签申请出错:', e);
  }
  submitting.value = false;
}

// ===== 管理员审批相关 =====
async function loadPendingSupplements() {
  if (!isAdmin.value) return;
  try {
    const resp = await api.get('/attendance/supplement/pending/');
    if (resp.success) {
      pendingSupplements.value = Array.isArray(resp.data) ? resp.data : [];
    }
  } catch (e) {
    console.error('加载待审批补签失败:', e);
  }
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
      await loadPendingSupplements();
      await load(); // 刷新考勤列表
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
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2563eb;
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
  color: #2563eb;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1rem;
  left: 0;
  right: 0;
  height: 2px;
  background: #2563eb;
}

.btn-supplement {
  padding: 0.5rem 1.25rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-supplement:hover {
  background: #1d4ed8;
}

/* 筛选栏 */
.filters-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  flex-wrap: nowrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.filter-label {
  font-size: 14px;
  color: #374151;
  white-space: nowrap;
}

.filter-date-group {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 0.25rem;
}

.filter-date {
  padding: 0.5rem 0.5rem;
  padding-right: 1.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
  outline: none;
  background: white url("/icons/calendar.svg") no-repeat right 0.5rem center;
  background-size: 14px;
  position: relative;
  width: 130px;
}

.filter-date::-webkit-calendar-picker-indicator {
  cursor: pointer;
  opacity: 0;
  position: absolute;
  right: 0;
  top: 0;
  width: 2rem;
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

.export-btn {
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

.export-btn:hover:not(:disabled) {
  background: #f1f5f9;
}

.export-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #94a3b8;
  color: #94a3b8;
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
  color: #2563eb;
  border-bottom: 2px solid #2563eb;
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

.data-row.row-selected {
  background: #eff6ff;
}

.data-row.row-selected:hover {
  background: #dbeafe;
}

.col-check {
  width: 40px;
  padding: 0 !important;
  text-align: center;
  vertical-align: middle;
}

.data-table th.col-check,
.data-table td.col-check {
  text-align: center;
  vertical-align: middle;
}

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

.checkbox:focus {
  outline: none !important;
  box-shadow: none !important;
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

.col-date {
  min-width: 180px;
}

.col-time {
  min-width: 160px;
}

.col-absent {
  min-width: 100px;
}

.col-status {
  min-width: 100px;
}

.col-reason {
  min-width: 120px;
  color: #9ca3af;
}

.reason-line {
  line-height: 1.5;
}

.reason-line + .reason-line {
  margin-top: 4px;
}

.col-settings {
  width: 40px;
  text-align: center;
}

.settings-icon {
  width: 18px;
  height: 18px;
  color: #9ca3af;
  cursor: pointer;
  vertical-align: middle;
}

.date-link {
  color: #2563eb;
  text-decoration: none;
}

.date-link:hover {
  text-decoration: underline;
}

.weekend-icon {
  margin-left: 0.5rem;
  font-size: 12px;
}

.status-text {
  font-weight: 500;
}

.status-text.status-normal {
  color: #059669;
}

.status-text.status-late {
  color: #d97706;
}

.status-text.status-early_leave {
  color: #d97706;
}

.status-text.status-absent {
  color: #dc2626;
}

.status-text.status-pending {
  color: #d97706;
}

.status-text.status-approved {
  color: #059669;
}

.status-text.status-rejected {
  color: #dc2626;
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

/* 底部统计 */
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-top: 1px solid #e5e7eb;
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

/* 弹窗 */
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
  width: 420px;
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
}

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

.form-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
}

.form-textarea {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  min-height: 80px;
  resize: vertical;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: #2563eb;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e5e7eb;
  background: #f8fafc;
  border-radius: 0 0 8px 8px;
}

.btn-cancel {
  padding: 0.625rem 1.25rem;
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #f3f4f6;
}

.btn-submit {
  padding: 0.625rem 1.25rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-submit:disabled {
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

/* 待审批补签样式 */
.pending-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: #ef4444;
  color: white;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  margin-left: 8px;
}

.col-action {
  white-space: nowrap;
}

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
</style>
