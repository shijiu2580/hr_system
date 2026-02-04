<template>
  <div class="custom-select" :class="{ open: isOpen, disabled }" ref="selectRef">
    <div class="select-trigger" @click="toggle" :tabindex="disabled ? -1 : 0" @keydown="onKeydown">
      <span class="select-value">{{ displayValue }}</span>
      <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M6 9l6 6 6-6" />
      </svg>
    </div>
    <Teleport to="body">
      <Transition name="dropdown">
        <div v-if="isOpen" class="select-dropdown" :style="dropdownStyle" ref="dropdownRef" @click.stop>
          <div v-if="searchable" class="search-box">
            <input
              ref="searchInput"
              type="text"
              v-model="searchQuery"
              class="search-input"
              placeholder="搜索..."
              @click.stop
              @keydown="onSearchKeydown"
            />
          </div>
          <div class="options-list">
            <div v-if="filteredOptions.length === 0" class="no-results">
              无匹配结果
            </div>
            <div
              v-for="(opt, idx) in filteredOptions"
              :key="opt.value"
              class="select-option"
              :class="{ selected: opt.value === modelValue, highlighted: idx === highlightedIndex }"
              @mousedown.prevent.stop="select(opt.value)"
              @mouseenter="highlightedIndex = idx"
            >
              {{ opt.label }}
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  modelValue: { type: [String, Number, Boolean], default: '' },
  options: { type: Array, default: () => [] }, // [{ value, label }]
  placeholder: { type: String, default: '请选择' },
  disabled: { type: Boolean, default: false },
  searchable: { type: Boolean, default: false },
  dropUp: { type: Boolean, default: false }
});

const emit = defineEmits(['update:modelValue', 'change']);

const isOpen = ref(false);
const highlightedIndex = ref(-1);
const selectRef = ref(null);
const dropdownRef = ref(null);
const searchInput = ref(null);
const searchQuery = ref('');
const dropdownStyle = ref({});

const displayValue = computed(() => {
  const found = props.options.find(o => o.value === props.modelValue);
  return found ? found.label : props.placeholder;
});

const filteredOptions = computed(() => {
  if (!searchQuery.value || !props.searchable) {
    return props.options;
  }
  const query = searchQuery.value.toLowerCase();
  return props.options.filter(opt =>
    String(opt.label).toLowerCase().includes(query)
  );
});

function updateDropdownPosition() {
  if (!selectRef.value) return;
  const rect = selectRef.value.getBoundingClientRect();
  const scrollX = window.scrollX || window.pageXOffset;
  const scrollY = window.scrollY || window.pageYOffset;

  // 处理 body zoom (Fix: zoom 导致坐标偏移)
  let zoom = 1;
  const bodyZoom = getComputedStyle(document.body).zoom;
  if (bodyZoom) {
    zoom = parseFloat(bodyZoom) || 1;
  }

  if (props.dropUp) {
    // 向上展开
    dropdownStyle.value = {
      position: 'absolute',
      top: `${(rect.top + scrollY) / zoom}px`,
      left: `${(rect.left + scrollX) / zoom}px`,
      width: `${rect.width / zoom}px`,
      zIndex: 99999,
      transform: 'translateY(-100%)'
    };
  } else {
    // 默认向下展开
    dropdownStyle.value = {
      position: 'absolute',
      top: `${(rect.bottom + scrollY) / zoom}px`,
      left: `${(rect.left + scrollX) / zoom}px`,
      width: `${rect.width / zoom}px`,
      zIndex: 99999
    };
  }
}

watch(isOpen, (val) => {
  if (val) {
    updateDropdownPosition();
    if (props.searchable) {
      searchQuery.value = '';
      nextTick(() => {
        searchInput.value?.focus();
      });
    }
  }
});

watch(searchQuery, () => {
  highlightedIndex.value = 0;
});

function toggle() {
  if (props.disabled) return;
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    highlightedIndex.value = filteredOptions.value.findIndex(o => o.value === props.modelValue);
    if (highlightedIndex.value < 0) highlightedIndex.value = 0;
  }
}

function select(val) {
  emit('update:modelValue', val);
  emit('change', val);
  nextTick(() => {
    isOpen.value = false;
    searchQuery.value = '';
  });
}

