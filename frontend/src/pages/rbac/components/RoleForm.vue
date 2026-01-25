<template>
  <Teleport to="body">
    <transition name="modal">
      <div v-if="showRoleForm" class="modal-overlay" @click.self="handleCancel">
        <div class="modal-container">
          <!-- 弹窗头部 -->
          <div class="modal-header">
            <div class="modal-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
              <h3>{{ editingRole ? '编辑角色' : '新建角色' }}</h3>
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
            <!-- 基本信息 -->
            <div class="form-section">
              <div class="section-title">基本信息</div>
              <div class="form-grid">
                <div class="form-group">
                  <label>角色名称 <span class="required">*</span></label>
                  <input 
                    v-model.trim="roleForm.name" 
                    required 
                    :disabled="editingRole?.is_system" 
                    placeholder="例如：人事经理" 
                  />
                </div>
                <div class="form-group">
                  <label>角色代码 <span class="required">*</span></label>
                  <input 
                    v-model.trim="roleForm.code" 
                    required 
                    :disabled="editingRole?.is_system || !!editingRole" 
                    placeholder="例如：hr_manager" 
                  />
                </div>
              </div>
              <div class="form-group">
                <label>角色描述</label>
                <textarea 
                  v-model.trim="roleForm.description" 
                  rows="2" 
                  placeholder="可选，描述此角色的职责" 
                  :disabled="editingRole?.is_system"
                ></textarea>
              </div>
            </div>

            <!-- 权限分配 -->
            <div class="form-section">
              <div class="section-title">
                <span>权限分配</span>
                <span class="badge">{{ roleForm.permission_ids.length }} 项已选</span>
                <div class="section-actions">
                  <button type="button" class="link-btn" @click="selectAllPerms" :disabled="editingRole?.is_system">全选</button>
                  <button type="button" class="link-btn" @click="clearAllPerms" :disabled="editingRole?.is_system">清空</button>
                </div>
              </div>
              <div class="permission-groups">
                <div v-for="group in sortedPermissionGroups" :key="group.name" class="perm-group">
                  <div class="perm-group-header" @click="toggleGroup(group.name)">
                    <svg :class="{ expanded: expandedGroups[group.name] }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <polyline points="9 18 15 12 9 6"/>
                    </svg>
                    <span class="perm-group-name">{{ group.name }}</span>
                    <span class="perm-group-count">{{ getGroupSelectedCount(group) }}/{{ group.permissions.length }}</span>
                    <button type="button" class="mini-btn" @click.stop="selectGroup(group)" :disabled="editingRole?.is_system">
                      {{ isGroupAllSelected(group) ? '取消' : '全选' }}
                    </button>
                  </div>
                  <div v-show="expandedGroups[group.name]" class="perm-group-body">
                    <label 
                      v-for="p in group.permissions" 
                      :key="p.id" 
                      class="perm-item"
                      :class="{ checked: roleForm.permission_ids.includes(p.id), disabled: editingRole?.is_system }"
                    >
                      <input 
                        type="checkbox" 
                        :value="p.id" 
                        v-model="roleForm.permission_ids" 
                        :disabled="editingRole?.is_system" 
                      />
                      <div class="perm-info">
                        <span class="perm-name">{{ p.name }}</span>
                        <code class="perm-key">{{ p.key }}</code>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- 关联用户 -->
            <div class="form-section">
              <div class="section-title">
                <span>关联用户</span>
                <span class="badge">{{ roleForm.user_ids.length }} 人</span>
                <div class="section-actions">
                  <button type="button" class="link-btn" @click="selectAllUsers">全选</button>
                  <button type="button" class="link-btn" @click="clearAllUsers">清空</button>
                </div>
              </div>
              <div class="user-groups">
                <!-- 如果没有员工数据，显示平铺的用户列表 -->
                <template v-if="employees.length === 0 && users.length > 0">
                  <div class="user-flat-list">
                    <label 
                      v-for="u in users" 
                      :key="u.id" 
                      class="user-item"
                      :class="{ checked: roleForm.user_ids.includes(u.id) }"
                    >
                      <input 
                        type="checkbox" 
                        :value="u.id" 
                        v-model="roleForm.user_ids" 
                      />
                      <div class="user-avatar">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                          <circle cx="12" cy="7" r="4"/>
                        </svg>
                      </div>
                      <span class="user-name">{{ u.username }}</span>
                    </label>
                  </div>
                </template>
                <!-- 有员工数据时，按部门/职位层级显示 -->
                <template v-else>
                <div v-for="dept in sortedDepartments" :key="dept.id" class="user-dept-group">
                  <div class="user-dept-header" @click="toggleDept(dept.id)">
                    <svg :class="{ expanded: expandedDepts[dept.id] }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <polyline points="9 18 15 12 9 6"/>
                    </svg>
                    <span class="user-dept-name">{{ dept.name }}</span>
                    <span class="user-dept-count">{{ getDeptSelectedCount(dept.id) }}/{{ getDeptTotalCount(dept.id) }}</span>
                    <button type="button" class="mini-btn" @click.stop="selectDept(dept.id)">
                      {{ isDeptAllSelected(dept.id) ? '取消' : '全选' }}
                    </button>
                  </div>
                  <div v-show="expandedDepts[dept.id]" class="user-dept-body">
                    <!-- 按职位分组 -->
                    <div v-for="position in getDeptPositions(dept.id)" :key="position.id" class="user-position-group">
                      <div class="user-position-header" @click.stop="togglePosition(dept.id, position.id)">
                        <svg :class="{ expanded: expandedPositions[dept.id + '-' + position.id] }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                          <polyline points="9 18 15 12 9 6"/>
                        </svg>
                        <span class="user-position-name">{{ position.name }}</span>
                        <span class="user-position-count">{{ getPositionSelectedCount(dept.id, position.id) }}/{{ getPositionTotalCount(dept.id, position.id) }}</span>
                        <button type="button" class="mini-btn" @click.stop="selectPosition(dept.id, position.id)">
                          {{ isPositionAllSelected(dept.id, position.id) ? '取消' : '全选' }}
                        </button>
                      </div>
                      <div v-show="expandedPositions[dept.id + '-' + position.id]" class="user-position-body">
                        <label 
                          v-for="emp in getPositionEmployees(dept.id, position.id)" 
                          :key="emp.user?.id || emp.id" 
                          class="user-item"
                          :class="{ checked: emp.user && roleForm.user_ids.includes(emp.user.id), disabled: !emp.user }"
                        >
                          <input 
                            type="checkbox" 
                            :value="emp.user?.id" 
                            v-model="roleForm.user_ids" 
                            :disabled="!emp.user" 
                          />
                          <div class="user-avatar" :class="{ 'has-avatar': emp.avatar }">
                            <img v-if="emp.avatar" :src="emp.avatar" :alt="emp.name" />
                            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                              <circle cx="12" cy="7" r="4"/>
                            </svg>
                          </div>
                          <div class="user-info">
                            <span class="user-name">{{ emp.name }}</span>
                            <span v-if="!emp.user" class="user-no-account">无账号</span>
                          </div>
                        </label>
                      </div>
                    </div>
                    <!-- 无职位的员工 -->
                    <div v-if="getDeptEmployeesNoPosition(dept.id).length > 0" class="user-position-group">
                      <div class="user-position-header" @click.stop="togglePosition(dept.id, 0)">
                        <svg :class="{ expanded: expandedPositions[dept.id + '-0'] }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                          <polyline points="9 18 15 12 9 6"/>
                        </svg>
                        <span class="user-position-name" style="color: #6b7280;">未分配职位</span>
                        <span class="user-position-count">{{ getNoPositionSelectedCount(dept.id) }}/{{ getDeptEmployeesNoPosition(dept.id).length }}</span>
                      </div>
                      <div v-show="expandedPositions[dept.id + '-0']" class="user-position-body">
                        <label 
                          v-for="emp in getDeptEmployeesNoPosition(dept.id)" 
                          :key="emp.user?.id || emp.id" 
                          class="user-item"
                          :class="{ checked: emp.user && roleForm.user_ids.includes(emp.user.id), disabled: !emp.user }"
                        >
                          <input 
                            type="checkbox" 
                            :value="emp.user?.id" 
                            v-model="roleForm.user_ids" 
                            :disabled="!emp.user" 
                          />
                          <div class="user-avatar">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                              <circle cx="12" cy="7" r="4"/>
                            </svg>
                          </div>
                          <div class="user-info">
                            <span class="user-name">{{ emp.name }}</span>
                            <span v-if="!emp.user" class="user-no-account">无账号</span>
                          </div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
                <!-- 无部门用户 -->
                <div v-if="usersWithoutDept.length > 0" class="user-dept-group">
                  <div class="user-dept-header" @click="toggleDept(0)">
                    <svg :class="{ expanded: expandedDepts[0] }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <polyline points="9 18 15 12 9 6"/>
                    </svg>
                    <span class="user-dept-name" style="color: #6b7280;">未分配部门</span>
                    <span class="user-dept-count">{{ getNoDeptSelectedCount() }}/{{ usersWithoutDept.length }}</span>
                  </div>
                  <div v-show="expandedDepts[0]" class="user-dept-body">
                    <div class="user-position-body" style="padding-left: 0;">
                      <label 
                        v-for="u in usersWithoutDept" 
                        :key="u.id" 
                        class="user-item"
                        :class="{ checked: roleForm.user_ids.includes(u.id) }"
                      >
                        <input 
                          type="checkbox" 
                          :value="u.id" 
                          v-model="roleForm.user_ids" 
                        />
                        <div class="user-avatar">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                            <circle cx="12" cy="7" r="4"/>
                          </svg>
                        </div>
                        <span class="user-name">{{ u.username }}</span>
                      </label>
                    </div>
                  </div>
                </div>
                </template>
              </div>
            </div>

            <!-- 弹窗底部 -->
            <div class="modal-footer">
              <button class="btn btn-primary" type="submit" :disabled="savingRole">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                {{ savingRole ? '保存中...' : '保存' }}
              </button>
              <button class="btn btn-secondary" type="button" @click="handleCancel">
                取消
              </button>
              <button 
                v-if="editingRole && !editingRole.is_system" 
                class="btn btn-danger" 
                type="button" 
                @click="handleRemove" 
                :disabled="deletingRoleId===editingRole.id"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
                {{ deletingRoleId === editingRole?.id ? '删除中...' : '删除' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { reactive, computed, watch } from 'vue';
import { useRbac } from '../composables/useRbac';

const {
  showRoleForm,
  editingRole,
  savingRole,
  deletingRoleId,
  roleForm,
  permissions,
  permissionGroups,
  users,
  employees,
  submitRole,
  cancelRole,
  removeRole
} = useRbac();

// 分组展开状态
const expandedGroups = reactive({});
const expandedDepts = reactive({});
const expandedPositions = reactive({});

// 当弹窗打开时，自动展开有已选用户的部门
watch(showRoleForm, (visible) => {
  if (visible) {
    // 重置展开状态
    Object.keys(expandedDepts).forEach(k => delete expandedDepts[k]);
    Object.keys(expandedPositions).forEach(k => delete expandedPositions[k]);
    
    // 默认展开所有部门和职位，方便用户直接查看所有可选用户
    setTimeout(() => {
      const depts = sortedDepartments.value;
      for (const dept of depts) {
        expandedDepts[dept.id] = true;
        // 展开该部门的所有职位
        const positions = getDeptPositions(dept.id);
        for (const pos of positions) {
          expandedPositions[`${dept.id}-${pos.id}`] = true;
        }
        // 展开无职位分组
        if (getDeptEmployeesNoPosition(dept.id).length > 0) {
          expandedPositions[`${dept.id}-0`] = true;
        }
      }
      // 展开无部门用户分组
      if (usersWithoutDept.value.length > 0) {
        expandedDepts[0] = true;
      }
    }, 50);
  }
});

// 按导航顺序排列的分组
const GROUP_ORDER = [
  '员工管理', '考勤管理', '请假管理', '出差管理', '薪资管理', '报销管理',
  '职位管理', '部门管理', '文档管理', '报表统计', '离职管理',
  '系统管理', '权限管理', '用户管理'
];

const sortedPermissionGroups = computed(() => {
  if (!permissionGroups.value || permissionGroups.value.length === 0) {
    return [];
  }
  const groupMap = {};
  for (const g of permissionGroups.value) {
    groupMap[g.name] = g;
  }
  const sorted = [];
  for (const name of GROUP_ORDER) {
    if (groupMap[name]) {
      sorted.push(groupMap[name]);
      delete groupMap[name];
    }
  }
  for (const name of Object.keys(groupMap)) {
    sorted.push(groupMap[name]);
  }
  return sorted;
});

// 从员工数据中提取部门列表
const sortedDepartments = computed(() => {
  const deptMap = {};
  for (const emp of employees.value) {
    if (emp.department) {
      const deptId = emp.department.id || emp.department;
      const deptName = emp.department_name || emp.department?.name || `部门${deptId}`;
      if (!deptMap[deptId]) {
        deptMap[deptId] = { id: deptId, name: deptName };
      }
    }
  }
  return Object.values(deptMap).sort((a, b) => a.name.localeCompare(b.name, 'zh'));
});

// 获取部门下的职位列表
function getDeptPositions(deptId) {
  const posMap = {};
  for (const emp of employees.value) {
    const empDeptId = emp.department?.id || emp.department;
    if (empDeptId === deptId && emp.position) {
      const posId = emp.position.id || emp.position;
      const posName = emp.position_name || emp.position?.name || `职位${posId}`;
      if (!posMap[posId]) {
        posMap[posId] = { id: posId, name: posName };
      }
    }
  }
  return Object.values(posMap).sort((a, b) => a.name.localeCompare(b.name, 'zh'));
}

// 获取职位下的员工
function getPositionEmployees(deptId, posId) {
  return employees.value.filter(emp => {
    const empDeptId = emp.department?.id || emp.department;
    const empPosId = emp.position?.id || emp.position;
    return empDeptId === deptId && empPosId === posId;
  });
}

// 获取部门下没有职位的员工
function getDeptEmployeesNoPosition(deptId) {
  return employees.value.filter(emp => {
    const empDeptId = emp.department?.id || emp.department;
    return empDeptId === deptId && !emp.position;
  });
}

// 获取没有部门的用户（直接从users中查找未被员工关联的）
const usersWithoutDept = computed(() => {
  const empUserIds = new Set(employees.value.filter(e => e.user).map(e => e.user.id || e.user));
  return users.value.filter(u => !empUserIds.has(u.id));
});

// 展开/折叠部门
function toggleDept(deptId) {
  expandedDepts[deptId] = !expandedDepts[deptId];
}

// 展开/折叠职位
function togglePosition(deptId, posId) {
  const key = `${deptId}-${posId}`;
  expandedPositions[key] = !expandedPositions[key];
}

// 部门相关计数
function getDeptTotalCount(deptId) {
  return employees.value.filter(emp => {
    const empDeptId = emp.department?.id || emp.department;
    return empDeptId === deptId && emp.user;
  }).length;
}

function getDeptSelectedCount(deptId) {
  return employees.value.filter(emp => {
    const empDeptId = emp.department?.id || emp.department;
    return empDeptId === deptId && emp.user && roleForm.value.user_ids.includes(emp.user.id || emp.user);
  }).length;
}

function isDeptAllSelected(deptId) {
  const deptEmps = employees.value.filter(emp => {
    const empDeptId = emp.department?.id || emp.department;
    return empDeptId === deptId && emp.user;
  });
  return deptEmps.length > 0 && deptEmps.every(emp => roleForm.value.user_ids.includes(emp.user.id || emp.user));
}

function selectDept(deptId) {
  const deptUserIds = employees.value
    .filter(emp => {
      const empDeptId = emp.department?.id || emp.department;
      return empDeptId === deptId && emp.user;
    })
    .map(emp => emp.user.id || emp.user);
  
  if (isDeptAllSelected(deptId)) {
    roleForm.value.user_ids = roleForm.value.user_ids.filter(id => !deptUserIds.includes(id));
  } else {
    const newIds = deptUserIds.filter(id => !roleForm.value.user_ids.includes(id));
    roleForm.value.user_ids.push(...newIds);
  }
}

// 职位相关计数
function getPositionTotalCount(deptId, posId) {
  return getPositionEmployees(deptId, posId).filter(emp => emp.user).length;
}

function getPositionSelectedCount(deptId, posId) {
  return getPositionEmployees(deptId, posId).filter(emp => emp.user && roleForm.value.user_ids.includes(emp.user.id || emp.user)).length;
}

function isPositionAllSelected(deptId, posId) {
  const posEmps = getPositionEmployees(deptId, posId).filter(emp => emp.user);
  return posEmps.length > 0 && posEmps.every(emp => roleForm.value.user_ids.includes(emp.user.id || emp.user));
}

function selectPosition(deptId, posId) {
  const posUserIds = getPositionEmployees(deptId, posId)
    .filter(emp => emp.user)
    .map(emp => emp.user.id || emp.user);
  
  if (isPositionAllSelected(deptId, posId)) {
    roleForm.value.user_ids = roleForm.value.user_ids.filter(id => !posUserIds.includes(id));
  } else {
    const newIds = posUserIds.filter(id => !roleForm.value.user_ids.includes(id));
    roleForm.value.user_ids.push(...newIds);
  }
}

// 无职位员工计数
function getNoPositionSelectedCount(deptId) {
  return getDeptEmployeesNoPosition(deptId).filter(emp => emp.user && roleForm.value.user_ids.includes(emp.user.id || emp.user)).length;
}

// 无部门用户计数
function getNoDeptSelectedCount() {
  return usersWithoutDept.value.filter(u => roleForm.value.user_ids.includes(u.id)).length;
}

// 全选/清空所有用户
function selectAllUsers() {
  const allUserIds = [
    ...employees.value.filter(emp => emp.user).map(emp => emp.user.id || emp.user),
    ...usersWithoutDept.value.map(u => u.id)
  ];
  roleForm.value.user_ids = [...new Set(allUserIds)];
}

function clearAllUsers() {
  roleForm.value.user_ids = [];
}

function toggleGroup(name) {
  expandedGroups[name] = !expandedGroups[name];
}

function getGroupSelectedCount(group) {
  return group.permissions.filter(p => roleForm.value.permission_ids.includes(p.id)).length;
}

function isGroupAllSelected(group) {
  return group.permissions.every(p => roleForm.value.permission_ids.includes(p.id));
}

function selectGroup(group) {
  const groupIds = group.permissions.map(p => p.id);
  const allSelected = isGroupAllSelected(group);
  if (allSelected) {
    roleForm.value.permission_ids = roleForm.value.permission_ids.filter(id => !groupIds.includes(id));
  } else {
    const newIds = groupIds.filter(id => !roleForm.value.permission_ids.includes(id));
    roleForm.value.permission_ids.push(...newIds);
  }
}

function selectAllPerms() {
  const allIds = permissions.value.map(p => p.id);
  roleForm.value.permission_ids = [...allIds];
}

function clearAllPerms() {
  roleForm.value.permission_ids = [];
}

function handleSubmit() {
  submitRole();
}

function handleCancel() {
  cancelRole();
}

function handleRemove() {
  if (editingRole.value) {
    removeRole(editingRole.value);
  }
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
  max-width: 720px;
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

/* 表单区块 */
.form-section {
  margin-bottom: 1.5rem;
}

.form-section:last-of-type {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.section-actions {
  margin-left: auto;
  display: flex;
  gap: 0.5rem;
}

.badge {
  background: #dbeafe;
  color: #2563eb;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.link-btn {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 12px;
  cursor: pointer;
  padding: 0.125rem 0.25rem;
}

.link-btn:hover:not(:disabled) {
  text-decoration: underline;
}

.link-btn:disabled {
  color: #9ca3af;
  cursor: not-allowed;
}

/* 表单网格 */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 0.75rem;
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

.form-group input,
.form-group textarea {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
  box-sizing: border-box;
  width: 100%;
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

/* 权限分组 */
.permission-groups {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  max-height: 280px;
  overflow-y: auto;
}

.perm-group {
  border-bottom: 1px solid #e5e7eb;
}

.perm-group:last-child {
  border-bottom: none;
}

.perm-group-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  background: #f9fafb;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.perm-group-header:hover {
  background: #f3f4f6;
}

.perm-group-header svg {
  color: #6b7280;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.perm-group-header svg.expanded {
  transform: rotate(90deg);
}

.perm-group-name {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.perm-group-count {
  font-size: 11px;
  color: #6b7280;
  background: #e5e7eb;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
}

.mini-btn {
  font-size: 11px;
  color: #2563eb;
  background: #eff6ff;
  border: none;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.mini-btn:hover:not(:disabled) {
  background: #dbeafe;
}

.mini-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.perm-group-body {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.375rem;
  padding: 0.625rem;
  background: #fff;
}

.perm-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  background: #fff;
}

.perm-item:hover:not(.disabled) {
  border-color: #93c5fd;
  background: #f8fafc;
}

.perm-item.checked {
  border-color: #93c5fd;
  background: #eff6ff;
}

.perm-item.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.perm-item input[type="checkbox"] {
  width: 14px;
  height: 14px;
  margin: 0;
  cursor: inherit;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  border: 1.5px solid #c9cdd4;
  border-radius: 3px;
  background: #f3f4f6;
  flex-shrink: 0;
}

.perm-item input[type="checkbox"]:checked {
  background: #2563eb;
  border-color: #2563eb;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3E%3C/svg%3E");
  background-size: 100%;
  background-position: center;
  background-repeat: no-repeat;
}

.perm-item input[type="checkbox"]:focus {
  outline: none;
  box-shadow: none;
}

.perm-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.perm-name {
  font-size: 12px;
  font-weight: 500;
  color: #1f2937;
}

.perm-key {
  font-size: 10px;
  color: #6b7280;
  background: transparent;
  padding: 0;
  font-family: ui-monospace, monospace;
}

/* 用户分组 - 部门/职位/员工层级 */
.user-groups {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  max-height: 280px;
  overflow-y: auto;
}

/* 平铺用户列表（无员工数据时使用） */
.user-flat-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.5rem;
  padding: 0.625rem;
}

.user-dept-group {
  border-bottom: 1px solid #e5e7eb;
}

.user-dept-group:last-child {
  border-bottom: none;
}

.user-dept-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  background: #f9fafb;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.user-dept-header:hover {
  background: #f3f4f6;
}

.user-dept-header svg {
  color: #6b7280;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.user-dept-header svg.expanded {
  transform: rotate(90deg);
}

.dept-icon {
  color: #2563eb !important;
}

.user-dept-name {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.user-dept-count {
  font-size: 11px;
  color: #6b7280;
  background: #e5e7eb;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
}

.user-dept-body {
  background: #fff;
  padding-left: 1.25rem;
}

/* 职位分组 */
.user-position-group {
  border-bottom: 1px solid #f3f4f6;
}

.user-position-group:last-child {
  border-bottom: none;
}

.user-position-header {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.5rem;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.user-position-header:hover {
  background: #f9fafb;
}

.user-position-header svg {
  color: #9ca3af;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.user-position-header svg.expanded {
  transform: rotate(90deg);
}

.user-position-name {
  flex: 1;
  font-size: 12px;
  font-weight: 500;
  color: #374151;
}

.user-position-count {
  font-size: 10px;
  color: #9ca3af;
  background: #f3f4f6;
  padding: 0.0625rem 0.375rem;
  border-radius: 8px;
}

.user-position-body {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.375rem;
  padding: 0.375rem 0.5rem 0.625rem 1.25rem;
}

/* 用户项 */
.user-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  background: #fff;
}

.user-item:hover:not(.disabled) {
  border-color: #93c5fd;
  background: #f8fafc;
}

.user-item.checked {
  border-color: #93c5fd;
  background: #eff6ff;
}

.user-item.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.user-item input[type="checkbox"] {
  display: none;
}

.user-avatar {
  width: 24px;
  height: 24px;
  background: #e5e7eb;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.user-item.checked .user-avatar {
  background: #2563eb;
  color: #fff;
}

.user-avatar.has-avatar {
  padding: 0;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-name {
  font-size: 13px;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-no-account {
  font-size: 10px;
  color: #f59e0b;
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

.btn-danger {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  margin-left: auto;
}

.btn-danger:hover:not(:disabled) {
  background: #fee2e2;
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
