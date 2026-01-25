<template>
  <div class="modal-overlay" @click.self="goBack">
    <div class="modal-container">
      <!-- 模态框头部 -->
      <div class="modal-header">
        <h2 class="modal-title">请假申请</h2>
        <button class="modal-close" @click="goBack">×</button>
      </div>

      <!-- 模态框内容 -->
      <div class="modal-body">
        <div v-if="error" class="alert alert-error">
          <span>{{ error }}</span>
          <button @click="error = ''" class="alert-close">×</button>
        </div>

        <form @submit.prevent="handleSubmit" class="leave-form">
          <div class="form-group">
            <label class="form-label">开始日期</label>
            <CustomDateInput 
              v-model="form.start_date" 
              placeholder="选择日期"
              class="form-date"
            />
          </div>

          <div class="form-group">
            <label class="form-label">结束日期</label>
            <CustomDateInput 
              v-model="form.end_date" 
              placeholder="选择日期"
              class="form-date"
            />
          </div>

          <div class="form-group">
            <label class="form-label">请假类型</label>
            <CustomSelect
              v-model="form.leave_type"
              :options="leaveTypes"
              placeholder="选择请假类型"
              class="form-select"
            />
          </div>

          <div class="form-group">
            <label class="form-label">请假原因</label>
            <textarea 
              v-model="form.reason" 
              class="form-textarea" 
              rows="4"
              placeholder="请填写请假原因"
              required
            ></textarea>
          </div>
        </form>
      </div>

      <!-- 模态框底部 -->
      <div class="modal-footer">
        <button type="button" class="btn btn-cancel" @click="goBack">取消</button>
        <button type="button" class="btn btn-submit" :disabled="saving" @click="handleSubmit">
          {{ saving ? '提交中...' : '提交申请' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'
import CustomDateInput from '../../components/CustomDateInput.vue'

const router = useRouter()

const saving = ref(false)
const error = ref('')

const form = ref({
  leave_type: 'personal',
  start_date: '',
  end_date: '',
  reason: ''
})

const leaveTypes = [
  { value: 'annual', label: '年假' },
  { value: 'sick', label: '病假' },
  { value: 'personal', label: '事假' },
  { value: 'marriage', label: '婚假' },
  { value: 'bereavement', label: '丧假' },
  { value: 'maternity', label: '产假' }
]

function goBack() {
  router.push('/leaves')
}

async function handleSubmit() {
  if (!form.value.leave_type || !form.value.start_date || !form.value.end_date || !form.value.reason) {
    error.value = '请填写完整信息'
    return
  }
  
  if (new Date(form.value.end_date) < new Date(form.value.start_date)) {
    error.value = '结束日期不能早于开始日期'
    return
  }
  
  saving.value = true
  error.value = ''
  try {
    await api.post('/leaves/', form.value)
    router.push('/leaves')
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.error?.message || '提交失败'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: #fff;
  border-radius: 8px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}

.modal-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.modal-close {
  width: 28px;
  height: 28px;
  border: none;
  background: none;
  font-size: 20px;
  color: #9ca3af;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #6b7280;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.modal-body::-webkit-scrollbar {
  display: none;
}

.alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 14px;
}

.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.alert-close {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: inherit;
  padding: 0;
  margin-left: 10px;
}

.leave-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #1f2937;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: none;
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-select {
  width: 100%;
}

.form-select :deep(.select-trigger) {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
}

.form-select :deep(.select-trigger:focus) {
  border-color: #3b82f6;
  box-shadow: none;
}

.form-date {
  width: 100%;
}

.form-date :deep(.date-display) {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
}

.form-date :deep(.custom-date.focused .date-display) {
  border-color: #3b82f6;
  box-shadow: none;
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #1f2937;
  background: #fff;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: none;
}

.form-textarea::placeholder {
  color: #9ca3af;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #fff;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-cancel:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-submit {
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

@media (max-width: 520px) {
  .modal-container {
    margin: 16px;
    max-width: calc(100% - 32px);
  }
}
</style>