function onSearchKeydown(e) {
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    highlightedIndex.value = Math.min(highlightedIndex.value + 1, filteredOptions.value.length - 1);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (highlightedIndex.value >= 0 && filteredOptions.value[highlightedIndex.value]) {
      select(filteredOptions.value[highlightedIndex.value].value);
    }
  } else if (e.key === 'Escape') {
    isOpen.value = false;
  }
}

function onKeydown(e) {
  if (props.disabled) return;

  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    if (isOpen.value && highlightedIndex.value >= 0) {
      select(filteredOptions.value[highlightedIndex.value].value);
    } else {
      toggle();
    }
  } else if (e.key === 'Escape') {
    isOpen.value = false;
  } else if (e.key === 'ArrowDown') {
    e.preventDefault();
    if (!isOpen.value) {
      isOpen.value = true;
      highlightedIndex.value = 0;
    } else {
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, filteredOptions.value.length - 1);
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0);
  }
}

function onClickOutside(e) {
  if (!isOpen.value) return;
  if (selectRef.value && !selectRef.value.contains(e.target)) {
    if (!dropdownRef.value || !dropdownRef.value.contains(e.target)) {
      isOpen.value = false;
    }
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside);
});
</script>

<style scoped>
.custom-select {
  position: relative;
  width: 100%;
  font-size: 14px;
}

.select-trigger {
  position: relative;
  display: flex;
  align-items: center;
  padding: 0 0.75rem;
  padding-right: 2.2rem;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 36px;
  min-height: 36px;
  box-sizing: border-box;
}

.select-trigger:hover {
  border-color: #9ca3af;
  background: #f9fafb;
}

.select-trigger:focus {
  outline: none;
  border-color: #2563eb;
  background: #fff;
}

.custom-select.open .select-trigger {
  border-color: #2563eb;
  background: #fff;
}

.custom-select.disabled .select-trigger {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f8fafc;
}

.select-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #374151;
}

.select-arrow {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  color: #6b7280;
  transition: transform 0.2s ease;
  pointer-events: none;
}

.custom-select.open .select-arrow {
  transform: translateY(-50%) rotate(180deg);
}

/* 暗黑模式 */
:root[data-theme='dark'] .select-trigger {
  background: var(--color-surface, #1e293b);
  border-color: var(--color-border, #475569);
}

:root[data-theme='dark'] .select-trigger:hover {
  background: var(--color-surface-alt, #334155);
}

:root[data-theme='dark'] .select-value {
  color: var(--color-text, #f8fafc);
}
</style>

<!-- 下拉框样式(teleport到body，需要全局样式) -->
<style>
.select-dropdown {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 0.35rem 0;
  z-index: 99999 !important;
  pointer-events: auto;
}

.select-dropdown .search-box {
  padding: 0 6px 6px;
}

.select-dropdown .search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
}

.select-dropdown .search-input:focus {
  border-color: #6366f1;
}

.select-dropdown .options-list {
  max-height: 280px;
  overflow-y: auto;
  overflow-x: hidden;
}

.select-dropdown .no-results {
  padding: 0.75rem;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}

.select-dropdown .select-option {
  padding: 0.5rem 0.75rem;
  border-radius: 0;
  cursor: pointer;
  transition: background 0.15s;
  color: #374151;
  font-size: 13px;
  user-select: none;
}

.select-dropdown .select-option:hover,
.select-dropdown .select-option.highlighted {
  background: #f1f5f9;
}

.select-dropdown .select-option.selected {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

/* 滚动条美化 */
.select-dropdown .options-list::-webkit-scrollbar {
  width: 6px;
}

.select-dropdown .options-list::-webkit-scrollbar-track {
  background: transparent;
}

.select-dropdown .options-list::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.4);
  border-radius: 3px;
}

.select-dropdown .options-list::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.6);
}

/* 动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 暗黑模式 */
:root[data-theme='dark'] .select-dropdown {
  background: var(--color-surface, #1e293b);
  border-color: var(--color-border, #475569);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

:root[data-theme='dark'] .select-dropdown .select-option {
  color: var(--color-text-secondary, #94a3b8);
}

:root[data-theme='dark'] .select-dropdown .select-option:hover,
:root[data-theme='dark'] .select-dropdown .select-option.highlighted {
  background: rgba(99, 102, 241, 0.15);
  color: #e2e8f0;
}

:root[data-theme='dark'] .select-dropdown .select-option.selected {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
}
</style>
