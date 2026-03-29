<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <img src="/icons/rbac.svg" alt="" />
        </div>
        <h1 class="header-title">权限与角色管理</h1>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="reload" :disabled="loading">
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
        <button class="btn-primary" @click="startCreateRole">
          + 新建角色
        </button>
        <button class="btn-secondary" @click="startCreatePerm">
          + 新建权限
        </button>
      </div>
    </div>

    <!-- 提示消息 -->
    <div v-if="error" class="message message-error">
      {{ error }}
      <button class="close-btn" @click="error = ''">×</button>
    </div>
    <div v-if="success" class="message message-success">
      {{ success }}
      <button class="close-btn" @click="success = ''">×</button>
    </div>

    <!-- 表单组件 -->
    <RoleForm />
    <PermissionForm />

    <!-- 删除确认弹框 -->
    <Teleport to="body">
      <transition name="modal">
        <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDeleteConfirm">
          <div class="confirm-modal">
            <div class="confirm-header">
              <h3>确认删除</h3>
              <button class="close-btn" @click="cancelDeleteConfirm">×</button>
            </div>
            <p class="confirm-text">
              确定删除{{ deleteContext.type === 'role' ? '角色' : '权限' }}
              <strong>“{{ deleteContext.name }}”</strong>吗？
            </p>
            <p class="confirm-warning">该操作不可撤销，请谨慎操作。</p>
            <div class="confirm-actions">
              <button class="btn-secondary" @click="cancelDeleteConfirm">取消</button>
              <button class="btn-danger" @click="confirmDelete">确认删除</button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

    <!-- Tab 切换 -->
    <div class="tab-bar">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'roles' }"
        @click="activeTab = 'roles'"
      >
        角色列表
        <span class="tab-count">{{ roles.length }}</span>
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'permissions' }"
        @click="activeTab = 'permissions'"
      >
        权限列表
        <span class="tab-count">{{ permissions.length }}</span>
      </button>
    </div>

    <!-- 列表组件 -->
    <RoleList v-show="activeTab === 'roles'" />
    <PermissionList v-show="activeTab === 'permissions'" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRbac } from './composables/useRbac';
import RoleForm from './components/RoleForm.vue';
import PermissionForm from './components/PermissionForm.vue';
import RoleList from './components/RoleList.vue';
import PermissionList from './components/PermissionList.vue';

const activeTab = ref('roles');

const {
  loading,
  error,
  success,
  roles,
  permissions,
  showRoleForm,
  showPermForm,
  showDeleteConfirm,
  deleteContext,
  reload,
  startCreateRole,
  startCreatePerm,
  confirmDelete,
  cancelDeleteConfirm
} = useRbac();

onMounted(reload);
</script>

<style scoped>
.page-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  min-height: 400px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon img {
  width: 24px;
  height: 24px;
}

.header-title {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-secondary:disabled,
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 消息提示 */
.message {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  margin: 1rem 1.5rem 0;
  border-radius: 6px;
  font-size: 14px;
}

.message-error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.message-success {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.6;
  color: inherit;
}

.close-btn:hover {
  opacity: 1;
}

/* Tab 切换 */
.tab-bar {
  display: flex;
  gap: 0;
  padding: 0 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  margin-top: 1rem;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-btn:hover {
  color: #374151;
}

.tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}

.tab-count {
  background: #e5e7eb;
  color: #6b7280;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 12px;
}

.tab-btn.active .tab-count {
  background: #dbeafe;
  color: #2563eb;
}

.confirm-modal {
  width: min(420px, 92vw);
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.25);
  padding: 1rem 1rem 0.9rem;
}

.confirm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.65rem;
}

.confirm-header h3 {
  margin: 0;
  font-size: 18px;
  color: #111827;
}

.confirm-text {
  margin: 0;
  color: #374151;
  font-size: 14px;
}

.confirm-warning {
  margin: 0.5rem 0 0;
  font-size: 13px;
  color: #b91c1c;
}

.confirm-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-danger {
  padding: 0.5rem 1rem;
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.btn-danger:hover {
  background: #b91c1c;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.18s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.42);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 6000;
}
</style>
