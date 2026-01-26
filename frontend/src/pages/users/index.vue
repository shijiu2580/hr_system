<template>
  <div class="users-page">
    <section class="hero-panel">
      <div class="hero-info">
        <div class="hero-icon">
          <img src="/icons/users.svg" alt="" style="width:100%;height:100%;" />
        </div>
        <div>
          <h1>用户管理</h1>
          <p class="hero-text">系统账号与角色管理</p>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn-primary icon-btn" @click="router.push('/users/create')">
          <img src="/icons/add.svg" alt="" class="btn-icon" />
          <span>新增用户</span>
        </button>
        <button class="btn-secondary icon-btn" @click="reload" :disabled="loading">
          <img src="/icons/refresh.svg" alt="" class="btn-icon" />
          <span>{{ loading ? '刷新中...' : '刷新' }}</span>
        </button>
      </div>
    </section>

    <transition name="fade">
      <div v-if="error" class="alert alert-error">
        <div class="alert-text">{{ error }}</div>
        <button type="button" class="alert-close" @click="error = ''">×</button>
      </div>
    </transition>

    <section class="card metrics-card" v-if="!loading">
      <header class="card-header">
        <div class="section-title">
          <img src="/icons/stats.svg" alt="" class="section-icon" />
          <h2>账号概览</h2>
        </div>
      </header>
      <div class="metrics-grid">
        <div class="metric-card">
          <span class="metric-label">用户数量</span>
          <strong class="metric-value">{{ summary.total }}</strong>
          <span class="metric-desc">含所有角色类型。</span>
        </div>
        <div class="metric-card highlight">
          <span class="metric-label">已激活</span>
          <strong class="metric-value">{{ summary.activeCount }}</strong>
          <span class="metric-desc">激活率 {{ activeRatio }}%</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">管理员</span>
          <strong class="metric-value">{{ summary.staffCount }}</strong>
          <span class="metric-desc">包含超管</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">超级管理员</span>
          <strong class="metric-value">{{ summary.superCount }}</strong>
          <span class="metric-desc">拥有全部权限</span>
        </div>
      </div>
    </section>

    <!-- 筛选栏 -->
    <section class="filters-bar">
      <div class="filter-item filter-search">
        <input
          v-model.trim="q"
          @keyup.enter="applyFilters"
          placeholder="搜索用户名 / 邮箱"
          class="filter-input"
        />
      </div>
      <CustomSelect
        v-model="active"
        :options="[{ value: '', label: '全部状态' }, { value: '1', label: '激活' }, { value: '0', label: '禁用' }]"
        placeholder="全部状态"
        class="filter-select"
        @change="applyFilters"
      />
      <CustomSelect
        v-model="staff"
        :options="[{ value: '', label: '全部权限' }, { value: '1', label: '管理员' }, { value: 'super', label: '超级管理员' }]"
        placeholder="全部权限"
        class="filter-select"
        @change="applyFilters"
      />
      <button class="btn-query" type="button" @click="applyFilters" :disabled="loading">查询</button>
      <button class="btn-reset" type="button" @click="resetFilters" :disabled="loading">重置</button>
    </section>

    <section class="card table-card">
      <header class="card-header">
        <div class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="16" rx="2" />
            <path d="M3 10h18" />
          </svg>
          <h2>用户列表</h2>
        </div>
        <span class="section-hint">{{ users.length ? `共 ${users.length} 条` : '暂无数据' }}</span>
      </header>

      <div v-if="loading" class="table-skeleton">
        <div class="skeleton-row" v-for="n in 6" :key="`user-skeleton-${n}`"></div>
      </div>

      <template v-else>
        <div v-if="users.length" class="table-container">
          <table class="user-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>员工编号</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>状态</th>
                <th>权限</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id" :class="{ 'row-inactive': !u.is_active }">
                <td>{{ u.id }}</td>
                <td>{{ u.employee_id || '-' }}</td>
                <td>
                  <div class="name-cell">
                    <span>{{ u.username }}</span>
                    <span v-if="u.has_employee" class="tag tag-employee">员工</span>
                  </div>
                </td>
                <td>{{ u.email || '未填写' }}</td>
                <td>
                  <div class="role-chips" v-if="u.roles?.length">
                    <span v-for="role in u.roles" :key="role.id" class="chip">{{ role.name }}</span>
                  </div>
                  <span v-else class="muted">未分配角色</span>
                </td>
                <td>
                  <span class="status-pill" :class="u.is_active ? 'success' : 'danger'">
                    {{ u.is_active ? '激活' : '禁用' }}
                  </span>
                </td>
                <td>
                  <span v-if="u.is_superuser" class="permission-pill super">超管</span>
                  <span v-else-if="u.is_staff" class="permission-pill admin">管理员</span>
                  <span v-else class="permission-pill default">普通用户</span>
                </td>
                <td>
                  <div class="row-actions">
                    <button class="btn-ghost btn-xs" @click="router.push(`/users/${u.id}/edit`)">编辑</button>
                    <button class="btn-danger btn-xs" @click="confirmDelete(u)" :disabled="deletingId === u.id">
                      {{ deletingId === u.id ? '删除中...' : '删除' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty">暂无符合条件的用户</p>
      </template>
    </section>

    <dialog ref="confirmDialog" class="confirm-dialog">
      <div class="dialog-banner">操作确认</div>
      <h3>删除用户</h3>
      <p>确定要删除 <strong>{{ toDelete?.username }}</strong> 吗？</p>
      <div class="dialog-actions">
        <button class="btn-danger" type="button" @click="openSecondConfirm" :disabled="deletingId === toDelete?.id">继续</button>
        <button class="btn-ghost" type="button" @click="closeDialog">取消</button>
      </div>
    </dialog>
    <dialog ref="confirmDialog2" class="confirm-dialog">
      <div class="dialog-banner warning">危险操作</div>
      <h3>二次确认</h3>
      <p>此操作 <strong class="text-danger">不可撤销</strong>，确认删除 <strong>{{ toDelete?.username }}</strong> 吗？</p>
      <div class="dialog-actions">
        <button class="btn-danger" type="button" @click="doDelete" :disabled="deletingId === toDelete?.id">永久删除</button>
        <button class="btn-ghost" type="button" @click="closeSecond">返回</button>
      </div>
    </dialog>
  </div>
</template>
<script setup>
import { ref, onMounted, nextTick, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../utils/api';
import CustomSelect from '../../components/CustomSelect.vue';

const router = useRouter();

const users = ref([]);
const loading = ref(false);
const error = ref('');
const deletingId = ref(null);
const toDelete = ref(null);
const confirmDialog = ref(null);
const confirmDialog2 = ref(null);
const q = ref('');
const active = ref('');
const staff = ref('');

const summary = computed(() => {
  const list = users.value || [];
  const total = list.length;
  const activeCount = list.filter((user) => user.is_active).length;
  const staffCount = list.filter((user) => user.is_staff || user.is_superuser).length;
  const superCount = list.filter((user) => user.is_superuser).length;
  return { total, activeCount, staffCount, superCount };
});

const activeRatio = computed(() => {
  if (!summary.value.total) return 0;
  return Math.round((summary.value.activeCount / summary.value.total) * 100);
});

async function loadUsers() {
  loading.value = true; error.value = '';
  try {
    const params = {};
    if (q.value) params.q = q.value;
    if (active.value !== '') params.is_active = active.value;
    if (staff.value === '1') params.is_staff = '1';
    else if (staff.value === 'super') params.is_superuser = '1';

    const res = await api.get('/users/manage/', { params });
    if (res.success) {
      const data = res.data;
      users.value = data.results || data;
    } else {
      error.value = res.error?.message || '加载失败';
    }
  } catch (e) {
    error.value = '加载失败';
  } finally {
    loading.value = false;
  }
}

function confirmDelete(user) { toDelete.value = user; confirmDialog.value.showModal(); }
function openSecondConfirm() { if (confirmDialog.value) { confirmDialog.value.close(); } if (confirmDialog2.value) { confirmDialog2.value.showModal(); } }
function closeSecond() { if (confirmDialog2.value) { confirmDialog2.value.close(); } }
function closeDialog() { confirmDialog.value.close(); toDelete.value = null; }

async function doDelete() {
  if (!toDelete.value) return;
  deletingId.value = toDelete.value.id; error.value = '';
  try {
    await api.delete(`/users/manage/${toDelete.value.id}/`);
    await loadUsers();
  } catch (e) {
    error.value = extractErr(e);
  } finally {
    deletingId.value = null; closeDialog(); closeSecond();
  }
}

function extractErr(e) {
  return e.response?.data?.error?.message || e.response?.data?.detail || '操作失败';
}

function reload() { loadUsers(); }
function applyFilters() { loadUsers(); }
function resetFilters() { q.value = ''; active.value = ''; staff.value = ''; loadUsers(); }

onMounted(async () => {
  await loadUsers();
});
</script>

<style scoped>
.users-page {
  display: flex;
  flex-direction: column;
  gap: 1.6rem;
  padding-bottom: 2rem;
}

.hero-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.2rem;
  flex-wrap: wrap;
  padding: 1.6rem 1.8rem;
  border-radius: 12px;
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
}

.hero-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1 1 320px;
}

.hero-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-panel h1 {
  margin: 0 0 0.2rem;
  font-size: 26px;
  color: #0f172a;
}

.hero-text {
  margin: 0;
  font-size: 14px;
  color: #475569;
  max-width: 520px;
}

.hero-actions {
  display: flex;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.6rem 1.1rem;
  border-radius: 10px;
  font-weight: 500;
  letter-spacing: 0.01em;
}

.btn-primary {
  background: #4f46e5;
  color: #fff;
  border: none;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary:not(:disabled):hover {
  background: #4338ca;
}

.btn-secondary {
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: #fff;
  color: #475569;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary:not(:disabled):hover {
  background: #f8fafc;
  border-color: rgba(148, 163, 184, 0.6);
}

.alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  font-size: 13px;
}

.alert-error {
  background: rgba(254, 242, 242, 0.8);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #b91c1c;
}

.alert-text {
  flex: 1;
  margin-right: 0.8rem;
}

.alert-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: inherit;
}

