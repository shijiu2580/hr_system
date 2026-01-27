import axios from 'axios';
import { useAuthStore } from '../stores/auth';

// 后端基地址：支持部署时通过环境变量注入；开发默认 '/api'
const baseURL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '/api';

const axiosInstance = axios.create({
  baseURL,
  timeout: 30000,  // 30秒超时（上传等场景需要更长时间）
});

// ============ 请求缓存 ============
const cache = new Map();
const CACHE_TTL = 30 * 1000; // 30秒
const MAX_CACHE_SIZE = 100;

function getCacheKey(url, params) {
  return `${url}?${JSON.stringify(params || {})}`;
}

function getFromCache(key) {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.time < CACHE_TTL) {
    return cached.data;
  }
  cache.delete(key);
  return null;
}

function setCache(key, data) {
  cache.set(key, { data, time: Date.now() });
  // 清理过期缓存（LRU 策略）
  if (cache.size > MAX_CACHE_SIZE) {
    const now = Date.now();
    for (const [k, v] of cache) {
      if (now - v.time > CACHE_TTL) cache.delete(k);
      if (cache.size <= MAX_CACHE_SIZE / 2) break;
    }
  }
}

// 清除缓存（在数据变更后调用）
export function clearCache(urlPrefix) {
  if (!urlPrefix) {
    cache.clear();
  } else {
    for (const key of cache.keys()) {
      if (key.startsWith(urlPrefix)) cache.delete(key);
    }
  }
}

// ============ 请求队列（防止重复请求）============
const pendingRequests = new Map();

function getRequestKey(config) {
  return `${config.method}:${config.url}:${JSON.stringify(config.params || {})}`;
}

function addPendingRequest(config) {
  const key = getRequestKey(config);
  if (pendingRequests.has(key)) {
    // 取消之前的重复请求
    const cancel = pendingRequests.get(key);
    cancel('Duplicate request cancelled');
  }
  const controller = new AbortController();
  config.signal = controller.signal;
  pendingRequests.set(key, () => controller.abort());
}

function removePendingRequest(config) {
  const key = getRequestKey(config);
  pendingRequests.delete(key);
}

// ============ 请求/响应拦截器 ============
let refreshPromise = null; // 防止并发重复刷新
let requestCount = 0; // 请求计数

axiosInstance.interceptors.request.use(cfg => {
  requestCount++;

  // 添加请求ID
  cfg.headers['X-Request-ID'] = `${Date.now()}-${requestCount}`;

  // 添加认证头
  const auth = useAuthStore();
  if (auth.accessToken) {
    cfg.headers.Authorization = `Bearer ${auth.accessToken}`;
  }

  // 防止重复请求（GET 请求）
  if (cfg.method === 'get' && !cfg.skipDuplicateCheck) {
    addPendingRequest(cfg);
  }

  return cfg;
}, err => Promise.reject(err));

axiosInstance.interceptors.response.use(
  response => {
    removePendingRequest(response.config);
    return response;
  },
  async err => {
    if (err.config) {
      removePendingRequest(err.config);
    }

    // 请求被取消
    if (axios.isCancel(err)) {
      return Promise.reject({ cancelled: true, message: err.message });
    }

    const { response, config } = err;
    if (!response) {
      // 网络错误
      return Promise.reject({
        message: '网络连接失败，请检查网络',
        networkError: true,
      });
    }

    // 401 未授权：尝试刷新 token
    if (response.status === 401 && !config.__isRetry) {
      const auth = useAuthStore();
      if (!auth.refreshToken) {
        auth.forceLogout();
        return Promise.reject(err);
      }
      try {
        if (!refreshPromise) {
          refreshPromise = auth.refresh();
        }
        await refreshPromise;
        refreshPromise = null;
        config.__isRetry = true;
        return axiosInstance(config);
    } catch (e) {
      refreshPromise = null;
      auth.forceLogout();
    }
  }

  // 429 限流
  if (response.status === 429) {
    return Promise.reject({
      message: '请求过于频繁，请稍后再试',
      rateLimited: true,
      retryAfter: response.headers['retry-after'],
    });
  }

  return Promise.reject(err);
});

// ============ 统一请求方法 ============
async function request(method, url, options = {}) {
  const cfg = { method, url, ...options };

  // GET 请求使用缓存（除非明确指定 noCache）
  if (method === 'get' && !options.noCache) {
    const cacheKey = getCacheKey(url, options.params);
    const cached = getFromCache(cacheKey);
    if (cached) {
      return cached;
    }
  }

  try {
    const resp = await axiosInstance(cfg);
    const result = {
      success: true,
      data: resp.data?.data ?? resp.data,
      detail: resp.data?.detail,
      raw: resp,
      error: null,
    };

    // 缓存 GET 请求结果
    if (method === 'get' && !options.noCache) {
      const cacheKey = getCacheKey(url, options.params);
      setCache(cacheKey, result);
    }

    return result;
  } catch (err) {
    // 请求被取消
    if (err.cancelled) {
      return { success: false, data: null, error: { message: '请求已取消', cancelled: true } };
    }

    const message = err.message
      || err.response?.data?.error?.message
      || err.response?.data?.detail
      || '请求失败';

    return {
      success: false,
      data: null,
      detail: null,
      raw: err.response,
      error: {
        message,
        code: err.response?.data?.error?.code,
        status: err.response?.status,
        networkError: err.networkError,
        rateLimited: err.rateLimited,
        raw: err,
      },
    };
  }
}

// ============ 文件上传 ============
async function uploadFile(url, file, options = {}) {
  const formData = new FormData();
  formData.append(options.fieldName || 'file', file);

  // 添加额外字段
  if (options.data) {
    Object.entries(options.data).forEach(([key, value]) => {
      formData.append(key, value);
    });
  }

  return request('post', url, {
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: options.timeout || 120000, // 上传默认 2 分钟超时
    onUploadProgress: options.onProgress,
    skipDuplicateCheck: true,
  });
}

// ============ 导出 API 对象 ============
const api = {
  get(url, config) {
    return request('get', url, { ...config });
  },
  post(url, data, config) {
    clearCache(); // POST 后清除缓存
    return request('post', url, { data, ...config });
  },
  put(url, data, config) {
    clearCache(); // PUT 后清除缓存
    return request('put', url, { data, ...config });
  },
  patch(url, data, config) {
    clearCache(); // PATCH 后清除缓存
    return request('patch', url, { data, ...config });
  },
  delete(url, config) {
    clearCache(); // DELETE 后清除缓存
    return request('delete', url, { ...config });
  },

  // 文件上传
  upload: uploadFile,

  // 下载文件
  async download(url, filename, config = {}) {
    try {
      const resp = await axiosInstance({
        url,
        method: 'get',
        responseType: 'blob',
        ...config,
      });

      // 创建下载链接
      const blobUrl = window.URL.createObjectURL(resp.data);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);

      return { success: true };
    } catch (err) {
      return { success: false, error: { message: '下载失败' } };
    }
  },

  // 暴露原始 axios 实例以兼容旧用法
  raw: axiosInstance,

  // 手动清除缓存
  clearCache,

  // 取消所有进行中的请求
  cancelAll() {
    for (const cancel of pendingRequests.values()) {
      cancel('Request cancelled by user');
    }
    pendingRequests.clear();
  },
};

export default api;
