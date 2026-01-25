<template>
  <form @submit.prevent="onSubmit" class="emp-form">
    <!-- 基本信息分组 -->
    <fieldset class="fieldset">
      <legend>基本信息</legend>
      <div class="grid">
        <FormField label="用户" :error="errors.user_id">
          <CustomSelect
            v-model="model.user_id"
            :options="[{ value: '', label: '选择用户' }, ...users.map(u => ({ value: u.id, label: u.username }))]"
            placeholder="选择用户"
          />
        </FormField>
        <FormField label="员工编号" :error="errors.employee_id">
          <input v-model.trim="model.employee_id" :disabled="isEdit" />
        </FormField>
        <FormField label="姓名" :error="errors.name">
          <input v-model.trim="model.name" />
        </FormField>
        <FormField label="性别" :error="errors.gender">
          <CustomSelect
            v-model="model.gender"
            :options="[{ value: 'M', label: '男' }, { value: 'F', label: '女' }]"
            placeholder="选择性别"
          />
        </FormField>
        <FormField label="出生日期" :error="errors.birth_date">
          <input type="date" v-model="model.birth_date" />
        </FormField>
        <FormField label="入职日期" :error="errors.hire_date">
          <input type="date" v-model="model.hire_date" />
        </FormField>
      </div>
    </fieldset>
    <!-- 联系方式分组 -->
    <fieldset class="fieldset">
      <legend>联系方式</legend>
      <div class="grid">
        <FormField label="手机" :error="errors.phone"><input v-model="model.phone" /></FormField>
        <FormField label="邮箱" :error="errors.email"><input type="email" v-model="model.email" /></FormField>
        <FormField label="地址" :error="errors.address"><input v-model="model.address" /></FormField>
        <FormField label="身份证" :error="errors.id_card"><input v-model="model.id_card" /></FormField>
      </div>
    </fieldset>
    <!-- 个人状态分组 -->
    <fieldset class="fieldset">
      <legend>个人状态</legend>
      <div class="grid">
        <FormField label="婚姻状况" :error="errors.marital_status">
          <CustomSelect
            v-model="model.marital_status"
            :options="[
              { value: 'single', label: '未婚' },
              { value: 'married', label: '已婚' },
              { value: 'divorced', label: '离婚' },
              { value: 'widowed', label: '丧偶' }
            ]"
            placeholder="选择婚姻状况"
          />
        </FormField>
        <FormField label="紧急联系人" :error="errors.emergency_contact"><input v-model="model.emergency_contact" /></FormField>
        <FormField label="紧急电话" :error="errors.emergency_phone"><input v-model="model.emergency_phone" /></FormField>
      </div>
    </fieldset>
    <!-- 任职信息分组 -->
    <fieldset class="fieldset">
      <legend>任职信息</legend>
      <div class="grid">
        <FormField label="部门" :error="errors.department_id">
          <CustomSelect
            v-model="model.department_id"
            :options="[{ value: '', label: '(可选)' }, ...departments.map(d => ({ value: d.id, label: d.name }))]"
            placeholder="选择部门"
          />
        </FormField>
        <FormField label="职位" :error="errors.position_id">
          <CustomSelect
            v-model="model.position_id"
            :options="[{ value: '', label: '(可选)' }, ...positions.map(p => ({ value: p.id, label: p.name }))]"
            placeholder="选择职位"
          />
        </FormField>
        <FormField label="基本工资" :error="errors.salary">
          <input type="number" step="0.01" v-model.number="model.salary" />
        </FormField>
        <FormField label="在职状态" :error="errors.is_active">
          <CustomSelect
            v-model="model.is_active"
            :options="[{ value: true, label: '是' }, { value: false, label: '否' }]"
            placeholder="选择状态"
          />
        </FormField>
      </div>
    </fieldset>
    <!-- 考勤地点分组 -->
    <fieldset class="fieldset" v-if="checkinLocations.length > 0">
      <legend>考勤地点 <span class="legend-tip">(可选，不选则使用全局设置)</span></legend>
      <div class="location-list">
        <label v-for="loc in checkinLocations" :key="loc.id" class="location-item">
          <input 
            type="checkbox" 
            :value="loc.id" 
            v-model="model.checkin_location_ids"
          />
          <div class="location-info">
            <span class="location-name">{{ loc.name }}</span>
            <span class="location-addr">{{ loc.address }} · {{ loc.radius }}米范围</span>
          </div>
          <span class="location-status" :class="loc.is_active ? 'active' : 'inactive'">
            {{ loc.is_active ? '启用' : '停用' }}
          </span>
        </label>
        <p v-if="checkinLocations.length === 0" class="no-locations">暂无考勤地点</p>
      </div>
    </fieldset>
    <!-- 动作与反馈 -->
    <div class="actions">
      <button type="submit" :disabled="loading || !isValid">{{ loading ? '保存中...' : (isEdit? '更新' : '创建') }}</button>
      <button type="button" @click="$emit('cancel')" :disabled="loading">取消</button>
      <span v-if="dirty" class="dirty-tip">有未保存更改</span>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </form>
