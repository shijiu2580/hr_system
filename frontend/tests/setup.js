/**
 * 测试辅助工具和配置
 */
import { config } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { vi } from 'vitest';

// 全局配置
config.global.stubs = {
  // 存根路由组件
  'router-link': true,
  'router-view': true,
};

// 模拟 localStorage
const localStorageMock = {
  store: {},
  getItem: vi.fn((key) => localStorageMock.store[key] || null),
  setItem: vi.fn((key, value) => {
    localStorageMock.store[key] = value.toString();
  }),
  removeItem: vi.fn((key) => {
    delete localStorageMock.store[key];
  }),
  clear: vi.fn(() => {
    localStorageMock.store = {};
  }),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// 模拟 sessionStorage
Object.defineProperty(window, 'sessionStorage', {
  value: localStorageMock,
});

// 模拟 matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// 模拟 IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// 模拟 ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

/**
 * 创建测试用的 Pinia 实例
 */
export function createTestPinia() {
  const pinia = createPinia();
  setActivePinia(pinia);
  return pinia;
}

/**
 * 创建模拟的 API 响应
 */
export function createMockResponse(data, options = {}) {
  return {
    data,
    status: options.status || 200,
    statusText: options.statusText || 'OK',
    headers: options.headers || {},
    config: options.config || {},
  };
}

/**
 * 创建模拟的分页响应
 */
export function createMockPaginatedResponse(results, options = {}) {
  const { page = 1, pageSize = 20, total = results.length } = options;
  
  return createMockResponse({
    count: total,
    next: page * pageSize < total ? `/api/endpoint/?page=${page + 1}` : null,
    previous: page > 1 ? `/api/endpoint/?page=${page - 1}` : null,
    results,
  });
}

/**
 * 等待组件更新
 */
export async function flushPromises() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

/**
 * 模拟延迟
 */
export function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * 创建模拟用户数据
 */
export function createMockUser(overrides = {}) {
  return {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    is_staff: false,
    is_superuser: false,
    employee: {
      id: 1,
      name: '测试用户',
      employee_id: 'EMP001',
      department_name: '技术部',
      position_name: '工程师',
    },
    ...overrides,
  };
}

/**
 * 创建模拟员工数据
 */
export function createMockEmployee(overrides = {}) {
  return {
    id: 1,
    name: '张三',
    employee_id: 'EMP001',
    gender: 'male',
    phone: '13800138000',
    email: 'zhangsan@example.com',
    department: 1,
    department_name: '技术部',
    position: 1,
    position_name: '软件工程师',
    status: 'active',
    hire_date: '2024-01-01',
    ...overrides,
  };
}

/**
 * 创建模拟考勤数据
 */
export function createMockAttendance(overrides = {}) {
  return {
    id: 1,
    employee: 1,
    employee_name: '张三',
    date: '2024-01-15',
    check_in: '09:00:00',
    check_out: '18:00:00',
    status: 'normal',
    ...overrides,
  };
}

/**
 * 创建模拟请假数据
 */
export function createMockLeave(overrides = {}) {
  return {
    id: 1,
    employee: 1,
    employee_name: '张三',
    leave_type: 'annual',
    leave_type_display: '年假',
    start_date: '2024-01-15',
    end_date: '2024-01-16',
    reason: '休息',
    status: 'pending',
    ...overrides,
  };
}
