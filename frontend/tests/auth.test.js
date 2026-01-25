/**
 * Auth Store 测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from '../src/stores/auth';

// 模拟 API
vi.mock('../src/utils/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

// 模拟 router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
  }),
}));

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      const store = useAuthStore();
      
      expect(store.user).toBeNull();
      expect(store.accessToken).toBeNull();
      expect(store.refreshToken).toBeNull();
      expect(store.isAuthenticated).toBe(false);
    });
  });

  describe('登录功能', () => {
    it('isAuthenticated 应该在有 token 时返回 true', () => {
      const store = useAuthStore();
      
      store.accessToken = 'test-token';
      store.user = { id: 1, username: 'test' };
      
      expect(store.isAuthenticated).toBe(true);
    });

    it('应该正确清除用户信息', () => {
      const store = useAuthStore();
      
      // 设置用户信息
      store.accessToken = 'test-token';
      store.refreshToken = 'test-refresh';
      store.user = { id: 1, username: 'test' };
      
      // 清除
      store.logout();
      
      expect(store.user).toBeNull();
      expect(store.accessToken).toBeNull();
      expect(store.refreshToken).toBeNull();
      expect(store.isAuthenticated).toBe(false);
    });
  });

  describe('权限检查', () => {
    it('管理员应该有所有权限', () => {
      const store = useAuthStore();
      
      store.user = {
        id: 1,
        username: 'admin',
        is_superuser: true,
      };
      
      expect(store.hasPermission('any_permission')).toBe(true);
    });

    it('普通用户应该根据角色权限检查', () => {
      const store = useAuthStore();
      
      store.user = {
        id: 1,
        username: 'user',
        is_superuser: false,
        role: {
          permissions: ['view_employee', 'view_attendance'],
        },
      };
      
      expect(store.hasPermission('view_employee')).toBe(true);
      expect(store.hasPermission('delete_employee')).toBe(false);
    });
  });

  describe('Token 刷新', () => {
    it('应该正确更新 access token', () => {
      const store = useAuthStore();
      
      store.accessToken = 'old-token';
      store.setAccessToken('new-token');
      
      expect(store.accessToken).toBe('new-token');
    });
  });
});

describe('Token 持久化', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('应该从 localStorage 恢复 token', () => {
    localStorage.setItem('accessToken', 'saved-token');
    localStorage.setItem('refreshToken', 'saved-refresh');
    
    setActivePinia(createPinia());
    const store = useAuthStore();
    
    // 初始化时应该从 localStorage 读取
    store.initFromStorage();
    
    expect(store.accessToken).toBe('saved-token');
    expect(store.refreshToken).toBe('saved-refresh');
  });

  it('登出时应该清除 localStorage', () => {
    localStorage.setItem('accessToken', 'test-token');
    localStorage.setItem('refreshToken', 'test-refresh');
    
    setActivePinia(createPinia());
    const store = useAuthStore();
    
    store.logout();
    
    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('refreshToken')).toBeNull();
  });
});
