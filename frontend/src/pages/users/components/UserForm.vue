<template>
  <form @submit.prevent="onSubmit" class="user-form">
    <fieldset class="fieldset">
      <legend>基本信息</legend>
      <div class="grid">
        <FormField label="用户名" :error="errors.username">
          <input v-model.trim="model.username" :disabled="isEdit" />
        </FormField>
        <FormField label="密码" :error="errors.password">
          <input type="password" v-model="model.password" :placeholder="isEdit ? '留空则不修改' : '必填'" />
        </FormField>
        <FormField label="邮箱" :error="errors.email">
          <input type="email" v-model.trim="model.email" />
        </FormField>
        <FormField label="姓" :error="errors.last_name">
          <input v-model.trim="model.last_name" />
        </FormField>
        <FormField label="名" :error="errors.first_name">
          <input v-model.trim="model.first_name" />
        </FormField>
        <FormField label="激活状态" :error="errors.is_active">
          <CustomSelect
            v-model="model.is_active"
            :options="[{ value: true, label: '是' }, { value: false, label: '否' }]"
            placeholder="选择状态"
          />
        </FormField>
      </div>
    </fieldset>
    <fieldset class="fieldset">
      <legend>权限设置</legend>
      <div class="grid">
        <FormField label="管理员" :error="errors.is_staff">
          <CustomSelect
            v-model="model.is_staff"
            :options="[{ value: false, label: '否' }, { value: true, label: '是' }]"
            placeholder="选择"
            @change="onStaffChange"
          />
          <span v-if="model.is_superuser && !model.is_staff" class="field-hint warning">超级管理员必须是管理员</span>
        </FormField>
        <FormField label="超级管理员" :error="errors.is_superuser">
          <CustomSelect
            v-model="model.is_superuser"
            :options="[{ value: false, label: '否' }, { value: true, label: '是' }]"
            placeholder="选择"
            @change="onSuperuserChange"
          />
          <span v-if="model.is_superuser" class="field-hint info">超级管理员拥有所有权限</span>
        </FormField>
      </div>
    </fieldset>
    <fieldset class="fieldset">
      <legend>角色分配</legend>
      <div class="role-list">
        <label v-for="role in roles" :key="role.id" class="role-checkbox">
          <input type="checkbox" :value="role.id" v-model="model.role_ids" />
          <span>{{ role.name }} ({{ role.code }})</span>
        </label>
        <p v-if="!roles.length" class="muted" style="font-size:12px;">暂无可分配角色</p>
      </div>
    </fieldset>
    <div class="actions">
      <button type="submit" :disabled="loading || !isValid">{{ loading ? '保存中...' : (isEdit ? '更新' : '创建') }}</button>
      <button type="button" @click="$emit('cancel')" :disabled="loading">取消</button>
      <span v-if="dirty" class="dirty-tip">有未保存更改</span>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </form>
</template>
<script setup>
import { reactive, watch, ref, computed, defineComponent, h } from 'vue';
import CustomSelect from '../../../components/CustomSelect.vue';

const FormField = defineComponent({
  name: 'FormField',
  props: { label: String, error: String },
  setup(props, { slots }) {
    return () => h('label', { class: ['form-field', props.error ? 'invalid' : ''] }, [
      h('span', { style: 'font-size:12px;color:#374151;font-weight:500;display:flex;align-items:center;gap:4px;' }, [
        props.label,
        props.error ? h('span', { style: 'color:#dc2626;font-size:11px;font-weight:400;margin-left:4px;' }, props.error) : null
      ]),
      slots.default ? slots.default() : null
    ]);
  }
});

const props = defineProps({
  value: { type: Object, default: null },
  roles: { type: Array, default: () => [] },
  loading: Boolean,
});
const emit = defineEmits(['save', 'cancel']);

const isEdit = ref(false);
const error = ref('');
const model = reactive(makeBlank());
const original = ref(null);
const errors = reactive({});
const dirty = computed(() => original.value && JSON.stringify(stripReactive(model)) !== JSON.stringify(stripReactive(original.value)));
const isValid = computed(() => validate(false));

function makeBlank() {
  return {
    username: '', password: '', email: '', first_name: '', last_name: '',
    is_active: true, is_staff: false, is_superuser: false, role_ids: []
  };
}

