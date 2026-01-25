<template>
  <div class="resign-approval-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1>离职审批</h1>
        <p class="header-subtitle">审批待处理的离职申请</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-ghost" :disabled="loading" @click="fetchData">
          <img src="/icons/refresh.svg" alt="" class="btn-icon" />
          刷新
        </button>
      </div>
    </header>

    <!-- 筛选栏 -->
    <div class="filters-bar">
      <div class="filter-tabs">
        <button 
          v-for="tab in filterTabs" 
          :key="tab.value" 
          class="filter-tab"
          :class="{ active: currentFilter === tab.value }"
          @click="currentFilter = tab.value"
        >
          {{ tab.label }}
          <span v-if="tab.count > 0" class="tab-badge">{{ tab.count }}</span>
        </button>
      </div>
    </div>

    <!-- 列表内容 -->
    <section class="content-area">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="!filteredList.length" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
        <p>暂无待审批的离职申请</p>
        <span>所有申请都已处理完毕</span>
      </div>

      <div v-else class="approval-list">
        <article v-for="item in filteredList" :key="item.id" class="approval-card">
          <div class="card-header">
            <div class="employee-info">
              <div class="avatar">{{ item.employee?.name?.charAt(0) || '?' }}</div>
              <div class="info">
                <h3>{{ item.employee?.name || '未知员工' }}</h3>
                <p>{{ item.employee?.department?.name || '未分配部门' }} · {{ item.employee?.position?.name || '未分配职位' }}</p>
              </div>
            </div>
            <div class="status-info">
              <span class="status-tag" :class="item.status">{{ statusText(item.status) }}</span>
              <span class="date">{{ formatDate(item.created_at) }} 提交</span>
            </div>
          </div>

          <div class="card-body">
            <div class="info-grid">
              <div class="info-item">
                <span class="label">交接开始日</span>
                <span class="value">{{ formatDate(item.start_date) }}</span>
              </div>
              <div class="info-item">
                <span class="label">最后工作日</span>
                <span class="value">{{ formatDate(item.end_date) }}</span>
              </div>
              <div class="info-item full">
                <span class="label">离职原因</span>
                <span class="value reason">{{ item.reason || '未填写' }}</span>
              </div>
            </div>

            <!-- 审批进度 -->
            <div class="approval-progress">
              <div class="progress-step" :class="getStepClass(item, 'manager')">
                <div class="step-marker"></div>
                <div class="step-content">
                  <span class="step-title">直属上级审批</span>
                  <span class="step-status">{{ stageText(item.resignation_manager_status) }}</span>
                  <span v-if="item.resignation_manager_by" class="step-meta">
                    {{ item.resignation_manager_by?.username }} · {{ formatDateTime(item.resignation_manager_at) }}
                  </span>
                  <span v-if="item.resignation_manager_comment" class="step-comment">
                    "{{ item.resignation_manager_comment }}"
                  </span>
                </div>
              </div>
              <div class="progress-step" :class="getStepClass(item, 'hr')">
                <div class="step-marker"></div>
                <div class="step-content">
                  <span class="step-title">人事终审</span>
                  <span class="step-status">{{ stageText(item.resignation_hr_status) }}</span>
                  <span v-if="item.resignation_hr_by" class="step-meta">
                    {{ item.resignation_hr_by?.username }} · {{ formatDateTime(item.resignation_hr_at) }}
                  </span>
                  <span v-if="item.resignation_hr_comment" class="step-comment">
                    "{{ item.resignation_hr_comment }}"
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="card-footer" v-if="canApprove(item)">
            <div class="comment-input">
              <input 
                type="text" 
                v-model="item._comment" 
                placeholder="审批意见（可选）"
                class="form-input"
              />
            </div>
            <div class="action-buttons">
              <button 
                class="btn btn-danger" 
                :disabled="item._processing"
                @click="handleApprove(item, 'reject')"
              >
                拒绝
              </button>
              <button 
                class="btn btn-success" 
                :disabled="item._processing"
                @click="handleApprove(item, 'approve')"
              >
                通过
              </button>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../utils/api';
import { useAuthStore } from '../../stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const resignations = ref([]);
const currentFilter = ref('pending');

const filterTabs = computed(() => {
  const pending = resignations.value.filter(r => r.status === 'pending').length;
  const approved = resignations.value.filter(r => r.status === 'approved').length;
  const rejected = resignations.value.filter(r => r.status === 'rejected').length;
  return [
    { label: '待审批', value: 'pending', count: pending },
    { label: '已通过', value: 'approved', count: approved },
    { label: '已拒绝', value: 'rejected', count: rejected },
    { label: '全部', value: 'all', count: resignations.value.length },
  ];
});

const filteredList = computed(() => {
  if (currentFilter.value === 'all') return resignations.value;
  return resignations.value.filter(r => r.status === currentFilter.value);
});

const isHR = computed(() => auth.user?.is_staff || auth.user?.is_superuser);

