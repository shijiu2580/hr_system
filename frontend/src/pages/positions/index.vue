<template>
  <div class="page-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 7h-9M14 17H5"/>
            <circle cx="17" cy="17" r="3"/>
            <circle cx="7" cy="7" r="3"/>
          </svg>
        </div>
        <span class="header-title">职位管理</span>
      </div>
      <button class="btn-apply" @click="showCreateModal = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        新建职位
      </button>
    </div>

    <!-- 筛选栏 -->
    <div class="filters-bar">
      <CustomSelect
        v-model="filterDept"
        :options="[{ value: '', label: '所有部门' }, ...departments.map(d => ({ value: d.id, label: d.name }))]"
        placeholder="所有部门"
        class="filter-dropdown"
        searchable
      />
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input v-model="searchKeyword" type="text" placeholder="搜索职位名称..." />
      </div>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-name">职位名称</th>
            <th class="col-dept">所属部门</th>
            <th class="col-salary">薪资范围</th>
            <th class="col-count">关联员工</th>
            <th class="col-desc">职位描述</th>
            <th class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody v-if="!loading && paged.length">
          <tr v-for="item in paged" :key="item.id" class="data-row">
            <td class="col-name">
              <span class="position-name">{{ item.name }}</span>
            </td>
            <td class="col-dept">{{ item.department?.name || '-' }}</td>
            <td class="col-salary">
              <span v-if="item.salary_range_min || item.salary_range_max" class="salary-range">
                {{ formatSalary(item.salary_range_min) }} - {{ formatSalary(item.salary_range_max) }}
              </span>
              <span v-else class="text-muted">未设置</span>
            </td>
            <td class="col-count">
              <span class="employee-count" @click="showEmployees(item)">
                {{ item.employee_count || 0 }}人
              </span>
            </td>
            <td class="col-desc">
              <span class="desc-ellipsis" :title="item.description">{{ item.description || '--' }}</span>
            </td>
            <td class="col-actions">
              <a href="javascript:;" class="action-link" @click="openEdit(item)">编辑</a>
              <a href="javascript:;" class="action-link" @click="showAssign(item)">关联员工</a>
              <a href="javascript:;" class="action-link danger" @click="remove(item)">删除</a>
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
        暂无职位数据
      </div>
    </div>

    <!-- 底部分页 -->
    <div class="table-footer">
      <span class="total-count">共{{ filtered.length }}条</span>
      <div class="pagination">
        <span class="page-size-label">每页</span>
        <CustomSelect
          v-model="pageSize"
          :options="[{value:10,label:'10'},{value:20,label:'20'},{value:50,label:'50'}]"
          class="page-size-select"
          @change="currentPage = 1"
          :dropUp="true"
        />
        <span class="page-size-label">条</span>
        <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage = 1">«</button>
        <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage--">‹</button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage++">›</button>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage = totalPages">»</button>
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

    <!-- 新建/编辑职位弹窗 -->
    <div v-if="showCreateModal || editItem" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editItem ? '编辑职位' : '新建职位' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label>职位名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" placeholder="请输入职位名称" />
          </div>
          <div class="form-row">
            <label>所属部门</label>
            <DeptTreeSelect
              v-model="form.department_id"
              :departments="departments"
              placeholder="请选择部门"
              empty-label="不指定部门"
            />
          </div>
          <div class="form-row-inline">
            <div class="form-row">
              <label>最低薪资</label>
              <div class="money-input">
                <span class="money-prefix">¥</span>
                <input v-model.number="form.salary_range_min" type="number" placeholder="0" />
              </div>
            </div>
            <div class="form-row">
              <label>最高薪资</label>
              <div class="money-input">
                <span class="money-prefix">¥</span>
                <input v-model.number="form.salary_range_max" type="number" placeholder="0" />
              </div>
            </div>
          </div>
          <div class="form-row">
            <label>职位描述</label>
            <textarea v-model="form.description" rows="3" placeholder="请输入职位描述..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModal">取消</button>
          <button class="btn-submit" :disabled="saving" @click="handleSubmit">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 关联员工弹窗 -->
    <div v-if="assignItem" class="modal-overlay" @click.self="assignItem = null">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>关联员工 - {{ assignItem.name }}</h3>
          <button class="modal-close" @click="assignItem = null">×</button>
        </div>
        <div class="modal-body">
          <div class="assign-section">
            <h4>当前关联的员工 ({{ assignedEmployees.length }}人)</h4>
            <div v-if="assignedEmployees.length" class="employee-tags">
              <span v-for="emp in assignedEmployees" :key="emp.id" class="employee-tag">
                {{ emp.name }}
                <button class="tag-remove" @click="unassignEmployee(emp)">×</button>
              </span>
            </div>
            <div v-else class="empty-hint">暂无关联员工</div>
          </div>
          <div class="assign-section">
            <h4>添加员工</h4>
            <div class="assign-search">
              <CustomSelect
                v-model="selectedEmployee"
                :options="[{ value: '', label: '搜索并选择员工' }, ...availableEmployees.map(e => ({ value: e.id, label: `${e.name} (${e.department?.name || '无部门'})` }))]"
                placeholder="搜索并选择员工"
                searchable
              />
              <button class="btn-add-emp" :disabled="!selectedEmployee" @click="assignEmployee">添加</button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="assignItem = null">关闭</button>
        </div>
      </div>
    </div>

    <!-- 查看员工列表弹窗 -->
    <div v-if="viewEmployeesItem" class="modal-overlay" @click.self="viewEmployeesItem = null">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ viewEmployeesItem.name }} - 关联员工</h3>
          <button class="modal-close" @click="viewEmployeesItem = null">×</button>
        </div>
        <div class="modal-body">
          <div v-if="viewEmployeesList.length" class="employee-list">
            <div v-for="emp in viewEmployeesList" :key="emp.id" class="employee-item">
              <div class="emp-avatar">{{ emp.name?.charAt(0) }}</div>
              <div class="emp-info">
                <span class="emp-name">{{ emp.name }}</span>
                <span class="emp-dept">{{ emp.department?.name || '无部门' }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-hint">暂无关联员工</div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="viewEmployeesItem = null">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'
import DeptTreeSelect from '../../components/DeptTreeSelect.vue'

const loading = ref(false)
const saving = ref(false)
const message = ref(null)

const items = ref([])
const departments = ref([])
const allEmployees = ref([])

const filterDept = ref('')
const searchKeyword = ref('')
const pageSize = ref(10)
const currentPage = ref(1)

const showCreateModal = ref(false)
const editItem = ref(null)
const assignItem = ref(null)
const viewEmployeesItem = ref(null)
const viewEmployeesList = ref([])
const assignedEmployees = ref([])
const selectedEmployee = ref('')

const form = ref({
  name: '',
  department_id: '',
  salary_range_min: null,
  salary_range_max: null,
  description: ''
})

// 筛选
const filtered = computed(() => {
  let list = items.value
  if (filterDept.value) {
    list = list.filter(p => p.department?.id === filterDept.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter(p => p.name?.toLowerCase().includes(kw))
  }
  return list
})

const totalPages = computed(() => Math.ceil(filtered.value.length / pageSize.value) || 1)

const paged = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filtered.value.slice(start, start + pageSize.value)
})

