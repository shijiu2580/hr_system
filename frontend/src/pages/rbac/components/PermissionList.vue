<template>
  <section class="list-section">
    <div v-if="loadingPerms" class="loading-dots">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>
    <div v-else-if="navGroups.length" class="page-groups-container">
      <!-- 一级：侧边栏父导航 -->
      <div v-for="nav in navGroups" :key="nav.name" class="page-group">
        <div class="page-group-header" @click="toggleNav(nav.name)">
          <div class="page-group-icon">
            <img :src="nav.icon" alt="" />
          </div>
          <span class="page-group-title">{{ nav.name }}</span>
          <span class="page-group-count">{{ nav.totalCount }} 个权限</span>
          <svg :class="{ rotated: expandedNavs[nav.name] }" class="expand-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </div>
        <transition name="slide">
          <div v-show="expandedNavs[nav.name]" class="page-group-content">
            <!-- 二级：子菜单分组 -->
            <div v-for="sub in nav.children" :key="sub.name" class="sub-group">
              <div class="sub-group-header" @click.stop="toggleSub(nav.name + '/' + sub.name)">
                <svg :class="{ rotated: expandedSubs[nav.name + '/' + sub.name] }" class="sub-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
                <span class="sub-group-title">{{ sub.name }}</span>
                <span class="sub-group-count">{{ sub.permissions.length }}</span>
              </div>
              <transition name="slide">
                <div v-show="expandedSubs[nav.name + '/' + sub.name]" class="sub-group-content">
                  <table class="perm-table">
                    <thead>
                      <tr>
                        <th style="width:180px;">权限键</th>
                        <th style="width:150px;">权限名称</th>
                        <th>描述</th>
                        <th style="width:80px;">关联角色</th>
                        <th style="width:140px;">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="p in sub.permissions" :key="p.id">
                        <td><code class="key-code">{{ p.key }}</code></td>
                        <td class="name-cell">{{ p.name }}</td>
                        <td class="desc-cell">{{ p.description || '-' }}</td>
                        <td class="count-cell">
                          <span class="badge-count">{{ getPermRoleCount(p) }}</span>
                        </td>
                        <td class="actions-cell">
                          <button class="btn outline small icon-btn" @click="handleEdit(p)">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                            编辑
                          </button>
                          <button class="btn danger small icon-btn" @click="handleRemove(p)" :disabled="deletingPermId===p.id">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                              <polyline points="3 6 5 6 21 6"/>
                              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                            {{ deletingPermId === p.id ? '删除中...' : '删除' }}
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </transition>
            </div>
          </div>
        </transition>
      </div>
    </div>
    <div v-else class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        <line x1="12" y1="16" x2="12" y2="16.01"/>
      </svg>
      <p>暂无权限</p>
      <span>点击上方"新建权限"按钮创建第一个权限</span>
    </div>
  </section>
</template>

<script setup>
import { reactive, computed } from 'vue';
import { useRbac } from '../composables/useRbac';

const {
  permissions,
  loadingPerms,
  deletingPermId,
  startEditPerm,
  removePerm,
  getPermRoleCount
} = useRbac();

// ========== 展开状态 ==========
const expandedNavs = reactive({});   // 一级父导航
const expandedSubs = reactive({});   // 二级子菜单

function toggleNav(name) {
  expandedNavs[name] = !expandedNavs[name];
}
function toggleSub(key) {
  expandedSubs[key] = !expandedSubs[key];
}

