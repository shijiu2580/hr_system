<template>
  <div class="resign-progress-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1>离职进度</h1>
        <p class="header-subtitle">{{ employee?.name || '—' }} · {{ employee?.department?.name || '未分配部门' }}</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-ghost" :disabled="!loaded" @click="refreshData">
          <img src="/icons/refresh.svg" alt="" class="btn-icon" />
          刷新
        </button>
        <router-link to="/resignation/apply" class="btn btn-primary" v-if="canSubmit">
          发起申请
        </router-link>
      </div>
    </header>

    <!-- 主内容区 -->
    <section class="content-area">
      <!-- 我的离职进度 -->
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
          <span>点击右上角"发起申请"即可开始流程</span>
        </div>
      </article>

      <!-- 历史记录 -->
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
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../utils/api';

const loaded = ref(false);
const employee = ref(null);
const resignations = ref([]);
const historyFilter = ref('all');

const historyFilters = [
  { label: '全部', value: 'all' },
  { label: '待审批', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
];

const activeRequest = computed(() => {
  return resignations.value.find(r => r.status === 'pending') || resignations.value[0] || null;
});

const canSubmit = computed(() => {
  // 没有进行中的申请才能发起新申请
  return !resignations.value.some(r => r.status === 'pending');
});

const historyList = computed(() => {
  if (historyFilter.value === 'all') return resignations.value;
  return resignations.value.filter(r => r.status === historyFilter.value);
});

function formatDate(d) {
  if (!d) return '--';
  return new Date(d).toLocaleDateString('zh-CN');
}

function formatDateTime(d) {
  if (!d) return '--';
  return new Date(d).toLocaleString('zh-CN');
}

function stageText(status) {
  const map = { pending: '待处理', approved: '已通过', rejected: '已拒绝' };
  return map[status] || status;
}

function statusText(status) {
  const map = { pending: '审批中', approved: '已通过', rejected: '已拒绝' };
  return map[status] || status;
}

function download(item) {
  if (item.attachment_url) {
    window.open(item.attachment_url, '_blank');
  }
}

async function fetchData() {
  loaded.value = false;
  try {
    const [empRes, resignRes] = await Promise.all([
      api.get('/employees/me/'),
      api.get('/leaves/?leave_type=resignation')
    ]);
    employee.value = empRes.data?.data || empRes.data;
    resignations.value = resignRes.data?.results || resignRes.data || [];
  } catch (e) {
    console.error(e);
  } finally {
    loaded.value = true;
  }
}

function refreshData() {
  fetchData();
}

onMounted(fetchData);
</script>

<style scoped>
.resign-progress-page {
  padding: 1.5rem;
  max-width: 1200px;
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
  text-decoration: none;
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

.btn-primary {
  background: #2563eb;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.content-area {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.card-header {
  padding: 1.25rem;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-header h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem;
}

.card-subtitle {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0;
}

.section-eyebrow {
  font-size: 0.75rem;
  font-weight: 500;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.25rem;
}

/* Timeline */
.timeline {
  padding: 1.25rem;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  padding-bottom: 1.5rem;
  position: relative;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 11px;
  top: 28px;
  bottom: 0;
  width: 2px;
  background: #e5e7eb;
}

.timeline-item.active::before {
  background: #2563eb;
}

.timeline-marker {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e5e7eb;
  flex-shrink: 0;
}

.timeline-marker.submitted,
.timeline-marker.approved {
  background: #10b981;
}

.timeline-marker.rejected {
  background: #ef4444;
}

.timeline-marker.pending {
  background: #f59e0b;
}

.timeline-body {
  flex: 1;
}

.timeline-body .row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.timeline-body h4 {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.stage-pill {
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 500;
}

.stage-pill.submitted,
.stage-pill.approved {
  background: #d1fae5;
  color: #065f46;
}

.stage-pill.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.stage-pill.pending {
  background: #fef3c7;
  color: #92400e;
}

.meta {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0 0 0.25rem;
}

.desc {
  font-size: 0.875rem;
  color: #374151;
  margin: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
}

.info-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0 0 0.25rem;
}

.info-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
  margin: 0;
}

.info-value.muted {
  color: #9ca3af;
}

.link-btn {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0;
}

.link-btn:hover {
  text-decoration: underline;
}

.link-btn.sm {
  font-size: 0.8125rem;
}

/* Empty state */
.empty-state {
  padding: 3rem 1.5rem;
  text-align: center;
  color: #6b7280;
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

.empty-state.compact {
  padding: 2rem 1.5rem;
}

/* Filter chips */
.filter-group {
  display: flex;
  gap: 0.5rem;
}

.chip {
  padding: 0.375rem 0.75rem;
  border-radius: 16px;
  font-size: 0.8125rem;
  font-weight: 500;
  background: #f3f4f6;
  color: #374151;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.chip:hover {
  background: #e5e7eb;
}

.chip.active {
  background: #2563eb;
  color: #fff;
}

/* History table */
.history-table {
  overflow-x: auto;
}

.history-row {
  display: grid;
  grid-template-columns: 1fr 1.5fr 0.8fr 1.2fr 1.2fr 0.6fr;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  font-size: 0.875rem;
  color: #374151;
  align-items: center;
}

.history-row.head {
  background: #f9fafb;
  font-weight: 500;
  font-size: 0.8125rem;
  color: #6b7280;
}

.history-row:not(.head) {
  border-top: 1px solid #f3f4f6;
}

.history-row .bold {
  font-weight: 500;
}

.status-tag {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
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

/* Skeleton */
.skeleton-block {
  padding: 1.5rem;
}

.skeleton-line {
  display: block;
  height: 16px;
  background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
  background-size: 200% 100%;
  animation: skeleton 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

.skeleton-line.short {
  width: 60%;
}

@keyframes skeleton {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