// 可用于关联的员工（未分配到当前职位的）
const availableEmployees = computed(() => {
  if (!assignItem.value) return []
  const assignedIds = new Set(assignedEmployees.value.map(e => e.id))
  return allEmployees.value.filter(e => !assignedIds.has(e.id))
})

function formatSalary(val) {
  if (!val) return '?'
  return '¥' + Number(val).toLocaleString()
}

async function loadData() {
  loading.value = true
  try {
    const [posRes, deptRes, empRes] = await Promise.all([
      api.get('/positions/'),
      api.get('/departments/'),
      api.get('/employees/')
    ])

    const posList = posRes.data?.results || posRes.data || []
    const empList = empRes.data?.results || empRes.data || []

    // 计算每个职位关联的员工数
    const empCountMap = {}
    empList.forEach(emp => {
      if (emp.position?.id) {
        empCountMap[emp.position.id] = (empCountMap[emp.position.id] || 0) + 1
      }
    })

    items.value = posList.map(p => ({
      ...p,
      employee_count: empCountMap[p.id] || 0
    }))

    departments.value = deptRes.data?.results || deptRes.data || []
    allEmployees.value = empList
  } catch (e) {
    message.value = { type: 'error', text: '加载数据失败' }
  } finally {
    loading.value = false
  }
}

