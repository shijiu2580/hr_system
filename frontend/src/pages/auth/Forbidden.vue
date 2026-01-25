<template>
  <div class="forbidden-page">
    <div class="forbidden-content">
      <div class="icon-container">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="80" height="80">
          <circle cx="12" cy="12" r="10"/>
          <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>
        </svg>
      </div>
      <h1>403</h1>
      <h2>权限不足</h2>
      <p>抱歉，您没有权限访问此页面</p>
      <div class="actions">
        <button class="btn-primary" @click="goBack">返回上一页</button>
        <button class="btn-secondary" @click="goHome">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

function goBack() {
  if (window.history.length > 2) {
    router.go(-1);
  } else {
    router.push('/');
  }
}

function goHome() {
  router.push('/');
}
</script>

<style scoped>
.forbidden-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
}

.forbidden-content {
  text-align: center;
  padding: 2rem;
}

.icon-container {
  margin-bottom: 1.5rem;
}

.icon-container svg {
  color: #ef4444;
}

h1 {
  font-size: 4rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.5rem;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 0.5rem;
}

p {
  font-size: 1rem;
  color: #6b7280;
  margin: 0 0 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #fff;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f3f4f6;
}
</style>
