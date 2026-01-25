/**
 * 请求防抖和节流工具
 * 用于优化频繁的 API 调用
 */

// 防抖函数
export function debounce(fn, delay = 300) {
  let timer = null;
  return function (...args) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

// 节流函数
export function throttle(fn, interval = 300) {
  let lastTime = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastTime >= interval) {
      lastTime = now;
      return fn.apply(this, args);
    }
  };
}

// 请求去重（同一时间只允许一个相同请求）
const pendingRequests = new Map();

export function dedupeRequest(key, requestFn) {
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key);
  }
  
  const promise = requestFn().finally(() => {
    pendingRequests.delete(key);
  });
  
  pendingRequests.set(key, promise);
  return promise;
}

/**
 * 批量请求合并
 * 将多个同类请求合并为一个批量请求
 */
export class BatchLoader {
  constructor(batchFn, options = {}) {
    this.batchFn = batchFn;
    this.delay = options.delay || 10; // 毫秒
    this.maxBatchSize = options.maxBatchSize || 50;
    this.queue = [];
    this.timer = null;
  }
  
  load(key) {
    return new Promise((resolve, reject) => {
      this.queue.push({ key, resolve, reject });
      
      if (this.queue.length >= this.maxBatchSize) {
        this.dispatch();
      } else if (!this.timer) {
        this.timer = setTimeout(() => this.dispatch(), this.delay);
      }
    });
  }
  
  dispatch() {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    
    const batch = this.queue;
    this.queue = [];
    
    if (batch.length === 0) return;
    
    const keys = batch.map(item => item.key);
    
    this.batchFn(keys)
      .then(results => {
        batch.forEach((item, index) => {
          item.resolve(results[index]);
        });
      })
      .catch(error => {
        batch.forEach(item => item.reject(error));
      });
  }
}

/**
 * 本地存储工具（带过期时间）
 */
export const storage = {
  set(key, value, ttl = null) {
    const item = {
      value,
      time: Date.now(),
      ttl
    };
    localStorage.setItem(key, JSON.stringify(item));
  },
  
  get(key) {
    const itemStr = localStorage.getItem(key);
    if (!itemStr) return null;
    
    try {
      const item = JSON.parse(itemStr);
      if (item.ttl && Date.now() - item.time > item.ttl) {
        localStorage.removeItem(key);
        return null;
      }
      return item.value;
    } catch {
      return null;
    }
  },
  
  remove(key) {
    localStorage.removeItem(key);
  },
  
  clear() {
    localStorage.clear();
  }
};

/**
 * 格式化工具函数
 */