function openEdit(item) {
  editItem.value = item
  form.value = {
    name: item.name || '',
    department_id: item.department?.id || '',
    salary_range_min: item.salary_range_min,
    salary_range_max: item.salary_range_max,
    description: item.description || ''
  }
}

function closeModal() {
  showCreateModal.value = false
  editItem.value = null
  form.value = { name: '', department_id: '', salary_range_min: null, salary_range_max: null, description: '' }
}

async function handleSubmit() {
  if (!form.value.name?.trim()) {
    message.value = { type: 'error', text: '请输入职位名称' }
    return
  }

  saving.value = true
  try {
    const payload = {
      name: form.value.name,
      department_id: form.value.department_id || null,
      salary_range_min: form.value.salary_range_min || null,
      salary_range_max: form.value.salary_range_max || null,
      description: form.value.description || ''
    }

    if (editItem.value) {
      await api.put(`/positions/${editItem.value.id}/`, payload)
      message.value = { type: 'success', text: '职位已更新' }
    } else {
      await api.post('/positions/', payload)
      message.value = { type: 'success', text: '职位已创建' }
    }

    closeModal()
    await loadData()
  } catch (e) {
    message.value = { type: 'error', text: e.response?.data?.detail || '操作失败' }
  } finally {
    saving.value = false
  }
}

async function remove(item) {
  if (!confirm(`确认删除职位「${item.name}」？\n注意：已关联该职位的员工将解除关联。`)) return

  try {
    await api.delete(`/positions/${item.id}/`)
    message.value = { type: 'success', text: '已删除' }
    await loadData()
  } catch (e) {
    message.value = { type: 'error', text: e.response?.data?.detail || '删除失败' }
  }
}

// 显示关联的员工
async function showEmployees(item) {
  viewEmployeesItem.value = item
  viewEmployeesList.value = allEmployees.value.filter(e => e.position?.id === item.id)
}

// 打开关联员工弹窗
async function showAssign(item) {
  assignItem.value = item
  assignedEmployees.value = allEmployees.value.filter(e => e.position?.id === item.id)
  selectedEmployee.value = ''
}

// 添加员工到职位
async function assignEmployee() {
  if (!selectedEmployee.value) return

  try {
    await api.patch(`/employees/${selectedEmployee.value}/`, {
      position_id: assignItem.value.id
    })
    message.value = { type: 'success', text: '员工已关联到该职位' }
    await loadData()
    assignedEmployees.value = allEmployees.value.filter(e => e.position?.id === assignItem.value.id)
    selectedEmployee.value = ''
  } catch (e) {
    message.value = { type: 'error', text: '关联失败' }
  }
}

