<template>
  <div class="page-container">
    <van-nav-bar title="登录" left-arrow @click-left="$router.back()" />

    <div class="form-container">
      <div class="page-title">欢迎回来</div>
      <p class="desc-text" style="text-align: center; margin-bottom: 30px;">
        使用您的账号登录
      </p>

      <van-form @submit="handleLogin">
        <van-cell-group inset>
          <van-field
            v-model="form.username"
            name="username"
            label="账号"
            placeholder="手机号/邮箱/员工编号"
            :rules="[{ required: true, message: '请输入账号' }]"
          />
          <van-field
            v-model="form.password"
            type="password"
            name="password"
            label="密码"
            placeholder="请输入密码"
            :rules="[{ required: true, message: '请输入密码' }]"
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
            登录
          </van-button>
        </div>
      </van-form>

      <div class="footer-links">
        <span @click="$router.push('/register')">还没有账号？立即注册</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast, showSuccessToast, closeToast } from 'vant'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const form = ref({
  username: '',
  password: '',
})
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await userStore.login(form.value)
    
    // 跳转前清除所有 Toast
    closeToast(true)
    
    // 直接跳转
    const redirect = route.query.redirect
    if (redirect) {
      router.replace(redirect)
    } else if (userStore.onboardStatus === 'onboarded') {
      router.replace('/home')
    } else {
      router.replace('/status')
    }
  } catch (e) {
    showToast(e.response?.data?.detail || '登录失败')
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
