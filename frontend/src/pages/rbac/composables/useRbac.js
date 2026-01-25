import { ref } from 'vue';
import api from '../../../utils/api';

// 共享状态
const loading = ref(false);
const error = ref('');
const success = ref('');
const roles = ref([]);
const permissions = ref([]);
const permissionGroups = ref([]);  // 权限分组
const users = ref([]);
const employees = ref([]);  // 员工列表（包含部门和职位）
const loadingRoles = ref(false);
const loadingPerms = ref(false);
const loadingUsers = ref(false);

// 角色表单状态
const showRoleForm = ref(false);
const editingRole = ref(null);
const savingRole = ref(false);
const deletingRoleId = ref(null);
const roleForm = ref({ name: '', code: '', description: '', permission_ids: [], user_ids: [] });

// 权限表单状态
const showPermForm = ref(false);
const editingPerm = ref(null);
const savingPerm = ref(false);
const deletingPermId = ref(null);
const permForm = ref({ key: '', name: '', description: '' });

export function useRbac() {
  // 数据加载
  async function loadRoles() {
    loadingRoles.value = true;
    try {
      const res = await api.get('/roles/manage/');
      roles.value = res.data?.results || res.data || [];
    } catch (e) {
      error.value = '加载角色失败';
    } finally {
      loadingRoles.value = false;
    }
  }

  async function loadPerms() {
    loadingPerms.value = true;
    try {
      const res = await api.get('/permissions/manage/');
      permissions.value = res.data?.results || res.data || [];
    } catch (e) {
      error.value = '加载权限失败';
    } finally {
      loadingPerms.value = false;
    }
  }

  async function loadPermGroups() {
    try {
      const res = await api.get('/permissions/groups/');
      permissionGroups.value = res.data || [];
    } catch (e) {
      // 忽略
    }
  }

  async function loadUsers() {
    loadingUsers.value = true;
    try {
      // 获取全部用户（设置较大的 page_size 避免分页）
      const res = await api.get('/users/?page_size=1000');
      users.value = res.data?.results || res.data || [];
    } catch (e) {
      // 忽略
    } finally {
      loadingUsers.value = false;
    }
  }

  async function loadEmployees() {
    try {
      // 获取全部员工（设置较大的 page_size 避免分页）
      const res = await api.get('/employees/?page_size=1000');
      employees.value = res.data?.results || res.data || [];
    } catch (e) {
      // 忽略
    }
  }

  async function reload() {
    loading.value = true;
    error.value = '';
    success.value = '';
    try {
      await Promise.all([loadRoles(), loadPerms(), loadPermGroups(), loadUsers(), loadEmployees()]);
    } finally {
      loading.value = false;
    }
  }

  // 角色操作
  function startCreateRole() {
    editingRole.value = null;
    roleForm.value = { name: '', code: '', description: '', permission_ids: [], user_ids: [] };
    showRoleForm.value = true;
    showPermForm.value = false;
    error.value = '';
    success.value = '';
  }

  function startEditRole(r) {
    editingRole.value = r;
    const roleUsers = users.value.filter(u => (u.roles || []).some(ur => ur.id === r.id)).map(u => u.id);
    roleForm.value = {
      name: r.name,
      code: r.code,
      description: r.description || '',
      permission_ids: r.permissions.map(p => p.id),
      user_ids: roleUsers
    };
    showRoleForm.value = true;
    showPermForm.value = false;
    error.value = '';
    success.value = '';
  }

  function cancelRole() {
    showRoleForm.value = false;
    editingRole.value = null;
    roleForm.value = { name: '', code: '', description: '', permission_ids: [], user_ids: [] };
  }

  async function submitRole() {
    savingRole.value = true;
    error.value = '';
    success.value = '';
    try {
      const payload = { ...roleForm.value };
      let res;
      if (editingRole.value) {
        res = await api.put(`/roles/manage/${editingRole.value.id}/`, payload);
      } else {
        res = await api.post('/roles/manage/', payload);
      }
      if (!res.success) {
        error.value = res.error?.message || '保存失败';
        return;
      }
      success.value = editingRole.value ? '更新角色成功' : '创建角色成功';
      await reload();
      showRoleForm.value = false;
      editingRole.value = null;
    } catch (e) {
      error.value = e.message || '保存失败';
    } finally {
      savingRole.value = false;
    }
  }

  async function removeRole(r) {
    if (!confirm(`确认删除角色 "${r.name}"?`)) return;
    deletingRoleId.value = r.id;
    error.value = '';
    success.value = '';
    try {
      const res = await api.delete(`/roles/manage/${r.id}/`);
      if (!res.success) {
        error.value = res.error?.message || '删除失败';
        return;
      }
      success.value = '已删除角色';
      await loadRoles();
      await loadUsers();
      if (editingRole.value && editingRole.value.id === r.id) {
        cancelRole();
      }
    } catch (e) {
      error.value = e.message || '删除失败';
    } finally {
      deletingRoleId.value = null;
    }
  }

  // 权限操作
  function startCreatePerm() {
    editingPerm.value = null;
    permForm.value = { key: '', name: '', description: '' };
    showPermForm.value = true;
    showRoleForm.value = false;
    error.value = '';
    success.value = '';
  }

  function startEditPerm(p) {
    editingPerm.value = p;
    permForm.value = { key: p.key, name: p.name, description: p.description || '' };
    showPermForm.value = true;
    showRoleForm.value = false;
    error.value = '';
    success.value = '';
  }

  function cancelPerm() {
    showPermForm.value = false;
    editingPerm.value = null;
    permForm.value = { key: '', name: '', description: '' };
  }

  async function submitPerm() {
    savingPerm.value = true;
    error.value = '';
    success.value = '';
    try {
      let res;
      if (editingPerm.value) {
        res = await api.put(`/permissions/manage/${editingPerm.value.id}/`, permForm.value);
      } else {
        res = await api.post('/permissions/manage/', permForm.value);
      }
      if (!res.success) {
        error.value = res.error?.message || '保存失败';
        return;
      }
      success.value = editingPerm.value ? '更新权限成功' : '创建权限成功';
      await loadPerms();
      showPermForm.value = false;
      editingPerm.value = null;
    } catch (e) {
      error.value = e.message || '保存失败';
    } finally {
      savingPerm.value = false;
    }
  }

  async function removePerm(p) {
    if (!confirm(`确认删除权限 "${p.name}"?`)) return;
    deletingPermId.value = p.id;
    error.value = '';
    success.value = '';
    try {
      const res = await api.delete(`/permissions/manage/${p.id}/`);
      if (!res.success) {
        error.value = res.error?.message || '删除失败';
        return;
      }
      success.value = '已删除权限';
      await loadPerms();
    } catch (e) {
      error.value = e.message || '删除失败';
    } finally {
      deletingPermId.value = null;
    }
  }

  // 辅助函数
  function getRoleUserCount(role) {
    return users.value.filter(u => (u.roles || []).some(r => r.id === role.id)).length;
  }

  function getPermRoleCount(perm) {
    return roles.value.filter(r => r.permissions.some(p => p.id === perm.id)).length;
  }

  return {
    // 状态
    loading,
    error,
    success,
    roles,
    permissions,
    permissionGroups,
    users,
    employees,
    loadingRoles,
    loadingPerms,
    loadingUsers,
    
    // 角色表单
    showRoleForm,
    editingRole,
    savingRole,
    deletingRoleId,
    roleForm,
    
    // 权限表单
    showPermForm,
    editingPerm,
    savingPerm,
    deletingPermId,
    permForm,
    
    // 方法
    loadRoles,
    loadPerms,
    loadPermGroups,
    loadUsers,
    loadEmployees,
    reload,
    startCreateRole,
    startEditRole,
    cancelRole,
    submitRole,
    removeRole,
    startCreatePerm,
    startEditPerm,
    cancelPerm,
    submitPerm,
    removePerm,
    getRoleUserCount,
    getPermRoleCount
  };
}
