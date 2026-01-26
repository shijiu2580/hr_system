<template>
  <div class="page-grid employees-page">
    <div class="card employees-card">
      <!-- 顶部标签栏 -->
      <div class="tab-header">
        <div class="tab-left">
          <div class="tab-icon">
            <img src="/icons/employees.svg" alt="" />
          </div>
          <div class="tab-nav">
            <router-link to="/employees/list" class="tab-btn active">
              员工列表
            </router-link>
          </div>
        </div>

        <div class="header-actions">
          <button v-if="isStaff" class="btn-secondary" @click="showImport = true">批量导入</button>
          <button class="btn-primary" @click="startCreate">新增员工</button>
          <button class="btn-secondary" @click="reload" :disabled="loading">{{ loading ? '刷新中...' : '刷新' }}</button>
        </div>
      </div>

      <!-- 批量导入弹窗 -->
      <ImportModal
        :show="showImport"
        title="批量导入员工"
        import-url="/api/import/employees/"
        template-type="employee"
        @close="showImport = false"
        @success="reload"
      />

      <!-- 错误提示 -->
      <transition name="fade">
        <div v-if="error" class="alert alert-error">
          <span class="alert-text">{{ error }}</span>
          <button type="button" class="alert-close" @click="error = ''">×</button>
        </div>
      </transition>

      <!-- 员工列表 -->
      <div v-if="activeTab === 'list'" class="tab-content">
        <!-- 筛选栏 -->
        <div class="filters-bar">
          <div class="filter-item filter-search">
            <span class="filter-label">关键字</span>
            <input
              v-model.trim="q"
              class="filter-input"
              placeholder="搜索姓名 / 工号 / 手机号"
              @keyup.enter="applyFilters"
            />
          </div>

          <div class="filter-item">
            <span class="filter-label">部门</span>
            <DeptTreeSelect
              v-model="department"
              :departments="departments"
              placeholder="全部"
              class="filter-custom-select"
              @change="applyFilters"
            />
          </div>

          <div class="filter-item">
            <span class="filter-label">职位</span>
            <CustomSelect
              v-model="position"
              :options="[{ value: '', label: '全部' }, ...positions.map(p => ({ value: p.id, label: p.name }))]"
              placeholder="全部"
              class="filter-custom-select"
              @change="applyFilters"
            />
          </div>

          <div class="filter-item">
            <span class="filter-label">状态</span>
            <CustomSelect
              v-model="active"
              :options="[{ value: '', label: '全部' }, { value: '1', label: '在职' }, { value: '0', label: '离职' }]"
              placeholder="全部"
              class="filter-custom-select"
              @change="applyFilters"
            />
          </div>

          <button class="btn-query" @click="applyFilters" :disabled="loading">查询</button>
          <button class="btn-reset" @click="resetFilters" :disabled="loading">重置</button>

          <button
            v-if="isStaff"
            class="btn-danger-outline"
            :disabled="selected.length === 0 || deleting"
            @click="batchDelete"
          >
            {{ deleting ? '删除中...' : `批量删除${selected.length ? `(${selected.length})` : ''}` }}
          </button>
        </div>

        <!-- 表格 -->
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-check">
                  <input
                    type="checkbox"
                    class="checkbox"
                    :checked="selectAll"
                    :indeterminate.prop="indeterminate"
                    @change="toggleSelectAll($event)"
                    :disabled="loading || !employees.length"
                  />
                </th>
                <th class="col-empid">工号</th>
                <th class="col-name">姓名</th>
                <th class="col-dept">部门</th>
                <th class="col-pos">职位</th>
                <th class="col-phone">手机号</th>
                <th class="col-location">考勤地点</th>
                <th class="col-hire">入职日期</th>
                <th class="col-status">状态</th>
                <th class="col-actions"><img src="/icons/setting.svg" class="settings-icon" alt="设置" /></th>
              </tr>
            </thead>
            <tbody v-if="!loading && employees.length">
              <tr
                v-for="e in employees"
                :key="e.id"
                class="data-row"
                :class="{ 'row-selected': selected.includes(e.id), 'row-inactive': !e.is_active }"
              >
                <td class="col-check">
                  <input type="checkbox" class="checkbox" v-model="selected" :value="e.id" />
                </td>
                <td class="col-empid">{{ e.employee_id || '--' }}</td>
                <td class="col-name">
                  <div class="name-cell">
                    <img v-if="e.avatar" :src="e.avatar" class="emp-avatar" alt="" />
                    <div v-else class="emp-avatar-placeholder" :style="{ background: getAvatarColor(e.id) }">{{ e.name?.charAt(0) || '?' }}</div>
                    <router-link :to="`/employees/${e.id}`" class="name-link">{{ e.name || '--' }}</router-link>
                  </div>
                </td>
                <td class="col-dept">{{ e.department?.name || '--' }}</td>
                <td class="col-pos">{{ e.position?.name || '--' }}</td>
                <td class="col-phone">{{ e.phone || '--' }}</td>
                <td class="col-location">
                  <span v-if="e.checkin_locations && e.checkin_locations.length" class="location-tags">
                    <span v-for="loc in e.checkin_locations" :key="loc.id" class="location-tag">{{ loc.name }}</span>
                  </span>
                  <span v-else class="text-muted">--</span>
                </td>
                <td class="col-hire">{{ e.hire_date || '--' }}</td>
                <td class="col-status">
                  <span class="status-text" :class="e.is_active ? 'status-active' : 'status-inactive'">
                    {{ e.is_active ? '在职' : '离职' }}
                  </span>
                </td>
                <td class="col-actions">
                  <div class="row-actions">
                    <button class="action-btn" @click="startEdit(e)">编辑</button>
                    <button class="action-btn" @click="openLocationModal(e)">关联地点</button>
                    <button class="action-btn danger" @click="deleteOne(e)" :disabled="deleting">删除</button>
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
          <div v-if="!loading && !employees.length" class="empty-state">暂无员工数据</div>

          <!-- 进度条 -->
          <div class="progress-bar" v-if="loading">
            <div class="progress-fill"></div>
          </div>
        </div>

        <!-- 底部统计和分页 -->
        <div class="table-footer">
          <span class="total-count">共{{ totalCount }}条</span>
          <div class="pagination">
            <span class="page-size-label">每页</span>
            <CustomSelect
              v-model="pageSize"
              :options="pageSizeSelectOptions"
              class="page-size-custom-select"
              :dropUp="true"
              @change="onPageSizeChange"
            />
            <span class="page-size-label">条</span>
            <button class="page-btn" :disabled="page <= 1" @click="goToPage(1)">«</button>
            <button class="page-btn" :disabled="page <= 1" @click="goToPage(page - 1)">‹</button>
            <span class="page-info">{{ page }} / {{ totalPages }}</span>
            <button class="page-btn" :disabled="page >= totalPages" @click="goToPage(page + 1)">›</button>
            <button class="page-btn" :disabled="page >= totalPages" @click="goToPage(totalPages)">»</button>
          </div>
        </div>
      </div>

      <!-- 导入说明 -->
      <div v-if="activeTab === 'import'" class="tab-content import-panel">
        <div class="import-card">
          <div class="import-title">批量导入员工</div>
          <div class="import-desc">下载模板后填充数据，再上传导入。</div>
          <button class="btn-primary" @click="showImport = true">打开导入弹窗</button>
        </div>
      </div>
    </div>

    <!-- 关联考勤地点弹窗 -->
    <div v-if="showLocationModal" class="modal-overlay" @click.self="closeLocationModal">
      <div class="modal-content modal-medium">
        <div class="modal-header">
          <h3>关联考勤地点 - {{ currentEmployee?.name }}</h3>
          <button class="modal-close" @click="closeLocationModal">×</button>
        </div>
        <div class="modal-body">
          <div v-if="locationsLoading" class="loading-dots">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
          <div v-else-if="allLocations.length === 0" class="empty-hint">
            暂无考勤地点，请先在考勤地点页面添加
          </div>
          <div v-else class="location-list">
            <label
              v-for="loc in allLocations"
              :key="loc.id"
              class="location-item"
              :class="{ disabled: !loc.is_active }"
            >
              <input
                type="checkbox"
                v-model="selectedLocationIds"
                :value="loc.id"
                :disabled="!loc.is_active"
              />
              <span class="location-name">{{ loc.name }}</span>
              <span v-if="loc.is_default" class="location-default">默认</span>
              <span v-if="!loc.is_active" class="location-inactive">已停用</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeLocationModal">取消</button>
          <button class="btn-primary" @click="saveLocations" :disabled="savingLocations">
            {{ savingLocations ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'
import DeptTreeSelect from '../../components/DeptTreeSelect.vue'
import ImportModal from '../../components/ImportModal.vue'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const isStaff = computed(() => !!(authStore.user?.is_staff || authStore.user?.is_superuser))

const activeTab = ref('list')

const employees = ref([])
const departments = ref([])
const positions = ref([])

const loading = ref(false)
const error = ref('')
const showImport = ref(false)

// 关联考勤地点
const showLocationModal = ref(false)
const currentEmployee = ref(null)
const allLocations = ref([])
const selectedLocationIds = ref([])
const locationsLoading = ref(false)
const savingLocations = ref(false)

// filters
const q = ref('')
const department = ref('')
const position = ref('')
const active = ref('')

// pagination
const page = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const pageSizeSelectOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' },
]

const totalPages = computed(() => {
  const t = Math.ceil((totalCount.value || 0) / (pageSize.value || 20))
  return t || 1
})

// selection
const selected = ref([])
const deleting = ref(false)

const selectAll = computed(() => employees.value.length > 0 && selected.value.length === employees.value.length)
const indeterminate = computed(() => selected.value.length > 0 && selected.value.length < employees.value.length)

function toggleSelectAll(e) {
  const checked = e?.target?.checked
  if (checked) {
    selected.value = employees.value.map(x => x.id)
  } else {
    selected.value = []
  }
}

watch(employees, () => {
  // 当翻页/筛选导致列表变化，移除不存在的已选项
  const ids = new Set(employees.value.map(x => x.id))
  selected.value = selected.value.filter(id => ids.has(id))
})

async function loadMeta() {
  const [d, p] = await Promise.all([api.get('/departments/'), api.get('/positions/')])
  if (d.success) departments.value = d.data?.results || d.data || []
  if (p.success) positions.value = p.data?.results || p.data || []
}

async function loadEmployees() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (q.value) params.q = q.value
    if (department.value) params.department = department.value
    if (position.value) params.position = position.value
    if (active.value !== '') params.active = active.value

    const res = await api.get('/employees/', { params })
    if (!res.success) {
      error.value = res.error?.message || '加载失败'
      employees.value = []
      totalCount.value = 0
      return
    }

    const data = res.data
    employees.value = data?.results || data || []
    totalCount.value = data?.count ?? employees.value.length
  } catch (e) {
    error.value = '加载失败'
  } finally {
    loading.value = false
  }
}

