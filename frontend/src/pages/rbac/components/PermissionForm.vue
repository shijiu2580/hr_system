<template>
  <Teleport to="body">
    <transition name="modal">
      <div v-if="showPermForm" class="modal-overlay" @click.self="handleCancel">
        <div class="modal-container">
          <!-- 弹窗头部 -->
          <div class="modal-header">
            <div class="modal-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <h3>{{ editingPerm ? '编辑权限' : '新建权限' }}</h3>
            </div>
            <button class="close-btn" @click="handleCancel" type="button">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- 弹窗内容 -->
          <form @submit.prevent="handleSubmit" class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label>权限键 <span class="required">*</span></label>
                <div class="tree-select" :class="{ disabled: !!editingPerm }" ref="keySelectRef">
                  <button
                    type="button"
                    class="tree-trigger"
                    :disabled="!!editingPerm"
                    @click="toggleKeyMenu"
                  >
                    <span>{{ selectedKeyLabel || '请选择权限键' }}</span>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <polyline points="6 9 12 15 18 9"/>
                    </svg>
                  </button>
                  <div v-if="showKeyMenu" class="tree-dropdown">
                    <div v-for="nav in navKeyGroups" :key="nav.name" class="tree-group">
                      <button type="button" class="tree-group-head" @click="toggleNav(nav.name)">
                        <svg :class="{ expanded: expandedNavs[nav.name] }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                          <polyline points="9 18 15 12 9 6"/>
                        </svg>
                        <span>{{ nav.name }}</span>
                        <span class="tree-count">{{ nav.options.length }}</span>
                      </button>
                      <div v-show="expandedNavs[nav.name]" class="tree-options">
                        <button
                          v-for="opt in nav.options"
                          :key="opt.value"
                          type="button"
                          class="tree-option"
                          :class="{ active: permForm.key === opt.value }"
                          @click="selectKey(opt.value)"
                        >
                          {{ opt.label }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <span class="form-hint">权限的唯一标识符，创建后不可修改</span>
              </div>
              <div class="form-group">
                <label>权限名称 <span class="required">*</span></label>
                <input
                  v-model.trim="permForm.name"
                  required
                  placeholder="例如：查看员工"
                />
              </div>
            </div>
            <div class="form-group">
              <label>权限描述</label>
              <textarea
                v-model.trim="permForm.description"
                rows="3"
                placeholder="可选，描述此权限的用途"
              ></textarea>
            </div>

            <!-- 弹窗底部 -->
            <div class="modal-footer">
              <button class="btn btn-primary" type="submit" :disabled="savingPerm">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                {{ savingPerm ? '保存中...' : '保存' }}
              </button>
              <button class="btn btn-secondary" type="button" @click="handleCancel">
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { computed, reactive, ref, watch, onMounted, onUnmounted } from 'vue';
import { useRbac } from '../composables/useRbac';

const {
  showPermForm,
  editingPerm,
  savingPerm,
  permForm,
  permissions,
  permissionGroups,
  submitPerm,
  cancelPerm
} = useRbac();

const NAV_CONFIG = [
  { name: '员工', keys: ['employee.view', 'employee.create', 'employee.edit', 'employee.delete', 'employee.import', 'employee.export', 'onboarding.view', 'onboarding.view_all', 'onboarding.approve', 'onboarding.reject'] },
  { name: '考勤', keys: ['attendance.view', 'attendance.view_all', 'attendance.create', 'attendance.edit', 'attendance.location', 'attendance.approve'] },
  { name: '请假', keys: ['leave.view', 'leave.create', 'leave.view_all', 'leave.approve', 'trip.view', 'trip.create', 'trip.view_all', 'trip.approve'] },
  { name: '薪资', keys: ['salary.view', 'salary.view_all', 'salary.create', 'salary.edit', 'salary.delete', 'salary.disburse', 'expense.view', 'expense.create', 'expense.view_all', 'expense.approve'] },
  { name: '职位', keys: ['position.view', 'position.create', 'position.edit', 'position.delete'] },
  { name: '部门', keys: ['department.view', 'department.create', 'department.edit', 'department.delete'] },
  { name: '文档中心', keys: ['document.view', 'document.create', 'document.edit', 'document.upload', 'document.delete', 'document.manage'] },
  { name: '报表', keys: ['report.view', 'report.export', 'report.employee', 'report.attendance', 'report.salary', 'report.leave', 'bi.view', 'bi.department_cost', 'bi.attendance_heat', 'bi.turnover', 'bi.salary_range', 'bi.leave_balance', 'bi.daily_attendance'] },
  { name: '离职申请', keys: ['resignation.view', 'resignation.view_all', 'resignation.create', 'resignation.approve'] },
  { name: '系统', keys: ['system.view', 'system.log', 'system.log_view', 'system.log_clear', 'system.backup', 'system.backup_view', 'system.backup_create', 'system.backup_restore', 'system.restore'] },
  { name: '权限管理', keys: ['rbac.view', 'rbac.manage', 'rbac.role_manage', 'rbac.permission_manage'] },
  { name: '用户管理', keys: ['user.view', 'user.create', 'user.edit', 'user.delete', 'user.reset_password'] },
];

const showKeyMenu = ref(false);
const keySelectRef = ref(null);
const expandedNavs = reactive({});

const allKeyMap = computed(() => {
  const map = new Map();
  for (const group of permissionGroups.value || []) {
    for (const p of group.permissions || []) {
      if (p?.key) map.set(p.key, p.name || p.key);
    }
  }
  if (!map.size) {
    for (const p of permissions.value || []) {
      if (p?.key) map.set(p.key, p.name || p.key);
    }
  }
  return map;
});

const navKeyGroups = computed(() => {
  const groups = [];
  const used = new Set();
  for (const nav of NAV_CONFIG) {
    const opts = [];
    for (const key of nav.keys) {
      if (!allKeyMap.value.has(key)) continue;
      used.add(key);
      opts.push({ value: key, label: `${key} - ${allKeyMap.value.get(key)}` });
    }
    if (opts.length) groups.push({ name: nav.name, options: opts });
  }

  const orphan = [];
  for (const [key, name] of allKeyMap.value.entries()) {
    if (!used.has(key)) orphan.push({ value: key, label: `${key} - ${name}` });
  }
  if (orphan.length) groups.push({ name: '其他', options: orphan.sort((a, b) => a.value.localeCompare(b.value)) });
  return groups;
});

const selectedKeyLabel = computed(() => {
  if (!permForm.value?.key) return '';
  for (const nav of navKeyGroups.value) {
    const found = nav.options.find((o) => o.value === permForm.value.key);
    if (found) return found.label;
  }
  return permForm.value.key;
});

watch(showKeyMenu, (open) => {
  if (!open) return;
  for (const nav of navKeyGroups.value) {
    if (expandedNavs[nav.name] === undefined) expandedNavs[nav.name] = false;
  }
});

watch(showPermForm, (visible) => {
  if (!visible) showKeyMenu.value = false;
});

function toggleKeyMenu() {
  if (editingPerm.value) return;
  showKeyMenu.value = !showKeyMenu.value;
}

function toggleNav(name) {
  expandedNavs[name] = !expandedNavs[name];
}

function selectKey(key) {
  permForm.value.key = key;
  showKeyMenu.value = false;
}

function onClickOutside(e) {
  if (!showKeyMenu.value) return;
  if (keySelectRef.value && !keySelectRef.value.contains(e.target)) {
    showKeyMenu.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside);
});