watch(() => props.value, (v) => {
  if (v) {
    isEdit.value = true;
    Object.assign(model, makeBlank(), pickEditable(v));
    original.value = JSON.parse(JSON.stringify(stripReactive(model)));
  } else {
    isEdit.value = false;
    Object.assign(model, makeBlank());
    original.value = JSON.parse(JSON.stringify(stripReactive(model)));
  }
  validate(false);
}, { immediate: true });

function pickEditable(u) {
  return {
    username: u.username || '',
    password: '',
    email: u.email || '',
    first_name: u.first_name || '',
    last_name: u.last_name || '',
    is_active: Boolean(u.is_active),
    is_staff: Boolean(u.is_staff),
    is_superuser: Boolean(u.is_superuser),
    role_ids: (u.roles || []).map(r => r.id)
  };
}

// 权限联动：设置超级管理员时自动设置为管理员
function onSuperuserChange() {
  if (model.is_superuser) {
    model.is_staff = true;
  }
}

// 权限联动：取消管理员时自动取消超级管理员
function onStaffChange() {
  if (!model.is_staff) {
    model.is_superuser = false;
  }
}

async function onSubmit() {
  error.value = '';
  const ok = validate(true);
  if (!ok) {
    error.value = '请修正表单错误后再提交';
    return;
  }
  try {
    const payload = JSON.parse(JSON.stringify(stripReactive(model)));
    // 编辑时如果密码为空则移除该字段
    if (isEdit.value && !payload.password) {
      delete payload.password;
    }
    emit('save', payload);
  } catch (e) {
    error.value = e.message || '提交失败';
  }
}

function stripReactive(obj) { return JSON.parse(JSON.stringify(obj)); }

function validate(mark) {
  Object.keys(errors).forEach(k => delete errors[k]);
  // 用户名必填
  if (!model.username) errors.username = '必填';
  // 创建时密码必填
  if (!isEdit.value && !model.password) errors.password = '必填';
  // 邮箱格式
  if (model.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(model.email)) errors.email = '邮箱格式不正确';
  return Object.keys(errors).length === 0;
}
</script>
<style scoped>
.user-form { display: flex; flex-direction: column; gap: 1.2rem; }
.fieldset { border: 1px solid var(--color-border, #e5e7eb); padding: .85rem 1rem; border-radius: 8px; background: var(--color-surface, #fff); }
.fieldset legend { font-size: 13px; font-weight: 600; padding: 0 .4rem; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .9rem; width: 100%; }
@media (max-width: 960px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .grid { grid-template-columns: 1fr; gap: .75rem; }
}
label { display: flex; flex-direction: column; font-size: 12px; color: #374151; gap: 4px; }
input, select {
  border: 1px solid var(--color-border, #d1d5db);
  padding: .5rem .65rem;
  border-radius: 10px;
  font-size: 13px;
  background: var(--color-surface, #fff);
  color: var(--color-text, #111827);
  width: 100%;
  box-sizing: border-box;
  transition: var(--transition, .18s cubic-bezier(.4,0,.2,1));
}
select {
  appearance: none;
  padding-right: 2.2rem;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right .75rem center;
}
input:focus, select:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: none;
}
select:hover:not(:disabled) { border-color: var(--color-border-strong, #b4bcc4); }
.actions { display: flex; align-items: center; gap: .75rem; }
button { background: #2563eb; color: #fff; border: 0; padding: .55rem 1.15rem; border-radius: 4px; font-size: 14px; cursor: pointer; transition: .15s background; }
button:hover:not(:disabled) { background: #1d4ed8; }
button:disabled { opacity: .55; cursor: not-allowed; }
button[type=button] { background: #6b7280; }
.error { color: #dc2626; font-size: 12px; }
.dirty-tip { font-size: 11px; color: #6b7280; }
.role-list { display: flex; flex-direction: column; gap: .5rem; }
.role-checkbox { display: flex; align-items: center; gap: .5rem; font-size: 13px; padding: .4rem .6rem; border: 1px solid #e5e7eb; border-radius: 4px; cursor: pointer; transition: .15s; }
.role-checkbox:hover { background: #f9fafb; border-color: #3b82f6; }
.role-checkbox input[type=checkbox] { width: auto; }
.form-field { display: flex; flex-direction: column; }
.form-field.invalid input, .form-field.invalid select { border-color: #dc2626; background: #fef2f2; }
.field-hint { font-size: 11px; margin-top: 4px; padding: 2px 6px; border-radius: 4px; }
.field-hint.warning { color: #b45309; background: #fef3c7; }
.field-hint.info { color: #0369a1; background: #e0f2fe; }
</style>
