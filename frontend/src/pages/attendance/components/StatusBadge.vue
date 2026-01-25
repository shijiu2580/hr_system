<template>
  <span class="badge" :class="cls">{{ text }}</span>
</template>
<script setup>
import { computed } from 'vue';
const props = defineProps({
  status: { type: String, required: true },
  map: { type: Object, default: () => ({}) }, // 自定义映射 {status: { color:'success', text:'已批准'}}
});
const lower = computed(()=> (props.status||'').toLowerCase());
const meta = computed(()=> props.map[props.status] || props.map[lower.value] || null);
const cls = computed(()=> {
  if(meta.value) return meta.value.color;
  // 通用自动推断
  if(lower.value.includes('error') || lower.value.includes('reject') || lower.value.includes('fail')) return 'danger';
  if(lower.value.includes('warn')) return 'warning';
  if(lower.value.includes('pend') || lower.value.includes('progress')) return 'warning';
  if(lower.value.includes('approv') || lower.value.includes('success') || lower.value.includes('done')) return 'success';
  if(lower.value.includes('inactive') || lower.value.includes('disabled')) return 'muted';
  return 'info';
});
const text = computed(()=> meta.value?.text || props.status);
</script>
<style scoped>
.badge{
  background: transparent;
  border: 1px solid var(--color-border-strong);
  border-style: solid;
  color: var(--color-text);
}

.badge.success{background:transparent;color:var(--color-success);border-color:var(--color-success);}
.badge.warning{background:transparent;color:var(--color-warning);border-color:var(--color-warning);}
.badge.danger{background:transparent;color:var(--color-danger);border-color:var(--color-danger);}
.badge.muted{background:transparent;color:var(--color-text-secondary);border-color:var(--color-border-strong);}
.badge.info{background:transparent;color:var(--color-primary);border-color:var(--color-primary);}
.badge.black{background:transparent;color:#000;border-color:#000;}
</style>