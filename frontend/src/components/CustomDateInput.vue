<template>
  <div class="custom-date" :class="{ focused: isFocused, 'has-value': modelValue }">
    <div class="date-display" @click="openPicker">
      <span class="date-text" :class="{ placeholder: !modelValue }">
        {{ displayText }}
      </span>
      <img src="/icons/calendar.svg" alt="日历" class="date-icon" />
    </div>
    <input
      ref="inputRef"
      type="date"
      :value="modelValue"
      @input="onInput"
      @focus="isFocused = true"
      @blur="isFocused = false"
      @click="openPicker"
      class="date-native-input"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '选择日期' }
});

const emit = defineEmits(['update:modelValue']);

const inputRef = ref(null);
const isFocused = ref(false);

const displayText = computed(() => {
  if (!props.modelValue) return props.placeholder;
  const [year, month, day] = props.modelValue.split('-');
  return `${year}年${parseInt(month)}月${parseInt(day)}日`;
});

function onInput(e) {
  emit('update:modelValue', e.target.value);
}

function openPicker() {
  if (inputRef.value && inputRef.value.showPicker) {
    inputRef.value.showPicker();
  } else {
    inputRef.value?.focus();
    inputRef.value?.click();
  }
}
</script>

<style scoped>
.custom-date {
  position: relative;
  width: 100%;
}

.date-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 20px;
  pointer-events: none;
}

.custom-date:hover .date-display {
  border-color: rgba(99, 102, 241, 0.5);
  background: rgba(248, 250, 252, 0.98);
}

.custom-date.focused .date-display {
  border-color: #6366f1;
  box-shadow: none;
}

.date-text {
  flex: 1;
  font-size: 14px;
  color: #1f2937;
}

.date-text.placeholder {
  color: #9ca3af;
}

.date-icon {
  width: 16px;
  height: 16px;
  opacity: 0.5;
  flex-shrink: 0;
}

.date-native-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 1;
  font-size: 16px; /* 防止iOS缩放 */
}

/* 暗黑模式 */
:root[data-theme='dark'] .date-display {
  background: var(--color-surface, #1e293b);
  border-color: var(--color-border, #475569);
}

:root[data-theme='dark'] .custom-date:hover .date-display {
  background: var(--color-surface-alt, #334155);
}

:root[data-theme='dark'] .date-text {
  color: var(--color-text, #f8fafc);
}

:root[data-theme='dark'] .date-text.placeholder {
  color: var(--color-text-secondary, #94a3b8);
}
</style>
