<template>
  <div class="login-page">
    <!-- 动态背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="login-card">
      <!-- Logo/品牌区 -->
      <div class="brand">
        <div class="logo-icon">
          <!-- 自定义Logo：将图片放到 public/icons/logo.svg -->
          <img src="/icons/logo.svg" alt="Logo" class="custom-logo" @error="logoError" />
        </div>
        <h1 class="brand-title"><img src="/icons/logo.svg" alt="HR" class="title-logo" /> 管理系统</h1>
        <p class="brand-subtitle">欢迎回来，请登录您的账号</p>
      </div>

      <form @submit.prevent="submit">
        <div v-if="error" class="error-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          {{ error }}
        </div>

        <div class="form-group">
          <label class="form-label">用户名</label>
          <div class="form-row" :class="{invalid: validationError === 'username'}">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
            <input
              v-model.trim="username"
              type="text"
              placeholder="请输入用户名或邮箱"
              @input="validationError = ''"
            />
          </div>
          <span v-if="validationError === 'username'" class="field-error">请输入对应的账号</span>
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <div class="form-row" :class="{invalid: validationError === 'password'}">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
            </svg>
            <input
              v-model="password"
              :type="showPwd?'text':'password'"
              placeholder="请输入密码"
              @input="validationError = ''"
            />
            <button type="button" class="toggle" @click="showPwd=!showPwd">
              <svg v-if="!showPwd" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/>
              </svg>
            </button>
          </div>
          <span v-if="validationError === 'password'" class="field-error">请输入对应的密码</span>
        </div>

        <button class="btn" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>

      <div class="footer-links">
        <router-link to="/forgot-password" class="link">忘记密码？</router-link>
      </div>
    </div>

    <!-- ICP备案号 -->
    <div class="icp-footer">
      <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">
        <svg class="icp-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        <span>蜀ICP备2026004175号-1</span>
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const username = ref('');
const password = ref('');
const showPwd = ref(false);
const loading = ref(false);
const error = ref('');
const validationError = ref('');

// Logo加载失败时的处理
function logoError(e) {
  e.target.style.display = 'none';
}

async function submit(){
  // 自定义验证
  if (!username.value) {
    validationError.value = 'username';
    return;
  }
  if (!password.value) {
    validationError.value = 'password';
    return;
  }
  validationError.value = '';
  error.value=''; loading.value=true;
  try {
    await auth.login(username.value, password.value);
    const next = route.query.redirect || '/';
    router.replace(next);
  } catch(e){
    error.value = auth.error || '登录失败';
  } finally { loading.value=false; }
}
</script>

<style scoped>
.login-page{
  min-height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:1rem;
  position: relative;
  overflow: hidden;
  /* 自定义壁纸 */
  background: url('/images/login-bg.jpg') no-repeat center center;
  background-size: cover;
}

/* 动态背景装饰圆 */
.bg-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}
.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  animation: float 20s infinite ease-in-out;
}
.circle-1 {
  width: 400px; height: 400px;
  top: -100px; left: -100px;
  animation-delay: 0s;
}
.circle-2 {
  width: 300px; height: 300px;
  bottom: -80px; right: -80px;
  animation-delay: -5s;
}
.circle-3 {
  width: 200px; height: 200px;
  top: 50%; left: 60%;
  animation-delay: -10s;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -30px) scale(1.05); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(20px, 10px) scale(1.02); }
}

.login-card{
  width: 400px;
  max-width: 92%;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 24px;
  padding: 40px 36px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: relative;
  z-index: 1;
  animation: slideUp 0.5s ease-out;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 品牌区 */
.brand {
  text-align: center;
  margin-bottom: 8px;
}
.logo-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 12px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.custom-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.brand-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.title-logo {
  height: 28px;
  width: auto;
  vertical-align: middle;
}
.brand-subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: #64748b;
}

/* 表单 */
form { display: flex; flex-direction: column; gap: 18px; }

.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  padding-left: 4px;
}

.form-row {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 0 12px;
  transition: all 0.2s;
}
.form-row.invalid {
  border-color: #ef4444;
  background: #fef2f2;
}
.form-row:focus-within {
  border-color: #0ea5e9;
  background: #fff;
  box-shadow: none;
}
.field-error {
  color: #ef4444;
  font-size: 12px;
  padding-left: 4px;
  margin-top: 2px;
}
.input-icon {
  color: #94a3b8;
  flex-shrink: 0;
}
.form-row:focus-within .input-icon {
  color: #0ea5e9;
}
.form-row input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 14px 12px;
  font-size: 15px;
  color: #1e293b;
}
.form-row input::placeholder {
  color: #94a3b8;
}

.toggle {
  border: none;
  background: transparent;
  color: #64748b;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.toggle:hover {
  background: #e2e8f0;
  color: #334155;
}

/* 登录按钮 */
.btn {
  width: 100%;
  border: none;
  background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
  color: #fff;
  font-weight: 600;
  padding: 16px 0;
  border-radius: 12px;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 8px 20px -4px rgba(14, 165, 233, 0.5);
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
}
.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px -4px rgba(14, 165, 233, 0.6);
}
.btn:active:not(:disabled) {
  transform: translateY(0);
}
.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 加载动画 */
.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 错误提示 */
.error-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  color: #b91c1c;
  padding: 12px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid #fca5a5;
  animation: shake 0.4s ease-out;
}
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-6px); }
  40%, 80% { transform: translateX(6px); }
}

/* 底部链接 */
.footer-links {
  text-align: center;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
}
.footer-links .link {
  color: #0ea5e9;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s;
}
.footer-links .link:hover {
  color: #0284c7;
  text-decoration: underline;
}

/* 版权信息 */
.copyright {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255,255,255,0.7);
  font-size: 12px;
  z-index: 1;
}

/* 响应式 */
@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px;
    border-radius: 20px;
  }
  .logo-icon {
    width: 56px;
    height: 56px;
  }
  .brand-title {
    font-size: 22px;
  }
}

/* ICP备案 */
.icp-footer {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  animation: fadeIn 1s ease-out 0.5s backwards;
}

.icp-footer a {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 99px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.icp-footer a:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
  color: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

.icp-icon {
  opacity: 0.8;
  transition: transform 0.3s ease;
}

.icp-footer a:hover .icp-icon {
  transform: scale(1.1);
  opacity: 1;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, 10px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
</style>