function formatDate(d) {
  if (!d) return '--';
  return new Date(d).toLocaleDateString('zh-CN');
}

function formatDateTime(d) {
  if (!d) return '--';
  return new Date(d).toLocaleString('zh-CN');
}

function statusText(status) {
  const map = { pending: '审批中', approved: '已通过', rejected: '已拒绝' };
  return map[status] || status;
}

function stageText(status) {
  const map = { pending: '待处理', approved: '已通过', rejected: '已拒绝' };
  return map[status] || status;
}

function getStepClass(item, stage) {
  const status = stage === 'manager' ? item.resignation_manager_status : item.resignation_hr_status;
  return {
    'step-pending': status === 'pending',
    'step-approved': status === 'approved',
    'step-rejected': status === 'rejected',
  };
}

function canApprove(item) {
  // 直属上级审批阶段：上级待处理
  if (item.resignation_manager_status === 'pending') {
    return true; // 让后端判断是否有权限
  }
  // 人事终审阶段：上级已通过，人事待处理
  if (item.resignation_manager_status === 'approved' && item.resignation_hr_status === 'pending') {
    return isHR.value;
  }
  return false;
}

function getApproveStage(item) {
  if (item.resignation_manager_status === 'pending') {
    return 'manager';
  }
  if (item.resignation_manager_status === 'approved' && item.resignation_hr_status === 'pending') {
    return 'hr';
  }
  return null;
}

async function handleApprove(item, action) {
  const stage = getApproveStage(item);
  if (!stage) return;

  item._processing = true;
  try {
    await api.post(`/leaves/${item.id}/approve/`, {
      action,
      stage,
      comments: item._comment || ''
    });
    await fetchData();
  } catch (e) {
    console.error(e);
    alert(e.response?.data?.message || '操作失败，请稍后重试');
  } finally {
    item._processing = false;
  }
}

async function fetchData() {
  loading.value = true;
  try {
    // 获取所有离职申请（管理员/有权限用户可以看到所有）
    const res = await api.get('/leaves/?leave_type=resignation&page_size=100');
    const list = res.data?.results || res.data || [];
    // 添加临时属性
    resignations.value = list.map(r => ({
      ...r,
      _comment: '',
      _processing: false
    }));
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchData);
</script>

<style scoped>
.resign-approval-page {
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.header-left h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem;
}

.header-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.btn-ghost {
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-ghost:hover:not(:disabled) {
  background: #f3f4f6;
}

.btn-success {
  background: #10b981;
  color: #fff;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.btn-danger {
  background: #ef4444;
  color: #fff;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Filter tabs */
.filters-bar {
  margin-bottom: 1.5rem;
}

.filter-tabs {
  display: flex;
  gap: 0.5rem;
  background: #f3f4f6;
  padding: 0.25rem;
  border-radius: 8px;
  width: fit-content;
}

.filter-tab {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.filter-tab:hover {
  color: #374151;
}

.filter-tab.active {
  background: #fff;
  color: #1f2937;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.tab-badge {
  background: #2563eb;
  color: #fff;
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
}

.filter-tab.active .tab-badge {
  background: #2563eb;
}

/* Content */
.content-area {
  min-height: 300px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 1rem;
  stroke: #9ca3af;
}

.empty-state p {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #374151;
  margin: 0 0 0.25rem;
}

.empty-state span {
  font-size: 0.8125rem;
}

/* Approval list */
.approval-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.approval-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.card-header {
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f3f4f6;
}

.employee-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 600;
}

.employee-info .info h3 {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.125rem;
}

.employee-info .info p {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0;
}

.status-info {
  text-align: right;
}

.status-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-tag.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-tag.approved {
  background: #d1fae5;
  color: #065f46;
}

.status-tag.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.status-info .date {
  display: block;
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.card-body {
  padding: 1.25rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item.full {
  grid-column: 1 / -1;
}

.info-item .label {
  font-size: 0.75rem;
  color: #6b7280;
}

.info-item .value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
}

.info-item .value.reason {
  font-weight: 400;
  line-height: 1.5;
}

/* Approval progress */
.approval-progress {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.progress-step {
  flex: 1;
  display: flex;
  gap: 0.75rem;
}

.step-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #d1d5db;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.step-pending .step-marker {
  background: #fbbf24;
}

.step-approved .step-marker {
  background: #10b981;
}

.step-rejected .step-marker {
  background: #ef4444;
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.step-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #374151;
}

.step-status {
  font-size: 0.75rem;
  color: #6b7280;
}

.step-meta {
  font-size: 0.75rem;
  color: #9ca3af;
}

.step-comment {
  font-size: 0.8125rem;
  color: #6b7280;
  font-style: italic;
  margin-top: 0.25rem;
}

/* Card footer */
.card-footer {
  padding: 1rem 1.25rem;
  background: #f9fafb;
  border-top: 1px solid #f3f4f6;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.comment-input {
  flex: 1;
}

.form-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: none;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}
</style>
