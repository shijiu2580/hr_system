<template>
  <div class="page-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <img src="/icons/employees.svg" alt="" />
        </div>
        <span class="header-title">员工列表</span>
      </div>
      <div class="header-right">
        <div class="stat-badges">
          <span class="stat-badge">
            <span class="stat-value">{{ summary.total }}</span>
            <span class="stat-label">总人数</span>
          </span>
          <span class="stat-badge active">
            <span class="stat-value">{{ summary.activeCount }}</span>
            <span class="stat-label">在职</span>
          </span>
        </div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filters-bar">
      <div class="filter-item">
        <input v-model="searchKeyword" type="text" placeholder="搜索姓名、工号、手机号" class="filter-input" @keyup.enter="applyFilters" />
      </div>
      <DeptTreeSelect
        v-model="filterDept"
        :departments="departments"
        placeholder="全部部门"
        class="filter-dropdown"
      />
      <CustomSelect
        v-model="filterPosition"
        :options="[{ value: '', label: '全部职位' }, ...positions.map(p => ({ value: p.id, label: p.name }))]"
        placeholder="全部职位"
        class="filter-dropdown"
      />
      <CustomSelect
        v-model="filterStatus"
        :options="[{ value: '', label: '全部状态' }, { value: '1', label: '在职' }, { value: '0', label: '离职' }]"
        placeholder="全部状态"
        class="filter-dropdown"
      />
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-name">员工姓名</th>
            <th class="col-id">工号</th>
            <th class="col-dept">部门</th>
            <th class="col-position">职位</th>
            <th class="col-phone">联系电话</th>
            <th class="col-hire-date sortable" @click="toggleSort('hire_date')">
              <span class="th-text">入职日期</span>
              <span class="sort-icon" :class="{ active: sortField === 'hire_date', desc: sortField === 'hire_date' && sortOrder === 'desc' }">
                <img src="/icons/up_down.svg" />
              </span>
            </th>
            <th class="col-status">状态</th>
            <th class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody v-if="!loading && paged.length">
          <tr v-for="item in paged" :key="item.id" class="data-row">
            <td class="col-name">
              <div class="employee-cell">
                <img v-if="item.avatar" :src="item.avatar" class="avatar avatar-img" alt="" />
                <div v-else class="avatar" :style="{ background: getAvatarColor(item.id) }">
                  {{ item.name?.charAt(0) || '?' }}
                </div>
                <router-link :to="`/employees/${item.id}`" class="employee-link">
                  {{ item.name || '-' }}
                </router-link>
              </div>
            </td>
            <td class="col-id">
              <span class="emp-id-text">{{ item.employee_id || '-' }}</span>
            </td>
            <td class="col-dept">
              <span class="dept-badge" v-if="item.department">{{ item.department.name }}</span>
              <span class="text-muted" v-else>未分配</span>
            </td>
            <td class="col-position">
              <span class="position-text">{{ item.position?.name || '-' }}</span>
            </td>
            <td class="col-phone">{{ item.phone || '-' }}</td>
            <td class="col-hire-date">{{ item.hire_date || '-' }}</td>
            <td class="col-status">
              <span class="status-badge" :class="getStatusClass(item)">
                {{ getStatusText(item) }}
              </span>
            </td>
            <td class="col-actions">
              <router-link :to="`/employees/${item.id}`" class="action-link">查看</router-link>
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
        暂无员工数据
      </div>
    </div>

    <!-- 底部分页 -->
    <div class="table-footer">
      <span class="total-count">共{{ filtered.length }}人</span>
      <div class="pagination">
        <span class="page-size-label">每页</span>
        <CustomSelect
          v-model="pageSize"
          :options="pageSizeOptions"
          class="page-size-custom-select"
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

    <!-- Toast 提示 -->
    <teleport to="body">
      <transition name="toast">
        <div v-if="message" class="toast" :class="`toast-${message.type}`">
          <span>{{ message.text }}</span>
          <button @click="message = null" class="toast-close">×</button>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'
import DeptTreeSelect from '../../components/DeptTreeSelect.vue'