</template>
<script setup>
import { reactive, watch, ref, computed, defineComponent, h } from 'vue';
import CustomSelect from '../../../components/CustomSelect.vue';

// 内联字段组件（无需 JSX）
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
  users: { type: Array, default: () => [] },
  departments: { type: Array, default: () => [] },
  positions: { type: Array, default: () => [] },
  checkinLocations: { type: Array, default: () => [] },
  loading: Boolean,
});
const emit = defineEmits(['save','cancel']);
const isEdit = ref(false);
const error = ref('');
const model = reactive(makeBlank());
const original = ref(null); // 用于dirty判断
const errors = reactive({});
const dirty = computed(() => original.value && JSON.stringify(stripReactive(model)) !== JSON.stringify(stripReactive(original.value)));
const isValid = computed(() => validate(false));

function makeBlank(){
  return {
    user_id: '', employee_id: '', name: '', gender: 'M', birth_date: '', hire_date: '',
    phone: '', email: '', address: '', id_card: '', marital_status: 'single', emergency_contact: '', emergency_phone: '',
    department_id: '', position_id: '', salary: 0, is_active: true, checkin_location_ids: [],
  };
}

watch(() => props.value, (v) => {
  if(v){
    isEdit.value = true;
    Object.assign(model, makeBlank(), pickEditable(v));
    original.value = JSON.parse(JSON.stringify(stripReactive(model)));
  } else {
    isEdit.value = false;
    Object.assign(model, makeBlank());
    original.value = JSON.parse(JSON.stringify(stripReactive(model)));
  }
  // 不在watch中调用validate，避免递归
}, { immediate: true });

function pickEditable(e){
  return {
    user_id: e.user?.id, employee_id: e.employee_id, name: e.name, gender: e.gender,
    birth_date: e.birth_date, hire_date: e.hire_date, phone: e.phone, email: e.email, address: e.address,
    id_card: e.id_card, marital_status: e.marital_status, emergency_contact: e.emergency_contact,
    emergency_phone: e.emergency_phone, department_id: e.department?.id || '', position_id: e.position?.id || '',
    salary: e.salary, is_active: e.is_active, checkin_location_ids: e.checkin_location_ids || [],
  };
}

async function onSubmit(){
  error.value = '';
  const ok = validate(true);
  if(!ok){
    error.value = '请修正表单错误后再提交';
    return;
  }
  try {
    const payload = JSON.parse(JSON.stringify(stripReactive(model)));
    // 将空字符串转换为 null（department_id 和 position_id）
    if (payload.department_id === '') payload.department_id = null;
    if (payload.position_id === '') payload.position_id = null;
    
    // 清理所有空字符串字段（除了必填的user_id和employee_id）
    const optionalFields = ['name', 'gender', 'birth_date', 'hire_date', 'phone', 'email', 
                            'address', 'id_card', 'emergency_contact', 'emergency_phone', 'marital_status'];
    optionalFields.forEach(field => {
      if (payload[field] === '') {
        delete payload[field];
      }
    });
    
    // salary为0时也可以删除，让后端使用默认值
    if (payload.salary === 0 || payload.salary === '') {
      delete payload.salary;
    }
    
    // 确保 checkin_location_ids 是数组
    if (!Array.isArray(payload.checkin_location_ids)) {
      payload.checkin_location_ids = [];
    }
    
    emit('save', payload);
  } catch(e){
    error.value = e.message || '提交失败';
  }
}

function stripReactive(obj){ return JSON.parse(JSON.stringify(obj)); }