.card {
  background: #fff;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.4);
  padding: 1.5rem 1.6rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: border-color 0.2s ease;
}

.card:hover {
  border-color: rgba(148, 163, 184, 0.6);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.section-title {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #0f172a;
}

.section-title h2 {
  margin: 0;
  font-size: inherit;
  font-weight: inherit;
  line-height: 1;
}

.section-title svg {
  width: 18px;
  height: 18px;
  color: #4f46e5;
  flex-shrink: 0;
}

.section-title img {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.btn-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.section-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.section-hint {
  font-size: 12px;
  color: #94a3b8;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metric-card {
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  padding: 1.1rem 1.2rem;
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  transition: border-color 0.2s ease;
}

.metric-card:hover {
  border-color: rgba(148, 163, 184, 0.6);
}

.metric-card.highlight {
  background: #f8fafc;
}

.metric-label {
  font-size: 12px;
  color: #94a3b8;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.metric-value {
  font-size: 26px;
  color: #0f172a;
  font-weight: 700;
}

.metric-desc {
  font-size: 13px;
  color: #64748b;
}

/* 筛选栏 - 统一风格 */
.filters-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-item.filter-search {
  width: 180px;
  flex-shrink: 0;
}

.filter-input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  background: #fff;
  font-size: 13px;
  color: #334155;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s, background 0.15s;
}

.filter-input::placeholder {
  color: #94a3b8;
}

.filter-input:hover,
.filter-input:focus {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}

.filter-select {
  width: 130px;
  flex-shrink: 0;
}

.filter-select:deep(.custom-select) {
  width: 130px;
}

.btn-query {
  flex-shrink: 0;
  padding: 0 16px;
  height: 36px;
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-query:hover:not(:disabled) {
  background: #4338ca;
}

.btn-query:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-reset {
  padding: 0 16px;
  height: 36px;
  background: #fff;
  color: #475569;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-reset:hover:not(:disabled) {
  background: #f8fafc;
  border-color: rgba(148, 163, 184, 0.6);
}

.btn-reset:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-ghost {
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: #fff;
  color: #475569;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.btn-ghost:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-ghost:not(:disabled):hover {
  background: #f8fafc;
  border-color: rgba(148, 163, 184, 0.6);
}

.link-btn {
  background: none;
  border: none;
  font-size: 13px;
  color: #4f46e5;
  cursor: pointer;
}

.form-shell {
  border: 1px dashed rgba(99, 102, 241, 0.3);
  border-radius: 16px;
  padding: 1.2rem 1.3rem;
  background: rgba(255, 255, 255, 0.94);
}

.table-card .table-container {
  overflow-x: auto;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 780px;
}

.user-table thead th {
  text-align: left;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.6rem 0.75rem;
  color: #94a3b8;
  border-bottom: 1px solid rgba(148, 163, 184, 0.3);
}

.user-table tbody td {
  padding: 0.75rem 0.75rem;
  font-size: 14px;
  color: #1f2937;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  vertical-align: top;
}

.user-table tbody tr:hover {
  background: #f8fafc;
}

.user-table tbody tr.row-inactive {
  opacity: 0.78;
}

.col-actions {
  width: 160px;
}

.name-cell {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-size: 11px;
  letter-spacing: 0.04em;
}

.tag-employee {
  background: rgba(16, 185, 129, 0.18);
  color: #059669;
}

.role-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.chip {
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  background: rgba(148, 163, 184, 0.18);
  font-size: 12px;
  color: #475569;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.8rem;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.status-pill.success {
  background: rgba(134, 239, 172, 0.35);
  color: #15803d;
}

.status-pill.danger {
  background: rgba(248, 113, 113, 0.35);
  color: #b91c1c;
}

.permission-pill {
  display: inline-flex;
  padding: 0.25rem 0.6rem;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.permission-pill.super {
  background: rgba(248, 113, 113, 0.35);
  color: #b91c1c;
}

.permission-pill.admin {
  background: rgba(251, 191, 36, 0.35);
  color: #92400e;
}

.permission-pill.default {
  background: rgba(148, 163, 184, 0.25);
  color: #475569;
}

.row-actions {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.btn-xs {
  padding: 0.38rem 0.78rem;
  border-radius: 8px;
  font-size: 12px;
}

.btn-danger {
  background: #dc2626;
  border: none;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger:not(:disabled):hover {
  background: #b91c1c;
}

.row-actions .btn-ghost,
.row-actions .btn-danger {
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: transparent;
  color: #1e293b;
  box-shadow: none;
  transform: none;
}

.row-actions .btn-ghost:not(:disabled):hover,
.row-actions .btn-danger:not(:disabled):hover {
  background: transparent;
  opacity: 0.85;
  box-shadow: none;
  transform: none;
}

.table-skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.skeleton-row {
  height: 48px;
  border-radius: 8px;
  background: linear-gradient(90deg, #f3f4f6, #e5e7eb, #f3f4f6);
  background-size: 200% 100%;
  animation: skeleton 1.2s infinite;
}

.empty {
  font-size: 13px;
  color: #94a3b8;
  text-align: center;
}

.confirm-dialog {
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  padding: 1.2rem 1.3rem 1rem;
  background: #fff;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.25);
  max-width: 360px;
}

.confirm-dialog::backdrop {
  background: rgba(15, 23, 42, 0.4);
}

.dialog-banner {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: #f1f5f9;
  color: #475569;
  margin-bottom: 0.6rem;
}

.dialog-banner.warning {
  background: #fef2f2;
  color: #b91c1c;
}

.confirm-dialog h3 {
  margin: 0 0 0.5rem;
  font-size: 18px;
  color: #0f172a;
}

.confirm-dialog p {
  margin: 0;
  font-size: 13px;
  color: #475569;
}

.dialog-actions {
  display: flex;
  gap: 0.8rem;
  margin-top: 1rem;
}

.dialog-actions .btn-danger,
.dialog-actions .btn-ghost {
  flex: 1;
}

.text-danger {
  color: #dc2626;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

@keyframes skeleton {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (max-width: 640px) {
  .card {
    padding: 1.35rem;
  }
  .hero-panel {
    padding: 1.4rem;
  }
  .user-table {
    min-width: 640px;
  }
  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-item.filter-search {
    width: 100%;
  }
  .filter-select {
    width: 100%;
  }
}

@media (max-width: 520px) {
  .row-actions {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-xs {
    width: 100%;
  }
}
</style>