const loading = ref(false)
const message = ref(null)
const employees = ref([])
const departments = ref([])
const positions = ref([])

const searchKeyword = ref('')
const filterDept = ref('')

const filterPosition = ref('')
const filterStatus = ref('')
const pageSize = ref(20)
const currentPage = ref(1)
const pageSizeOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' }
]

// 排序
const sortField = ref('')
const sortOrder = ref('desc')

function toggleSort(field) {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'desc'
  }
}

// 头像颜色
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

// 状态显示
function getStatusClass(item) {
  if (item.onboard_status === 'pending') return 'status-pending'
  return item.is_active ? 'status-active' : 'status-inactive'
}

function getStatusText(item) {
  if (item.onboard_status === 'pending') return '待入职'
  return item.is_active ? '在职' : '离职'
}

// 统计
const summary = computed(() => {
  const total = employees.value.length
  const activeCount = employees.value.filter(e => e.is_active).length
  return { total, activeCount }
})

// 筛选
const filtered = computed(() => {
  let list = employees.value

  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter(e =>
      e.name?.toLowerCase().includes(kw) ||
      e.employee_id?.toLowerCase().includes(kw) ||
      e.phone?.includes(kw)
    )
  }

  if (filterDept.value) {
    // 获取选中部门及其所有子部门的ID
    const deptIds = new Set([Number(filterDept.value)])
    // 递归添加子部门
    function addChildDepts(parentId) {
      departments.value.forEach(d => {
        const pId = d.parent?.id || d.parent
        if (pId === parentId && !deptIds.has(d.id)) {
          deptIds.add(d.id)
          addChildDepts(d.id)
        }
      })
    }
    addChildDepts(Number(filterDept.value))
    list = list.filter(e => deptIds.has(e.department?.id))
  }

  if (filterPosition.value) {
    list = list.filter(e => e.position?.id == filterPosition.value)
  }

  if (filterStatus.value !== '') {
    const isActive = filterStatus.value === '1'
    list = list.filter(e => e.is_active === isActive)
  }

  // 排序
  if (sortField.value) {
    list = [...list].sort((a, b) => {
      let aVal = a[sortField.value] || ''
      let bVal = b[sortField.value] || ''
      if (sortOrder.value === 'asc') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })
  }

  return list
})

const totalPages = computed(() => Math.ceil(filtered.value.length / pageSize.value) || 1)

const paged = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filtered.value.slice(start, start + pageSize.value)
})

function applyFilters() {
  currentPage.value = 1
}

function goToPage(page) {
  currentPage.value = page
}

