/**
 * Vue 组合式函数（Composables）
 * 提供可复用的响应式逻辑
 */
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { debounce } from './helpers';
import api from './api';

/**
 * 分页列表数据加载
 * @param {string} apiUrl - API 地址
 * @param {Object} options - 配置项
 */
export function usePaginatedList(apiUrl, options = {}) {
  const data = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const currentPage = ref(1);
  const pageSize = ref(options.pageSize || 20);
  const total = ref(0);
  const filters = ref(options.defaultFilters || {});

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value));
  const hasMore = computed(() => currentPage.value < totalPages.value);

  async function fetchData(resetPage = false) {
    if (resetPage) currentPage.value = 1;
    
    loading.value = true;
    error.value = null;
    
    try {
      const params = {
        page: currentPage.value,
        page_size: pageSize.value,
        ...filters.value
      };
      
      // 过滤掉空值
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });
      
      const res = await api.get(apiUrl, { params, noCache: true });
      if (res.success) {
        data.value = res.data?.results || res.data || [];
        total.value = res.data?.count || data.value.length;
      } else {
        error.value = res.error?.message || '加载失败';
      }
    } catch (e) {
      error.value = e.message || '请求失败';
    } finally {
      loading.value = false;
    }
  }

  function setFilter(key, value) {
    filters.value[key] = value;
    fetchData(true);
  }

  function goToPage(page) {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page;
      fetchData();
    }
  }

  function refresh() {
    fetchData();
  }

  // 搜索防抖
  const debouncedSearch = debounce((value) => {
    filters.value.search = value;
    fetchData(true);
  }, 300);

  return {
    data,
    loading,
    error,
    currentPage,
    pageSize,
    total,
    totalPages,
    hasMore,
    filters,
    fetchData,
    setFilter,
    goToPage,
    refresh,
    debouncedSearch
  };
}


/**
 * 表单状态管理
 * @param {Object} initialValues - 初始值
 */
export function useForm(initialValues = {}) {
  const form = ref({ ...initialValues });
  const errors = ref({});
  const isDirty = ref(false);
  const isSubmitting = ref(false);

  // 监听表单变化
  watch(form, () => {
    isDirty.value = true;
  }, { deep: true });

  function setFieldValue(field, value) {
    form.value[field] = value;
    // 清除该字段的错误
    if (errors.value[field]) {
      delete errors.value[field];
    }
  }

  function setFieldError(field, message) {
    errors.value[field] = message;
  }

  function reset() {
    form.value = { ...initialValues };
    errors.value = {};
    isDirty.value = false;
  }

  function validate(rules) {
    errors.value = {};
    let isValid = true;

    for (const [field, fieldRules] of Object.entries(rules)) {
      const value = form.value[field];
      
      for (const rule of fieldRules) {
        if (rule.required && !value && value !== 0) {
          errors.value[field] = rule.message || '此项必填';
          isValid = false;
          break;
        }
        if (rule.pattern && value && !rule.pattern.test(value)) {
          errors.value[field] = rule.message || '格式不正确';
          isValid = false;
          break;
        }
        if (rule.min && value && value.length < rule.min) {
          errors.value[field] = rule.message || `最少${rule.min}个字符`;
          isValid = false;
          break;
        }
        if (rule.max && value && value.length > rule.max) {
          errors.value[field] = rule.message || `最多${rule.max}个字符`;
          isValid = false;
          break;
        }
        if (rule.validator) {
          const result = rule.validator(value, form.value);
          if (result !== true) {
            errors.value[field] = result || rule.message || '验证失败';
            isValid = false;
            break;
          }
        }
      }
    }

    return isValid;
  }

  return {
    form,
    errors,
    isDirty,
    isSubmitting,
    setFieldValue,
    setFieldError,
    reset,
    validate
  };
}


/**
 * 确认对话框
 */
