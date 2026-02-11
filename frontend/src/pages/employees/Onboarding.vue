<template>
  <div class="page-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <img src="/icons/employees.svg" alt="" />
        </div>
        <span class="header-title">入职审核</span>
      </div>
      <div class="header-right">
        <div class="stat-badges">
          <span class="stat-badge" :class="{ active: pendingCount > 0 }">
            <span class="stat-value">{{ pendingCount }}</span>
            <span class="stat-label">待审核</span>
          </span>
          <span class="stat-badge">
            <span class="stat-value">{{ filtered.length }}</span>
            <span class="stat-label">当前列表</span>
          </span>
        </div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filters-bar">
      <div class="filter-item">
        <input v-model="searchKeyword" type="text" placeholder="搜索姓名、工号、手机号" class="filter-input" @keyup.enter="currentPage = 1" />
      </div>
      <CustomSelect
        v-model="statusFilter"
        :options="statusOptions"
        placeholder="审核状态"
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
            <th class="col-phone">手机号</th>
            <th class="col-email">邮箱</th>
            <th class="col-status">状态</th>
            <th class="col-date">注册时间</th>
            <th class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody v-if="!loading && paged.length">
          <tr v-for="item in paged" :key="item.id" class="data-row">
            <td class="col-name">
              <div class="employee-cell">
                <div class="avatar" v-if="item.avatar">
                  <img :src="item.avatar" alt="" />
                </div>
                <div class="avatar" v-else :style="{ background: getAvatarColor(item.id) }">
                  {{ item.name?.charAt(0) || '?' }}
                </div>
                <span class="employee-name">{{ item.name || '-' }}</span>
              </div>
            </td>
            <td class="col-id">
              <span class="emp-id-text">{{ item.employee_id || '-' }}</span>
            </td>
            <td class="col-phone">{{ item.phone || '-' }}</td>
            <td class="col-email">{{ item.email || '-' }}</td>
            <td class="col-status">
              <span class="status-badge" :class="getStatusClass(item.onboard_status)">
                {{ getStatusText(item.onboard_status) }}
              </span>
            </td>
            <td class="col-date">{{ formatDate(item.created_at) }}</td>
            <td class="col-actions">
              <button class="action-link" @click="viewDetail(item)">查看</button>
              <template v-if="item.onboard_status === 'pending'">
                <button class="action-link action-success" @click="approveOnboard(item)">通过</button>
                <button class="action-link action-danger" @click="rejectOnboard(item)">拒绝</button>
              </template>
              <button class="action-link action-danger" @click="deleteEmployee(item)">删除</button>
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

    <!-- 查看资料弹窗 -->
    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="detailVisible" class="modal-overlay" @click.self="detailVisible = false">
          <div class="modal-container modal-large">
            <header class="modal-header">
              <h3>员工资料详情</h3>
              <button class="close-btn" @click="detailVisible = false">×</button>
            </header>
            <div class="modal-body" v-if="currentEmployee">
              <div class="detail-section">
                <h4 class="section-title">基本信息</h4>
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="label">员工编号</span>
                    <span class="value">{{ currentEmployee.employee_id || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">姓名</span>
                    <span class="value">{{ currentEmployee.name || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">英文名</span>
                    <span class="value">{{ currentEmployee.english_name || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">性别</span>
                    <span class="value">{{ currentEmployee.gender === 'M' ? '男' : currentEmployee.gender === 'F' ? '女' : '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">出生日期</span>
                    <span class="value">{{ currentEmployee.birth_date || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">手机号</span>
                    <span class="value">{{ currentEmployee.phone || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">邮箱</span>
                    <span class="value">{{ currentEmployee.email || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">身份证号</span>
                    <span class="value">{{ currentEmployee.id_card || '-' }}</span>
                  </div>

                  <div class="detail-item">
                    <span class="label">婚姻状况</span>
                    <span class="value">{{ maritalMap[currentEmployee.marital_status] || '-' }}</span>
                  </div>
                </div>
              </div>

              <div class="detail-section">
                <h4 class="section-title">户籍信息</h4>
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="label">国籍</span>
                    <span class="value">{{ currentEmployee.nationality || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">民族</span>
                    <span class="value">{{ currentEmployee.ethnicity || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">籍贯</span>
                    <span class="value">{{ currentEmployee.native_place || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">户籍所在地</span>
                    <span class="value">{{ currentEmployee.hukou_location || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">户籍性质</span>
                    <span class="value">{{ currentEmployee.hukou_type || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">政治面貌</span>
                    <span class="value">{{ currentEmployee.political_status || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">血型</span>
                    <span class="value">{{ currentEmployee.blood_type || '-' }}</span>
                  </div>
                </div>
              </div>

              <div class="detail-section">
                <h4 class="section-title">学历信息</h4>
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="label">学历</span>
                    <span class="value">{{ currentEmployee.education || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">毕业学校</span>
                    <span class="value">{{ currentEmployee.school_name || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">专业</span>
                    <span class="value">{{ currentEmployee.major || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">毕业时间</span>
                    <span class="value">{{ currentEmployee.graduation_date || '-' }}</span>
                  </div>
                </div>
              </div>

              <div class="detail-section">
                <h4 class="section-title">联系信息</h4>
                <div class="detail-grid">
                  <div class="detail-item full-width">
                    <span class="label">联系地址</span>
                    <span class="value">{{ currentEmployee.address || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">紧急联系人</span>
                    <span class="value">{{ currentEmployee.emergency_contact || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">紧急联系电话</span>
                    <span class="value">{{ currentEmployee.emergency_phone || '-' }}</span>
                  </div>
                </div>
              </div>

              <div class="detail-section" v-if="currentEmployee.avatar">
                <h4 class="section-title">照片</h4>
                <div class="avatar-preview">
                  <img :src="currentEmployee.avatar" alt="头像" />
                </div>
              </div>
            </div>
            <footer class="modal-footer">
              <button class="btn-ghost" @click="detailVisible = false">关闭</button>
              <template v-if="currentEmployee?.onboard_status === 'pending'">
                <button class="btn-danger" @click="rejectOnboard(currentEmployee)">拒绝</button>
                <button class="btn-primary" @click="approveOnboard(currentEmployee)">通过审核</button>
              </template>
            </footer>
          </div>
        </div>
      </transition>
    </Teleport>

    <!-- 拒绝原因弹窗 -->
    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="rejectVisible" class="modal-overlay" @click.self="rejectVisible = false">
          <div class="modal-container modal-small">
            <header class="modal-header">
              <h3>拒绝入职</h3>
              <button class="close-btn" @click="rejectVisible = false">×</button>
            </header>
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label">拒绝原因 <span class="required">*</span></label>
                <textarea
                  v-model="rejectReason"
                  class="form-textarea"
                  rows="3"
                  placeholder="请输入拒绝原因"
                ></textarea>
              </div>
            </div>
            <footer class="modal-footer">
              <button class="btn-ghost" @click="rejectVisible = false">取消</button>
              <button class="btn-danger" @click="confirmReject">确认拒绝</button>
            </footer>
          </div>
        </div>
      </transition>
    </Teleport>

    <!-- 审核通过弹窗 -->
    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="approveVisible" class="modal-overlay" @click.self="approveVisible = false">
          <div class="modal-container">
            <header class="modal-header">
              <h3>审核通过 - 分配信息</h3>
              <button class="close-btn" @click="approveVisible = false">×</button>
            </header>
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label">部门 <span class="required">*</span></label>
                <DeptTreeSelect
                  v-model="approveForm.department_id"
                  :departments="departments"
                  placeholder="请选择部门"
                  class="form-dept-tree-select"
                />
              </div>
              <div class="form-group">
                <label class="form-label">职位 <span class="required">*</span></label>
                <CustomSelect
                  v-model="approveForm.position_id"
                  :options="positionOptions"
                  class="form-custom-select"
                />
              </div>
              <div class="form-group">
                <label class="form-label">入职日期 <span class="required">*</span></label>
                <input v-model="approveForm.hire_date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">基本工资</label>
                <input v-model.number="approveForm.salary" type="number" class="form-input" placeholder="可选" />
              </div>
            </div>
            <footer class="modal-footer">
              <button class="btn-ghost" @click="approveVisible = false">取消</button>
              <button class="btn-primary" @click="confirmApprove">确认入职</button>
            </footer>
          </div>
        </div>
      </transition>
    </Teleport>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="deleteVisible" class="modal-overlay" @click.self="deleteVisible = false">
          <div class="modal-container modal-small">
            <header class="modal-header">
              <h3>确认删除</h3>
              <button class="close-btn" @click="deleteVisible = false">×</button>
            </header>
            <div class="modal-body">
              <p style="color: #dc2626; margin: 0;">
                确定要删除员工 <strong>{{ deleteTarget?.name }}</strong> 吗？
              </p>
              <p style="color: #64748b; font-size: 13px; margin: 12px 0 0;">
                删除后，该员工的账号将被注销，其使用的邮箱可重新注册。
              </p>
            </div>
            <footer class="modal-footer">
              <button class="btn-ghost" @click="deleteVisible = false">取消</button>
              <button class="btn-danger" @click="confirmDelete">确认删除</button>
            </footer>
          </div>
        </div>
      </transition>
    </Teleport>

    <!-- Toast 提示 -->
    <Teleport to="body">
      <transition name="toast-fade">
        <div v-if="toast.show" class="toast" :class="toast.type">
          {{ toast.message }}
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'
import CustomSelect from '@/components/CustomSelect.vue'
import DeptTreeSelect from '@/components/DeptTreeSelect.vue'

const loading = ref(false)
const list = ref([])
const statusFilter = ref('pending')
const searchKeyword = ref('')
const pageSize = ref(20)
const currentPage = ref(1)

const statusOptions = [
  { value: 'pending', label: '待审核' },
  { value: 'onboarded', label: '已入职' },
  { value: 'rejected', label: '已拒绝' },
  { value: 'all', label: '全部' }
]

const pageSizeOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' }
]

const detailVisible = ref(false)
const currentEmployee = ref(null)

const rejectVisible = ref(false)
const rejectReason = ref('')
const rejectTarget = ref(null)

const approveVisible = ref(false)
const approveTarget = ref(null)
const approveForm = ref({
  department_id: '',
  position_id: '',
  hire_date: new Date().toISOString().split('T')[0],
  salary: null,
})

const deleteVisible = ref(false)
const deleteTarget = ref(null)

const departments = ref([])
const positions = ref([])

// 部门和职位选项（CustomSelect格式）
const departmentOptions = computed(() => {
  return [
    { label: '请选择部门', value: '' },
    ...departments.value.map(d => ({ label: d.name, value: d.id }))
  ]
})

const positionOptions = computed(() => {
  return [
    { label: '请选择职位', value: '' },
    ...positions.value.map(p => ({ label: p.name, value: p.id }))
  ]
})

const toast = ref({ show: false, message: '', type: 'success' })

const maritalMap = {
  single: '未婚',
  married: '已婚',
  divorced: '离异',
  widowed: '丧偶',
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

const pendingCount = computed(() => {
  return list.value.filter(e => e.onboard_status === 'pending').length
})

// 筛选
const filtered = computed(() => {
  let result = list.value

  // 按状态筛选
  if (statusFilter.value && statusFilter.value !== 'all') {
    result = result.filter(e => e.onboard_status === statusFilter.value)
  }

  // 按关键词搜索
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(e =>
      e.name?.toLowerCase().includes(kw) ||
      e.employee_id?.toLowerCase().includes(kw) ||
      e.phone?.includes(kw)
    )
  }

  return result
})

const totalPages = computed(() => Math.ceil(filtered.value.length / pageSize.value) || 1)

const paged = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filtered.value.slice(start, start + pageSize.value)
})

function goToPage(page) {
  currentPage.value = page
}

function showToast(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

onMounted(() => {
  loadList()
  loadDepartments()
  loadPositions()
})

async function loadList() {
  loading.value = true
  try {
    // 加载全部数据，前端筛选
    const res = await api.get('/onboarding/pending/', { params: { status: 'all' } })
    if (res.success) {
      list.value = res.data || []
    } else {
      showToast(res.error?.message || '加载失败', 'error')
    }
  } catch (e) {
    console.error('Load error:', e)
    showToast('加载失败', 'error')
  } finally {
    loading.value = false
  }
}

async function loadDepartments() {
  try {
    const res = await api.get('/departments/')
    departments.value = res.data?.results || res.data || []
  } catch (e) {}
}

async function loadPositions() {
  try {
    const res = await api.get('/positions/')
    positions.value = res.data?.results || res.data || []
  } catch (e) {}
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getStatusClass(status) {
  if (status === 'pending') return 'status-warning'
  if (status === 'onboarded') return 'status-active'
  if (status === 'rejected') return 'status-danger'
  return 'status-inactive'
}

function getStatusText(status) {
  if (status === 'pending') return '待审核'
  if (status === 'onboarded') return '已入职'
  if (status === 'rejected') return '已拒绝'
  if (status === 'resigned') return '已离职'
  return status
}

function viewDetail(row) {
  currentEmployee.value = row
  detailVisible.value = true
}

function approveOnboard(row) {
  approveTarget.value = row
  approveForm.value = {
    department_id: '',
    position_id: '',
    hire_date: new Date().toISOString().split('T')[0],
    salary: null,
  }
  approveVisible.value = true
  detailVisible.value = false
}

async function confirmApprove() {
  if (!approveForm.value.department_id || !approveForm.value.position_id || !approveForm.value.hire_date) {
    showToast('请填写部门、职位和入职日期', 'warning')
    return
  }

  try {
    const res = await api.post(`/onboarding/${approveTarget.value.id}/approve/`, {
      action: 'approve',
      department_id: approveForm.value.department_id,
      position_id: approveForm.value.position_id,
      hire_date: approveForm.value.hire_date,
      salary: approveForm.value.salary,
    })
    // 检查成功：success字段为true 或者 返回了employee_id
    if (res.success) {
      showToast('审核通过')
      approveVisible.value = false
      loadList()
    } else {
      showToast(res.error?.message || '操作失败', 'error')
    }
  } catch (e) {
    console.error('Approve error:', e)
    showToast('操作失败', 'error')
  }
}

function rejectOnboard(row) {
  rejectTarget.value = row
  rejectReason.value = ''
  rejectVisible.value = true
  detailVisible.value = false
}

async function confirmReject() {
  if (!rejectReason.value.trim()) {
    showToast('请输入拒绝原因', 'warning')
    return
  }

  try {
    const res = await api.post(`/onboarding/${rejectTarget.value.id}/approve/`, {
      action: 'reject',
      reason: rejectReason.value,
    })
    if (res.success) {
      showToast('已拒绝')
      rejectVisible.value = false
      loadList()
    } else {
      showToast(res.error?.message || '操作失败', 'error')
    }
  } catch (e) {
    showToast('操作失败', 'error')
  }
}

function deleteEmployee(row) {
  deleteTarget.value = row
  deleteVisible.value = true
  detailVisible.value = false
}

async function confirmDelete() {
  try {
    const res = await api.delete(`/employees/${deleteTarget.value.id}/`)
    if (res.success) {
      showToast('已删除')
      deleteVisible.value = false
      loadList()
    } else {
      showToast(res.error?.message || '删除失败', 'error')
    }
  } catch (e) {
    showToast('删除失败', 'error')
  }
}
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
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border-color: #fbbf24;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.stat-badge.active .stat-value {
  color: #d97706;
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
  padding: 0.55rem 0.75rem;
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
  overflow-x: auto;
}

/* 自定义滚动条 */
.table-container::-webkit-scrollbar {
  height: 6px;
}

.table-container::-webkit-scrollbar-track {
  background: transparent;
}

.table-container::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
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
.col-name { min-width: 140px; }
.col-id { min-width: 100px; }
.col-phone { min-width: 120px; }
.col-email { min-width: 180px; }
.col-status { min-width: 80px; }
.col-date { min-width: 160px; }
.col-actions { min-width: 180px; white-space: nowrap; }

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
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.employee-name {
  font-weight: 500;
  color: #1e293b;
}

.emp-id-text {
  color: #64748b;
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 13px;
}

/* 状态徽章 */
.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-warning {
  background: #fef3c7;
  color: #d97706;
}

.status-active {
  background: #dcfce7;
  color: #16a34a;
}

.status-danger {
  background: #fee2e2;
  color: #dc2626;
}

.status-inactive {
  background: #f3f4f6;
  color: #6b7280;
}

/* 操作链接 */
.action-link {
  background: none;
  border: none;
  color: #0ea5e9;
  cursor: pointer;
  font-size: 13px;
  padding: 4px 8px;
  margin-right: 4px;
}

.action-link:hover {
  text-decoration: underline;
}

.action-success {
  color: #059669;
}

.action-danger {
  color: #dc2626;
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

/* Modal styles */
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

.modal-container {
  background: #fff;
  border-radius: 12px;
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.modal-container *::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}

.modal-container *::-webkit-scrollbar-track {
  background: transparent;
}

.modal-container *::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.5);
  border-radius: 2px;
}

.modal-container *::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.8);
}

.modal-large {
  width: 700px;
}

.modal-small {
  width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #64748b;
  cursor: pointer;
  line-height: 1;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #1e293b;
  background: #e2e8f0;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
}

.modal-body::-webkit-scrollbar {
  width: 4px;
}

.modal-body::-webkit-scrollbar-track {
  background: transparent;
}

.modal-body::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.5);
  border-radius: 2px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.8);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 0 0 12px 12px;
}

/* Detail styles */
.detail-section {
  margin-bottom: 24px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 24px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item .label {
  font-size: 12px;
  color: #64748b;
}

.detail-item .value {
  font-size: 14px;
  color: #1e293b;
}

.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Form styles */
.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #1e293b;
}

.required {
  color: #dc2626;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  color: #1e293b;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 隐藏number输入框的上下箭头 */
.form-input[type="number"]::-webkit-outer-spin-button,
.form-input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  appearance: none;
  margin: 0;
}

.form-input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}

/* 表单中的CustomSelect样式 */
.form-custom-select {
  width: 100%;
}

.form-custom-select :deep(.select-trigger) {
  width: 100%;
  padding: 0 12px;
  padding-right: 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  height: 36px;
  display: flex;
  align-items: center;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-custom-select :deep(.select-trigger:hover) {
  border-color: #cbd5e1;
}

.form-custom-select :deep(.custom-select.open .select-trigger),
.form-custom-select :deep(.select-trigger:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-custom-select :deep(.select-value) {
  font-size: 14px;
  color: #1e293b;
}

.form-custom-select :deep(.select-arrow) {
  color: #64748b;
}

.form-custom-select :deep(.select-dropdown) {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 0.35rem 0;
  max-height: 200px;
  overflow-y: auto;
}

.form-custom-select :deep(.select-option) {
  padding: 0.6rem 0.75rem;
  font-size: 14px;
  color: #374151;
  transition: background 0.15s;
}

.form-custom-select :deep(.select-option:hover),
.form-custom-select :deep(.select-option.highlighted) {
  background: #f1f5f9;
  color: #1e293b;
}

.form-custom-select :deep(.select-option.selected) {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

/* 表单中的DeptTreeSelect样式 */
.form-dept-tree-select {
  width: 100%;
}

.form-dept-tree-select :deep(.select-trigger) {
  width: 100%;
  padding: 0 12px;
  padding-right: 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  height: 36px;
  display: flex;
  align-items: center;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
  position: relative;
}

.form-dept-tree-select :deep(.select-trigger:hover) {
  border-color: #cbd5e1;
}

.form-dept-tree-select :deep(.dept-tree-select.open .select-trigger),
.form-dept-tree-select :deep(.select-trigger:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-dept-tree-select :deep(.select-value) {
  font-size: 14px;
  color: #1e293b;
  flex: 1;
}

.form-dept-tree-select :deep(.select-arrow) {
  color: #64748b;
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
}

.form-dept-tree-select :deep(.dept-tree-select.open .select-arrow) {
  transform: translateY(-50%) rotate(180deg);
}

.form-dept-tree-select :deep(.select-dropdown) {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 0.35rem 0;
  max-height: 240px;
  overflow-y: auto;
}

.form-dept-tree-select :deep(.select-dropdown)::-webkit-scrollbar {
  width: 6px;
}

.form-dept-tree-select :deep(.select-dropdown)::-webkit-scrollbar-track {
  background: transparent;
}

.form-dept-tree-select :deep(.select-dropdown)::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.form-dept-tree-select :deep(.select-dropdown)::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.form-dept-tree-select :deep(.select-option) {
  padding: 0.6rem 0.75rem;
  font-size: 14px;
  color: #374151;
  transition: background 0.15s;
}

.form-dept-tree-select :deep(.select-option:hover),
.form-dept-tree-select :deep(.select-option.highlighted) {
  background: #f1f5f9;
  color: #1e293b;
}

.form-dept-tree-select :deep(.select-option.selected) {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

/* Buttons */
.btn-primary {
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-danger {
  padding: 10px 20px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-danger:hover {
  background: #b91c1c;
}

.btn-ghost {
  padding: 10px 20px;
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-ghost:hover {
  background: #f1f5f9;
  color: #1e293b;
}

/* Toast */
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  z-index: 2000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toast.success {
  background: #059669;
  color: white;
}

.toast.warning {
  background: #d97706;
  color: white;
}

.toast.error {
  background: #dc2626;
  color: white;
}

/* Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.3s;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}
</style>
