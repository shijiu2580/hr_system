<template>
  <div class="page-container">
    <van-nav-bar title="新员工注册" left-arrow @click-left="$router.back()" />

    <div class="form-container">
      <div class="page-title">入职登记</div>
      <p class="desc-text" style="text-align: center; margin-bottom: 20px;">
        请填写您的基本信息完成注册
      </p>

      <van-form @submit="handleRegister">
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            name="name"
            label="姓名"
            placeholder="请输入真实姓名"
            :rules="[{ required: true, message: '请输入姓名' }]"
          />
          <van-field
            v-model="form.phone"
            name="phone"
            label="手机号"
            type="tel"
            placeholder="请输入手机号"
            :rules="[
              { required: true, message: '请输入手机号' },
              { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' }
            ]"
          />
          <van-field
            v-model="form.email"
            name="email"
            label="邮箱"
            type="email"
            placeholder="请输入邮箱（用于接收验证码）"
            :rules="[
              { required: true, message: '请输入邮箱' },
              { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '邮箱格式不正确' }
            ]"
          />
          <van-field
            v-model="form.code"
            name="code"
            label="验证码"
            placeholder="请输入邮箱验证码"
            :rules="[{ required: true, message: '请输入验证码' }]"
          >
            <template #button>
              <van-button 
                size="small" 
                type="primary" 
                :disabled="countdown > 0"
                :loading="sendingCode"
                @click="sendCode"
              >
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </van-button>
            </template>
          </van-field>
          <van-field
            v-model="form.password"
            type="password"
            name="password"
            label="密码"
            placeholder="请设置登录密码（至少8位）"
            :rules="[
              { required: true, message: '请设置密码' },
              { pattern: /^.{8,}$/, message: '密码至少8位' }
            ]"
          />
          <van-field
            v-model="form.confirmPassword"
            type="password"
            name="confirmPassword"
            label="确认密码"
            placeholder="请再次输入密码"
            :rules="[
              { required: true, message: '请确认密码' },
              { validator: confirmPasswordValidator, message: '两次密码不一致' }
            ]"
          />
        </van-cell-group>

        <div style="margin: 24px 16px;">
          <van-button 
            round 
            block 
            type="primary" 
            native-type="submit"
            :loading="loading"
          >
            注册
          </van-button>
        </div>
      </van-form>

      <div class="footer-links">
        <span @click="$router.push('/login')">已有账号？立即登录</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import { useUserStore } from '../stores/user'
import api from '../utils/api'

const router = useRouter()
const userStore = useUserStore()

const form = ref({
  name: '',
  phone: '',
  email: '',
  code: '',
  password: '',
  confirmPassword: '',
})
const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)

function confirmPasswordValidator(val) {
  return val === form.value.password
}

async function sendCode() {
  if (!form.value.email) {
    showToast('请先输入邮箱')
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    showToast('邮箱格式不正确')
    return
  }

  sendingCode.value = true
  try {
    const res = await api.post('/api/onboarding/send-code/', {
      email: form.value.email,
    })
    if (res.data.success) {
      showSuccessToast('验证码已发送')
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    } else {
      showToast(res.data.error?.message || '发送失败')
    }
  } catch (e) {
    showToast(e.response?.data?.error?.message || '发送失败')
  } finally {
    sendingCode.value = false
  }
}

async function handleRegister() {
  loading.value = true
  try {
    const res = await userStore.register({
      name: form.value.name,
      phone: form.value.phone,
      email: form.value.email,
      code: form.value.code,
      password: form.value.password,
    })
    
    if (res.success) {
      showSuccessToast('注册成功')
      router.replace('/profile')
    } else {
      showToast(res.error?.message || '注册失败')
    }
  } catch (e) {
    showToast(e.response?.data?.error?.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.footer-links {
  text-align: center;
  color: #1989fa;
  font-size: 14px;
  margin-top: 20px;
}
</style>
