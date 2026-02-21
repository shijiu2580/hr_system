<template>
  <div class="page-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <img src="/icons/salaries.svg" alt="" />
        </div>
        <span class="header-title">薪资记录</span>
      </div>
      <div class="header-right">
        <!-- 发放薪资按钮（仅财务/管理员可见） -->
        <button
          v-if="canDisburse && (unpaidCount > 0 || selectedUnpaidIds.length > 0)"
          type="button"
          class="btn-disburse"
          :class="{ 'btn-disburse-selected': selectedUnpaidIds.length > 0 }"
          @click="openDisburseModal"
          :disabled="disbursing"
        >
          {{ disbursing ? '发放中...' : disburseButtonText }}
        </button>
        <button
          type="button"
          class="btn-export"
          @click="exportExcel"
          :disabled="exporting"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 3v12" />
            <path d="M8 11l4 4 4-4" />
            <path d="M4 21h16" />
          </svg>
          {{ exporting ? '导出中...' : (selectedIds.size > 0 ? `导出选中(${selectedIds.size})` : '导出Excel') }}
        </button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filters-bar">
      <div class="employee-search-wrapper" ref="employeeSearchRef">
        <input
          type="text"
          v-model="employeeSearchText"
          @focus="showEmployeeDropdown = true"
          @input="onEmployeeSearch"
          placeholder="搜索员工..."
          class="employee-search-input"
        />
        <button
          v-if="filterEmployee"
          type="button"
          class="clear-employee-btn"
          @click="clearEmployeeFilter"
        >×</button>
        <transition name="dropdown">
          <div v-if="showEmployeeDropdown" class="employee-dropdown">
            <div
              class="employee-option"
              :class="{ active: !filterEmployee }"
              @click="selectEmployee(null)"
            >
              全部员工
            </div>
            <div
              v-for="emp in filteredEmployeeOptions"
              :key="emp.id"
              class="employee-option"
              :class="{ active: filterEmployee === emp.id }"
              @click="selectEmployee(emp)"
            >
              <span class="emp-name">{{ emp.name }}</span>
              <span class="emp-id">{{ emp.employee_id }}</span>
            </div>
            <div v-if="filteredEmployeeOptions.length === 0 && employeeSearchText" class="no-result">
              未找到匹配员工
            </div>
          </div>
        </transition>
      </div>
      <CustomSelect
        v-model="filterYear"
        :options="yearOptions"
        placeholder="年份"
        class="filter-dropdown"
      />
      <CustomSelect
        v-model="filterMonth"
        :options="monthOptions"
        placeholder="月份"
        class="filter-dropdown"
      />
      <CustomSelect
        v-model="filterStatus"
        :options="[
          { value: '', label: '发放状态' },
          { value: 'paid', label: '已发放' },
          { value: 'unpaid', label: '未发放' }
        ]"
        placeholder="发放状态"
        class="filter-dropdown"
      />
      <button
        v-if="!showLastMonthAndUnpaid"
        class="reset-filter-btn"
        @click="resetFilters"
        title="重置为默认显示"
      >重置</button>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-checkbox">
              <input
                type="checkbox"
                :checked="isAllPageSelected"
                :indeterminate="isPartialSelected"
                @change="toggleSelectAll"
                class="checkbox"
              />
            </th>
            <th class="col-employee">员工姓名</th>
            <th class="col-period sortable" @click="toggleSort('year')">
              <span class="th-text">薪资周期</span>
              <span class="sort-icon" :class="{ active: sortField === 'year', desc: sortField === 'year' && sortOrder === 'desc' }">
                <img src="/icons/up_down.svg" />
              </span>
            </th>
            <th class="col-base">基本工资</th>
            <th class="col-bonus">奖金</th>
            <th class="col-allowance">津贴</th>
            <th class="col-net">实发工资</th>
            <th class="col-status">状态</th>
            <th class="col-paid-at sortable" @click="toggleSort('paid_at')">
              <span class="th-text">发放时间</span>
              <span class="sort-icon" :class="{ active: sortField === 'paid_at', desc: sortField === 'paid_at' && sortOrder === 'desc' }">
                <img src="/icons/up_down.svg" />
              </span>
            </th>
            <th class="col-actions">
              <div class="action-header">
                <span>操作</span>
                <img src="/icons/setting.svg" class="settings-icon" alt="设置" />
              </div>
            </th>
          </tr>
        </thead>
        <tbody v-if="!loading && paged.length">
          <tr v-for="item in paged" :key="item.id" class="data-row" :class="{ 'row-selected': selectedIds.has(item.id), 'row-unpaid': !item.paid && canDisburse }">
            <td class="col-checkbox">
              <input
                type="checkbox"
                :checked="selectedIds.has(item.id)"
                @change="toggleSelect(item.id)"
                class="checkbox"
                :class="{ 'checkbox-unpaid': !item.paid && canDisburse }"
              />
            </td>
            <td class="col-employee">
              <router-link
                v-if="item.employee?.id"
                :to="`/employees/${item.employee.id}`"
                class="employee-link"
              >
                {{ item.employee?.name || '-' }}
              </router-link>
              <span v-else>{{ item.employee?.name || '-' }}</span>
            </td>
            <td class="col-period">
              <a href="javascript:;" class="type-link">{{ item.year }}年{{ item.month }}月</a>
            </td>
            <td class="col-base">¥{{ formatMoney(item.basic_salary) }}</td>
            <td class="col-bonus">¥{{ formatMoney(item.bonus) }}</td>
            <td class="col-allowance">¥{{ formatMoney(item.allowance) }}</td>
            <td class="col-net">
              <span class="net-salary">¥{{ formatMoney(calcNetSalary(item)) }}</span>
            </td>
            <td class="col-status">
              <span class="status-badge" :class="item.paid ? 'status-paid' : 'status-unpaid'">
                {{ item.paid ? '已发放' : '未发放' }}
              </span>
            </td>
            <td class="col-paid-at">{{ item.paid_at ? formatDateTime(item.paid_at) : '--' }}</td>
            <td class="col-actions">
              <a href="javascript:;" class="action-link" @click="showDetail(item)">详情</a>
              <a v-if="!item.paid" href="javascript:;" class="action-link" @click="openEdit(item)">编辑</a>
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
        暂无薪资记录
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

    <!-- 详情弹窗 -->
    <div v-if="detailItem" class="modal-overlay" @click.self="detailItem = null">
      <div class="modal-content">
        <div class="modal-header">
          <h3>薪资详情</h3>
          <button class="modal-close" @click="detailItem = null">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <span class="detail-label">薪资周期</span>
            <span class="detail-value">{{ detailItem.year }}年{{ detailItem.month }}月</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">基本工资</span>
            <span class="detail-value">¥{{ formatMoney(detailItem.basic_salary) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">奖金</span>
            <span class="detail-value">¥{{ formatMoney(detailItem.bonus) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">津贴</span>
            <span class="detail-value">¥{{ formatMoney(detailItem.allowance) }}</span>
          </div>
          <div class="detail-row highlight">
            <span class="detail-label">实发工资</span>
            <span class="detail-value net">¥{{ formatMoney(calcNetSalary(detailItem)) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">发放状态</span>
            <span class="detail-value">
              <span class="status-badge" :class="detailItem.paid ? 'status-paid' : 'status-unpaid'">
                {{ detailItem.paid ? '已发放' : '未发放' }}
              </span>
            </span>
          </div>
          <div class="detail-row" v-if="detailItem.paid_at">
            <span class="detail-label">发放时间</span>
            <span class="detail-value">{{ formatDateTime(detailItem.paid_at) }}</span>
          </div>
          <div class="detail-row" v-if="detailItem.remarks">
            <span class="detail-label">备注</span>
            <span class="detail-value">{{ detailItem.remarks }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="detailItem = null">关闭</button>
          <button v-if="!detailItem.paid" class="btn-primary" @click="editFromDetail">编辑</button>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <div v-if="editItem" class="modal-overlay" @click.self="closeEdit">
      <div class="modal-content modal-edit">
        <div class="modal-header">
          <h3>编辑薪资记录</h3>
          <button class="modal-close" @click="closeEdit">×</button>
        </div>
        <div class="modal-body">
          <div class="edit-form">
            <div class="edit-row">
              <span class="edit-label">员工</span>
              <span class="edit-value employee-name">{{ editItem.employee?.name || '-' }}</span>
            </div>
            <div class="edit-row edit-row-double">
              <div class="edit-field">
                <span class="edit-label">年份 <span v-if="!editItem.paid" class="required">*</span></span>
                <input v-if="!editItem.paid" type="number" v-model.number="editForm.year" min="2020" max="2100" class="edit-input" />
                <span v-else class="edit-value">{{ editForm.year }}</span>
              </div>
              <div class="edit-field">
                <span class="edit-label">月份 <span v-if="!editItem.paid" class="required">*</span></span>
                <input v-if="!editItem.paid" type="number" v-model.number="editForm.month" min="1" max="12" class="edit-input" />
                <span v-else class="edit-value">{{ editForm.month }}</span>
              </div>
            </div>
            <div class="edit-row">
              <span class="edit-label">基本工资</span>
              <input v-if="!editItem.paid" type="number" v-model.number="editForm.basic_salary" step="0.01" min="0" class="edit-input" />
              <span v-else class="edit-value">¥{{ Number(editForm.basic_salary || 0).toFixed(2) }}</span>
            </div>
            <div class="edit-row">
              <span class="edit-label">奖金</span>
              <input type="number" v-model.number="editForm.bonus" step="0.01" min="0" class="edit-input" />
            </div>
            <div class="edit-row">
              <span class="edit-label">津贴</span>
              <input type="number" v-model.number="editForm.allowance" step="0.01" min="0" class="edit-input" />
            </div>
            <div class="edit-row">
              <span class="edit-label">备注</span>
              <textarea v-model="editForm.remarks" class="edit-textarea" rows="2" placeholder="选填"></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeEdit">取消</button>
          <button class="btn-primary" @click="saveEdit" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 发放薪资确认弹窗 -->
    <div v-if="showDisburseModal" class="modal-overlay" @click.self="showDisburseModal = false">
      <div class="modal-content modal-disburse">
        <div class="modal-header">
          <h3>发放薪资</h3>
          <button class="modal-close" @click="showDisburseModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="disburse-info">
            <div class="disburse-summary">
              <div class="summary-item">
                <span class="summary-label">待发放月份</span>
                <div class="summary-months">
                  <span v-for="p in pendingSummary" :key="`${p.year}-${p.month}`" class="month-tag">
                    {{ p.year }}年{{ p.month }}月 ({{ p.count }}人)
                  </span>
                </div>
              </div>
              <div class="summary-item">
                <span class="summary-label">待发放人数</span>
                <span class="summary-value">{{ unpaidCount }} 人</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">待发放总额</span>
                <span class="summary-value total">¥{{ formatMoney(unpaidTotal) }}</span>
              </div>
            </div>
            <div class="disburse-options">
              <label class="option-label">选择发放范围：</label>
              <div class="option-group">
                <div class="custom-radio-option" :class="{ active: disburseMode === 'all' }" @click="disburseMode = 'all'">
                  <div class="radio-header">
                    <div class="radio-circle">
                      <span class="radio-dot" :class="{ show: disburseMode === 'all' }"></span>
                    </div>
                    <span>全部待发放记录</span>
                  </div>
                </div>

                <div class="custom-radio-option" :class="{ active: disburseMode === 'month' }" @click="disburseMode = 'month'">
                  <div class="radio-header">
                    <div class="radio-circle">
                      <span class="radio-dot" :class="{ show: disburseMode === 'month' }"></span>
                    </div>
                    <span>按月份发放</span>
                  </div>
                  <div v-if="disburseMode === 'month'" class="radio-content" @click.stop>
                    <CustomSelect
                      v-model="disburseYearMonth"
                      :options="disburseMonthOptions"
                      placeholder="请选择月份"
                      class="full-width-select"
                    />
                  </div>
                </div>

                <div v-if="selectedUnpaidIds.length > 0" class="custom-radio-option" :class="{ active: disburseMode === 'selected' }" @click="disburseMode = 'selected'">
                  <div class="radio-header">
                    <div class="radio-circle">
                      <span class="radio-dot" :class="{ show: disburseMode === 'selected' }"></span>
                    </div>
                    <span>仅选中记录 ({{ selectedUnpaidIds.length }}条)</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="disburse-warning" :class="{ 'warning-error': disburseMode === 'month' && !disburseYearMonth }">
              <span v-if="disburseMode === 'month' && !disburseYearMonth">请选择月份</span>
              <span v-else>发放后将自动通知相关员工，请确认无误后再发放。</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDisburseModal = false">取消</button>
          <button class="btn-primary btn-confirm" @click="confirmDisburse" :disabled="disbursing || !canConfirmDisburse">
            {{ disbursing ? '发放中...' : '确认发放' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import CustomSelect from '../../components/CustomSelect.vue';
import api from '../../utils/api';
import { useAuthStore } from '../../stores/auth';
import { hasPermission, isAdmin, Permissions } from '../../utils/permissions';

// 权限
const auth = useAuthStore();
const canDisburse = computed(() =>
  isAdmin() || hasPermission(Permissions.SALARY_DISBURSE)
);

// 发放薪资相关
const showDisburseModal = ref(false);
const disbursing = ref(false);
const disburseMode = ref('all'); // 'all' | 'month' | 'selected'
const disburseYearMonth = ref('');

// 待发放记录统计
const unpaidRecords = computed(() => records.value.filter(r => !r.paid));
const unpaidCount = computed(() => unpaidRecords.value.length);
const unpaidTotal = computed(() =>
  unpaidRecords.value.reduce((sum, r) => sum + calcNetSalary(r), 0)
);

// 选中的未发放记录
const selectedUnpaidIds = computed(() =>
  Array.from(selectedIds.value).filter(id => {
    const r = records.value.find(rec => rec.id === id);
    return r && !r.paid;
  })
);

// 按月份汇总待发放记录
const pendingSummary = computed(() => {
  const map = new Map();
  unpaidRecords.value.forEach(r => {
    const key = `${r.year}-${r.month}`;
    if (!map.has(key)) {
      map.set(key, { year: r.year, month: r.month, count: 0, total: 0 });
    }
    const item = map.get(key);
    item.count++;
    item.total += calcNetSalary(r);
  });
  return Array.from(map.values()).sort((a, b) => {
    if (a.year !== b.year) return b.year - a.year;
    return b.month - a.month;
  });
});

// 下拉框选项
const disburseMonthOptions = computed(() => {
  return [
    { value: '', label: '请选择月份' },
    ...pendingSummary.value.map(p => ({
      value: `${p.year}-${p.month}`,
      label: `${p.year}年${p.month}月 - ${p.count}人 / ¥${formatMoney(p.total)}`
    }))
  ];
});

// 是否可以确认发放
const canConfirmDisburse = computed(() => {
  if (disburseMode.value === 'all') return unpaidCount.value > 0;
  if (disburseMode.value === 'month') return !!disburseYearMonth.value;
  if (disburseMode.value === 'selected') return selectedUnpaidIds.value.length > 0;
  return false;
});

// 发放按钮文字
const disburseButtonText = computed(() => {
  if (selectedUnpaidIds.value.length > 0) {
    return `发放选中(${selectedUnpaidIds.value.length})`;
  }
  return `发放薪资(${unpaidCount.value})`;
});

// 打开发放弹窗
function openDisburseModal() {
  // 如果有选中未发放记录，默认选择"仅选中记录"模式
  if (selectedUnpaidIds.value.length > 0) {
    disburseMode.value = 'selected';
  } else {
    disburseMode.value = 'all';
  }
  disburseYearMonth.value = '';
  showDisburseModal.value = true;
}

// 确认发放薪资
async function confirmDisburse() {
  if (!canConfirmDisburse.value) return;

  disbursing.value = true;
  try {
    let payload = {};

    if (disburseMode.value === 'all') {
      // 发放所有待发放记录
      payload.ids = unpaidRecords.value.map(r => r.id);
    } else if (disburseMode.value === 'month') {
      // 按月份发放
      const [year, month] = disburseYearMonth.value.split('-').map(Number);
      payload.year = year;
      payload.month = month;
    } else if (disburseMode.value === 'selected') {
      // 发放选中的记录
      payload.ids = selectedUnpaidIds.value;
    }

    const resp = await api.post('/salaries/disburse/', payload);

    if (resp.success) {
      showMessage('success', resp.detail || `成功发放 ${resp.data?.count || 0} 条薪资记录`);
      showDisburseModal.value = false;
      // 清空选择
      selectedIds.value = new Set();
    } else {
      showMessage('error', resp.error?.message || '发放失败');
    }
  } catch (err) {
    console.error('发放薪资错误:', err);
    showMessage('error', err?.response?.data?.error?.message || '发放失败');
  } finally {
    disbursing.value = false;
    // 无论成功失败，都重新加载数据
    fetchData().catch(() => {});
  }
}

// 数据状态
const loading = ref(false);
const records = ref([]);
const message = ref(null);
const detailItem = ref(null);
const exporting = ref(false);

// 编辑相关
const editItem = ref(null);
const editForm = ref({
  year: null,
  month: null,
  basic_salary: 0,
  bonus: 0,
  allowance: 0,
  remarks: ''
});
const saving = ref(false);

// 选择相关
const selectedIds = ref(new Set());

// 当前页是否全选
const isAllPageSelected = computed(() => {
  if (paged.value.length === 0) return false;
  return paged.value.every(item => selectedIds.value.has(item.id));
});

// 当前页是否部分选中
const isPartialSelected = computed(() => {
  if (paged.value.length === 0) return false;
  const selectedCount = paged.value.filter(item => selectedIds.value.has(item.id)).length;
  return selectedCount > 0 && selectedCount < paged.value.length;
});

// 切换单个选择
function toggleSelect(id) {
  const newSet = new Set(selectedIds.value);
  if (newSet.has(id)) {
    newSet.delete(id);
  } else {
    newSet.add(id);
  }
  selectedIds.value = newSet;
}

// 切换全选（当前页）
function toggleSelectAll() {
  const newSet = new Set(selectedIds.value);
  if (isAllPageSelected.value) {
    // 取消当前页全选
    paged.value.forEach(item => newSet.delete(item.id));
  } else {
    // 选中当前页所有
    paged.value.forEach(item => newSet.add(item.id));
  }
  selectedIds.value = newSet;
}

// 导出Excel
async function exportExcel() {
  exporting.value = true;
  try {
    const params = {};
    // 如果有选中记录，导出选中的；否则按筛选条件导出
    if (selectedIds.value.size > 0) {
      params.ids = Array.from(selectedIds.value).join(',');
    } else {
      // 按当前筛选条件导出
      if (filterYear.value) params.year = filterYear.value;
      if (filterMonth.value) params.month = filterMonth.value;
      if (filterEmployee.value) params.employee = filterEmployee.value;
    }

    const resp = await api.raw.get('/export/salaries/', {
      params,
      responseType: 'blob',
    });

    const blob = new Blob([resp.data], { type: resp.headers?.['content-type'] || 'application/octet-stream' });

    let filename = '薪资记录.xlsx';
    const cd = resp.headers?.['content-disposition'] || resp.headers?.['Content-Disposition'];
    if (cd) {
      const match = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i.exec(cd);
      const name = match?.[1] || match?.[2];
      if (name) {
        try {
          filename = decodeURIComponent(name);
        } catch {
          filename = name;
        }
      }
    }

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

    showMessage('success', '导出成功');
  } catch (err) {
    let errText = '导出失败';
    const data = err?.response?.data;
    if (data && typeof data.text === 'function') {
      try {
        const t = await data.text();
        if (t) errText = t;
      } catch {
        // ignore
      }
    }
    showMessage('error', errText);
  } finally {
    exporting.value = false;
  }
}

// 员工搜索
const employeeSearchRef = ref(null);
const employeeSearchText = ref('');
const showEmployeeDropdown = ref(false);
const employeeOptions = ref([]);
const filterEmployee = ref(null);

// 过滤后的员工选项（根据搜索文本）
const filteredEmployeeOptions = computed(() => {
  if (!employeeSearchText.value) return employeeOptions.value;
  const keyword = employeeSearchText.value.toLowerCase();
  return employeeOptions.value.filter(emp =>
    emp.name.toLowerCase().includes(keyword) ||
    emp.employee_id.toLowerCase().includes(keyword)
  );
});

// 员工搜索相关方法
function onEmployeeSearch() {
  showEmployeeDropdown.value = true;
}

function selectEmployee(emp) {
  if (emp) {
    filterEmployee.value = emp.id;
    employeeSearchText.value = emp.name;
  } else {
    filterEmployee.value = null;
    employeeSearchText.value = '';
  }
  showEmployeeDropdown.value = false;
}

function clearEmployeeFilter() {
  filterEmployee.value = null;
  employeeSearchText.value = '';
}

// 点击外部关闭下拉
function handleClickOutside(event) {
  if (employeeSearchRef.value && !employeeSearchRef.value.contains(event.target)) {
    showEmployeeDropdown.value = false;
  }
}

// 筛选 - 默认不筛选，显示所有记录
const filterYear = ref('');
const filterMonth = ref('');
const filterStatus = ref('');
const showLastMonthAndUnpaid = ref(true); // 默认显示上个月已发放 + 所有未发放

// 排序
const sortField = ref('');
const sortOrder = ref('desc');

// 分页
const currentPage = ref(1);
const pageSize = ref(20);
const pageSizeSelectOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' }
];

// 年份选项
const currentYear = new Date().getFullYear();
const yearOptions = computed(() => {
  const options = [{ value: '', label: '年份' }];
  for (let y = currentYear; y >= currentYear - 5; y--) {
    options.push({ value: String(y), label: String(y) + '年' });
  }
  return options;
});

// 月份选项
const monthOptions = computed(() => {
  const options = [{ value: '', label: '月份' }];
  for (let m = 1; m <= 12; m++) {
    options.push({ value: String(m), label: m + '月' });
  }
  return options;
});

// 计算上个月的年份和月份
const lastMonth = computed(() => {
  const now = new Date();
  let year = now.getFullYear();
  let month = now.getMonth(); // 0-11，getMonth()返回的是0-11，所以这正好是上个月
  if (month === 0) {
    year -= 1;
    month = 12;
  }
  return { year, month };
});

// 筛选后的数据
const filtered = computed(() => {
  let result = [...records.value];

  // 员工筛选
  if (filterEmployee.value) {
    result = result.filter(r => r.employee?.id === filterEmployee.value);
  }

  // 默认模式：显示上个月已发放 + 所有未发放
  if (showLastMonthAndUnpaid.value && !filterYear.value && !filterMonth.value && !filterStatus.value) {
    const { year: lastY, month: lastM } = lastMonth.value;
    result = result.filter(r => {
      // 未发放的全部显示
      if (!r.paid) return true;
      // 已发放的只显示上个月
      return r.year === lastY && r.month === lastM;
    });
  } else {
    // 手动筛选模式
    if (filterYear.value) {
      result = result.filter(r => String(r.year) === filterYear.value);
    }
    if (filterMonth.value) {
      result = result.filter(r => String(r.month) === filterMonth.value);
    }
    if (filterStatus.value) {
      if (filterStatus.value === 'paid') {
        result = result.filter(r => r.paid);
      } else if (filterStatus.value === 'unpaid') {
        result = result.filter(r => !r.paid);
      }
    }
  }

  // 排序
  if (sortField.value) {
    result.sort((a, b) => {
      let aVal, bVal;
      if (sortField.value === 'year') {
        aVal = a.year * 100 + a.month;
        bVal = b.year * 100 + b.month;
      } else if (sortField.value === 'paid_at') {
        aVal = a.paid_at || '';
        bVal = b.paid_at || '';
      } else {
        aVal = a[sortField.value];
        bVal = b[sortField.value];
      }
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

// 计算实发工资（基本工资 + 奖金 + 津贴）
function calcNetSalary(item) {
  const basic = Number(item.basic_salary) || 0;
  const bonus = Number(item.bonus) || 0;
  const allowance = Number(item.allowance) || 0;
  return basic + bonus + allowance;
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
  if (!item) return;
  detailItem.value = item;
}

// 从详情弹窗进入编辑
function editFromDetail() {
  const item = detailItem.value;
  if (!item) return;
  detailItem.value = null;
  openEdit(item);
}

// 编辑相关函数
function openEdit(item) {
  if (!item) return;
  editItem.value = item;
  editForm.value = {
    year: item.year,
    month: item.month,
    basic_salary: Number(item.basic_salary) || 0,
    bonus: Number(item.bonus) || 0,
    allowance: Number(item.allowance) || 0,
    remarks: item.remarks || ''
  };
}

function closeEdit() {
  editItem.value = null;
  editForm.value = {
    year: null,
    month: null,
    basic_salary: 0,
    bonus: 0,
    allowance: 0,
    remarks: ''
  };
}

async function saveEdit() {
  if (!editItem.value) return;
  if (!editForm.value.year || !editForm.value.month) {
    showMessage('error', '年份和月份不能为空');
    return;
  }

  saving.value = true;
  try {
    // 已发放的记录只能修改奖金和津贴
    const data = editItem.value.paid
      ? { bonus: editForm.value.bonus, allowance: editForm.value.allowance }
      : {
          year: editForm.value.year,
          month: editForm.value.month,
          basic_salary: editForm.value.basic_salary,
          bonus: editForm.value.bonus,
          allowance: editForm.value.allowance
        };

    const resp = await api.patch(`/salaries/${editItem.value.id}/`, data);

    if (resp.success) {
      // 更新本地数据
      const idx = records.value.findIndex(r => r.id === editItem.value.id);
      if (idx !== -1) {
        records.value[idx] = { ...records.value[idx], ...resp.data };
      }
      showMessage('success', '保存成功');
      closeEdit();
    } else {
      // 提取详细错误信息
      let errMsg = resp.error?.message || '保存失败';
      if (resp.error?.errors) {
        const errors = resp.error.errors;
        const msgs = [];
        for (const key in errors) {
          const val = errors[key];
          msgs.push(Array.isArray(val) ? val.join(', ') : val);
        }
        if (msgs.length) errMsg = msgs.join('; ');
      }
      showMessage('error', errMsg);
    }
  } catch (err) {
    showMessage('error', err.message || '保存失败');
  } finally {
    saving.value = false;
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
    const [salaryRes, empRes] = await Promise.all([
      api.get('/salaries/', { params: { page_size: 9999 } }),
      api.get('/employees/', { params: { page_size: 9999 } })
    ]);
    records.value = salaryRes.data.results || salaryRes.data || [];
    employeeOptions.value = (empRes.data.results || empRes.data || []).map(e => ({
      id: e.id,
      name: e.name,
      employee_id: e.employee_id || '-'
    }));

    // 默认显示上个月已发放 + 所有未发放（不设置筛选条件）
  } catch (err) {
    showMessage('error', '加载失败');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  load();
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// 当用户手动设置筛选条件时，关闭默认模式
watch([filterYear, filterMonth, filterStatus], ([year, month, status]) => {
  if (year || month || status) {
    showLastMonthAndUnpaid.value = false;
  }
});

// 重置筛选（恢复默认模式）
function resetFilters() {
  filterYear.value = '';
  filterMonth.value = '';
  filterStatus.value = '';
  filterEmployee.value = null;
  employeeSearchText.value = '';
  showLastMonthAndUnpaid.value = true;
  currentPage.value = 1;
}
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
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  border-radius: 8px;
}

.header-icon img {
  width: 20px;
  height: 20px;
  filter: brightness(0) invert(1);
}

.header-title {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-export {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-export:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-export:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-export svg {
  width: 16px;
  height: 16px;
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

.reset-filter-btn {
  margin-left: auto;
  padding: 0.5rem 1rem;
  font-size: 14px;
  color: #6b7280;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-filter-btn:hover {
  color: #374151;
  background: #f3f4f6;
  border-color: #9ca3af;
}

/* 表格容器 */
.table-container {
  position: relative;
  min-height: 200px;
  flex: 1;
}

/* 选择工具栏 */
.selection-toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: #eff6ff;
  border-bottom: 1px solid #bfdbfe;
  font-size: 14px;
  color: #1e40af;
}

.btn-text {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 14px;
  cursor: pointer;
  padding: 0;
}

.btn-text:hover {
  text-decoration: underline;
}

/* .data-table definition removed to use global style */
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

/* data-table td removed to use global style */

/* data-row:hover removed to use global style */

.data-row.row-selected {
  background: #eff6ff;
}

.data-row.row-selected:hover {
  background: #dbeafe;
}

/* 未发放记录高亮提示 */
.data-row.row-unpaid {
  background: linear-gradient(90deg, #fef3c7 0%, transparent 8%);
}

.data-row.row-unpaid:hover {
  background: linear-gradient(90deg, #fde68a 0%, #fafafa 8%);
}

.data-row.row-unpaid.row-selected {
  background: linear-gradient(90deg, #fde68a 0%, #eff6ff 8%);
}

/* 勾选框列 */
.col-checkbox {
  width: 40px;
  text-align: center;
  padding: 0 !important;
}

.data-table th.col-checkbox,
.data-table td.col-checkbox {
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
  background: var(--color-primary) !important;
  border-color: var(--color-primary) !important;
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
  background: var(--color-primary) !important;
  border-color: var(--color-primary) !important;
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

/* 列宽 */
.col-period { width: 120px; }
.col-base { width: 120px; }
.col-bonus { width: 100px; }
.col-allowance { width: 100px; }
.col-net { width: 130px; }
.col-status { width: 90px; }
.col-paid-at { width: 150px; }
.col-actions { width: 80px; }

.type-link {
  color: var(--color-primary);
  text-decoration: none;
}

.type-link:hover {
  text-decoration: underline;
}

.net-salary {
  font-weight: 600;
  color: #059669;
}

.status-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.status-paid {
  background: #d1fae5;
  color: #059669;
}

.status-badge.status-unpaid {
  background: #fef3c7;
  color: #d97706;
}

.action-link {
  color: var(--color-primary);
  text-decoration: none;
  font-size: 14px;
  margin-right: 16px;
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
  background: var(--color-primary);
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
  max-width: 480px;
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

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
}

.detail-value {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.detail-value.net {
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

/* 员工搜索 */
.employee-search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 120px;
  flex-shrink: 0;
}

.employee-search-input {
  width: 100%;
  padding: 0 2rem 0 0.75rem;
  height: 36px;
  line-height: normal;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 4px;
  font-size: 14px;
  color: #374151;
  background: #fff;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.employee-search-input:focus {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}

.employee-search-input::placeholder {
  color: #9ca3af;
}

.clear-employee-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 16px;
  color: #9ca3af;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.clear-employee-btn:hover {
  color: #374151;
}

.employee-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  min-width: 200px;
  max-height: 240px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1001;
  margin-top: 0;
}

.employee-option:hover {
  background: #f3f4f6;
}

.employee-option.active {
  background: var(--color-primary);
  color: #fff;
}

.employee-option .emp-name {
  font-weight: 500;
}

.employee-option .emp-id {
  font-size: 12px;
  color: #6b7280;
}

.employee-option.active .emp-id {
  color: rgba(255,255,255,0.8);
}

.no-result {
  padding: 0.75rem;
  font-size: 13px;
  color: #9ca3af;
  text-align: center;
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 员工列 */
.col-employee {
  width: 120px;
}

.employee-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}

.employee-link:hover {
  text-decoration: underline;
}

/* 编辑表单样式 */
.modal-edit {
  width: min(480px, 95vw);
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.edit-row {
  display: flex;
  align-items: center;
}

.edit-row-double {
  gap: 16px;
}

.edit-row-double .edit-field {
  flex: 1;
  display: flex;
  align-items: center;
}

.edit-label {
  width: 80px;
  min-width: 80px;
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.edit-value {
  flex: 1;
  font-size: 14px;
  color: #374151;
}

.edit-value.employee-name {
  padding: 8px 12px;
  background: #f3f4f6;
  border-radius: 6px;
  color: #6b7280;
}

.edit-input {
  flex: 1;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
  -moz-appearance: textfield;
  appearance: textfield;
}

.edit-input::-webkit-outer-spin-button,
.edit-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.edit-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: none;
}

.edit-textarea {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.edit-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: none;
}

.required {
  color: #ef4444;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--color-primary-hover);
}

.btn-primary:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

/* 发放薪资按钮 */
.btn-disburse {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--color-success, #16a34a);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--shadow-sm);
}

.btn-disburse:hover {
  background: #15803d; /* green-700 */
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.btn-disburse:active {
  transform: translateY(0);
}

.btn-disburse:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 选中记录后的发放按钮 - 保持绿色但加深，去掉突兀的橙色和动画 */
.btn-disburse-selected {
  background: var(--color-success, #16a34a);
  position: relative;
}

.btn-disburse-selected::after {
  content: '';
  position: absolute;
  top: -4px;
  right: -4px;
  width: 10px;
  height: 10px;
  background: var(--color-warning, #f59e0b);
  border: 2px solid white;
  border-radius: 50%;
}

/* 发放薪资弹窗 */
.modal-disburse {
  max-width: 520px;
}

.disburse-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.disburse-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.summary-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.summary-label {
  min-width: 80px;
  color: #64748b;
  font-size: 14px;
}

.summary-value {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.summary-value.total {
  font-size: 18px;
  color: #059669;
}

.summary-months {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.month-tag {
  padding: 4px 10px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-size: 13px;
}

.disburse-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.custom-radio-option {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.custom-radio-option:hover {
  border-color: var(--color-primary-light);
  background: var(--color-bg-hover);
}

.custom-radio-option.active {
  border-color: var(--color-primary);
  background: #eff6ff;
}

.radio-header {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.radio-content {
  margin-top: 12px;
  padding-left: 32px;
  width: 100%;
  box-sizing: border-box;
}

.radio-circle {
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.custom-radio-option.active .radio-circle {
  border-color: var(--color-primary);
  background: var(--color-primary);
}

.radio-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  opacity: 0;
  transform: scale(0);
  transition: all 0.2s;
}

.radio-dot.show {
  opacity: 1;
  transform: scale(1);
}

.hidden-radio {
  display: none;
}

.full-width-select {
  width: 100%;
}

.disburse-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  background: transparent;
  border: none;
  color: #9ca3af;
  font-size: 12px;
  transition: all 0.3s;
  margin-top: 8px;
}

.disburse-warning.warning-error {
  background: transparent;
  border: none;
  color: #ef4444;
}

.disburse-warning.warning-error svg {
  stroke: #ef4444;
}

.disburse-warning svg {
  flex-shrink: 0;
  stroke: #9ca3af;
}

.btn-confirm {
  background: var(--color-success, #16a34a);
  color: white;
  border: 1px solid transparent;
}

.btn-confirm:hover {
  background: #15803d; /* green-700 */
}

.btn-confirm:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  opacity: 0.7;
}
</style>
