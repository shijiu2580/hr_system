<template>
  <div class="page-grid create-salary-page">
    <div class="card">
      <!-- 顶部标签栏 -->
      <div class="tab-header">
        <div class="tab-left">
          <div class="tab-icon">
            <img src="/icons/salaries.svg" alt="" />
          </div>
          <div class="tab-title">新建薪资记录</div>
        </div>
        <div class="header-actions">
          <button class="btn-primary" @click="triggerFileInput" :disabled="loading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            导入Excel
          </button>
          <button class="btn-secondary" @click="goBack">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            返回列表
          </button>
          <button class="btn-add" @click="addEmptyRow" :disabled="loading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="16"/>
              <line x1="8" y1="12" x2="16" y2="12"/>
            </svg>
            添加一行
          </button>
          <button class="btn-template" @click="downloadTemplate" :disabled="loading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            下载模板
          </button>
          <input
            ref="fileInput"
            type="file"
            accept=".xlsx,.xls"
            style="display:none"
            @change="handleFileImport"
          />
        </div>
      </div>

      <!-- 右上角弹框提示 -->
      <teleport to="body">
        <transition name="toast">
          <div v-if="message" class="toast" :class="`toast-${message.type}`">
            <span>{{ message.text }}</span>
          <button @click="message = null" class="toast-close">×</button>
        </div>
      </transition>
    </teleport>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>加载数据...</span>
    </div>

    <div v-else>
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="record-count">共 <strong>{{ records.length }}</strong> 条记录</span>
          <span v-if="records.length > 0" class="total-amount">
            合计实发：<strong>{{ formatCurrency(totalNetSalary) }}</strong>
          </span>
        </div>
      </div>

        <!-- 表格式表单 -->
        <div class="table-container">
          <table class="salary-table">
            <thead>
              <tr>
                <th class="col-index">#</th>
                <th>员工姓名</th>
                <th>薪资周期</th>
                <th>基本工资</th>
                <th class="col-net">实发工资</th>
                <th class="col-action">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="records.length === 0" class="empty-row">
                <td colspan="6">
                  <div class="empty-hint">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="12" y1="18" x2="12" y2="12"/>
                      <line x1="9" y1="15" x2="15" y2="15"/>
                    </svg>
                    <p>暂无记录，点击"添加一行"或"导入Excel"添加薪资数据</p>
                  </div>
                </td>
              </tr>
              <tr v-for="(row, index) in records" :key="row._uid" class="input-row">
                <td class="col-index">{{ index + 1 }}</td>
                <td class="col-employee">
                  <CustomSelect
                    v-model="row.employee_id"
                    :options="[{ value: '', label: '请选择' }, ...employees.map(emp => ({ value: emp.id, label: emp.name }))]"
                    placeholder="请选择"
                    class="table-select"
                    searchable
                  />
                </td>
                <td class="col-period">
                  <div class="period-inputs">
                    <input type="number" min="2000" v-model.number="row.year" class="form-control year-input" placeholder="年" />
                    <span class="period-sep">年</span>
                    <input type="number" min="1" max="12" v-model.number="row.month" class="form-control month-input" placeholder="月" />
                    <span class="period-sep">月</span>
                  </div>
                </td>
                <td>
                  <div class="money-input">
                    <span class="money-prefix">¥</span>
                    <input type="number" min="0" step="0.01" v-model.number="row.basic_salary" class="form-control" placeholder="0.00" />
                  </div>
                </td>
                <td class="col-net">
                  <span class="net-value">{{ formatCurrency(computeRowNet(row)) }}</span>
                </td>
                <td class="col-action">
                  <button type="button" class="btn-delete" @click="removeRow(index)" title="删除此行">
                    <img src="/icons/delete.svg" alt="删除" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="form-actions">
          <button type="button" class="btn-primary" :disabled="saving || records.length === 0" @click="handleSubmitAll">
            <svg v-if="!saving" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17 21 17 13 7 13 7 21"/>
              <polyline points="7 3 7 8 15 8"/>
            </svg>
            <span class="spinner-small" v-else></span>
            {{ saving ? '保存中...' : `保存全部 (${records.length} 条)` }}
          </button>
          <button type="button" class="btn-danger" v-if="records.length > 0" @click="clearAll">
            清空全部
          </button>
          <button type="button" class="btn-secondary" @click="goBack">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as XLSX from 'xlsx'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'

