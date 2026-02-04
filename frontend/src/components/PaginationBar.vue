<template>
  <div class="pagination-bar">
    <div class="pagination-info">
      共 <strong>{{ total }}</strong> 条，第 {{ currentPage }} / {{ totalPages }} 页
    </div>
    <div class="pagination-controls">
      <div class="page-size-select">
        <label>每页</label>
        <CustomSelect
          :modelValue="pageSize"
          @update:modelValue="$emit('update:pageSize', Number($event))"
          :options="pageSizeSelectOptions"
          class="size-dropdown"
          :dropUp="true"
        />
      </div>
      <div class="page-btns">
        <button type="button" class="pager-btn" @click="$emit('prev')" :disabled="currentPage <= 1">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
        </button>
        <span class="page-num">{{ currentPage }}</span>
        <button type="button" class="pager-btn" @click="$emit('next')" :disabled="currentPage >= totalPages">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CustomSelect from './CustomSelect.vue'

const props = defineProps({
  total: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  pageSizeOptions: { type: Array, default: () => [20, 50, 100] }
})

defineEmits(['prev', 'next', 'update:pageSize'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
const pageSizeSelectOptions = computed(() => props.pageSizeOptions.map(opt => ({ value: opt, label: `${opt} 条` })))
</script>

<style scoped>
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-top: 1px solid var(--color-border, #e2e8f0);
  margin-top: 16px;
  gap: 16px;
  flex-wrap: wrap;
}

.pagination-info {
  font-size: 13px;
  color: var(--color-text-secondary, #64748b);
}

.pagination-info strong {
  color: var(--color-text-primary, #1e293b);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-size-select {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text-secondary, #64748b);
}

.page-size-select :deep(.custom-select) {
  min-width: 90px;
}

.page-size-select :deep(.select-trigger) {
  padding: 6px 10px;
  font-size: 13px;
}

.page-btns {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pager-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 6px;
  background: var(--color-bg-primary, #fff);
  color: var(--color-text-primary, #1e293b);
  cursor: pointer;
  transition: all 0.15s;
}

.pager-btn:hover:not(:disabled) {
  background: var(--color-bg-secondary, #f1f5f9);
  border-color: var(--color-primary, #3b82f6);
  color: var(--color-primary, #3b82f6);
}

.pager-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-num {
  min-width: 40px;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary, #1e293b);
}

[data-theme="dark"] .pager-btn {
  background: var(--color-bg-secondary, #1e293b);
  border-color: var(--color-border, #334155);
  color: var(--color-text-primary, #e2e8f0);
}

[data-theme="dark"] .pager-btn:hover:not(:disabled) {
  background: var(--color-bg-tertiary, #334155);
}
</style>
