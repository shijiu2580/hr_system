<template>
  <div class="forgot-password-page">
    <div class="forgot-card">
      <h2 class="title">找回密码</h2>
	  <p class="subtitle">通过邮箱验证码重置您的密码。</p>

	  <!-- 步骤指示 -->
      <div class="steps">
        <div :class="['step', {active: currentStep >= 1, completed: currentStep > 1}]">
          <div class="step-number">1</div>
		  <div class="step-label">输入邮箱</div>
        </div>
        <div class="step-line" :class="{completed: currentStep > 1}"></div>
        <div :class="['step', {active: currentStep >= 2, completed: currentStep > 2}]">
          <div class="step-number">2</div>
		  <div class="step-label">验证邮箱</div>
        </div>
        <div class="step-line" :class="{completed: currentStep > 2}"></div>
        <div :class="['step', {active: currentStep >= 3}]">
          <div class="step-number">3</div>
          <div class="step-label">重置密码</div>
        </div>
      </div>

      <!-- 步骤1：输入邮箱 -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="form-group">
		  <label>邮箱地址</label>
          <input
            v-model="email"
            type="email"
            placeholder="请输入注册时的邮箱"
            @keyup.enter="sendCode"
          />
        </div>
        <button class="btn-primary" @click="sendCode" :disabled="sending || countdown > 0">
          {{ countdown > 0 ? `${countdown}秒后重试` : (sending ? '发送中...' : '发送验证码') }}
        </button>
        <p v-if="error" class="message error">{{ error }}</p>
      </div>

      <!-- 步骤2：输入验证码 -->
      <div v-if="currentStep === 2" class="step-content">
        <p class="hint">验证码已发送到 <strong>{{ email }}</strong></p>
        <div class="form-group">
		  <label>验证码</label>
          <input
            v-model="code"
            type="text"
			placeholder="请输入6位验证码"
            maxlength="6"
            @keyup.enter="nextStep"
          />
        </div>
        <div class="actions">
      <button class="btn-secondary" @click="prevStep">上一步</button>
          <button class="btn-primary" @click="nextStep" :disabled="!code || code.length !== 6">
      下一步
          </button>
        </div>
        <button class="link-button" @click="resendCode" :disabled="countdown > 0">
          {{ countdown > 0 ? `${countdown}秒后可重新发送` : '重新发送验证码' }}
        </button>
      </div>

      <!-- 步骤3：设置新密码 -->
      <div v-if="currentStep === 3" class="step-content">
        <div class="form-group">
		  <label>新密码</label>
          <input
            v-model="newPassword"
            type="password"
			placeholder="至少 8 位，包含字母和数字"
            @keyup.enter="submitReset"
          />
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input
            v-model="confirmPassword"
            type="password"
			placeholder="再次输入新密码"
            @keyup.enter="submitReset"
          />
        </div>
        <div class="actions">
      <button class="btn-secondary" @click="prevStep">上一步</button>
          <button class="btn-primary" @click="submitReset" :disabled="resetting">
      {{ resetting ? '提交中...' : '完成重置' }}
          </button>
        </div>
        <p v-if="error" class="message error">{{ error }}</p>
      </div>

      <div class="footer">
        <router-link to="/login" class="link">返回登录</router-link>
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
import { useRouter } from 'vue-router';
import api from '../../utils/api';

const router = useRouter();

const currentStep = ref(1);
const email = ref('');
const code = ref('');
const newPassword = ref('');
const confirmPassword = ref('');

const sending = ref(false);
const resetting = ref(false);
const countdown = ref(0);
const error = ref('');

let countdownTimer = null;

function startCountdown() {
  countdown.value = 60;
  countdownTimer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      clearInterval(countdownTimer);
    }
  }, 1000);
}

async function sendCode() {
  error.value = '';

  if (!email.value) {
    error.value = '请输入邮箱地址';
    return;
  }

  if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email.value)) {
    error.value = '邮箱格式不正确';
    return;
  }

  sending.value = true;

  const result = await api.post('/auth/send_code/', {
    email: email.value,
    code_type: 'reset_password'
  });

  if (result.success) {
    currentStep.value = 2;
    startCountdown();
  } else {
	  error.value = result.error?.message || '发送失败';
  }

  sending.value = false;
}