async function loadData() {
  loading.value = true
  try {
    const [empRes, deptRes, posRes] = await Promise.all([
      api.get('/employees/'),
      api.get('/departments/'),
      api.get('/positions/')
    ])
    employees.value = empRes.data?.results || empRes.data || []
    departments.value = deptRes.data?.results || deptRes.data || []
    positions.value = posRes.data?.results || posRes.data || []
  } catch (e) {
    message.value = { type: 'error', text: '加载数据失败' }
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  min-height: 100vh;
  background: #f8fafc;
  box-sizing: border-box;
}

/* 顶部标题栏 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon img {
  width: 24px;
  height: 24px;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-badges {
  display: flex;
  gap: 0.75rem;
}

.stat-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.4rem 0.75rem;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.stat-badge.active {
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  border-color: #a7f3d0;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.stat-badge.active .stat-value {
  color: #059669;
}

.stat-label {
  font-size: 11px;
  color: #64748b;
}

/* 筛选栏 */
.filters-bar {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.filter-item {
  width: 200px;
  flex-shrink: 0;
}

.filter-input {
  width: 100%;
  padding: 0 0.75rem;
  padding-right: 2.2rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  background: #fff;
  font-size: 14px;
  color: #1e293b;
  outline: none;
  transition: all 0.2s ease;
  box-sizing: border-box;
  height: 36px;
}

.filter-input::placeholder {
  color: #94a3b8;
}

.filter-input:hover,
.filter-input:focus {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
  outline: none;
  box-shadow: none;
}

.filter-dropdown {
  width: 120px;
  flex-shrink: 0;
}

/* CustomSelect 统一样式 */
.filter-dropdown :deep(.select-trigger) {
  padding: 0 0.75rem;
  padding-right: 2rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  background: #fff;
  transition: all 0.2s ease;
}
.filter-dropdown :deep(.select-trigger:hover) {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}
.filter-dropdown :deep(.custom-select.open .select-trigger),
.filter-dropdown :deep(.select-trigger:focus) {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}
.filter-dropdown :deep(.select-value) {
  font-size: 14px;
  color: #1e293b;
}
.filter-dropdown :deep(.select-arrow) {
  color: #64748b;
}
.filter-dropdown :deep(.select-dropdown) {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 0.35rem 0;
}
.filter-dropdown :deep(.select-option) {
  padding: 0.5rem 0.75rem;
  font-size: 13px;
  color: #374151;
  transition: background 0.15s;
}
.filter-dropdown :deep(.select-option:hover),
.filter-dropdown :deep(.select-option.highlighted) {
  background: #f1f5f9;
  color: #1e293b;
}
.filter-dropdown :deep(.select-option.selected) {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

/* 表格容器 */
.table-container {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: #f8fafc;
}

.data-table th {
  padding: 0.85rem 1rem;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  color: #334155;
}

.th-text {
  margin-right: 4px;
}

.sort-icon {
  display: inline-flex;
  width: 12px;
  height: 12px;
  color: #cbd5e1;
  transition: transform 0.2s;
}

.sort-icon img {
  width: 100%;
  height: 100%;
}

.sort-icon.desc {
  transform: rotate(180deg);
}

.sort-icon.active {
  color: #0ea5e9;
}

.data-table td {
  padding: 0.85rem 1rem;
  font-size: 14px;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
}

.data-row:hover td {
  background: #f8fafc;
}

/* 列宽 */
.col-name { min-width: 160px; }
.col-id { min-width: 100px; }
.col-dept { min-width: 120px; }
.col-position { min-width: 100px; }
.col-phone { min-width: 120px; }
.col-hire-date { min-width: 110px; }
.col-status { min-width: 80px; }
.col-actions { min-width: 80px; }

/* 员工单元格 */
.employee-cell {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.avatar-img {
  object-fit: cover;
}

.employee-link {
  color: #0ea5e9;
  text-decoration: none;
  font-weight: 500;
}

.employee-link:hover {
  text-decoration: underline;
}

.emp-id-text {
  color: #64748b;
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 13px;
}

/* 部门徽章 */
.dept-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  background: #f0f9ff;
  color: #0284c7;
  border-radius: 4px;
  font-size: 12px;
}

.position-text {
  color: #475569;
}

.text-muted {
  color: #94a3b8;
}

/* 状态徽章 */
.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-active {
  background: #dcfce7;
  color: #16a34a;
}

.status-inactive {
  background: #fee2e2;
  color: #dc2626;
}

.status-pending {
  background: #fef3c7;
  color: #d97706;
}

/* 操作链接 */
.action-link {
  color: #0ea5e9;
  text-decoration: none;
  font-size: 13px;
}

.action-link:hover {
  text-decoration: underline;
}

/* 加载状态 */
.loading-state {
  padding: 2rem;
}

.progress-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  width: 30%;
  background: linear-gradient(90deg, #38bdf8, #0ea5e9);
  animation: loading 1s ease-in-out infinite;
}

@keyframes loading {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}

/* 空状态 */
.empty-state {
  padding: 3rem;
  text-align: center;
  color: #94a3b8;
}

/* 底部分页 */
.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.total-count {
  font-size: 13px;
  color: #64748b;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-size-label {
  font-size: 13px;
  color: #64748b;
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
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #64748b;
}

.page-btn:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #475569;
  min-width: 60px;
  text-align: center;
}

/* Toast */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-width: 400px;
}

.toast-success { color: #059669; }
.toast-error { color: #dc2626; }

.toast-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: inherit;
  opacity: 0.6;
}

.toast-close:hover { opacity: 1; }

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