function startCreate() {
  router.push('/employees/create')
}

function startEdit(emp) {
  router.push(`/employees/${emp.id}/edit`)
}

async function deleteOne(emp) {
  if (!isStaff.value) return
  const ok = window.confirm(`确定删除 ${emp.employee_id || ''} ${emp.name || ''} 吗？此操作不可撤销。`)
  if (!ok) return

  deleting.value = true
  error.value = ''
  try {
    const res = await api.delete(`/employees/${emp.id}/`)
    if (!res.success) throw new Error(res.error?.message || '删除失败')
    await loadEmployees()
  } catch (e) {
    error.value = e.message || '删除失败'
  } finally {
    deleting.value = false
  }
}

async function batchDelete() {
  if (!isStaff.value) return
  if (!selected.value.length) return

  const ok = window.confirm(`确定删除选中的 ${selected.value.length} 个员工吗？此操作不可撤销。`)
  if (!ok) return

  deleting.value = true
  error.value = ''
  try {
    for (const id of selected.value) {
      const res = await api.delete(`/employees/${id}/`)
      if (!res.success) {
        throw new Error(res.error?.message || '批量删除失败')
      }
    }
    selected.value = []
    await loadEmployees()
  } catch (e) {
    error.value = e.message || '批量删除失败'
  } finally {
    deleting.value = false
  }
}

