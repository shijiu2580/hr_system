<template>
  <div class="stat-card" :class="variant" :title="title">
    <div class="stat-top">
      <div class="stat-title">{{ title }}</div>
      <slot name="extra" />
    </div>
    <div class="stat-value" :class="{ small }">
      <slot>{{ value }}</slot>
    </div>
    <div v-if="sub" class="stat-sub">{{ sub }}</div>
    <div v-if="loading" class="stat-loading">加载中...</div>
    <div v-if="error" class="stat-error">{{ error }}</div>
  </div>
</template>
<script setup>
const props = defineProps({
  title: String,
  value: [String, Number],
  sub: String,
  loading: Boolean,
  error: String,
  variant: { type: String, default: '' },
  small: Boolean,
});
</script>
<style scoped>
.stat-card {
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  padding: 0.9rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  position: relative;
  min-height: 92px;
  transition: border-color 0.2s ease;
}

.stat-card:hover {
  border-color: rgba(148, 163, 184, 0.6);
}

.stat-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  line-height: 1.1;
  color: #111827;
}

.stat-value.small {
  font-size: 22px;
}

.stat-sub {
  font-size: 11px;
  color: #6b7280;
}

.stat-loading {
  font-size: 11px;
  color: #6b7280;
  position: absolute;
  right: 0.7rem;
  bottom: 0.55rem;
}

.stat-error {
  font-size: 11px;
  color: #dc2626;
  position: absolute;
  right: 0.7rem;
  bottom: 0.55rem;
  max-width: 50%;
  text-align: right;
}

.stat-card.primary {
  background: #f8fafc;
}

.stat-card.danger {
  background: #f8fafc;
}

.stat-card.success {
  background: #f8fafc;
}

.stat-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