// ========== 侧边栏导航结构配置 ==========
// 每个父导航 → 子菜单 → 各子菜单对应的权限 key
const NAV_CONFIG = [
  {
    name: '员工',
    icon: '/icons/employees.svg',
    children: [
      { name: '员工管理', keys: ['employee.create', 'employee.edit', 'employee.delete', 'employee.import', 'employee.export'] },
      { name: '员工列表', keys: ['employee.view'] },
      { name: '入职审核', keys: ['onboarding.view', 'onboarding.view_all', 'onboarding.approve', 'onboarding.reject'] },
    ]
  },
  {
    name: '考勤',
    icon: '/icons/attendance.svg',
    children: [
      { name: '考勤记录', keys: ['attendance.view'] },
      { name: '考勤管理', keys: ['attendance.view_all', 'attendance.create', 'attendance.edit'] },
      { name: '考勤地点', keys: ['attendance.location'] },
      { name: '补签审批', keys: ['attendance.approve'] },
    ]
  },
  {
    name: '请假',
    icon: '/icons/leaves.svg',
    children: [
      { name: '请假申请', keys: ['leave.view', 'leave.create'] },
      { name: '出差申请', keys: ['trip.view', 'trip.create'] },
      { name: '审批流程', keys: ['leave.view_all', 'leave.approve', 'trip.view_all', 'trip.approve'] },
    ]
  },
  {
    name: '薪资',
    icon: '/icons/salaries.svg',
    children: [
      { name: '薪资管理', keys: ['salary.view_all', 'salary.create', 'salary.edit', 'salary.delete', 'salary.disburse'] },
      { name: '薪资记录', keys: ['salary.view'] },
      { name: '差旅报销', keys: ['expense.view', 'expense.create'] },
      { name: '报销审批', keys: ['expense.view_all', 'expense.approve'] },
    ]
  },
  {
    name: '职位',
    icon: '/icons/positions.svg',
    children: [
      { name: '职位管理', keys: ['position.view', 'position.create', 'position.edit', 'position.delete'] },
    ]
  },
  {
    name: '部门',
    icon: '/icons/departments.svg',
    children: [
      { name: '部门管理', keys: ['department.view', 'department.create', 'department.edit', 'department.delete'] },
    ]
  },
  {
    name: '文档中心',
    icon: '/icons/documents.svg',
    children: [
      { name: '文档管理', keys: ['document.view', 'document.create', 'document.edit', 'document.upload', 'document.delete', 'document.manage'] },
    ]
  },
  {
    name: '报表',
    icon: '/icons/reports.svg',
    children: [
      { name: '大数据报表', keys: ['report.view', 'report.export', 'report.employee', 'report.attendance', 'report.salary', 'report.leave'] },
      { name: 'BI 报表', keys: ['bi.view', 'bi.department_cost', 'bi.attendance_heat', 'bi.turnover', 'bi.salary_range', 'bi.leave_balance', 'bi.daily_attendance'] },
    ]
  },
  {
    name: '离职申请',
    icon: '/icons/resignation.svg',
    children: [
      { name: '离职进度', keys: ['resignation.view'] },
      { name: '发起申请', keys: ['resignation.create'] },
      { name: '离职审批', keys: ['resignation.view_all', 'resignation.approve'] },
    ]
  },
  {
    name: '系统',
    icon: '/icons/system.svg',
    children: [
      { name: '系统管理', keys: ['system.view', 'system.log', 'system.log_view', 'system.log_clear', 'system.backup', 'system.backup_view', 'system.backup_create', 'system.backup_restore', 'system.restore'] },
    ]
  },
  {
    name: '权限管理',
    icon: '/icons/rbac.svg',
    children: [
      { name: '角色与权限', keys: ['rbac.view', 'rbac.manage', 'rbac.role_manage', 'rbac.permission_manage'] },
    ]
  },
  {
    name: '用户管理',
    icon: '/icons/users.svg',
    children: [
      { name: '用户管理', keys: ['user.view', 'user.create', 'user.edit', 'user.delete', 'user.reset_password'] },
    ]
  },
];

