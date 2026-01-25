/**
 * 通用数据 Store - 管理下拉选项等全局共享数据
 */
import { defineStore } from 'pinia';
import api from '../utils/api';

// 缓存配置
const CACHE_CONFIG = {
  departments: { ttl: 5 * 60 * 1000, key: 'cache_departments' },
  positions: { ttl: 5 * 60 * 1000, key: 'cache_positions' },
  roles: { ttl: 10 * 60 * 1000, key: 'cache_roles' },
};

export const useDataStore = defineStore('data', {
  state: () => ({
    // 组织架构
    departments: [],
    departmentTree: [],
    positions: [],
    
    // RBAC
    roles: [],
    
    // 加载状态
    loading: {
      departments: false,
      positions: false,
      roles: false,
    },
    
    // 加载时间戳（用于缓存判断）
    loadedAt: {
      departments: null,
      positions: null,
      roles: null,
    },
    
    // 错误信息
    errors: {},
  }),
  
  getters: {
    // 部门选项（用于下拉框）
    departmentOptions: (state) => {
      return state.departments.map(d => ({
        value: d.id,
        label: d.name,
        disabled: !d.is_active,
      }));
    },
    
    // 岗位选项（按部门分组）
    positionOptionsByDept: (state) => {
      const groups = {};
      state.positions.forEach(p => {
        const deptId = p.department?.id || 0;
        const deptName = p.department?.name || '未分配';
        if (!groups[deptId]) {
          groups[deptId] = {
            label: deptName,
            options: [],
          };
        }
        groups[deptId].options.push({
          value: p.id,
          label: p.name,
        });
      });
      return Object.values(groups);
    },
    
    // 角色选项
    roleOptions: (state) => {
      return state.roles.map(r => ({
        value: r.id,
        label: r.name,
        description: r.description,
      }));
    },
    
    // 根据ID获取部门
    getDepartmentById: (state) => (id) => {
      return state.departments.find(d => d.id === id);
    },
    
    // 根据ID获取岗位
    getPositionById: (state) => (id) => {
      return state.positions.find(p => p.id === id);
    },
  },
  
  actions: {
    /**
     * 检查缓存是否有效
     */
    isCacheValid(type) {
      const config = CACHE_CONFIG[type];
      if (!config || !this.loadedAt[type]) return false;
      return Date.now() - this.loadedAt[type] < config.ttl;
    },
    
    /**
     * 从本地存储恢复缓存
     */
    restoreFromStorage(type) {
      const config = CACHE_CONFIG[type];
      if (!config) return false;
      
      try {
        const cached = localStorage.getItem(config.key);
        if (cached) {
          const { data, timestamp } = JSON.parse(cached);
          if (Date.now() - timestamp < config.ttl) {
            this[type] = data;
            this.loadedAt[type] = timestamp;
            return true;
          }
        }
      } catch (e) {
        console.warn(`Failed to restore ${type} from storage:`, e);
      }
      return false;
    },
    
    /**
     * 保存到本地存储
     */
    saveToStorage(type, data) {
      const config = CACHE_CONFIG[type];
      if (!config) return;
      
      try {
        localStorage.setItem(config.key, JSON.stringify({
          data,
          timestamp: Date.now(),
        }));
      } catch (e) {
        console.warn(`Failed to save ${type} to storage:`, e);
      }
    },
    
    /**
     * 加载部门列表
     */
    async loadDepartments(force = false) {
      // 检查缓存
      if (!force && this.isCacheValid('departments')) {
        return this.departments;
      }
      
      // 尝试从本地存储恢复
      if (!force && this.restoreFromStorage('departments')) {
        return this.departments;
      }
      
      this.loading.departments = true;
      this.errors.departments = null;
      
      try {
        const resp = await api.get('/departments/', { params: { page_size: 1000 } });
        const data = resp.data?.results || resp.data || [];
        
        this.departments = data;
        this.departmentTree = this.buildDepartmentTree(data);
        this.loadedAt.departments = Date.now();
        this.saveToStorage('departments', data);
        
        return data;
      } catch (e) {
        this.errors.departments = e.message;
        throw e;
      } finally {
        this.loading.departments = false;
      }
    },
    
    /**
     * 构建部门树
     */
    buildDepartmentTree(departments) {
      const map = {};
      const tree = [];
      
      // 先建立映射
      departments.forEach(d => {
        map[d.id] = { ...d, children: [] };
      });
      
      // 构建树形结构
      departments.forEach(d => {
        const node = map[d.id];
        if (d.parent_id && map[d.parent_id]) {
          map[d.parent_id].children.push(node);
        } else {
          tree.push(node);
        }
      });
      
      return tree;
    },
    
    /**
     * 加载岗位列表
     */
    async loadPositions(force = false) {
      if (!force && this.isCacheValid('positions')) {
        return this.positions;
      }
      
      if (!force && this.restoreFromStorage('positions')) {
        return this.positions;
      }
      
      this.loading.positions = true;
      this.errors.positions = null;
      
      try {
        const resp = await api.get('/positions/', { params: { page_size: 1000 } });
        const data = resp.data?.results || resp.data || [];
        
        this.positions = data;
        this.loadedAt.positions = Date.now();
        this.saveToStorage('positions', data);
        
        return data;
      } catch (e) {
        this.errors.positions = e.message;
        throw e;
      } finally {
        this.loading.positions = false;
      }
    },
    
    /**
     * 加载角色列表
     */
    async loadRoles(force = false) {
      if (!force && this.isCacheValid('roles')) {
        return this.roles;
      }
      
      if (!force && this.restoreFromStorage('roles')) {
        return this.roles;
      }
      
      this.loading.roles = true;
      this.errors.roles = null;
      
      try {
        const resp = await api.get('/roles/');
        const data = resp.data?.results || resp.data || [];
        
        this.roles = data;
        this.loadedAt.roles = Date.now();
        this.saveToStorage('roles', data);
        
        return data;
      } catch (e) {
        this.errors.roles = e.message;
        throw e;
      } finally {
        this.loading.roles = false;
      }
    },
    
    /**
     * 预加载所有基础数据
     */
    async preloadAll() {
      await Promise.all([
        this.loadDepartments(),
        this.loadPositions(),
        this.loadRoles(),
      ]);
    },
    
    /**
     * 清除所有缓存
     */
    clearCache() {
      Object.keys(CACHE_CONFIG).forEach(type => {
        const config = CACHE_CONFIG[type];
        localStorage.removeItem(config.key);
        this.loadedAt[type] = null;
      });
    },
    
    /**
     * 失效指定类型的缓存（数据变更时调用）
     */
    invalidate(type) {
      if (this.loadedAt[type]) {
        this.loadedAt[type] = null;
        const config = CACHE_CONFIG[type];
        if (config) {
          localStorage.removeItem(config.key);
        }
      }
    },
  },
});


