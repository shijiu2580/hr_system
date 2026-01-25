<template>
  <div class="resign-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1>离职申请</h1>
        <p class="header-subtitle">{{ employee?.name || '—' }} · {{ employee?.department?.name || '未分配部门' }}</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-ghost" :disabled="!loaded" @click="refreshData">
          <img src="/icons/refresh.svg" alt="" class="btn-icon" />
          刷新
        </button>
        <button class="btn btn-primary" :disabled="!canSubmit" @click="startApplication">
          发起申请
        </button>
      </div>
    </header>

    <!-- 主标签页导航 -->
    <section class="main-tabs-wrapper">
      <div class="main-tabs">
        <button class="main-tab" :class="{ active: activeTab === 'progress' }" @click="activeTab = 'progress'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v6l3 3" />
          </svg>
          <span>我的离职进度</span>
        </button>
        <button class="main-tab" :class="{ active: activeTab === 'submit' }" @click="activeTab = 'submit'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="12" y1="18" x2="12" y2="12" />
            <line x1="9" y1="15" x2="15" y2="15" />
          </svg>
          <span>提交离职申请</span>
        </button>
      </div>
    </section>

    <!-- 标签页内容区 -->
    <section class="tab-content-area">
      <!-- 我的离职进度 -->
      <div v-if="activeTab === 'progress'" class="tab-panel">
        <article class="card flow-card">
          <header class="card-header">
            <div>
              <h2>我的离职进度</h2>
              <p class="card-subtitle">最新一次离职申请的完整状态</p>
            </div>
          </header>
          <div v-if="activeRequest" class="timeline">
            <div class="timeline-item">
              <div class="timeline-marker submitted"></div>
              <div class="timeline-body">
                <div class="row">
                  <h4>已提交申请</h4>
                  <span class="stage-pill submitted">记录创建</span>
                </div>
                <p class="meta">{{ formatDateTime(activeRequest.created_at) }}</p>
                <p class="desc">{{ activeRequest.reason }}</p>
              </div>
            </div>
            <div class="timeline-item" :class="{ active: activeRequest.resignation_manager_status !== 'pending' }">
              <div class="timeline-marker" :class="activeRequest.resignation_manager_status"></div>
              <div class="timeline-body">
                <div class="row">
                  <h4>直属上级审批</h4>
                  <span class="stage-pill" :class="activeRequest.resignation_manager_status">
                    {{ stageText(activeRequest.resignation_manager_status) }}
                  </span>
                </div>
                <p class="meta">{{ activeRequest.resignation_manager_by?.username || '待处理' }}</p>
                <p v-if="activeRequest.resignation_manager_comment" class="desc">
                  {{ activeRequest.resignation_manager_comment }}
                </p>
              </div>
            </div>
            <div class="timeline-item" :class="{ active: activeRequest.resignation_hr_status !== 'pending' }">
              <div class="timeline-marker" :class="activeRequest.resignation_hr_status"></div>
              <div class="timeline-body">
                <div class="row">
                  <h4>人事终审</h4>
                  <span class="stage-pill" :class="activeRequest.resignation_hr_status">
                    {{ stageText(activeRequest.resignation_hr_status) }}
                  </span>
                </div>
                <p class="meta">{{ activeRequest.resignation_hr_by?.username || '待处理' }}</p>
                <p v-if="activeRequest.resignation_hr_comment" class="desc">
                  {{ activeRequest.resignation_hr_comment }}
                </p>
              </div>
            </div>
            <div class="info-grid">
              <div>
                <p class="info-label">交接开始日</p>
                <p class="info-value">{{ formatDate(activeRequest.start_date) }}</p>
              </div>
              <div>
                <p class="info-label">最后工作日</p>
                <p class="info-value">{{ formatDate(activeRequest.end_date) }}</p>
              </div>
              <div>
                <p class="info-label">附件</p>
                <button v-if="activeRequest.attachment_url" class="link-btn" @click="download(activeRequest)">查看附件</button>
                <span v-else class="info-value muted">无</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="12" y1="18" x2="12" y2="12" />
              <line x1="9" y1="15" x2="15" y2="15" />
            </svg>
            <p>暂无离职申请记录</p>
            <span>点击右侧“发起申请”即可开始流程</span>
          </div>
        </article>

        <article class="card history-card">
          <header class="card-header">
            <div>
              <p class="section-eyebrow">历史</p>
              <h2>提交记录</h2>
              <p class="card-subtitle">支持按状态快速筛选</p>
            </div>
            <div class="filter-group">
              <button v-for="item in historyFilters" :key="item.value" class="chip" :class="{ active: historyFilter === item.value }" @click="historyFilter = item.value">
                {{ item.label }}
              </button>
            </div>
          </header>
          <div v-if="!loaded" class="skeleton-block">
            <span class="skeleton-line"></span>
            <span class="skeleton-line"></span>
            <span class="skeleton-line short"></span>
          </div>
          <div v-else-if="!historyList.length" class="empty-state compact">
            <p>暂无记录</p>
            <span>当你发起申请后，这里会展示完整流水</span>
          </div>
          <div v-else class="history-table">
            <div class="history-row head">
              <span>员工</span>
              <span>周期</span>
              <span>状态</span>
              <span>节点</span>
              <span>提交时间</span>
              <span>附件</span>
            </div>
            <div class="history-row" v-for="item in historyList" :key="item.id">
              <span class="bold">{{ item.employee?.name || '员工' }}</span>
              <span>{{ formatDate(item.start_date) }} - {{ formatDate(item.end_date) }}</span>
              <span>
                <span class="status-tag" :class="item.status">{{ statusText(item.status) }}</span>
              </span>
              <span>{{ stageText(item.resignation_manager_status) }} / {{ stageText(item.resignation_hr_status) }}</span>
              <span>{{ formatDateTime(item.created_at) }}</span>
              <span>
                <button v-if="item.attachment_url" class="link-btn sm" @click="download(item)">查看</button>
                <span v-else class="info-value muted">--</span>
              </span>
            </div>
          </div>
        </article>
      </div>

      <!-- 提交离职申请 -->
      <div v-if="activeTab === 'submit'" class="action-column">
        <article class="card form-card">
          <header class="card-header">
            <div class="header-content">
              <div class="icon-wrapper">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="12" y1="18" x2="12" y2="12" />
                  <line x1="9" y1="15" x2="15" y2="15" />
                </svg>
              </div>
              <div>
                <h2>提交离职申请</h2>
                <p class="card-subtitle">请填写以下信息以发起流程</p>
              </div>
            </div>
          </header>

          <div v-if="!loaded" class="skeleton-block">
            <span class="skeleton-line"></span>
            <span class="skeleton-line short"></span>
            <span class="skeleton-line"></span>
          </div>

          <div v-else-if="!canSubmit" class="locked-notice">
            <div class="notice-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </div>
            <div class="notice-content">
              <h4>申请通道已锁定</h4>
              <p>您当前有正在进行中的离职申请，请等待审批完成后再发起新的申请。</p>
            </div>
          </div>

          <div v-else-if="!showForm" class="form-intro">
            <p class="intro-text">填写离职申请，建议提前 30 天发起，方便人事和部门做好交接安排。</p>
            <button class="btn btn-primary" @click="showForm = true">开始填写申请</button>
          </div>

          <form v-else class="resign-form" @submit.prevent="submitResignation">
            <div class="form-section">
              <div class="section-head">
                <span class="section-index">01</span>
                <div>
                  <h3>基本信息</h3>
                  <p class="section-hint">先确认计划的离职时间安排</p>
                </div>
              </div>
              <div class="section-body">
                <div class="form-row">
                  <div class="form-group">
                    <label>预计最后工作日 <span class="required">*</span></label>
                    <div class="input-wrapper">
                      <input type="date" v-model="form.last_date" required />
                    </div>
                    <p class="field-hint">通常为提交申请后的 30 天</p>
                  </div>
                  <div class="form-group">
                    <label>交接开始日期 <span class="required">*</span></label>
                    <div class="input-wrapper">
                      <input type="date" v-model="form.notice_date" required />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-section">
              <div class="section-head">
                <span class="section-index">02</span>
                <div>
                  <h3>离职详情</h3>
                  <p class="section-hint">说明离职原因与交接安排</p>
                </div>
              </div>
              <div class="section-body">
                <div class="form-group">
                  <label>离职原因 <span class="required">*</span></label>
                  <textarea rows="4" v-model.trim="form.reason" placeholder="请详细说明您的离职原因..." required></textarea>
                </div>
                <div class="form-group">
                  <label>交接计划</label>
                  <textarea rows="3" v-model.trim="form.handover" placeholder="请列出主要工作交接事项、文档存放位置及对接人..."></textarea>
                </div>
              </div>
            </div>

            <div class="form-section">
              <div class="section-head">
                <span class="section-index">03</span>
                <div>
                  <h3>附件材料</h3>
                  <p class="section-hint">可上传交接资料或补充说明</p>
                </div>
              </div>
              <div class="section-body">
                <div class="file-upload-area" :class="{ 'has-file': form.attachment }">
                  <input type="file" id="file-upload" accept=".pdf,.doc,.docx,.xls,.xlsx,.zip,.rar" @change="handleFile" />
                  <label for="file-upload" class="file-upload-label">
                    <div class="upload-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                      </svg>
                    </div>
                    <div class="upload-text" v-if="!form.attachment">
                      <span class="link-text">点击上传</span> 或拖拽文件至此处
                      <p class="upload-hint">支持 PDF, Word, Excel, Zip 等格式</p>
                    </div>
                    <div class="file-info" v-else>
                      <span class="file-name">{{ form.attachment.name }}</span>
                      <button type="button" class="remove-file" @click.prevent="form.attachment = null">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <line x1="18" y1="6" x2="6" y2="18" />
                          <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                      </button>
                    </div>
                  </label>
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn btn-ghost" @click="cancelForm">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner"></span>
                {{ submitting ? '提交中...' : '确认提交申请' }}
              </button>
            </div>
          </form>
        </article>

        <article v-if="managerQueue.length" class="card approvals-card">
          <header class="card-header">
            <div>
              <p class="section-eyebrow">待办</p>
              <h2>直属上级审批</h2>
            </div>
            <span class="badge warning">{{ managerQueue.length }}</span>
          </header>
          <div class="approval-list">
            <article class="approval-card-item" v-for="item in managerQueue" :key="item.id">
              <div class="approval-head">
                <div>
                  <p class="applicant">{{ item.employee?.name || '员工' }}</p>
                  <p class="dept">{{ item.employee?.department?.name || '未分配部门' }}</p>
                </div>
                <span class="duration-tag">{{ formatDuration(item) }}</span>
              </div>
              <p class="approval-reason">{{ item.reason }}</p>
              <textarea rows="2" v-model="draft[item.id]" placeholder="审批意见（可选）" class="comment-input"></textarea>
              <div class="approval-actions">
                <button class="btn btn-danger-outline btn-sm" @click="decide(item, 'manager', 'reject')">驳回</button>
                <button class="btn btn-success btn-sm" @click="decide(item, 'manager', 'approve')">同意</button>
              </div>
            </article>
          </div>
        </article>

        <article v-if="hrQueue.length" class="card approvals-card hr">
          <header class="card-header">
            <div>
              <p class="section-eyebrow">待办</p>
              <h2>人事终审</h2>
            </div>
            <span class="badge info">{{ hrQueue.length }}</span>
          </header>
          <div class="approval-list">
            <article class="approval-card-item" v-for="item in hrQueue" :key="item.id">
              <div class="approval-head">
                <div>
                  <p class="applicant">{{ item.employee?.name || '员工' }}</p>
                  <p class="dept">{{ item.employee?.department?.name || '未分配部门' }}</p>
                </div>
                <span class="stage-passed">上级已通过</span>
              </div>
              <p class="approval-reason">{{ item.reason }}</p>
              <textarea rows="2" v-model="draft[item.id]" placeholder="审批意见（可选）" class="comment-input"></textarea>
              <div class="approval-actions">
                <button class="btn btn-danger-outline btn-sm" @click="decide(item, 'hr', 'reject')">驳回</button>
                <button class="btn btn-success btn-sm" @click="decide(item, 'hr', 'approve')">同意</button>
              </div>
            </article>
          </div>
        </article>
      </div>
    </section>

    <transition name="toast">
      <div v-if="toast" class="toast" :class="toast.type">
        <span>{{ toast.message }}</span>
        <button class="toast-close" @click="toast = null">×</button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import api from '../../utils/api'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const employee = ref(null)