// ========== 计算二级分组结构 ==========
const navGroups = computed(() => {
  // 建立 key → perm 映射
  const permMap = {};
  for (const p of permissions.value) {
    permMap[p.key] = p;
  }

  const result = [];
  let firstNav = true;

  for (const nav of NAV_CONFIG) {
    const children = [];
    let totalCount = 0;

    for (const sub of nav.children) {
      const matched = sub.keys.map(k => permMap[k]).filter(Boolean);
      if (matched.length > 0) {
        children.push({ name: sub.name, permissions: matched });
        totalCount += matched.length;
      }
    }

    if (children.length > 0) {
      result.push({ name: nav.name, icon: nav.icon, children, totalCount });
      // 默认展开第一个父导航及其所有子分组
      if (firstNav) {
        if (expandedNavs[nav.name] === undefined) expandedNavs[nav.name] = true;
        for (const sub of children) {
          const subKey = nav.name + '/' + sub.name;
          if (expandedSubs[subKey] === undefined) expandedSubs[subKey] = true;
        }
        firstNav = false;
      }
    }
  }

  // 检查是否有未分配的权限
  const allConfigKeys = new Set();
  for (const nav of NAV_CONFIG) {
    for (const sub of nav.children) {
      for (const k of sub.keys) allConfigKeys.add(k);
    }
  }
  const orphans = permissions.value.filter(p => !allConfigKeys.has(p.key));
  if (orphans.length > 0) {
    result.push({
      name: '其他',
      icon: null,
      children: [{ name: '未分类权限', permissions: orphans }],
      totalCount: orphans.length
    });
  }

  return result;
});

function handleEdit(p) {
  startEditPerm(p);
}

function handleRemove(p) {
  removePerm(p);
}
</script>

<style scoped>
.list-section {
  padding: 1.5rem;
}

/* ===== 一级：父导航分组 ===== */
.page-groups-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.page-group {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
  transition: box-shadow 0.2s;
}

.page-group:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.page-group-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: linear-gradient(to right, #f9fafb, #fff);
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
}

.page-group-header:hover {
  background: linear-gradient(to right, #f3f4f6, #f9fafb);
}

.page-group-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #eff6ff;
  color: #2563eb;
}

.page-group-icon img {
  width: 18px;
  height: 18px;
  object-fit: contain;
}

.page-group-title {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.page-group-count {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.25rem 0.625rem;
  border-radius: 12px;
}

.expand-arrow {
  color: #9ca3af;
  transition: transform 0.25s ease;
}

.expand-arrow.rotated {
  transform: rotate(90deg);
}

.page-group-content {
  border-top: 1px solid #e5e7eb;
}

/* ===== 二级：子菜单分组 ===== */
.sub-group {
  border-bottom: 1px solid #f3f4f6;
}

.sub-group:last-child {
  border-bottom: none;
}

.sub-group-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem 0.625rem 1.5rem;
  background: #fafbfc;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}

.sub-group-header:hover {
  background: #f3f4f6;
}

.sub-arrow {
  color: #9ca3af;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.sub-arrow.rotated {
  transform: rotate(90deg);
}

.sub-group-title {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}

.sub-group-count {
  font-size: 11px;
  color: #9ca3af;
  background: #f3f4f6;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

.sub-group-content {
  background: #fff;
}

/* ===== 折叠动画 ===== */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  max-height: 2000px;
}

/* ===== 表格样式 ===== */
.perm-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.perm-table th {
  padding: 0.5rem 1rem 0.5rem 1.5rem;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: #fafbfc;
  border-bottom: 1px solid #f3f4f6;
}

.perm-table td {
  padding: 0.625rem 1rem 0.625rem 1.5rem;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.perm-table tbody tr:last-child td {
  border-bottom: none;
}

.perm-table tbody tr:hover {
  background: #fafbfc;
}

.key-code {
  display: inline-block;
  background: #f3f4f6;
  color: #374151;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
}

.name-cell {
  font-weight: 500;
  color: #1f2937;
}

.desc-cell {
  color: #6b7280;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.count-cell {
  text-align: center;
}

.badge-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
  font-weight: 500;
}

.actions-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* ===== 按钮 ===== */
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

/* ===== 空状态和加载状态 ===== */
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

.loading-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 2rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2563eb;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
