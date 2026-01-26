<template>
  <fieldset class="fieldset">
    <legend>设备信息</legend>
    <div class="grid">
      <div class="form-group">
        <label>电脑信息</label>
        <select :value="modelValue.computer_info"
          @change="emit('update:modelValue', { ...modelValue, computer_info: $event.target.value })">
          <option value="">(可选)</option>
          <option value="自带">自带</option>
          <option value="公司配发">公司配发</option>
        </select>
      </div>
      <div class="form-group">
        <label>电脑品牌</label>
        <input type="text" :value="modelValue.computer_brand"
          @input="emit('update:modelValue', { ...modelValue, computer_brand: $event.target.value })"
          placeholder="(可选)" />
      </div>
    </div>
  </fieldset>

  <fieldset class="fieldset">
    <legend>证件上传</legend>
    <div class="grid">
      <div class="form-group">
        <label>头像</label>
        <div class="file-row">
          <a v-if="modelValue.avatar" :href="modelValue.avatar" target="_blank" rel="noreferrer">查看</a>
          <span v-else class="muted">未上传</span>
          <input type="file" accept="image/*" @change="onFileChange('avatar', $event)" />
        </div>
        <small class="hint" v-if="selectedFiles?.avatar">已选择：{{ selectedFiles.avatar.name }}</small>
      </div>
      <div class="form-group">
        <label>身份证人像面</label>
        <div class="file-row">
          <a v-if="modelValue.id_card_front" :href="modelValue.id_card_front" target="_blank" rel="noreferrer">查看</a>
          <span v-else class="muted">未上传</span>
          <input type="file" accept="image/*" @change="onFileChange('id_card_front', $event)" />
        </div>
        <small class="hint" v-if="selectedFiles?.id_card_front">已选择：{{ selectedFiles.id_card_front.name }}</small>
      </div>
      <div class="form-group">
        <label>身份证国徽面</label>
        <div class="file-row">
          <a v-if="modelValue.id_card_back" :href="modelValue.id_card_back" target="_blank" rel="noreferrer">查看</a>
          <span v-else class="muted">未上传</span>
          <input type="file" accept="image/*" @change="onFileChange('id_card_back', $event)" />
        </div>
        <small class="hint" v-if="selectedFiles?.id_card_back">已选择：{{ selectedFiles.id_card_back.name }}</small>
      </div>
    </div>
  </fieldset>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Object, required: true },
  selectedFiles: { type: Object, default: () => ({}) },
  onFileChange: { type: Function, required: true }
})
const emit = defineEmits(['update:modelValue'])
</script>
