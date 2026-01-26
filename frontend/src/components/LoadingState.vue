<template>
  <div class="loading-state" :class="{ 'is-fullscreen': fullscreen }">
    <!-- 骨架屏 -->
    <template v-if="type === 'skeleton'">
      <div class="skeleton-wrapper">
        <div v-for="i in rows" :key="i" class="skeleton-row">
          <div
            v-for="j in columns"
            :key="j"
            class="skeleton-item"
            :style="{ width: getItemWidth(j) }"
          ></div>
        </div>
      </div>
    </template>

    <!-- 加载动画 -->
    <template v-else-if="type === 'spinner'">
      <div class="spinner-wrapper">
        <div class="spinner"></div>
        <p v-if="text" class="loading-text">{{ text }}</p>
      </div>
    </template>

    <!-- 进度条 -->
    <template v-else-if="type === 'progress'">
      <div class="progress-wrapper">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
        </div>
        <p class="progress-text">{{ progress }}%</p>
      </div>
    </template>

    <!-- 默认点状加载 -->
    <template v-else>
      <div class="dots-wrapper">
        <div class="dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <p v-if="text" class="loading-text">{{ text }}</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  type: {
    type: String,
    default: 'dots', // dots, spinner, skeleton, progress
    validator: (v) => ['dots', 'spinner', 'skeleton', 'progress'].includes(v)
  },
  text: {
    type: String,
    default: ''
  },
  fullscreen: {
    type: Boolean,
    default: false
  },
  // 骨架屏配置
  rows: {
    type: Number,
    default: 3
  },
  columns: {
    type: Number,
    default: 3
  },
  // 进度条配置
  progress: {
    type: Number,
    default: 0
  }
});

function getItemWidth(index) {
  // 随机宽度使骨架屏更自然
  const widths = ['100%', '80%', '60%', '90%', '70%'];
  return widths[(index - 1) % widths.length];
}
</script>

<style scoped>
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.loading-state.is-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  z-index: 9999;
}

.loading-text {
  color: #909399;
  font-size: 14px;
  margin-top: 12px;
}

/* 点状加载动画 */
.dots-wrapper {
  text-align: center;
}

.dots {
  display: inline-flex;
  gap: 8px;
}

.dots span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--color-primary, #409eff);
  animation: dots-pulse 1.4s infinite ease-in-out both;
}

.dots span:nth-child(1) { animation-delay: -0.32s; }
.dots span:nth-child(2) { animation-delay: -0.16s; }
.dots span:nth-child(3) { animation-delay: 0s; }

@keyframes dots-pulse {
  0%, 80%, 100% {
    transform: scale(0.5);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 旋转加载动画 */
.spinner-wrapper {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 骨架屏 */
.skeleton-wrapper {
  width: 100%;
  max-width: 600px;
}

.skeleton-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.skeleton-item {
  height: 20px;
  background: linear-gradient(90deg, #f2f2f2 25%, #e6e6e6 50%, #f2f2f2 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 进度条 */
.progress-wrapper {
  width: 100%;
  max-width: 300px;
  text-align: center;
}

.progress-bar {
  height: 8px;
  background: #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #409eff;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  color: #409eff;
  font-size: 14px;
  font-weight: 500;
  margin-top: 8px;
}
</style>