export const formatters = {
  // 金额格式化
  currency(value, decimals = 2) {
    if (value === null || value === undefined) return '--';
    const num = parseFloat(value);
    if (isNaN(num)) return '--';
    return `¥${num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
  },
  
  // 日期格式化
  date(dateStr, format = 'YYYY-MM-DD') {
    if (!dateStr) return '--';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return '--';
    
    const pad = n => String(n).padStart(2, '0');
    const replacements = {
      'YYYY': d.getFullYear(),
      'MM': pad(d.getMonth() + 1),
      'DD': pad(d.getDate()),
      'HH': pad(d.getHours()),
      'mm': pad(d.getMinutes()),
      'ss': pad(d.getSeconds()),
    };
    
    let result = format;
    for (const [key, value] of Object.entries(replacements)) {
      result = result.replace(key, value);
    }
    return result;
  },
  
  // 相对时间
  relativeTime(dateStr) {
    if (!dateStr) return '--';
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now - d;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;
    return this.date(dateStr);
  },
  
  // 文件大小格式化
  fileSize(bytes) {
    if (!bytes) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    let i = 0;
    while (bytes >= 1024 && i < units.length - 1) {
      bytes /= 1024;
      i++;
    }
    return `${bytes.toFixed(2)} ${units[i]}`;
  },
  
  // 手机号脱敏
  phone(phone) {
    if (!phone) return '--';
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
  },
  
  // 身份证脱敏
  idCard(idCard) {
    if (!idCard) return '--';
    return idCard.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2');
  }
};

/**
 * 表单验证规则
 */
export const validators = {
  required: (message = '此字段必填') => ({
    required: true,
    message,
    trigger: 'blur'
  }),
  
  phone: {
    pattern: /^1[3-9]\d{9}$/,
    message: '请输入有效的手机号',
    trigger: 'blur'
  },
  
  email: {
    type: 'email',
    message: '请输入有效的邮箱',
    trigger: 'blur'
  },
  
  idCard: {
    pattern: /^\d{17}[\dXx]$/,
    message: '请输入有效的身份证号',
    trigger: 'blur'
  },
  
  minLength: (min, message) => ({
    min,
    message: message || `最少${min}个字符`,
    trigger: 'blur'
  }),
  
  maxLength: (max, message) => ({
    max,
    message: message || `最多${max}个字符`,
    trigger: 'blur'
  })
};

/**
 * API 请求增强工具
 */
export class ApiHelper {
  /**
   * 带重试的请求
   * @param {Function} requestFn - 请求函数
   * @param {Object} options - 配置选项
   */
  static async withRetry(requestFn, options = {}) {
    const {
      maxRetries = 3,
      retryDelay = 1000,
      retryOn = [408, 500, 502, 503, 504],
      onRetry = null,
    } = options;
    
    let lastError;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await requestFn();
      } catch (error) {
        lastError = error;
        const status = error.response?.status;
        
        // 检查是否应该重试
        if (attempt < maxRetries && retryOn.includes(status)) {
          if (onRetry) {
            onRetry(attempt + 1, error);
          }
          // 指数退避
          await new Promise(resolve => 
            setTimeout(resolve, retryDelay * Math.pow(2, attempt))
          );
          continue;
        }
        throw error;
      }
    }
    throw lastError;
  }
  
  /**
   * 带超时的请求
   */
  static async withTimeout(requestFn, timeout = 30000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
      return await requestFn(controller.signal);
    } finally {
      clearTimeout(timeoutId);
    }
  }
  
  /**
   * 带缓存的请求
   */
  static async withCache(key, requestFn, ttl = 60000) {
    const cached = storage.get(key);
    if (cached) return cached;
    
    const result = await requestFn();
    storage.set(key, result, ttl);
    return result;
  }
}

/**
 * 错误处理工具
 */
export const errorHandler = {
  // 解析 API 错误
  parseApiError(error) {
    if (error.response) {
      const { status, data } = error.response;
      return {
        status,
        message: data?.message || data?.detail || this.getStatusMessage(status),
        code: data?.code || 'api_error',
        errors: data?.errors || null
      };
    }
    
    if (error.request) {
      return {
        status: 0,
        message: '网络连接失败，请检查网络',
        code: 'network_error',
        errors: null
      };
    }
    
    return {
      status: -1,
      message: error.message || '未知错误',
      code: 'unknown_error',
      errors: null
    };
  },
  
  // 获取状态码对应消息
  getStatusMessage(status) {
    const messages = {
      400: '请求参数错误',
      401: '登录已过期，请重新登录',
      403: '没有操作权限',
      404: '请求的资源不存在',
      408: '请求超时',
      429: '请求过于频繁，请稍后再试',
      500: '服务器内部错误',
      502: '网关错误',
      503: '服务暂时不可用',
      504: '网关超时'
    };
    return messages[status] || `请求失败 (${status})`;
  },
  
  // 处理表单验证错误
  parseFieldErrors(errors) {
    if (!errors || typeof errors !== 'object') return {};
    
    const result = {};
    for (const [field, messages] of Object.entries(errors)) {
      result[field] = Array.isArray(messages) ? messages.join('; ') : messages;
    }
    return result;
  }
};

/**
 * 数组工具函数
 */
export const arrayUtils = {
  // 数组去重
  unique(arr, key = null) {
    if (!key) return [...new Set(arr)];
    const seen = new Set();
    return arr.filter(item => {
      const k = item[key];
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });
  },
  
  // 数组分组
  groupBy(arr, key) {
    return arr.reduce((groups, item) => {
      const k = typeof key === 'function' ? key(item) : item[key];
      (groups[k] = groups[k] || []).push(item);
      return groups;
    }, {});
  },
  
  // 数组排序
  sortBy(arr, key, order = 'asc') {
    return [...arr].sort((a, b) => {
      const va = typeof key === 'function' ? key(a) : a[key];
      const vb = typeof key === 'function' ? key(b) : b[key];
      const cmp = va < vb ? -1 : va > vb ? 1 : 0;
      return order === 'asc' ? cmp : -cmp;
    });
  },
  
  // 数组转树形结构
  toTree(arr, { id = 'id', parentId = 'parent_id', children = 'children' } = {}) {
    const map = {};
    const result = [];
    
    arr.forEach(item => {
      map[item[id]] = { ...item, [children]: [] };
    });
    
    arr.forEach(item => {
      const node = map[item[id]];
      const parent = map[item[parentId]];
      if (parent) {
        parent[children].push(node);
      } else {
        result.push(node);
      }
    });
    
    return result;
  },
  
  // 树形结构扁平化
  flattenTree(tree, children = 'children') {
    const result = [];
    const traverse = (nodes, level = 0) => {
      nodes.forEach(node => {
        const { [children]: childNodes, ...rest } = node;
        result.push({ ...rest, level });
        if (childNodes?.length) {
          traverse(childNodes, level + 1);
        }
      });
    };
    traverse(tree);
    return result;
  }
};

/**
 * 对象工具函数
 */
export const objectUtils = {
  // 深拷贝
  deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj);
    if (obj instanceof Array) return obj.map(item => this.deepClone(item));
    if (obj instanceof Object) {
      const copy = {};
      Object.keys(obj).forEach(key => {
        copy[key] = this.deepClone(obj[key]);
      });
      return copy;
    }
    return obj;
  },
  
  // 选取指定字段
  pick(obj, keys) {
    return keys.reduce((result, key) => {
      if (key in obj) result[key] = obj[key];
      return result;
    }, {});
  },
  
  // 排除指定字段
  omit(obj, keys) {
    const keySet = new Set(keys);
    return Object.keys(obj).reduce((result, key) => {
      if (!keySet.has(key)) result[key] = obj[key];
      return result;
    }, {});
  },
  
  // 判断是否为空对象
  isEmpty(obj) {
    return !obj || Object.keys(obj).length === 0;
  },
  
  // 深度合并
  deepMerge(target, source) {
    const result = { ...target };
    for (const key of Object.keys(source)) {
      if (source[key] instanceof Object && key in target) {
        result[key] = this.deepMerge(target[key], source[key]);
      } else {
        result[key] = source[key];
      }
    }
    return result;
  }
};