export function useConfirm() {
  const visible = ref(false);
  const title = ref('');
  const message = ref('');
  const confirmText = ref('确定');
  const cancelText = ref('取消');
  const loading = ref(false);
  let resolvePromise = null;

  function confirm(options = {}) {
    title.value = options.title || '确认';
    message.value = options.message || '确定要执行此操作吗？';
    confirmText.value = options.confirmText || '确定';
    cancelText.value = options.cancelText || '取消';
    visible.value = true;

    return new Promise((resolve) => {
      resolvePromise = resolve;
    });
  }

  function handleConfirm() {
    visible.value = false;
    resolvePromise?.(true);
  }

  function handleCancel() {
    visible.value = false;
    resolvePromise?.(false);
  }

  return {
    visible,
    title,
    message,
    confirmText,
    cancelText,
    loading,
    confirm,
    handleConfirm,
    handleCancel
  };
}


/**
 * 消息提示
 */
export function useMessage() {
  const messages = ref([]);
  let messageId = 0;

  function addMessage(type, content, duration = 3000) {
    const id = ++messageId;
    messages.value.push({ id, type, content });

    if (duration > 0) {
      setTimeout(() => {
        removeMessage(id);
      }, duration);
    }

    return id;
  }

  function removeMessage(id) {
    const index = messages.value.findIndex(m => m.id === id);
    if (index > -1) {
      messages.value.splice(index, 1);
    }
  }

  return {
    messages,
    success: (content, duration) => addMessage('success', content, duration),
    error: (content, duration) => addMessage('error', content, duration),
    warning: (content, duration) => addMessage('warning', content, duration),
    info: (content, duration) => addMessage('info', content, duration),
    remove: removeMessage
  };
}


/**
 * 定时轮询
 * @param {Function} fn - 要执行的函数
 * @param {number} interval - 间隔时间（毫秒）
 */
export function usePolling(fn, interval = 30000) {
  const isActive = ref(false);
  let timer = null;

  function start() {
    if (isActive.value) return;
    isActive.value = true;
    
    const poll = async () => {
      if (!isActive.value) return;
      await fn();
      if (isActive.value) {
        timer = setTimeout(poll, interval);
      }
    };
    
    poll();
  }

  function stop() {
    isActive.value = false;
    if (timer) {
      clearTimeout(timer);
      timer = null;
    }
  }

  onUnmounted(stop);

  return { isActive, start, stop };
}


/**
 * 本地存储响应式包装
 * @param {string} key - 存储键
 * @param {*} defaultValue - 默认值
 */
export function useLocalStorage(key, defaultValue = null) {
  const storedValue = localStorage.getItem(key);
  const value = ref(storedValue ? JSON.parse(storedValue) : defaultValue);

  watch(value, (newValue) => {
    if (newValue === null || newValue === undefined) {
      localStorage.removeItem(key);
    } else {
      localStorage.setItem(key, JSON.stringify(newValue));
    }
  }, { deep: true });

  return value;
}


/**
 * 屏幕尺寸响应式
 */
export function useScreenSize() {
  const width = ref(window.innerWidth);
  const height = ref(window.innerHeight);
  
  const isMobile = computed(() => width.value < 768);
  const isTablet = computed(() => width.value >= 768 && width.value < 1024);
  const isDesktop = computed(() => width.value >= 1024);

  function handleResize() {
    width.value = window.innerWidth;
    height.value = window.innerHeight;
  }

  onMounted(() => {
    window.addEventListener('resize', handleResize);
  });

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
  });

  return { width, height, isMobile, isTablet, isDesktop };
}


/**
 * 快捷键绑定
 * @param {Object} keyMap - 键位映射 { 'ctrl+s': handler }
 */
export function useKeyboard(keyMap) {
  function handleKeydown(event) {
    const key = [];
    if (event.ctrlKey || event.metaKey) key.push('ctrl');
    if (event.shiftKey) key.push('shift');
    if (event.altKey) key.push('alt');
    key.push(event.key.toLowerCase());
    
    const combo = key.join('+');
    
    if (keyMap[combo]) {
      event.preventDefault();
      keyMap[combo](event);
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
  });

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
  });
}
