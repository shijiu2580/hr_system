<template>
  <div class="error-boundary">
    <slot v-if="!hasError" />
    <div v-else class="error-fallback">
      <div class="error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <h3 class="error-title">{{ title }}</h3>
      <p class="error-message">{{ errorMessage }}</p>
      <div class="error-actions">
        <button class="btn-retry" @click="handleRetry">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          重试
        </button>
        <button v-if="showHome" class="btn-home" @click="handleHome">
          返回首页
        </button>
      </div>
      <details v-if="showDetails && errorDetails" class="error-details">
        <summary>错误详情</summary>
        <pre>{{ errorDetails }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup>
import { ref, onErrorCaptured, computed } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  title: {
    type: String,
    default: '页面出错了'
  },
  fallbackMessage: {
    type: String,
    default: '抱歉，页面加载时发生了错误，请尝试刷新页面。'
  },
  showHome: {
    type: Boolean,
    default: true
  },
  showDetails: {
    type: Boolean,
    default: import.meta.env.DEV // 仅开发环境显示详情
  },
  onError: {
    type: Function,
    default: null
  }
});

const emit = defineEmits(['error', 'retry']);

const router = useRouter();
const hasError = ref(false);
const error = ref(null);

const errorMessage = computed(() => {
  if (!error.value) return props.fallbackMessage;
  return error.value.message || props.fallbackMessage;
});

const errorDetails = computed(() => {
  if (!error.value) return '';
  return `${error.value.name}: ${error.value.message}\n\n${error.value.stack || ''}`;
});

// 捕获子组件错误
onErrorCaptured((err, instance, info) => {
  console.error('Error captured by ErrorBoundary:', err);
  console.error('Component:', instance);
  console.error('Info:', info);
  
  hasError.value = true;
  error.value = err;
  
  // 触发回调
  if (props.onError) {
    props.onError(err, instance, info);
  }
  emit('error', { error: err, instance, info });
  
  // 上报错误（可以接入监控系统）
  reportError(err, info);
  
  // 返回 false 阻止错误继续传播
  return false;
});

function handleRetry() {
  hasError.value = false;
  error.value = null;
  emit('retry');
}

function handleHome() {
  hasError.value = false;
  error.value = null;
  router.push('/');
}

function reportError(err, info) {
  // 这里可以接入错误监控系统，如 Sentry
  if (import.meta.env.PROD) {
    // 生产环境上报错误
    console.error('[Error Report]', {
      message: err.message,
      stack: err.stack,
      info,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
    });
  }
}

// 暴露重置方法
defineExpose({
  reset() {
    hasError.value = false;
    error.value = null;
  }
});
</script>

<style scoped>
.error-boundary {
  width: 100%;
  height: 100%;
}

.error-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 40px 20px;
  text-align: center;
}

.error-icon {
  color: #f56c6c;
  margin-bottom: 20px;
}

.error-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
}

.error-message {
  font-size: 14px;
  color: #909399;
  margin: 0 0 24px 0;
  max-width: 400px;
}

.error-actions {
  display: flex;
  gap: 12px;
}

.btn-retry,
.btn-home {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-retry {
  background: #409eff;
  color: white;
  border: none;
}

.btn-retry:hover {
  background: #66b1ff;
}

.btn-home {
  background: white;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.btn-home:hover {
  color: #409eff;
  border-color: #c6e2ff;
  background: #ecf5ff;
}

.error-details {
  margin-top: 24px;
  width: 100%;
  max-width: 600px;
  text-align: left;
}

.error-details summary {
  cursor: pointer;
  color: #909399;
  font-size: 13px;
  margin-bottom: 8px;
}

.error-details pre {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  overflow-x: auto;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
