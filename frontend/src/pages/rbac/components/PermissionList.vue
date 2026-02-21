<template>
  <section class="list-section">
    <div v-if="loadingPerms" class="loading-dots">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>
    <div v-else-if="pageGroups.length" class="page-groups-container">
      <!-- 按页面分组展示 -->
      <div v-for="group in pageGroups" :key="group.name" class="page-group">
        <div class="page-group-header" @click="toggleGroup(group.name)">
          <div class="page-group-icon">
            <img :src="group.icon" alt="" v-if="group.icon" />
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
          </div>
          <span class="page-group-title">{{ group.name }}</span>
          <span class="page-group-count">{{ group.permissions.length }} 个权限</span>
          <svg :class="{ rotated: expandedGroups[group.name] }" class="expand-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </div>
        <transition name="slide">
          <div v-show="expandedGroups[group.name]" class="page-group-content">
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
                <tr v-for="p in group.permissions" :key="p.id">
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
import { ref, reactive, computed } from 'vue';
import { useRbac } from '../composables/useRbac';

const {
  permissions,
  loadingPerms,
  deletingPermId,
  startEditPerm,
  removePerm,
  getPermRoleCount
} = useRbac();

// 展开状态
const expandedGroups = reactive({});

function toggleGroup(name) {
  expandedGroups[name] = !expandedGroups[name];
}

// 按导航栏页面结构分组
const PAGE_GROUP_CONFIG = [
  {
    name: '首页',
    icon: '/icons/dashboard.svg',
    prefixes: ['dashboard.'],
    keys: []
  },
  {
    name: '员工管理',
    icon: '/icons/employees.svg',
    prefixes: ['employee.'],
    keys: []
  },
  {
    name: '入职管理',
    icon: '/icons/employees.svg',
    prefixes: ['onboarding.'],
    keys: []
  },
  {
    name: '考勤管理',
    icon: '/icons/attendance.svg',
    prefixes: ['attendance.'],
    keys: []
  },
  {
    name: '请假管理',
    icon: '/icons/leaves.svg',
    prefixes: ['leave.', 'trip.'],
    keys: []
  },
  {
    name: '薪资管理',
    icon: '/icons/salaries.svg',
    prefixes: ['salary.', 'expense.'],
    keys: []
  },
  {
    name: '职位管理',
    icon: '/icons/positions.svg',
    prefixes: ['position.'],
    keys: []
  },
  {
    name: '部门管理',
    icon: '/icons/departments.svg',
    prefixes: ['department.'],
    keys: []
  },
  {
    name: '文档中心',
    icon: '/icons/documents.svg',
    prefixes: ['document.'],
    keys: []
  },
  {
    name: '大数据报表',
    icon: '/icons/reports.svg',
    prefixes: ['report.'],
    keys: []
  },
  {
    name: 'BI 报表',
    icon: '/icons/stats.svg',
    prefixes: ['bi.'],
    keys: []
  },
  {
    name: '离职管理',
    icon: '/icons/resignation.svg',
    prefixes: ['resignation.'],
    keys: []
  },
  {
    name: '系统管理',
    icon: '/icons/system.svg',
    prefixes: ['system.'],
    keys: []
  },
  {
    name: '权限管理',
    icon: '/icons/rbac.svg',
    prefixes: ['rbac.'],
    keys: []
  },
  {
    name: '用户管理',
    icon: '/icons/users.svg',
    prefixes: ['user.'],
    keys: []
  }
];

// 根据权限key匹配分组
function matchGroup(perm) {
  const key = perm.key;
  for (const group of PAGE_GROUP_CONFIG) {
    // 优先精确匹配
    if (group.keys.includes(key)) return group.name;
    // 前缀匹配
    for (const prefix of group.prefixes) {
      if (key.startsWith(prefix)) return group.name;
    }
  }
  return '其他';
}

// 计算分组后的权限
const pageGroups = computed(() => {
  const groupMap = {};

  // 初始化已配置的分组
  for (const config of PAGE_GROUP_CONFIG) {
    groupMap[config.name] = {
      name: config.name,
      icon: config.icon,
      permissions: []
    };
  }
  groupMap['其他'] = { name: '其他', icon: null, permissions: [] };

  // 分配权限到各分组
  for (const perm of permissions.value) {
    const groupName = matchGroup(perm);
    if (groupMap[groupName]) {
      groupMap[groupName].permissions.push(perm);
    }
  }

  // 返回有权限的分组（按配置顺序）
  const result = [];
  for (const config of PAGE_GROUP_CONFIG) {
    if (groupMap[config.name].permissions.length > 0) {
      result.push(groupMap[config.name]);
      // 默认展开第一个
      if (result.length === 1 && expandedGroups[config.name] === undefined) {
        expandedGroups[config.name] = true;
      }
    }
  }
  if (groupMap['其他'].permissions.length > 0) {
    result.push(groupMap['其他']);
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

/* 页面分组容器 */
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
  border-bottom: 1px solid transparent;
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

/* 折叠动画 */
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
  max-height: 1000px;
}

/* 表格样式 */
.perm-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.perm-table thead {
  /* 使用全局样式 */
}

.perm-table th {
  /* 使用全局样式 */
}

.perm-table td {
  padding: 0.75rem 1rem;
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

/* 空状态和加载状态 */
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