function applyFilters() {
  page.value = 1
  selected.value = []
  loadEmployees()
}

function resetFilters() {
  q.value = ''
  department.value = ''
  position.value = ''
  active.value = ''
  applyFilters()
}

function goToPage(p) {
  const next = Math.min(Math.max(1, p), totalPages.value)
  if (next === page.value) return
  page.value = next
  selected.value = []
  loadEmployees()
}

function onPageSizeChange() {
  page.value = 1
  selected.value = []
  loadEmployees()
}

function reload() {
  selected.value = []
  loadEmployees()
  loadMeta()
}

// 关联考勤地点相关函数
async function openLocationModal(emp) {
  currentEmployee.value = emp
  selectedLocationIds.value = emp.checkin_location_ids || []
  showLocationModal.value = true
  await loadAllLocations()
}

function closeLocationModal() {
  showLocationModal.value = false
  currentEmployee.value = null
  selectedLocationIds.value = []
}

async function loadAllLocations() {
  locationsLoading.value = true
  try {
    const resp = await api.get('/checkin-locations/')
    if (resp.success) {
      allLocations.value = resp.data.results || resp.data || []
    }
  } catch (e) {
    console.error('加载考勤地点失败', e)
  } finally {
    locationsLoading.value = false
  }
}

async function saveLocations() {
  if (!currentEmployee.value) return
  savingLocations.value = true
  try {
    const resp = await api.patch(`/employees/${currentEmployee.value.id}/`, {
      checkin_location_ids: selectedLocationIds.value
    })
    if (resp.success) {
      // 更新本地数据
      const emp = employees.value.find(e => e.id === currentEmployee.value.id)
      if (emp) {
        emp.checkin_location_ids = selectedLocationIds.value
        emp.checkin_locations = allLocations.value
          .filter(loc => selectedLocationIds.value.includes(loc.id))
          .map(loc => ({ id: loc.id, name: loc.name }))
      }
      closeLocationModal()
    } else {
      error.value = resp.error?.message || '保存失败'
    }
  } catch (e) {
    error.value = e.message || '保存失败'
  } finally {
    savingLocations.value = false
  }
}

