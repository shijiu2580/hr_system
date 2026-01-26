<template>
  <fieldset class="fieldset">
    <legend>联系方式</legend>
    <div class="grid">
      <div class="form-group" :class="{'invalid': errors?.phone}">
        <label>手机</label>
        <input type="text" 
          :value="modelValue.phone"
          @input="emit('update:modelValue', { ...modelValue, phone: $event.target.value })"
          placeholder="请输入手机号" />
        <span class="hint error-hint" v-if="errors?.phone">{{ errors.phone }}</span>
      </div>
      <div class="form-group" :class="{'invalid': errors?.email}">
        <label>邮箱</label>
        <input type="email" 
          :value="modelValue.email"
          @input="emit('update:modelValue', { ...modelValue, email: $event.target.value })"
          placeholder="your@email.com" />
        <span class="hint error-hint" v-if="errors?.email">{{ errors.email }}</span>
      </div>
      <div class="form-group" :class="{'invalid': errors?.address}">
        <label>地址</label>
        <input type="text" 
          :value="modelValue.address"
          @input="emit('update:modelValue', { ...modelValue, address: $event.target.value })"
          placeholder="请输入联系地址" />
        <span class="hint error-hint" v-if="errors?.address">{{ errors.address }}</span>
      </div>
      <div class="form-group" :class="{'invalid': errors?.id_card}">
        <label>身份证号</label>
        <input type="text" 
          :value="modelValue.id_card"
          @input="emit('update:modelValue', { ...modelValue, id_card: $event.target.value })"
          placeholder="(可选)" />
        <span class="hint error-hint" v-if="errors?.id_card">{{ errors.id_card }}</span>
      </div>
      <div class="form-group">
        <label>护照号码</label>
        <input type="text" 
          :value="modelValue.passport_no"
          @input="emit('update:modelValue', { ...modelValue, passport_no: $event.target.value })"
          placeholder="(可选)" />
      </div>
    </div>
  </fieldset>

  <fieldset class="fieldset">
    <legend>紧急联系人</legend>
    <div class="grid">
      <div class="form-group">
        <label>紧急联系人</label>
        <input type="text" 
          :value="modelValue.emergency_contact"
          @input="emit('update:modelValue', { ...modelValue, emergency_contact: $event.target.value })"
          placeholder="(可选)" />
      </div>
      <div class="form-group">
        <label>与本人关系</label>
        <input type="text" 
          :value="modelValue.emergency_relation"
          @input="emit('update:modelValue', { ...modelValue, emergency_relation: $event.target.value })"
          placeholder="如：父亲" />
      </div>
      <div class="form-group" :class="{'invalid': errors?.emergency_phone}">
        <label>紧急电话</label>
        <input type="text" 
          :value="modelValue.emergency_phone"
          @input="emit('update:modelValue', { ...modelValue, emergency_phone: $event.target.value })"
          placeholder="(可选)" />
        <span class="hint error-hint" v-if="errors?.emergency_phone">{{ errors.emergency_phone }}</span>
      </div>
    </div>
  </fieldset>
</template>

<script setup>
defineProps({
  modelValue: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['update:modelValue'])
</script>
