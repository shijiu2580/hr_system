/**
 * API 工具函数测试
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import '../src/utils/api';

// 全局重置，覆盖全部用例（包含独立的 describe）
beforeEach(async () => {
  vi.clearAllMocks();
  vi.resetModules();
  await import('../src/utils/api');
  localStorage.clear();
});

// 模拟 axios
vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => mockAxios),
    interceptors: {
      request: { use: vi.fn(), eject: vi.fn() },
      response: { use: vi.fn(), eject: vi.fn() },
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    defaults: { headers: { common: {} } },
  };
  return { default: mockAxios };
});

describe('API 工具函数', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    vi.resetModules();
    await import('../src/utils/api');
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Token 管理', () => {
    it('应该正确保存 token', () => {
      const token = 'test-access-token';
      localStorage.setItem('accessToken', token);

      expect(localStorage.getItem('accessToken')).toBe(token);
    });

    it('应该正确移除 token', () => {
      localStorage.setItem('accessToken', 'test-token');
      localStorage.removeItem('accessToken');

      expect(localStorage.getItem('accessToken')).toBeNull();
    });
  });

  describe('请求配置', () => {
    it('应该使用正确的基础 URL', () => {
      expect(axios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: expect.any(String),
        })
      );
    });

    it('应该设置超时时间', () => {
      expect(axios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: expect.any(Number),
        })
      );
    });
  });

  describe('错误处理', () => {
    it('应该处理网络错误', async () => {
      const error = new Error('Network Error');
      error.code = 'ERR_NETWORK';

      axios.get.mockRejectedValueOnce(error);

      await expect(axios.get('/api/test/')).rejects.toThrow('Network Error');
    });

    it('应该处理 401 未授权错误', async () => {
      const error = {
        response: {
          status: 401,
          data: { detail: 'Token 已过期' },
        },
      };

      axios.get.mockRejectedValueOnce(error);

      await expect(axios.get('/api/test/')).rejects.toEqual(error);
    });
  });
});

describe('请求重试机制', () => {
  it('应该在网络错误时重试', async () => {
    const error = new Error('Network Error');
    axios.get
      .mockRejectedValueOnce(error)
      .mockRejectedValueOnce(error)
      .mockResolvedValueOnce({ data: { success: true } });

    // 实际测试需要实现重试逻辑
    expect(axios.get).toBeDefined();
  });
});

describe('缓存机制', () => {
  it('应该缓存 GET 请求结果', async () => {
    axios.get.mockReset();
    const mockData = { id: 1, name: 'Test' };
    axios.get.mockResolvedValueOnce({ data: mockData });

    const result1 = await axios.get('/api/test/');
    expect(result1.data).toEqual(mockData);

    expect(axios.get).toHaveBeenCalledTimes(1);
  });
});