async function resendCode() {
  await sendCode();
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--;
    error.value = '';
  }
}

function nextStep() {
  if (currentStep.value === 2 && code.value.length === 6) {
    currentStep.value = 3;
    error.value = '';
  }
}

async function submitReset() {
  error.value = '';

  if (!newPassword.value || !confirmPassword.value) {
	error.value = '请填写完整信息';
    return;
  }

  if (newPassword.value !== confirmPassword.value) {
	error.value = '两次输入的密码不一致';
    return;
  }

  if (newPassword.value.length < 8) {
	error.value = '密码长度至少 8 位';
    return;
  }

  if (!(/[a-zA-Z]/.test(newPassword.value) && /\d/.test(newPassword.value))) {
	error.value = '密码需包含字母和数字';
    return;
  }

  resetting.value = true;

  const result = await api.post('/auth/reset_password/', {
    email: email.value,
    code: code.value,
    new_password: newPassword.value
  });

  if (result.success) {
  alert('密码重置成功！请使用新密码登录');
    router.replace('/login');
  } else {
    error.value = result.error?.message || '重置失败';
  }

  resetting.value = false;
}
</script>

<style scoped>
.forgot-password-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  /* 自定义壁纸：将图片放到 public/images/login-bg.jpg */
  background: url('/images/login-bg.jpg') no-repeat center center;
  background-size: cover;
}

/* 动态背景装饰圆 */
.forgot-password-page::before,
.forgot-password-page::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  animation: float 20s infinite ease-in-out;
  pointer-events: none;
}
.forgot-password-page::before {
  width: 400px; height: 400px;
  top: -100px; left: -100px;
}
.forgot-password-page::after {
  width: 300px; height: 300px;
  bottom: -80px; right: -80px;
  animation-delay: -5s;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -30px) scale(1.05); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(20px, 10px) scale(1.02); }
}

.forgot-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
  max-width: 480px;
  width: 100%;
  padding: 2.5rem;
  opacity: 0;
  transform: translateY(20px) scale(.98);
  animation: cardFade 0.45s ease forwards;
  position: relative;
  z-index: 1;
}

.title {
  margin: 0 0 0.5rem;
  font-size: 28px;
  color: #1e293b;
  text-align: center;
}

.subtitle {
  margin: 0 0 2rem;
  color: #64748b;
  font-size: 14px;
  text-align: center;
}

.steps {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex: 0 0 auto;
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.3s;
}

.step.active .step-number {
  background: #2563eb;
  color: white;
}

.step.completed .step-number {
  background: #10b981;
  color: white;
}

.step-label {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
}

.step.active .step-label {
  color: #2563eb;
  font-weight: 500;
}

.step-line {
  flex: 1;
  height: 2px;
  background: #e2e8f0;
  margin: 0 0.5rem;
  margin-bottom: 1.5rem;
  transition: all 0.3s;
}

.step-line.completed {
  background: #10b981;
}

.step-content {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: none;
}

.btn-primary,
.btn-secondary {
  width: 100%;
  padding: 0.875rem;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.link-button {
  width: 100%;
  padding: 0.625rem;
  border: none;
  background: transparent;
  color: #2563eb;
  font-size: 13px;
  cursor: pointer;
  text-decoration: underline;
}

.link-button:hover:not(:disabled) {
  color: #1d4ed8;
}

.link-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hint {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 1rem;
}

.hint strong {
  color: #1e3a8a;
}

.message {
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 13px;
  margin-top: 1rem;
}

.message.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.footer {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.link {
  color: #2563eb;
  text-decoration: none;
  font-size: 14px;
}

.link:hover {
  text-decoration: underline;
}

@keyframes cardFade {
  from {
    opacity: 0;
    transform: translateY(20px) scale(.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 640px) {
  .forgot-card {
    padding: 1.5rem;
  }

  .step-label {
    font-size: 10px;
  }

  .actions {
    grid-template-columns: 1fr;
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
}
</style>
