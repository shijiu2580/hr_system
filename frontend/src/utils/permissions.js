/**
 * 前端权限辅助模块
 * 依赖 auth store 的 permissions / roles
 */
import { useAuthStore } from '../stores/auth';

// ================== 权限常量定义 ==================
export const Permissions = {
  // -------- 员工管理 --------
  EMPLOYEE_VIEW: 'employee.view',
  EMPLOYEE_CREATE: 'employee.create',
  EMPLOYEE_EDIT: 'employee.edit',
  EMPLOYEE_DELETE: 'employee.delete',
  EMPLOYEE_IMPORT: 'employee.import',
  EMPLOYEE_EXPORT: 'employee.export',

  // -------- 部门管理 --------
  DEPARTMENT_VIEW: 'department.view',
  DEPARTMENT_CREATE: 'department.create',
  DEPARTMENT_EDIT: 'department.edit',
  DEPARTMENT_DELETE: 'department.delete',

  // -------- 职位管理 --------
  POSITION_VIEW: 'position.view',
  POSITION_CREATE: 'position.create',
  POSITION_EDIT: 'position.edit',
  POSITION_DELETE: 'position.delete',

  // -------- 考勤管理 --------
  ATTENDANCE_VIEW: 'attendance.view',
  ATTENDANCE_VIEW_ALL: 'attendance.view_all',
  ATTENDANCE_CREATE: 'attendance.create',
  ATTENDANCE_EDIT: 'attendance.edit',
  ATTENDANCE_APPROVE: 'attendance.approve',
  ATTENDANCE_LOCATION: 'attendance.location',

  // -------- 请假管理 --------
  LEAVE_VIEW: 'leave.view',
  LEAVE_VIEW_ALL: 'leave.view_all',
  LEAVE_CREATE: 'leave.create',
  LEAVE_APPROVE: 'leave.approve',

  // -------- 出差管理 --------
  TRIP_VIEW: 'trip.view',
  TRIP_VIEW_ALL: 'trip.view_all',
  TRIP_CREATE: 'trip.create',
  TRIP_APPROVE: 'trip.approve',

  // -------- 薪资管理 --------
  SALARY_VIEW: 'salary.view',
  SALARY_VIEW_ALL: 'salary.view_all',
  SALARY_CREATE: 'salary.create',
  SALARY_EDIT: 'salary.edit',
  SALARY_DELETE: 'salary.delete',
  SALARY_DISBURSE: 'salary.disburse',

  // -------- 报销管理 --------
  EXPENSE_VIEW: 'expense.view',
  EXPENSE_VIEW_ALL: 'expense.view_all',
  EXPENSE_CREATE: 'expense.create',
  EXPENSE_APPROVE: 'expense.approve',

  // -------- 文档管理 --------
  DOCUMENT_VIEW: 'document.view',
  DOCUMENT_CREATE: 'document.create',
  DOCUMENT_EDIT: 'document.edit',
  DOCUMENT_UPLOAD: 'document.upload',
  DOCUMENT_DELETE: 'document.delete',
  DOCUMENT_MANAGE: 'document.manage',

  // -------- 报表统计 --------
  REPORT_VIEW: 'report.view',
  REPORT_EXPORT: 'report.export',
  REPORT_EMPLOYEE: 'report.employee',
  REPORT_ATTENDANCE: 'report.attendance',
  REPORT_SALARY: 'report.salary',
  REPORT_LEAVE: 'report.leave',

  // -------- 系统管理 --------
  SYSTEM_VIEW: 'system.view',
  SYSTEM_LOG: 'system.log',
  SYSTEM_LOG_VIEW: 'system.log_view',
  SYSTEM_LOG_CLEAR: 'system.log_clear',
  SYSTEM_BACKUP: 'system.backup',
  SYSTEM_BACKUP_VIEW: 'system.backup_view',
  SYSTEM_BACKUP_CREATE: 'system.backup_create',
  SYSTEM_BACKUP_RESTORE: 'system.backup_restore',
  SYSTEM_RESTORE: 'system.restore',

  // -------- 用户管理 --------
  USER_VIEW: 'user.view',
  USER_CREATE: 'user.create',
  USER_EDIT: 'user.edit',
  USER_DELETE: 'user.delete',
  USER_RESET_PASSWORD: 'user.reset_password',

  // -------- 权限管理 --------
  RBAC_VIEW: 'rbac.view',
  RBAC_MANAGE: 'rbac.manage',
  RBAC_ROLE_MANAGE: 'rbac.role_manage',
  RBAC_PERMISSION_MANAGE: 'rbac.permission_manage',

  // -------- 入职管理 --------
  ONBOARDING_VIEW: 'onboarding.view',
  ONBOARDING_VIEW_ALL: 'onboarding.view_all',
  ONBOARDING_APPROVE: 'onboarding.approve',
  ONBOARDING_REJECT: 'onboarding.reject',

  // -------- 离职管理 --------
  RESIGNATION_VIEW: 'resignation.view',
  RESIGNATION_VIEW_ALL: 'resignation.view_all',
  RESIGNATION_CREATE: 'resignation.create',
  RESIGNATION_APPROVE: 'resignation.approve',
};

