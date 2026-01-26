<template>
  <div class="security-section">
    <h3>密码安全</h3>
    
    <div v-if="auth?.mustChangePassword" class="alert warning">
      <strong> 首次登录必须修改密码</strong>
      <p>完成密码修改后才能访问其它页面。</p>
    </div>

    <form @submit.prevent="changePassword" class="form-stack" novalidate>
      <div class="form-group">
        <label>旧密码<span class="required">*</span></label>
        <input type="password" v-model="oldPassword" required autocomplete="current-password" />
      </div>

      <div class="form-group">
        <label>新密码<span class="required">*</span></label>
        <input type="password" v-model="newPassword" required autocomplete="new-password" />
        <span class="hint">至少 8 位，需包含字母和数字</span>
      </div>

      <div class="form-group">
        <label>确认新密码<span class="required">*</span></label>
        <input type="password" v-model="confirmPassword" required autocomplete="new-password" />
      </div>

      <div class="actions actions-inline">
        <button type="submit" class="btn-primary btn-full" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '处理中...' : '修改密码' }}
        </button>
        <button type="button" class="btn-secondary btn-full" 
          :disabled="loading || !hasInput" @click="resetFields">清空</button>
      </div>

      <transition name="fade-msg">
        <p v-if="error" class="message error">{{ error }}</p>
      </transition>
      <transition name="fade-msg">
        <p v-if="success" class="message success">{{ success }}</p>
      </transition>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../../utils/api'
import { useRouter } from 'vue-router'

const props = defineProps({
  auth: { type: Object, default: null }
})

const router = useRouter()

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref(null)
const success = ref(null)

const hasInput = computed(() => oldPassword.value || newPassword.value || confirmPassword.value)

function resetFields() {
  oldPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  error.value = null
  success.value = null
}

async function changePassword() {
  error.value = null
  success.value = null
  
  if (!oldPassword.value || !newPassword.value || !confirmPassword.value) {
    error.value = '请填写所有密码字段'
    return
  }
  if (newPassword.value.length < 8) {
    error.value = '新密码至少 8 位'
    return
  }
  if (!/[0-9]/.test(newPassword.value) || !/[A-Za-z]/.test(newPassword.value)) {
    error.value = '新密码需包含字母和数字'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = '两次输入的新密码不一致'
    return
  }

  loading.value = true
  try {
    const resp = await api.post('/auth/change-password/', {
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    if (resp.success) {
      success.value = '密码修改成功'
      resetFields()
      if (props.auth?.mustChangePassword) {
        props.auth.mustChangePassword = false
        router.push('/')
      }
    } else {
      error.value = resp.message || '修改失败'
    }
  } catch (e) {
    error.value = e.message || '网络错误'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.security-section h3 {
  margin: 0 0 1.25rem;
  padding-bottom: 0.75rem;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  border-bottom: 1px solid rgba(148, 163, 184, 0.3);
}
[data-theme="dark"] .security-section h3 {
  color: #f1f5f9;
}
</style>