// 解除员工与职位的关联
async function unassignEmployee(emp) {
  if (!confirm(`确认解除「${emp.name}」与该职位的关联？`)) return

  try {
    await api.patch(`/employees/${emp.id}/`, {
      position_id: null
    })
    message.value = { type: 'success', text: '已解除关联' }
    await loadData()
    assignedEmployees.value = allEmployees.value.filter(e => e.position?.id === assignItem.value.id)
  } catch (e) {
    message.value = { type: 'error', text: '操作失败' }
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
  padding: 0.75rem 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon svg {
  width: 20px;
  height: 20px;
  color: #fff;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.btn-apply {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-apply svg {
  width: 16px;
  height: 16px;
}

.btn-apply:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
}

/* 筛选栏 */
.filters-bar {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-dropdown {
  width: 180px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 0.75rem;
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  max-width: 300px;
  height: 36px;
  box-sizing: border-box;
}

.search-box svg {
  width: 16px;
  height: 16px;
  color: #94a3b8;
}

.search-box input {
  border: none;
  outline: none;
  font-size: 14px;
  flex: 1;
  background: transparent;
  height: 100%;
  padding: 0;
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
  /* 使用全局样式 */
}

.data-table th {
  /* 使用全局样式 */
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

.col-name { min-width: 140px; }
.col-dept { min-width: 120px; }
.col-salary { min-width: 150px; }
.col-count { min-width: 100px; }
.col-desc { min-width: 180px; }
.col-actions { min-width: 180px; }

.position-name {
  font-weight: 500;
  color: #1e293b;
}

.salary-range {
  color: #059669;
  font-weight: 500;
}

.text-muted {
  color: #94a3b8;
}

.employee-count {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.6rem;
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.employee-count:hover {
  background: rgba(14, 165, 233, 0.2);
}

.desc-ellipsis {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: #64748b;
}

.action-link {
  color: #0ea5e9;
  text-decoration: none;
  font-size: 13px;
  margin-right: 0.75rem;
}

.action-link:hover {
  text-decoration: underline;
}

.action-link.danger {
  color: #ef4444;
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

.page-size-select {
  width: 70px;
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
.toast-warning { color: #d97706; }

.toast-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #999;
}

.toast-enter-active { animation: toastIn 0.3s ease; }
.toast-leave-active { animation: toastOut 0.2s ease; }

@keyframes toastIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes toastOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-large {
  max-width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1e293b;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f1f5f9;
  border-radius: 8px;
  font-size: 20px;
  cursor: pointer;
  color: #64748b;
}

.modal-close:hover {
  background: #e2e8f0;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e2e8f0;
}

/* 表单 */
.form-row {
  margin-bottom: 1rem;
}

.form-row label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.4rem;
}

.required {
  color: #ef4444;
}

.form-row input,
.form-row textarea {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-row input:focus,
.form-row textarea:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: none;
}

.form-row-inline {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.money-input {
  position: relative;
}

.money-prefix {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 14px;
}

.money-input input {
  padding-left: 1.5rem;
}

.btn-cancel {
  padding: 0.6rem 1.2rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  color: #475569;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-submit {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  color: #fff;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 关联员工 */
.assign-section {
  margin-bottom: 1.5rem;
}

.assign-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 0.75rem;
}

.employee-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.employee-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.65rem;
  background: rgba(14, 165, 233, 0.1);
  color: #0284c7;
  border-radius: 20px;
  font-size: 13px;
}

.tag-remove {
  width: 18px;
  height: 18px;
  border: none;
  background: rgba(14, 165, 233, 0.2);
  border-radius: 50%;
  font-size: 14px;
  cursor: pointer;
  color: #0284c7;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-remove:hover {
  background: rgba(14, 165, 233, 0.3);
}

.empty-hint {
  font-size: 13px;
  color: #94a3b8;
  padding: 0.5rem 0;
}

.assign-search {
  display: flex;
  gap: 0.5rem;
}

.assign-search .custom-select {
  flex: 1;
}

.btn-add-emp {
  padding: 0 1rem;
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
}

.btn-add-emp:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 员工列表 */
.employee-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.employee-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem;
  background: #f8fafc;
  border-radius: 8px;
}

.emp-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

.emp-info {
  display: flex;
  flex-direction: column;
}

.emp-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.emp-dept {
  font-size: 12px;
  color: #64748b;
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .filters-bar {
    flex-direction: column;
  }

  .search-box {
    max-width: none;
  }

  .table-container {
    overflow-x: auto;
  }

  .data-table {
    min-width: 800px;
  }

  .form-row-inline {
    grid-template-columns: 1fr;
  }
}
</style>
