<template>
  <div class="page-container">
    <!-- 表单卡片 -->
    <div class="form-card">
      <div class="form-header">
        <div class="header-content">
          <img src="/icons/leaves.svg" alt="" class="header-icon" />
          <h2 class="form-title">出差申请</h2>
        </div>
        <button class="btn-close" @click="router.back()">×</button>
      </div>

      <div class="form-body">
        <div class="form-group">
          <label class="form-label">出差地点 <span class="required">*</span></label>
          <input
            type="text"
            v-model="form.destination"
            class="form-input"
            placeholder="请输入出差地点"
          />
        </div>

        <div class="form-group">
          <label class="form-label">出差类型 <span class="required">*</span></label>
          <CustomSelect
            v-model="form.trip_type"
            :options="[
              { value: 'domestic', label: '国内出差' },
              { value: 'overseas', label: '海外出差' }
            ]"
            placeholder="请选择出差类型"
            class="form-select"
          />
        </div>

        <div class="form-row">
          <div class="form-group half">
            <label class="form-label">开始日期 <span class="required">*</span></label>
            <CustomDateInput v-model="form.start_date" placeholder="选择日期" class="form-date-input" />
          </div>

          <div class="form-group half">
            <label class="form-label">结束日期 <span class="required">*</span></label>
            <CustomDateInput v-model="form.end_date" placeholder="选择日期" class="form-date-input" />
          </div>
        </div>

        <div class="form-group" v-if="form.start_date && form.end_date">
          <label class="form-label">出差时长</label>
          <div class="duration-display">{{ calculateDays }}天</div>
        </div>

        <div class="form-group">
          <label class="form-label">出差事由 <span class="required">*</span></label>
          <textarea
            v-model="form.reason"
            class="form-textarea"
            rows="4"
            placeholder="请填写出差事由"
          ></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">备注</label>
          <textarea
            v-model="form.remarks"
            class="form-textarea"
            rows="3"
            placeholder="如有其他说明请填写（选填）"
          ></textarea>
        </div>
      </div>

      <div class="form-footer">
        <button class="btn-cancel" @click="router.back()">取消</button>
        <button class="btn-submit" @click="submit" :disabled="submitting">
          {{ submitting ? '提交中...' : '提交申请' }}
        </button>
      </div>
    </div>

    <!-- 提示消息 -->
    <div v-if="message" class="message" :class="'message-' + message.type">
      {{ message.text }}
      <button class="close-btn" @click="message = null">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'
import CustomDateInput from '../../components/CustomDateInput.vue'

const router = useRouter()

const form = ref({
  destination: '',
  trip_type: 'domestic',
  start_date: '',
  end_date: '',
  reason: '',
  remarks: ''
})

const submitting = ref(false)
const message = ref(null)

// 计算出差天数
const calculateDays = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 0
  const start = new Date(form.value.start_date)
  const end = new Date(form.value.end_date)
  const diffTime = end.getTime() - start.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
  return diffDays > 0 ? diffDays : 0
})

function showMessage(type, text) {
  message.value = { type, text }
  setTimeout(() => { message.value = null }, 3000)
}

async function submit() {
  // 验证
  if (!form.value.destination) {
    showMessage('error', '请输入出差地点')
    return
  }
  if (!form.value.start_date) {
    showMessage('error', '请选择开始日期')
    return
  }
  if (!form.value.end_date) {
    showMessage('error', '请选择结束日期')
    return
  }
  if (form.value.start_date > form.value.end_date) {
    showMessage('error', '结束日期不能早于开始日期')
    return
  }
  if (!form.value.reason) {
    showMessage('error', '请填写出差事由')
    return
  }

  submitting.value = true
  try {
    const data = {
      destination: form.value.destination,
      trip_type: form.value.trip_type,
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      reason: form.value.reason,
      remarks: form.value.remarks,
      days: calculateDays.value
    }

    const resp = await api.post('/business-trips/', data)
    if (resp.success) {
      showMessage('success', '出差申请已提交')
      setTimeout(() => {
        router.push('/leaves/business')
      }, 1000)
    } else {
      showMessage('error', resp.error?.message || '提交失败')
    }
  } catch (e) {
    showMessage('error', '提交失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.page-container {
  min-height: 100vh;
  background: #f3f4f6;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.form-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 560px;
  overflow: hidden;
}

.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 24px;
  height: 24px;
  filter: invert(39%) sepia(90%) saturate(1352%) hue-rotate(196deg) brightness(96%) contrast(101%);
}

.form-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: #9ca3af;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #f3f4f6;
  color: #6b7280;
}

.form-body {
  padding: 24px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group.half {
  flex: 1;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #ef4444;
}

.form-input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #1f2937;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: none;
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-select :deep(.select-trigger) {
  padding: 12px 14px;
  padding-right: 36px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  min-height: 46px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-select :deep(.select-trigger:focus),
.form-select :deep(.custom-select.open .select-trigger) {
  border-color: #3b82f6;
  box-shadow: none;
}

.form-select :deep(.select-dropdown) {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 6px;
}

.form-select :deep(.select-option) {
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 14px;
}

.form-select :deep(.select-option:hover),
.form-select :deep(.select-option.highlighted) {
  background: #f3f4f6;
}

.form-select :deep(.select-option.selected) {
  background: #2563eb;
  color: #fff;
}

.form-date-input :deep(.date-input-wrapper) {
  position: relative;
}

.form-date-input :deep(.date-input) {
  width: 100%;
  padding: 12px 14px;
  padding-right: 40px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #1f2937;
  background: #fff;
  box-sizing: border-box;
}

.form-date-input :deep(.date-input:focus) {
  outline: none;
  border-color: #3b82f6;
  box-shadow: none;
}

.duration-display {
  padding: 12px 14px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.form-textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #1f2937;
  background: #fff;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: none;
}

.form-textarea::placeholder {
  color: #9ca3af;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-cancel:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-submit {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: #3b82f6;
  color: #fff;
  border: none;
}

.btn-submit:hover:not(:disabled) {
  background: #2563eb;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 消息提示 */
.message {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  padding: 12px 16px;
  border-radius: 8px;
  color: white;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 2000;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  font-size: 14px;
}

.message-success {
  background: #22c55e;
}

.message-error {
  background: #ef4444;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.8;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  opacity: 1;
}

/* 响应式 */
@media (max-width: 640px) {
  .page-container {
    padding: 1rem;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-group.half {
    flex: none;
  }
}
</style>