/**
 * UI 状态 Store - 管理全局 UI 状态
 */
export const useUIStore = defineStore('ui', {
  state: () => ({
    // 侧边栏状态
    sidebarCollapsed: localStorage.getItem('sidebar_collapsed') === 'true',
    
    // 全局加载状态
    globalLoading: false,
    loadingText: '',
    
    // 移动端状态
    isMobile: window.innerWidth < 768,
    
    // 主题
    theme: localStorage.getItem('theme') || 'light',
    
    // 全局消息
    messages: [],
  }),
  
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
      localStorage.setItem('sidebar_collapsed', this.sidebarCollapsed);
    },
    
    setSidebarCollapsed(value) {
      this.sidebarCollapsed = value;
      localStorage.setItem('sidebar_collapsed', value);
    },
    
    setGlobalLoading(loading, text = '') {
      this.globalLoading = loading;
      this.loadingText = text;
    },
    
    setMobile(isMobile) {
      this.isMobile = isMobile;
      // 移动端默认收起侧边栏
      if (isMobile) {
        this.sidebarCollapsed = true;
      }
    },
    
    setTheme(theme) {
      this.theme = theme;
      localStorage.setItem('theme', theme);
      document.documentElement.setAttribute('data-theme', theme);
    },
    
    addMessage(message) {
      const id = Date.now();
      this.messages.push({ id, ...message });
      
      // 自动移除
      if (message.duration !== 0) {
        setTimeout(() => {
          this.removeMessage(id);
        }, message.duration || 3000);
      }
      
      return id;
    },
    
    removeMessage(id) {
      const index = this.messages.findIndex(m => m.id === id);
      if (index > -1) {
        this.messages.splice(index, 1);
      }
    },
  },
});


/**
 * 请求 Store - 管理 API 请求状态
 */
export const useRequestStore = defineStore('request', {
  state: () => ({
    // 进行中的请求
    pending: new Map(),
    
    // 请求历史（用于调试）
    history: [],
    maxHistory: 50,
  }),
  
  getters: {
    // 是否有进行中的请求
    hasPending: (state) => state.pending.size > 0,
    
    // 获取指定请求的状态
    getRequestStatus: (state) => (key) => state.pending.get(key),
  },
  
  actions: {
    startRequest(key, config = {}) {
      this.pending.set(key, {
        startTime: Date.now(),
        ...config,
      });
    },
    
    endRequest(key, success = true, error = null) {
      const request = this.pending.get(key);
      if (request) {
        // 记录到历史
        this.history.unshift({
          key,
          duration: Date.now() - request.startTime,
          success,
          error: error?.message,
          timestamp: new Date().toISOString(),
        });
        
        // 限制历史记录数量
        if (this.history.length > this.maxHistory) {
          this.history.pop();
        }
        
        this.pending.delete(key);
      }
    },
    
    clearHistory() {
      this.history = [];
    },
  },
});