const router = useRouter()

const employees = ref([])
const loading = ref(true)
const saving = ref(false)
const message = ref(null)
const fileInput = ref(null)

const now = new Date()

// 多行记录
const records = ref([])

// 生成唯一ID
let uidCounter = 0
function generateUid() {
  return `row_${Date.now()}_${uidCounter++}`
}

// 创建空行
function createEmptyRow() {
  return {
    _uid: generateUid(),
    employee_id: '',
    year: now.getFullYear(),
    month: now.getMonth() + 1,
    basic_salary: 0
  }
}

// 添加空行
function addEmptyRow() {
  records.value.push(createEmptyRow())
}

// 删除行
function removeRow(index) {
  records.value.splice(index, 1)
}

// 清空全部
function clearAll() {
  if (confirm('确定要清空所有记录吗？')) {
    records.value = []
  }
}

// 计算单行实发（只有基本工资）
function computeRowNet(row) {
  return Number(row.basic_salary) || 0
}

// 计算总实发
const totalNetSalary = computed(() => {
  return records.value.reduce((sum, row) => sum + computeRowNet(row), 0)
})

function formatCurrency(val) {
  return '¥' + Number(val || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

// 触发文件选择
function triggerFileInput() {
  fileInput.value?.click()
}

// 下载模板
async function downloadTemplate() {
  try {
    const response = await api.get('/export/salary-template/', {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '薪资导入模板.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    message.value = { type: 'error', text: '下载模板失败：' + (e.response?.data?.detail || e.message) }
  }
}

// 处理Excel导入
async function handleFileImport(event) {
  const file = event.target.files?.[0]
  if (!file) return

  try {
    const data = await file.arrayBuffer()
    const workbook = XLSX.read(data, { type: 'array' })
    const sheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[sheetName]
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })

    if (jsonData.length < 2) {
      message.value = { type: 'error', text: 'Excel文件为空或格式不正确' }
      return
    }

    // 跳过表头，解析数据行
    const headers = jsonData[0]
    const importedRows = []

    for (let i = 1; i < jsonData.length; i++) {
      const row = jsonData[i]
      if (!row || row.length === 0) continue

      // 查找员工（支持按姓名或工号匹配）
      const empNameOrId = String(row[0] || '').trim()
      const emp = employees.value.find(e =>
        e.name === empNameOrId ||
        e.employee_id === empNameOrId ||
        String(e.id) === empNameOrId
      )

      importedRows.push({
        _uid: generateUid(),
        employee_id: emp?.id || '',
        employee_name_hint: empNameOrId, // 用于提示未匹配的员工
        year: parseInt(row[1]) || now.getFullYear(),
        month: parseInt(row[2]) || now.getMonth() + 1,
        basic_salary: parseFloat(row[3]) || 0
      })
    }

    if (importedRows.length === 0) {
      message.value = { type: 'error', text: '未能解析到有效数据' }
      return
    }

    // 追加到现有记录
    records.value.push(...importedRows)

    // 检查未匹配的员工
    const unmatchedCount = importedRows.filter(r => !r.employee_id).length
    if (unmatchedCount > 0) {
      message.value = {
        type: 'warning',
        text: `成功导入 ${importedRows.length} 条记录，其中 ${unmatchedCount} 条未能匹配员工，请手动选择`
      }
    } else {
      message.value = { type: 'success', text: `成功导入 ${importedRows.length} 条记录` }
    }
  } catch (e) {
    console.error('Import error:', e)
    message.value = { type: 'error', text: '导入失败：' + (e.message || '文件格式错误') }
  } finally {
    // 重置文件输入，允许再次选择同一文件
    event.target.value = ''
  }
}

onMounted(async () => {
  try {
    const res = await api.get('/employees/')
    employees.value = res.data.results || res.data || []
  } catch (e) {
    message.value = { type: 'error', text: '加载员工列表失败：' + (e.response?.data?.detail || e.message) }
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.push('/salaries')
}

// 批量提交
async function handleSubmitAll() {
  // 验证
  const invalidRows = records.value.filter((row, idx) => !row.employee_id)
  if (invalidRows.length > 0) {
    message.value = { type: 'error', text: `有 ${invalidRows.length} 条记录未选择员工，请检查` }
    return
  }

  saving.value = true
  message.value = null

  try {
    // 逐条提交（也可以改成批量接口）
    let successCount = 0
    let failCount = 0
    const errors = []

    for (const row of records.value) {
      try {
        await api.post('/salaries/', {
          employee_id: row.employee_id,
          year: row.year,
          month: row.month,
          basic_salary: row.basic_salary,
          paid: false
        })
        successCount++
      } catch (e) {
        failCount++
        const emp = employees.value.find(emp => emp.id === row.employee_id)
        // 提取错误信息：可能在 detail, month, non_field_errors 或直接在 data 中
        const errData = e.response?.data
        let errMsg = ''
        if (errData) {
          if (errData.detail) errMsg = errData.detail
          else if (errData.month) errMsg = errData.month
          else if (errData.non_field_errors) errMsg = errData.non_field_errors.join(', ')
          else if (typeof errData === 'string') errMsg = errData
          else errMsg = JSON.stringify(errData)
        } else {
          errMsg = e.message
        }
        errors.push(`${emp?.name || '未知'} ${row.year}年${row.month}月: ${errMsg}`)
      }
    }

    if (failCount === 0) {
      message.value = { type: 'success', text: `成功保存 ${successCount} 条薪资记录` }
      setTimeout(() => router.push('/salaries/records'), 1500)
    } else {
      message.value = {
        type: 'error',
        text: `成功 ${successCount} 条，失败 ${failCount} 条: ${errors.slice(0, 3).join('; ')}${errors.length > 3 ? '...' : ''}`
      }
    }
  } catch (e) {
    message.value = { type: 'error', text: '保存失败：' + (e.response?.data?.detail || e.message) }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* 页面布局 - 与员工列表等页面保持一致 */
.page-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
}

.create-salary-page {
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

.tab-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.header-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.header-actions button {
  width: 100%;
  justify-content: center;
}

/* 按钮样式 */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary svg {
  width: 16px;
  height: 16px;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  color: #1e293b;
  font-size: 13px;
  font-weight: 500;
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

.btn-secondary svg {
  width: 16px;
  height: 16px;
}

.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid rgba(220, 38, 38, 0.3);
  border-radius: 8px;
  color: #dc2626;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover {
  background: rgba(220, 38, 38, 0.08);
}

/* Toast 右上角弹框 */
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
  padding: 0;
  line-height: 1;
}

.toast-close:hover { color: #333; }

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

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem;
  color: #64748b;
  font-size: 14px;
}

.spinner {
  width: 22px;
  height: 22px;
  border: 2.5px solid rgba(37, 99, 235, 0.2);
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.record-count {
  font-size: 13px;
  color: #64748b;
  background: #f1f5f9;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}

.record-count strong {
  color: #334155;
  font-weight: 600;
  font-size: 13px;
}

.total-amount {
  font-size: 13px;
  color: #64748b;
  padding-left: 0;
  border-left: none;
  background: #f0fdf4;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  border: 1px solid #dcfce7;
}

.total-amount strong {
  color: #15803d;
  font-size: 13px;
  font-weight: 600;
}

.toolbar-right {
  display: flex;
  gap: 0.6rem;
}

.btn-add, .btn-template {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-add {
  border: 1px solid #e0e7ff;
  background: #eef2ff;
  color: var(--color-primary);
}

.btn-add:hover {
  background: #e0e7ff;
}

.btn-template {
  border: 1px solid #d1fae5;
  background: #ecfdf5;
  color: var(--color-success);
}

.btn-template:hover {
  background: #d1fae5;
}

.btn-add svg, .btn-template svg {
  width: 15px;
  height: 15px;
}

/* Table */
.table-container {
  border: 1px solid #e2e8f0;
  border-radius: 8px; /* Slightly reducing border radius */
  overflow: visible;
  background: #fff;
}

.salary-table {
  width: 100%;
  border-collapse: separate; /* Changed to separate for border radius on rows if needed */
  border-spacing: 0;
  font-size: 13.5px; /* Slightly refined font size */
  overflow: visible;
}

.salary-table thead {
  background: #f9fafb; /* Lighter gray */
}

.salary-table th {
  padding: 0.75rem 1rem; /* Adjusted padding */
  text-align: left;
  font-weight: 500; /* Less bold */
  color: #64748b; /* Softer text color */
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.salary-table td {
  padding: 0.5rem 1rem;
  vertical-align: middle;
  border-bottom: 1px solid #f1f5f9; /* Even lighter border */
}

.salary-table tr:last-child td {
  border-bottom: none;
}

.salary-table .col-index {
  width: 40px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}

.salary-table .col-employee {
  min-width: 140px;
}

.salary-table .col-period {
  min-width: 165px;
}

.salary-table .col-net {
  text-align: right;
  min-width: 110px;
}

.salary-table thead th.col-net {
  text-align: right;
  padding-right: 1rem;
}

.salary-table .col-action {
  width: 60px;
  text-align: center;
}

.input-row {
  position: relative;
}

.input-row:has(.custom-select.open) {
  z-index: 50;
}

.input-row td {
  background: transparent;
}

.input-row:hover td {
  background: var(--color-surface-alt, #f0f2f5);
}

/* Empty State */
.empty-row td {
  padding: 2.5rem 1rem;
}

.empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  color: #94a3b8;
}

.empty-hint svg {
  width: 42px;
  height: 42px;
  opacity: 0.5;
}

.empty-hint p {
  margin: 0;
  font-size: 14px;
}

/* Form Controls */
.form-control {
  width: 100%;
  padding: 0.4rem 0.5rem;
  border: 1px solid transparent; /* Hidden default border */
  border-bottom: 1px solid #cbd5e1; /* Only bottom border visible initially */
  border-radius: 4px; /* Smaller radius */
  font-size: 13.5px;
  color: #1e293b;
  background: transparent;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.form-control:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.form-control:focus {
  outline: none;
  background: #fff;
  border-color: var(--color-primary, #2563eb);
  box-shadow: none;
}

.form-control::placeholder {
  color: #94a3b8;
}

.form-control[type="number"] {
  appearance: textfield;
  -moz-appearance: textfield;
  -webkit-appearance: textfield;
}

.form-control[type="number"]::-webkit-outer-spin-button,
.form-control[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Period Input */
.period-inputs {
  display: flex;
  align-items: center;
  gap: 0.2rem;
}

.year-input {
  width: 65px;
}

.month-input {
  width: 45px;
}

.period-sep {
  font-size: 12px;
  color: #64748b;
}

/* Money Input */
.money-input {
  position: relative;
  display: flex;
  align-items: center;
}

.money-prefix {
  position: absolute;
  left: 0.55rem;
  font-size: 13px;
  color: #64748b;
  z-index: 1;
}

.money-input .form-control {
  padding-left: 1.35rem;
  width: 100px;
}

/* Net Value */
.net-value {
  display: block;
  padding-right: 0.5rem;
  font-size: 15px;
  font-weight: 700;
  color: #059669;
}

/* Table Select */
.table-select {
  min-width: 125px;
  position: relative;
  z-index: 10;
}

.table-select :deep(.custom-select) {
  min-width: 125px;
}

.table-select :deep(.select-dropdown) {
  z-index: 100;
}

/* Delete Button */
.btn-delete {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: rgba(239, 68, 68, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-delete img {
  width: 16px;
  height: 16px;
}

.btn-delete:hover {
  background: rgba(239, 68, 68, 0.15);
  transform: scale(1.05);
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid rgba(226, 232, 240, 0.8);
}

/* Animation */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .create-salary-page {
    padding: 1rem;
  }

  .table-container {
    overflow-x: auto;
  }

  .salary-table {
    min-width: 900px;
  }
}

@media (max-width: 640px) {
  .create-salary-page {
    padding: 0.75rem;
  }

  .tab-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .header-actions button {
    flex: 1;
    justify-content: center;
  }

  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .total-amount {
    padding-left: 0;
    border-left: none;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions button {
    width: 100%;
    justify-content: center;
  }
}
</style>
