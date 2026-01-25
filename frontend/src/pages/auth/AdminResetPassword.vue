<template>
  <div class="panel">
    <h2>管理员重置用户密码</h2>
    <div v-if="!isAdmin" class="warn">当前账号不是管理员，无法使用本页面。</div>
    <form v-else @submit.prevent="submit" class="form">
      <label>
        用户名
        <input v-model="username" required placeholder="要重置的用户名" />
      </label>
      <label class="row">
        <input type="checkbox" v-model="generateRandom" /> 自动生成随机强密码
      </label>
        <label class="row">
          <input type="checkbox" v-model="forceChange" /> 重置后强制用户下次登录修改密码
        </label>
      <label v-if="!generateRandom">
        新密码
        <input type="password" v-model="newPassword" minlength="8" placeholder="至少8位，含字母和数字" />
      </label>
      <button :disabled="loading">{{ loading ? '提交中...' : '重置密码' }}</button>
    </form>
    <div v-if="result" class="result-box">
      <p>已重置：<strong>{{ result.username }}</strong></p>
      <p>新密码：<code>{{ result.new_password }}</code></p>
      <p class="tip">请立即复制并安全保存，页面刷新后不会再次显示。</p>
    </div>
    <div v-if="error" class="error-box">{{ error }}</div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '../../stores/auth';
import api from '../../utils/api';

const auth = useAuthStore();
const username = ref('');
const newPassword = ref('');
const generateRandom = ref(false);
const forceChange = ref(false);
const loading = ref(false);
const error = ref(null);
const result = ref(null);

const isAdmin = computed(()=> auth.user && (auth.user.is_superuser || auth.roles.some(r=> r.code==='admin')));

async function submit(){
  error.value = null; result.value = null;
  if(!isAdmin.value){ error.value = '没有权限'; return; }
  if(!generateRandom.value){
    if(newPassword.value.length < 8){ error.value = '密码至少8位'; return; }
    if(!(/[0-9]/.test(newPassword.value) && /[A-Za-z]/.test(newPassword.value))){ error.value = '需包含字母与数字'; return; }
  }
  loading.value = true;
  try {
    const { data } = await api.post('/auth/admin_reset_password/', {
      username: username.value.trim(),
      new_password: generateRandom.value ? '' : newPassword.value,
      generate_random: generateRandom.value,
      force_change_password: forceChange.value
    });
    if(data.success){
      result.value = data.data;
    } else {
      error.value = data.error?.message || '重置失败';
    }
  } catch(e){
    error.value = e.response?.data?.error?.message || e.response?.data?.detail || '请求失败';
  } finally { loading.value = false; }
}
</script>
<style scoped>
.panel {
  max-width: 460px;
  background: #fff;
  padding: 1.2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}

[data-theme="dark"] .panel {
  background: #1f1f1f;
  border-color: #333;
}

form {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  margin-top: 0.6rem;
}

label {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  gap: 0.35rem;
}

input[type="text"],
input[type="password"] {
  padding: 0.55rem 0.6rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}

[data-theme="dark"] input {
  background: #2a2a2a;
  border-color: #444;
  color: #eee;
}

button {
  padding: 0.65rem 0.9rem;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.warn {
  background: #fef3c7;
  color: #92400e;
  padding: 0.6rem 0.75rem;
  border: 1px solid #fde68a;
  border-radius: 6px;
  font-size: 13px;
}

.error-box {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.6rem 0.75rem;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 13px;
  margin-top: 1rem;
}

.result-box {
  background: #ecfdf5;
  color: #065f46;
  padding: 0.7rem 0.8rem;
  border: 1px solid #d1fae5;
  border-radius: 6px;
  font-size: 13px;
  margin-top: 1rem;
}

code {
  background: #f1f5f9;
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 13px;
}

[data-theme="dark"] code {
  background: #334155;
  color: #e2e8f0;
}

.tip {
  font-size: 12px;
  color: #555;
  margin-top: 0.4rem;
}

[data-theme="dark"] .tip {
  color: #aaa;
}
</style>