function validate(mark){
  // 清空错误
  Object.keys(errors).forEach(k => delete errors[k]);
  // 必填校验 - 只有用户和员工编号必填
  if(!model.user_id) errors.user_id = '必填';
  if(!model.employee_id) errors.employee_id = '必填';
  
  // 格式校验（如果填写了才验证）
  if(model.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(model.email)) errors.email = '邮箱格式不正确';
  if(model.phone && !/^1[3-9]\d{9}$/.test(model.phone)) errors.phone = '请输入有效的11位手机号';
  if(model.emergency_phone && !/^1[3-9]\d{9}$/.test(model.emergency_phone)) errors.emergency_phone = '请输入有效的11位手机号';
  if(model.id_card && !/^\d{17}[\dXx]$/.test(model.id_card)) errors.id_card = '请输入有效的18位身份证号';
  
  // 日期逻辑：如果都填了，出生日期不能晚于入职
  if(model.birth_date && model.hire_date && model.birth_date > model.hire_date) errors.birth_date = '出生日期不能晚于入职日期';
  
  // 工资非负
  if(model.salary < 0) errors.salary = '工资不能为负数';
  
  // 返回是否有效
  return Object.keys(errors).length === 0;
}
</script>
<style scoped>
.emp-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.fieldset {
  border: 1px solid var(--color-border, #e5e7eb);
  padding: 0.85rem 1rem;
  border-radius: 8px;
  background: var(--color-surface, #fff);
}

.fieldset legend {
  font-size: 13px;
  font-weight: 600;
  padding: 0 0.4rem;
}

.legend-tip {
  font-size: 11px;
  font-weight: 400;
  color: #6b7280;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.9rem;
  width: 100%;
}

@media (max-width: 960px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
}

label {
  display: flex;
  flex-direction: column;
  font-size: 12px;
  color: #374151;
  gap: 4px;
}

input,
select {
  border: 1px solid #d1d5db;
  height: 36px;
  padding: 0 0.65rem;
  border-radius: 10px;
  font-size: 13px;
  background: #fff;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

select {
  appearance: none;
  cursor: pointer;
  padding-right: 2.2rem;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2.5'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
}

select:hover:not(:disabled) {
  border-color: rgba(99, 102, 241, 0.5);
  background-color: rgba(248, 250, 252, 0.98);
}

input:focus,
select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

button {
  background: #2563eb;
  color: #fff;
  border: 0;
  padding: 0.55rem 1.15rem;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: 0.15s background;
}

button:hover:not(:disabled) {
  background: #1d4ed8;
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

button[type="button"] {
  background: #6b7280;
}

.error {
  color: #dc2626;
  font-size: 12px;
}

.field-error {
  color: #dc2626;
  font-size: 11px;
  margin-top: 3px;
}

.dirty-tip {
  font-size: 11px;
  color: #6b7280;
}

.checkbox-inline {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 12px;
  color: #374151;
}

/* CustomSelect 统一样式 */
:deep(.custom-select .select-trigger) {
  height: 36px;
  padding: 0 0.65rem;
  display: flex;
  align-items: center;
  padding-right: 2rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  background: #fff;
  font-size: 13px;
  transition: all 0.2s ease;
}

:deep(.custom-select .select-trigger:hover) {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}

:deep(.custom-select.open .select-trigger),
:deep(.custom-select .select-trigger:focus) {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}

:deep(.custom-select .select-value) {
  font-size: 13px;
  color: #1e293b;
}

:deep(.custom-select .select-arrow) {
  color: #64748b;
}

:deep(.custom-select .select-dropdown) {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 0.35rem 0;
}

:deep(.custom-select .select-option) {
  padding: 0.5rem 0.75rem;
  font-size: 13px;
  color: #374151;
  transition: background 0.15s;
}

:deep(.custom-select .select-option:hover),
:deep(.custom-select .select-option.highlighted) {
  background: #f1f5f9;
  color: #1e293b;
}

:deep(.custom-select .select-option.selected) {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

/* 考勤地点样式 */
.location-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.location-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.location-item:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.location-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #2563eb;
  outline: none;
}

.location-item input[type="checkbox"]:focus {
  outline: none;
  box-shadow: none;
}

.location-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.location-name {
  font-size: 13px;
  font-weight: 500;
  color: #1f2937;
}

.location-addr {
  font-size: 12px;
  color: #6b7280;
}

.location-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
}

.location-status.active {
  background: #dcfce7;
  color: #166534;
}

.location-status.inactive {
  background: #f1f5f9;
  color: #64748b;
}

.no-locations {
  font-size: 13px;
  color: #6b7280;
  text-align: center;
  padding: 16px;
}
</style>

<style scoped>
/* 内联组件样式（FormField） */
.form-field {
  display: flex;
  flex-direction: column;
}

.form-field.invalid input,
.form-field.invalid select {
  border-color: #dc2626;
  background: #fef2f2;
}
</style>