function handleSubmit() {
  if (!permForm.value?.key) return;
  submitPerm();
}

function handleCancel() {
  cancelPerm();
}
</script>

<style scoped>
/* 弹窗遮罩 */
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
  padding: 1rem;
}

/* 弹窗容器 */
.modal-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 弹窗头部 */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-title svg {
  color: #2563eb;
}

.modal-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: #6b7280;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

/* 弹窗内容 */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
}

/* 表单网格 */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

@media (max-width: 500px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #dc2626;
}

.form-hint {
  font-size: 11px;
  color: #9ca3af;
}

.tree-select {
  position: relative;
}

.tree-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #fff;
  padding: 0.5rem 0.75rem;
  font-size: 14px;
  color: #374151;
  text-align: left;
  cursor: pointer;
}

.tree-trigger:hover {
  border-color: #9ca3af;
}

.tree-select.disabled .tree-trigger {
  background: #f3f4f6;
  cursor: not-allowed;
  color: #9ca3af;
}

.tree-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  max-height: 280px;
  overflow: auto;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #fff;
  z-index: 1400;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
}

.tree-group {
  border-bottom: 1px solid #f1f5f9;
}

.tree-group:last-child {
  border-bottom: none;
}

.tree-group-head {
  width: 100%;
  border: none;
  background: #f8fafc;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.55rem 0.7rem;
  cursor: pointer;
  color: #334155;
  font-size: 13px;
  font-weight: 600;
}

.tree-group-head svg {
  transition: transform 0.18s ease;
}

.tree-group-head svg.expanded {
  transform: rotate(90deg);
}

.tree-count {
  margin-left: auto;
  font-size: 12px;
  color: #64748b;
}

.tree-options {
  padding: 0.3rem;
}

.tree-option {
  width: 100%;
  border: none;
  background: transparent;
  text-align: left;
  padding: 0.42rem 0.5rem;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
}

.tree-option:hover {
  background: #f1f5f9;
}

.tree-option.active {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 600;
}

.form-group input,
.form-group textarea {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: none;
}

.form-group input:disabled,
.form-group textarea:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

/* 弹窗底部 */
.modal-footer {
  display: flex;
  gap: 0.5rem;
  padding-top: 1rem;
  margin-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background: #2563eb;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 弹窗动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95) translateY(-20px);
}
</style>
