/**
 * v-permission 权限指令
 * 
 * 用法：
 *   v-permission="'employee.view'"              - 需要单个权限
 *   v-permission="['employee.view']"            - 需要所有列出的权限
 *   v-permission.any="['employee.edit', 'admin']" - 只需任一权限
 *   v-permission.admin                          - 需要管理员权限
 *   v-permission.hide="'employee.edit'"         - 无权限时隐藏元素（默认）
 *   v-permission.disable="'employee.edit'"      - 无权限时禁用元素
 */
import { hasPermission, anyPermission, isAdmin } from './permissions';

function checkPermission(binding) {
  const { value, modifiers } = binding;
  
  // 管理员修饰符
  if (modifiers.admin) {
    return isAdmin();
  }
  
  if (!value) return true;
  
  const permissions = Array.isArray(value) ? value : [value];
  
  // any 修饰符：只需任一权限
  if (modifiers.any) {
    return anyPermission(permissions);
  }
  
  // 默认：需要所有权限
  return permissions.every(p => hasPermission(p));
}

function updateElement(el, binding) {
  const hasAccess = checkPermission(binding);
  
  if (hasAccess) {
    // 恢复元素
    el.style.display = el._originalDisplay || '';
    if (el._wasDisabled !== undefined) {
      el.disabled = el._wasDisabled;
    }
    el.classList.remove('permission-disabled');
  } else {
    // disable 修饰符：禁用而非隐藏
    if (binding.modifiers.disable) {
      if (el._wasDisabled === undefined) {
        el._wasDisabled = el.disabled;
      }
      el.disabled = true;
      el.classList.add('permission-disabled');
      el.title = el.title || '权限不足';
    } else {
      // 默认隐藏
      if (!el._originalDisplay) {
        el._originalDisplay = el.style.display || '';
      }
      el.style.display = 'none';
    }
  }
}

export const permissionDirective = {
  mounted(el, binding) {
    updateElement(el, binding);
  },
  updated(el, binding) {
    updateElement(el, binding);
  },
};

/**
 * 安装权限指令
 * @param {import('vue').App} app 
 */
export function setupPermissionDirective(app) {
  app.directive('permission', permissionDirective);
}

export default permissionDirective;
