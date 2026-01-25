<template>
  <section class="list-section">
    <div class="section-header">
      <div class="section-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
        <h3>角色列表</h3>
        <span class="badge-count">{{ roles.length }}</span>
      </div>
    </div>
    <div v-if="loadingRoles" class="loading-state">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>
    <div v-else-if="roles.length" class="role-cards">
      <div v-for="r in roles" :key="r.id" class="role-card" :class="{ system: r.is_system }">
        <div class="role-header">
          <div class="role-icon" :class="{ system: r.is_system }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div class="role-title">
            <strong>{{ r.name }}</strong>
            <code>{{ r.code }}</code>
          </div>
          <span v-if="r.is_system" class="badge system">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            系统
          </span>
          <span v-else class="badge custom">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
              <path d="M12 20h9"/>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
            </svg>
            自定义
          </span>
        </div>
        <p class="role-desc">{{ r.description || '暂无描述' }}</p>
        <div class="role-meta">
          <div class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <strong>{{ r.permissions.length }}</strong> 个权限
          </div>
          <div class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <strong>{{ getRoleUserCount(r) }}</strong> 个用户
          </div>
        </div>
        <div class="role-perms" v-if="r.permissions.length">
          <span v-for="p in r.permissions.slice(0, 5)" :key="p.id" class="perm-tag">{{ p.name }}</span>
          <span v-if="r.permissions.length > 5" class="perm-more">+{{ r.permissions.length - 5 }}</span>
        </div>
        <div class="role-actions">
          <button class="btn outline small icon-btn" @click="handleEdit(r)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            编辑
          </button>
          <button v-if="!r.is_system" class="btn danger small icon-btn" @click="handleRemove(r)" :disabled="deletingRoleId===r.id">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            {{ deletingRoleId === r.id ? '删除中...' : '删除' }}
          </button>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <line x1="17" y1="11" x2="23" y2="11"/>
      </svg>
      <p>暂无角色</p>
      <span>点击上方"新建角色"按钮创建第一个角色</span>
    </div>
  </section>
</template>

<script setup>
import { useRbac } from '../composables/useRbac';

const {
  roles,
  loadingRoles,
  deletingRoleId,
  startEditRole,
  removeRole,
  getRoleUserCount
} = useRbac();

function handleEdit(r) {
  startEditRole(r);
}

function handleRemove(r) {
  removeRole(r);
}
</script>

<style scoped>
.list-section {
  padding: 1.5rem;
}

.section-header {
  display: none;
}

.role-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.role-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #fff;
  transition: box-shadow 0.2s;
}

.role-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.role-card.system {
  border-left: 3px solid #2563eb;
}

.role-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.role-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #eff6ff;
  color: #2563eb;
}

.role-icon.system {
  background: #dbeafe;
}

.role-title {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.role-title strong {
  font-size: 14px;
  color: #1f2937;
}

.role-title code {
  font-size: 11px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-family: monospace;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.badge svg {
  width: 12px;
  height: 12px;
}

.badge.system {
  background: #dbeafe;
  color: #1d4ed8;
}

.badge.custom {
  background: #dcfce7;
  color: #16a34a;
}

.role-desc {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
  margin: 0;
}

.role-meta {
  display: flex;
  gap: 1rem;
  font-size: 12px;
  color: #9ca3af;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.meta-item svg {
  width: 14px;
  height: 14px;
  color: #2563eb;
}

.meta-item strong {
  color: #374151;
  font-weight: 600;
}

.role-perms {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.perm-tag {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 11px;
  background: #f3f4f6;
  color: #6b7280;
}

.perm-more {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 11px;
  background: #dbeafe;
  color: #2563eb;
}

.role-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn.small {
  padding: 0.25rem 0.5rem;
}

.btn svg {
  width: 14px;
  height: 14px;
}

.btn.outline {
  border: 1px solid #d1d5db;
  color: #374151;
  background: #fff;
}

.btn.outline:hover {
  background: #f3f4f6;
}

.btn.danger {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.btn.danger:hover {
  background: #fee2e2;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 3rem 1rem;
  color: #9ca3af;
}

.empty-state svg {
  color: #d1d5db;
}

.empty-state p {
  margin: 0;
  font-weight: 500;
  color: #6b7280;
}

.empty-state span {
  font-size: 13px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: #6b7280;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #e5e7eb;
  border-top-color: #2563eb;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