/**
 * 检查是否拥有指定权限
 * @param {string} key - 权限标识
 * @returns {boolean}
 */
export function hasPermission(key) {
  const auth = useAuthStore();
  return auth.hasPermissionKey(key);
}

/**
 * 检查是否拥有任一权限
 * @param {string[]} keys - 权限标识数组
 * @returns {boolean}
 */
export function anyPermission(keys) {
  return keys.some(k => hasPermission(k));
}

/**
 * 检查是否拥有所有权限
 * @param {string[]} keys - 权限标识数组
 * @returns {boolean}
 */
export function allPermissions(keys) {
  return keys.every(k => hasPermission(k));
}

/**
 * 检查是否为管理员
 * @returns {boolean}
 */
export function isAdmin() {
  const auth = useAuthStore();
  return auth.user?.is_staff || auth.user?.is_superuser || false;
}

/**
 * 检查是否为超级管理员
 * @returns {boolean}
 */
export function isSuperAdmin() {
  const auth = useAuthStore();
  return auth.user?.is_superuser || false;
}

/**
 * 检查是否有指定角色
 * @param {string} roleCode - 角色代码
 * @returns {boolean}
 */
export function hasRole(roleCode) {
  const auth = useAuthStore();
  return auth.roles?.some(r => r.code === roleCode) || false;
}

/**
 * 检查是否有任一角色
 * @param {string[]} roleCodes - 角色代码数组
 * @returns {boolean}
 */
export function anyRole(roleCodes) {
  return roleCodes.some(code => hasRole(code));
}

// ================== 路由权限配置 ==================
// 定义每个路由所需的权限
export const routePermissions = {
  // 员工管理
  '/employees/manage': [Permissions.EMPLOYEE_VIEW],
  '/employees/create': [Permissions.EMPLOYEE_CREATE],
  '/employees/:id/edit': [Permissions.EMPLOYEE_EDIT],

  // 考勤管理
  '/attendance/manage': [Permissions.ATTENDANCE_VIEW_ALL],
  '/attendance/approval': [Permissions.ATTENDANCE_APPROVE],
  '/attendance/locations': [Permissions.ATTENDANCE_LOCATION],

  // 请假管理
  '/leaves/approval': [Permissions.LEAVE_APPROVE],

  // 薪资管理
  '/salaries': [Permissions.SALARY_VIEW_ALL],
  '/salaries/create': [Permissions.SALARY_CREATE],
  '/salaries/expense-approval': [Permissions.EXPENSE_APPROVE],

  // 组织架构
  '/departments/create': [Permissions.DEPARTMENT_CREATE],
  '/departments/:id/edit': [Permissions.DEPARTMENT_EDIT],
  '/positions/create': [Permissions.POSITION_CREATE],
  '/positions/:id/edit': [Permissions.POSITION_EDIT],

  // 系统管理
  '/system': [Permissions.SYSTEM_VIEW],
  '/rbac': [Permissions.RBAC_VIEW],
  '/users': [Permissions.USER_VIEW],
  '/users/create': [Permissions.USER_CREATE],
  '/users/:id/edit': [Permissions.USER_EDIT],
  '/admin-reset-password': [Permissions.USER_RESET_PASSWORD],

  // 报表
  '/reports': [Permissions.REPORT_VIEW],
};

/**
 * 检查用户是否有权访问指定路由
 * @param {string} path - 路由路径
 * @returns {boolean}
 */
export function canAccessRoute(path) {
  // 管理员可访问所有路由
  if (isAdmin()) return true;

  // 查找匹配的路由权限配置
  for (const [pattern, perms] of Object.entries(routePermissions)) {
    // 简单的路径匹配（支持 :id 这样的参数）
    const regex = new RegExp('^' + pattern.replace(/:[^/]+/g, '[^/]+') + '$');
    if (regex.test(path)) {
      return perms.every(p => hasPermission(p));
    }
  }

  // 没有配置权限的路由默认可访问
  return true;
}

