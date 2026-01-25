<template>
  <div class="welcome-page">
    <div class="logo-section">
      <div class="logo-wrapper">
        <img src="/logo.svg" alt="Logo" class="logo-img" />
      </div>
      <h1 class="title">HR员工自助入职</h1>
      <p class="subtitle">快速完成入职登记，开启职场新旅程</p>
    </div>

    <div class="action-buttons">
      <van-button type="primary" block round size="large" @click="goRegister">
        新员工注册
      </van-button>
      <van-button plain type="primary" block round size="large" @click="goLogin">
        已有账号登录
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { onMounted } from 'vue'

const router = useRouter()
const userStore = useUserStore()

onMounted(async () => {
  // 如果已登录，跳转到对应页面
  if (userStore.isLoggedIn) {
    if (userStore.onboardStatus === 'onboarded') {
      router.replace('/home')
    } else {
      router.replace('/status')
    }
  }
})

function goRegister() {
  router.push('/register')
}

function goLogin() {
  router.push('/login')
}
</script>

<style scoped>
.welcome-page {
  min-height: 100vh;
  background: url('/bg-pattern.jpg') no-repeat center center;
  background-size: cover;
  display: flex;
  flex-direction: column;
  padding: 60px 24px 40px;
}

.logo-section {
  text-align: center;
  color: #fff;
  margin-bottom: 40px;
}

.logo-wrapper {
  width: 80px;
  height: 80px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  padding: 15px;
  box-sizing: border-box;
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.title {
  font-size: 28px;
  font-weight: 600;
  margin: 20px 0 8px;
}

.subtitle {
  font-size: 14px;
  opacity: 0.8;
}

.action-buttons {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-buttons :deep(.van-button--primary) {
  background: #fff;
  color: #409EFF;
  border: none;
}

.action-buttons :deep(.van-button--plain) {
  background: transparent;
  color: #fff;
  border-color: #fff;
}
</style>
