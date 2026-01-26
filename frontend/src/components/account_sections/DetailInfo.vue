<template>
  <fieldset class="fieldset">
    <legend>户籍信息</legend>
    <div class="grid">
      <div class="form-group">
        <label>国籍(地区)</label>
        <input type="text" :value="modelValue.nationality"
          @input="emit('update:modelValue', { ...modelValue, nationality: $event.target.value })"
          placeholder="中国" />
      </div>
      <div class="form-group">
        <label>籍贯</label>
        <input type="text" :value="modelValue.native_place"
          @input="emit('update:modelValue', { ...modelValue, native_place: $event.target.value })"
          placeholder="如：四川省/宜宾市" />
      </div>
      <div class="form-group">
        <label>户籍所在地</label>
        <input type="text" :value="modelValue.hukou_location"
          @input="emit('update:modelValue', { ...modelValue, hukou_location: $event.target.value })"
          placeholder="(可选)" />
      </div>
      <div class="form-group">
        <label>户籍性质</label>
        <select :value="modelValue.hukou_type"
          @change="emit('update:modelValue', { ...modelValue, hukou_type: $event.target.value })">
          <option value="">(可选)</option>
          <option value="农村">农村</option>
          <option value="城镇">城镇</option>
        </select>
      </div>
      <div class="form-group">
        <label>户籍地址</label>
        <input type="text" :value="modelValue.hukou_address"
          @input="emit('update:modelValue', { ...modelValue, hukou_address: $event.target.value })"
          placeholder="(可选)" />
      </div>
      <div class="form-group">
        <label>民族</label>
        <input type="text" :value="modelValue.ethnicity"
          @input="emit('update:modelValue', { ...modelValue, ethnicity: $event.target.value })"
          placeholder="汉族" />
      </div>
      <div class="form-group">
        <label>血型</label>
        <select :value="modelValue.blood_type"
          @change="emit('update:modelValue', { ...modelValue, blood_type: $event.target.value })">
          <option value="">(可选)</option>
          <option value="A型">A型</option>
          <option value="B型">B型</option>
          <option value="O型">O型</option>
          <option value="AB型">AB型</option>
          <option value="未知">未知</option>
        </select>
      </div>
      <div class="form-group">
        <label>政治面貌</label>
        <select :value="modelValue.political_status"
          @change="emit('update:modelValue', { ...modelValue, political_status: $event.target.value })">
          <option value="">(可选)</option>
          <option value="群众">群众</option>
          <option value="共青团员">共青团员</option>
          <option value="中共党员">中共党员</option>
          <option value="民主党派">民主党派</option>
          <option value="其他">其他</option>
        </select>
      </div>
      <div class="form-group">
        <label>入党/团日期</label>
        <input type="date" :value="modelValue.party_date"
          @input="emit('update:modelValue', { ...modelValue, party_date: $event.target.value })" />
      </div>
    </div>
  </fieldset>

  <fieldset class="fieldset">
    <legend>教育信息</legend>
    <div class="grid">
      <div class="form-group">
        <label>学校分类</label>
        <select :value="modelValue.school_type"
          @change="emit('update:modelValue', { ...modelValue, school_type: $event.target.value })">
          <option value="">(可选)</option>
          <option value="普通本科">普通本科</option>
          <option value="211">211</option>
          <option value="985">985</option>
          <option value="双一流">双一流</option>
          <option value="大专">大专</option>
          <option value="高中/中专">高中/中专</option>
          <option value="其他">其他</option>
        </select>
      </div>
      <div class="form-group">
        <label>毕业学校</label>
        <input type="text" :value="modelValue.school_name"
          @input="emit('update:modelValue', { ...modelValue, school_name: $event.target.value })"
          placeholder="(可选)" />
      </div>
      <div class="form-group">
        <label>专业</label>
        <input type="text" :value="modelValue.major"
          @input="emit('update:modelValue', { ...modelValue, major: $event.target.value })"
          placeholder="(可选)" />
      </div>
      <div class="form-group">
        <label>毕业时间</label>
        <input type="date" :value="modelValue.graduation_date"
          @input="emit('update:modelValue', { ...modelValue, graduation_date: $event.target.value })" />
      </div>
      <div class="form-group">
        <label>学历</label>
        <select :value="modelValue.education"
          @change="emit('update:modelValue', { ...modelValue, education: $event.target.value })">
          <option value="">(可选)</option>
          <option value="高中/中专">高中/中专</option>
          <option value="大专">大专</option>
          <option value="本科">本科</option>
          <option value="硕士">硕士</option>
          <option value="博士">博士</option>
        </select>
      </div>
    </div>
  </fieldset>

  <fieldset class="fieldset">
    <legend>银行信息</legend>
    <div class="grid">
      <div class="form-group">
        <label>工资卡账号</label>
        <input type="text" :value="modelValue.bank_card_no"
          @input="emit('update:modelValue', { ...modelValue, bank_card_no: $event.target.value })"
          placeholder="(可选)" />
      </div>
      <div class="form-group">
        <label>报销卡账号</label>
        <input type="text" :value="modelValue.expense_card_no"
          @input="emit('update:modelValue', { ...modelValue, expense_card_no: $event.target.value })"
          placeholder="(可选)" />
      </div>
    </div>
  </fieldset>

  <fieldset class="fieldset">
    <legend>入职信息（只读）</legend>
    <div class="grid">
      <div class="form-group">
        <label>部门</label>
        <input type="text" :value="modelValue.department_name || '(未设置)'" disabled />
      </div>
      <div class="form-group">
        <label>职位</label>
        <input type="text" :value="modelValue.position_name || '(未设置)'" disabled />
      </div>
      <div class="form-group">
        <label>入职日期</label>
        <input type="text" :value="modelValue.hire_date || '(未设置)'" disabled />
      </div>
      <div class="form-group">
        <label>入职状态</label>
        <input type="text" :value="modelValue.onboard_status || '(未设置)'" disabled />
      </div>
    </div>
  </fieldset>
</template>

<script setup>
defineProps({
  modelValue: { type: Object, required: true }
})
const emit = defineEmits(['update:modelValue'])
</script>
