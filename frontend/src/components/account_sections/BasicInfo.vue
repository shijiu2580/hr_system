<template>
  <fieldset class="fieldset">
    <legend>基本信息</legend>
    <div class="grid">
      <div class="form-group">
        <label>员工编号</label>
        <input type="text" :value="modelValue.employee_id" disabled />
        <span class="hint">系统自动生成</span>
      </div>
      <div class="form-group" :class="{'invalid': errors?.name}">
        <label>员工姓名<span class="required">*</span></label>
        <input type="text" 
          :value="modelValue.name"
          @input="emit('update:modelValue', { ...modelValue, name: $event.target.value })"
          maxlength="50" 
          placeholder="请输入姓名" />
        <span class="hint error-hint" v-if="errors?.name">{{ errors.name }}</span>
      </div>
      <div class="form-group">
        <label>登录用户名</label>
        <input type="text" :value="auth?.user?.username" disabled />
        <span class="hint">用于系统登录</span>
      </div>
      <div class="form-group">
        <label>英文名</label>
        <input type="text" 
          :value="modelValue.english_name"
          @input="emit('update:modelValue', { ...modelValue, english_name: $event.target.value })"
          placeholder="(可选)" />
      </div>
      <div class="form-group">
        <label>性别</label>
        <select 
          :value="modelValue.gender"
          @change="emit('update:modelValue', { ...modelValue, gender: $event.target.value })">
          <option value="">(可选)</option>
          <option value="M">男</option>
          <option value="F">女</option>
        </select>
      </div>
      <div class="form-group">
        <label>出生日期</label>
        <input type="date" 
          :value="modelValue.birth_date"
          @input="emit('update:modelValue', { ...modelValue, birth_date: $event.target.value })" />
      </div>
      <div class="form-group">
        <label>婚姻状况</label>
        <select 
          :value="modelValue.marital_status"
          @change="emit('update:modelValue', { ...modelValue, marital_status: $event.target.value })">
          <option value="single">未婚</option>
          <option value="married">已婚</option>
          <option value="divorced">离异</option>
          <option value="widowed">丧偶</option>
        </select>
      </div>
    </div>
  </fieldset>
</template>

<script setup>
defineProps({
  modelValue: { type: Object, required: true },
  auth: { type: Object, default: null },
  errors: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['update:modelValue'])
</script>