// 头像颜色
const avatarColors = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
]
function getAvatarColor(id) {
  return avatarColors[(id || 0) % avatarColors.length]
}

onMounted(async () => {
  await Promise.all([loadMeta(), loadEmployees()])
})
</script>

<style scoped>
.page-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
}

.employees-page {
  padding: 1.2rem;
}

.card {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
  padding: 1rem 1.1rem;
}

/* 顶部标签栏 */
.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 0.9rem;
}

.tab-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.tab-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-icon img {
  width: 24px;
  height: 24px;
}

.tab-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-btn {
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: #fff;
  color: #374151;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
  text-decoration: none;
}

.tab-btn:hover {
  background: #f3f4f6;
}

.tab-btn.active {
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  color: #1e293b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background: #f1f5f9;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 错误提示 */
.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  margin-bottom: 0.8rem;
}

.alert-error {
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #7f1d1d;
}

.alert-text {
  flex: 1;
  font-size: 13px;
}

.alert-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: inherit;
}

/* 筛选栏（同考勤管理风格） */
.filters-bar {
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.9rem;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.filter-label {
  font-size: 12px;
  color: #6b7280;
}

.filter-input {
  padding: 0 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  background: #fff;
  font-size: 14px;
  width: 180px;
  height: 36px;
  box-sizing: border-box;
  outline: none;
  transition: all 0.2s ease;
}

.filter-input:hover,
.filter-input:focus {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
  outline: none;
  box-shadow: none;
}

.filter-custom-select {
  min-width: 140px;
}

.filter-custom-select :deep(.select-trigger) {
  padding: 0 0.75rem;
  padding-right: 2rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  background: #fff;
  transition: all 0.2s ease;
}

.filter-custom-select :deep(.select-trigger:hover) {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}

.filter-custom-select :deep(.select-trigger:focus),
.filter-custom-select :deep(.custom-select.open .select-trigger) {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}

.filter-custom-select :deep(.select-value) {
  font-size: 14px;
  color: #1e293b;
}

.filter-custom-select :deep(.select-arrow) {
  color: #64748b;
}

.filter-custom-select :deep(.select-dropdown) {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 0.35rem 0;
}

.filter-custom-select :deep(.select-option) {
  padding: 0.5rem 0.75rem;
  border-radius: 0;
  font-size: 13px;
  color: #374151;
  transition: background 0.15s;
}

.filter-custom-select :deep(.select-option:hover),
.filter-custom-select :deep(.select-option.highlighted) {
  background: #f1f5f9;
  color: #1e293b;
}

.filter-custom-select :deep(.select-option.selected) {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

.filter-custom-select :deep(.select-option.selected::before) {
  display: none;
}

.btn-query,
.btn-reset {
  padding: 0.5rem 0.9rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: transparent;
  color: #1e293b;
  height: 36px;
}

.btn-query:hover:not(:disabled),
.btn-reset:hover:not(:disabled) {
  background: #f1f5f9;
}

.btn-query:disabled,
.btn-reset:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger-outline {
  margin-left: auto;
  padding: 0.5rem 0.9rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  border: 1px solid #dc2626;
  color: #dc2626;
  background: transparent;
  height: 36px;
}

.btn-danger-outline:hover:not(:disabled) {
  background: #fee2e2;
}

.btn-danger-outline:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 表格（同考勤管理风格） */
.table-wrapper {
  position: relative;
  min-height: 320px;
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

.data-row.row-inactive {
  opacity: 0.78;
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

.name-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.emp-avatar {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.emp-avatar-placeholder {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.name-link {
  color: #2563eb;
  text-decoration: none;
}

.name-link:hover {
  text-decoration: underline;
}

.status-text {
  font-weight: 500;
}

.status-active {
  color: #059669;
}

.status-inactive {
  color: #dc2626;
}

.settings-icon {
  width: 18px;
  height: 18px;
  color: #9ca3af;
  cursor: default;
  vertical-align: middle;
}

.row-actions {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.35rem 0.6rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #fff;
  color: #374151;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  background: #f3f4f6;
}

.action-btn.danger {
  border-color: #fca5a5;
  color: #dc2626;
}

.action-btn.danger:hover {
  background: #fee2e2;
}

/* 加载/空状态 */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #9ca3af;
}

.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: #e5e7eb;
}

.progress-fill {
  height: 100%;
  width: 30%;
  background: #2563eb;
  animation: loading 1s ease-in-out infinite;
}

@keyframes loading {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(400%);
  }
}

/* 底部统计和分页 */
.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
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
  background: #f8fafc;
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
  font-size: 13px;
  color: #6b7280;
  min-width: 60px;
  text-align: center;
}

/* 导入页 */
.import-panel {
  padding: 1rem 0;
}

.import-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.2rem;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-width: 520px;
}

.import-title {
  font-weight: 600;
  color: #111827;
}

.import-desc {
  color: #6b7280;
  font-size: 13px;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* 考勤地点列 */
.col-location {
  min-width: 120px;
}

.location-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.location-tag {
  display: inline-block;
  padding: 2px 8px;
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 4px;
  font-size: 12px;
}

.text-muted {
  color: #9ca3af;
}

/* 关联地点弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 16px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

.modal-content.modal-medium {
  width: min(500px, 96vw);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eef2f7;
  background: #f8fafc;
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 22px;
  cursor: pointer;
  color: #64748b;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eef2f7;
  background: #fafafa;
}

.btn-cancel {
  padding: 8px 20px;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.empty-hint {
  text-align: center;
  color: #9ca3af;
  padding: 40px 20px;
}

.location-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.location-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.location-item:hover:not(.disabled) {
  background: #f8fafc;
  border-color: #2563eb;
}

.location-item.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.location-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #2563eb;
  outline: none;
}

.location-item input[type="checkbox"]:focus {
  outline: none;
  box-shadow: none;
}

.location-item.disabled input[type="checkbox"] {
  cursor: not-allowed;
}

.location-name {
  flex: 1;
  font-size: 14px;
  color: #374151;
}

.location-default {
  padding: 2px 8px;
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 4px;
  font-size: 12px;
}

.location-inactive {
  padding: 2px 8px;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 4px;
  font-size: 12px;
}
</style>