const requests = ref([])
const loaded = ref(false)
const showForm = ref(false)
const activeTab = ref('progress')
const submitting = ref(false)
const toast = ref(null)
const draft = reactive({})
const historyFilter = ref('all')

const form = reactive({
  notice_date: todayISO(),
  last_date: todayISO(),
  reason: '',
  handover: '',
  attachment: null
})

const historyFilters = [
  { value: 'all', label: '全部' },
  { value: 'pending', label: '待审批' },
  { value: 'approved', label: '已通过' },
  { value: 'rejected', label: '已驳回' }
]

const STATUS_TEXT = { pending: '待审批', approved: '已通过', rejected: '已驳回' }
const STAGE_TEXT = { pending: '待处理', approved: '已同意', rejected: '已拒绝' }

// 后端已按用户过滤，这里直接使用
const activeRequest = computed(() => {
  if (!requests.value.length) return null
  return [...requests.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0]
})

const canSubmit = computed(() => !!employee.value && !requests.value.some(r => r.status === 'pending'))

const historyList = computed(() => {
  const sorted = [...requests.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  return historyFilter.value === 'all' ? sorted : sorted.filter(r => r.status === historyFilter.value)
})

// 审批队列 - 仅 HR/管理员需要
const isHR = computed(() => !!auth.user?.is_staff)
const managerQueue = computed(() => isHR.value ? requests.value.filter(r => 
  r.resignation_manager_status === 'pending'
) : [])
const hrQueue = computed(() => isHR.value ? requests.value.filter(r => 
  r.resignation_manager_status === 'approved' && r.resignation_hr_status === 'pending'
) : [])

watch(() => form.notice_date, val => {
  if (val && (!form.last_date || form.last_date < val)) form.last_date = val
})

// 工具函数
function todayISO() { return new Date().toISOString().slice(0, 10) }

function formatDate(v) {
  if (!v) return '--'
  const d = new Date(v)
  return isNaN(d) ? v : d.toLocaleDateString('zh-CN')
}

function formatDateTime(v) {
  if (!v) return '--'
  const d = new Date(v)
  return isNaN(d) ? v : d.toLocaleString('zh-CN')
}

const statusText = s => STATUS_TEXT[s] || s || '--'
const stageText = s => STAGE_TEXT[s] || '--'
const formatDuration = item => {
  if (!item.start_date || !item.end_date) return '--'
  return `${Math.max(1, Math.round((new Date(item.end_date) - new Date(item.start_date)) / 86400000))} 天`
}

function showToast(message, type = 'info') {
  toast.value = { message, type }
  setTimeout(() => { if (toast.value?.message === message) toast.value = null }, 3000)
}

// API 调用
async function fetchEmployee() {
  const resp = await api.get('/employees/me/')
  employee.value = resp.success ? resp.data : null
}

async function fetchRequests() {
  const resp = await api.get('/leaves/', { params: { leave_type: 'resignation' } })
  requests.value = resp.success ? (Array.isArray(resp.data) ? resp.data : resp.data?.results || resp.data?.data || []) : []
}

async function refreshData() {
  await Promise.all([fetchEmployee(), fetchRequests()])
  loaded.value = true
}

// 表单操作
function startApplication() {
  if (!canSubmit.value) return
  activeTab.value = 'submit'
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  activeTab.value = 'progress'
}

function handleFile(e) { form.attachment = e.target.files?.[0] || null }

async function submitResignation() {
  if (form.last_date < form.notice_date) return showToast('最后工作日不能早于交接开始日', 'error')
  
  submitting.value = true
  const fd = new FormData()
  fd.append('leave_type', 'resignation')
  fd.append('start_date', form.notice_date)
  fd.append('end_date', form.last_date)
  fd.append('reason', form.handover ? `离职原因：${form.reason}\n交接计划：${form.handover}` : `离职原因：${form.reason}`)
  if (form.attachment) fd.append('attachment', form.attachment)

  const resp = await api.post('/leaves/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  submitting.value = false

  if (resp.success) {
    showToast('离职申请提交成功', 'success')
    showForm.value = false
    Object.assign(form, { notice_date: todayISO(), last_date: todayISO(), reason: '', handover: '', attachment: null })
    await fetchRequests()
  } else {
    showToast(resp.error?.message || '提交失败', 'error')
  }
}

async function decide(item, stage, action) {
  const resp = await api.post(`/leaves/${item.id}/approve/`, { stage, action, comments: draft[item.id] || '' })
  if (resp.success) {
    showToast(action === 'approve' ? '已同意申请' : '已驳回申请', 'success')
    draft[item.id] = ''
    await fetchRequests()
  } else {
    showToast(resp.error?.message || '操作失败', 'error')
  }
}

function download(item) { if (item.attachment_url) window.open(item.attachment_url, '_blank') }

onMounted(refreshData)
</script>

<style scoped>
:global(body) {
  background: #edf1fb;
  font-family: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  color: #0f172a;
}

.resign-page {
  padding: 24px clamp(16px, 4vw, 48px) 48px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.action-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card {
  background: #fff;
  border-radius: 28px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.card-header h2 {
  margin: 0;
  font-size: 22px;
}

.card-subtitle {
  margin: 6px 0 0 0;
  color: #94a3b8;
  font-size: 14px;
}

.section-eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 11px;
  color: #94a3b8;
  margin: 0 0 4px 0;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: none;
  border-radius: 16px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn svg {
  width: 18px;
  height: 18px;
}

.btn-primary {
  background: #0ea5e9;
  color: #fff;
  box-shadow: 0 10px 25px rgba(14, 165, 233, 0.35);
}

.btn-ghost {
  background: rgba(255, 255, 255, 0.12);
  color: inherit;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.btn-success {
  background: #16a34a;
  color: #fff;
}

.btn-danger-outline {
  background: transparent;
  color: #dc2626;
  border: 1px solid #fecdd3;
}

.btn-sm {
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.timeline-item {
  display: flex;
  gap: 14px;
}

.timeline-marker {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid #e2e8f0;
  margin-top: 6px;
}

.timeline-marker.submitted { border-color: #0ea5e9; }
.timeline-marker.pending { border-color: #fbbf24; }
.timeline-marker.approved { border-color: #22c55e; }
.timeline-marker.rejected { border-color: #ef4444; }

.timeline-body {
  flex: 1;
  border-bottom: 1px dashed #e2e8f0;
  padding-bottom: 16px;
}

.timeline-item:last-child .timeline-body {
  border-bottom: none;
}

.timeline-body h4 {
  margin: 0;
  font-size: 16px;
}

.row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.meta {
  margin: 6px 0;
  color: #94a3b8;
  font-size: 13px;
}

.desc {
  margin: 0;
  color: #475569;
  white-space: pre-line;
  font-size: 14px;
}

.stage-pill {
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  background: #e2e8f0;
  text-transform: uppercase;
}

.stage-pill.pending { background: #fef3c7; color: #92400e; }
.stage-pill.approved { background: #dcfce7; color: #15803d; }
.stage-pill.rejected { background: #fee2e2; color: #b91c1c; }
.stage-pill.submitted { background: #dbeafe; color: #1d4ed8; }

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  padding-top: 8px;
}

.info-label {
  margin: 0;
  color: #94a3b8;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.info-value {
  margin: 4px 0 0 0;
  font-size: 16px;
}

.info-value.muted {
  color: #94a3b8;
}

.link-btn {
  border: none;
  background: transparent;
  color: #2563eb;
  font-weight: 600;
  cursor: pointer;
}

.link-btn.sm {
  font-size: 13px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
  border: 1px dashed #cbd5f5;
  border-radius: 20px;
  padding: 32px;
  text-align: center;
}

.empty-state svg {
  width: 44px;
  height: 44px;
}

.empty-state.compact {
  padding: 24px;
}

.history-card .history-table {
  width: 100%;
  display: grid;
  gap: 10px;
}

.history-row {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
  font-size: 14px;
  align-items: center;
}

.history-row.head {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #94a3b8;
}

.history-row:not(.head) {
  padding: 14px 0;
  border-bottom: 1px solid #f1f5f9;
}

.history-row:last-child {
  border-bottom: none;
}

.bold {
  font-weight: 600;
}

.status-tag {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: #f1f5f9;
  color: #64748b;
}

.status-tag.pending { background: #fff7ed; color: #c2410c; }
.status-tag.approved { background: #ecfdf5; color: #047857; }
.status-tag.rejected { background: #fef2f2; color: #b91c1c; }

.filter-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  border: 1px solid rgba(148, 163, 184, 0.6);
  border-radius: 999px;
  padding: 6px 14px;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  color: #64748b;
}

.chip.active {
  background: #0ea5e9;
  color: #fff;
  border-color: #0ea5e9;
}

.skeleton-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-line {
  height: 14px;
  border-radius: 999px;
  background: #e2e8f0;
}

.skeleton-line.short {
  width: 60%;
}

.main-tabs-wrapper {
  margin-top: 20px;
}

.main-tabs {
  display: flex;
  gap: 12px;
}

.main-tab {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #0f172a;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s ease-in-out;
}

.main-tab svg {
  width: 18px;
  height: 18px;
}

.main-tab:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.main-tab.active {
  border-color: #0ea5e9;
  background: #0ea5e9;
  color: #ffffff;
  box-shadow: 0 10px 25px rgba(14, 165, 233, 0.35);
}

.main-tab.active svg {
  color: #ffffff;
}

.tab-content-area {
  margin-top: 20px;
}

.tab-panel {
  display: grid;
  grid-template-columns: minmax(0, 2.1fr) minmax(0, 1.5fr);
  gap: 20px;
}

.locked-notice {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: #fef2f2;
  border: 1px solid #fee2e2;
  border-radius: 16px;
  color: #991b1b;
}

.notice-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  color: #ef4444;
}

.notice-content h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: #7f1d1d;
}

.notice-content p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #991b1b;
}

.form-intro {
  padding: 16px 0 8px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-wrapper {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  background: #eef2ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1d4ed8;
}

.icon-wrapper svg {
  width: 32px;
  height: 32px;
}

.resign-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  background: linear-gradient(145deg, #f9fbff, #f3f6ff);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

.section-head {
  display: flex;
  align-items: center;
  gap: 14px;
}

.section-index {
  width: 36px;
  height: 36px;
  border-radius: 14px;
  background: #fff;
  border: 1px solid #e0e7ff;
  color: #2563eb;
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.12);
}

.section-head h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.section-hint {
  margin: 2px 0 0 0;
  font-size: 13px;
  color: #64748b;
}

.section-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 18px;
  padding: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.input-wrapper {
  position: relative;
}

.resign-form input,
.resign-form textarea {
  width: 100%;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  font-family: inherit;
  background: #fff;
  transition: all 0.2s;
  color: #1e293b;
}

.resign-form input:focus,
.resign-form textarea:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: none;
}

.field-hint {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.required {
  color: #ef4444;
  margin-left: 2px;
}

.file-upload-area {
  position: relative;
}

.file-upload-area input[type="file"] {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.file-upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.file-upload-label:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}

.has-file .file-upload-label {
  border-style: solid;
  border-color: #e2e8f0;
  background: #fff;
  flex-direction: row;
  justify-content: space-between;
  padding: 12px 16px;
  gap: 12px;
}

.upload-icon {
  color: #94a3b8;
  margin-bottom: 8px;
}

.upload-icon svg {
  width: 24px;
  height: 24px;
}

.has-file .upload-icon {
  margin-bottom: 0;
  color: #0ea5e9;
}

.upload-text {
  font-size: 14px;
  color: #64748b;
}

.link-text {
  color: #0ea5e9;
  font-weight: 500;
}

.upload-hint {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #94a3b8;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  color: #334155;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.remove-file {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-file:hover {
  background: #f1f5f9;
  color: #ef4444;
}

.remove-file svg {
  width: 16px;
  height: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.badge {
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  background: #e0e7ff;
  color: #3730a3;
}

.badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.badge.info {
  background: #e0f2fe;
  color: #0369a1;
}

.approval-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.approval-card-item {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.approval-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.applicant {
  margin: 0;
  font-weight: 600;
}

.dept {
  font-size: 13px;
  color: #64748b;
}

.duration-tag {
  background: #f1f5f9;
  color: #64748b;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 12px;
}

.stage-passed {
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 12px;
}

.approval-reason {
  margin: 0;
  color: #475569;
  white-space: pre-line;
  font-size: 14px;
}

.comment-input {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  font-size: 14px;
}

.approval-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.toast-enter-active,
.toast-leave-active {
  transition: 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  transform: translateY(8px);
  opacity: 0;
}

.toast {
  position: fixed;
  bottom: 32px;
  right: 32px;
  background: #0f172a;
  color: #fff;
  padding: 14px 18px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.3);
  z-index: 1000;
}

.toast.success { background: #16a34a; }
.toast.error { background: #dc2626; }

.toast-close {
  background: transparent;
  border: none;
  color: inherit;
  font-size: 18px;
  cursor: pointer;
}

@media (max-width: 1200px) {
  .hero-banner {
    grid-template-columns: 1fr;
  }
  .tab-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .resign-page {
    padding: 18px;
  }
  .card {
    padding: 18px;
    border-radius: 18px;
  }
  .hero-banner {
    border-radius: 24px;
    padding: 24px;
  }
  .history-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .history-row.head {
    display: none;
  }
}

@media (max-width: 480px) {
  .hero-actions {
    flex-direction: column;
  }
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>

