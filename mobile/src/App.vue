<template>
  <router-view />
</template>

<script setup>
import { useUserStore } from './stores/user'
import { onMounted } from 'vue'

const userStore = useUserStore()

onMounted(() => {
  // 尝试恢复登录状态
  userStore.checkAuth()
})
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: #f7f8fa;
}
</style>
