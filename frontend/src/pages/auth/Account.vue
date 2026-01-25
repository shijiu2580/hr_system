<template>
  <div class="account-page">
    <section class="hero-panel">
      <div class="hero-main">
        <div class="avatar-large">{{ avatarInitials }}</div>
        <div class="hero-text-block">
          <div class="hero-title-row">
            <h1>{{ displayName }}</h1>
            <span v-if="auth.user?.is_staff" class="badge admin">管理员</span>
          </div>
          <p class="hero-subtitle">账号：{{ auth.user?.username }}</p>
          <p class="hero-meta-line">上次登录：{{ lastLoginText }}</p>
        </div>
      </div>
      <div class="hero-side">
        <div class="hero-item">
          <span class="hero-item-label">加入时间</span>
          <span class="hero-item-value">{{ joinedText }}</span>
        </div>
        <div class="hero-item">
          <span class="hero-item-label">邮箱状态</span>
          <span class="hero-item-value">{{ emailBoundText }}</span>
        </div>
      </div>
    </section>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">资料完整度</div>
        <div class="stat-main">
          <span class="stat-value">{{ profileCompletion }}%</span>
          <div class="progress">
            <div class="progress-bar" :style="{ width: profileCompletion + '%' }"></div>
          </div>
        </div>
      </div>
      <div class="stat-card" :class="emailBoundClass">
        <div class="stat-label">邮箱绑定</div>
        <div class="stat-main">
          <span class="stat-value">{{ emailBoundText }}</span>
          <small>{{ emailBoundHint }}</small>
        </div>
      </div>
      <div class="stat-card" :class="passwordStatusClass">
        <div class="stat-label">密码状态</div>
        <div class="stat-main">
          <span class="stat-value">{{ passwordStatus }}</span>
          <small>{{ passwordStatusHint }}</small>
        </div>
      </div>
    </div>

    <div class="account-main">
      <div class="account-column">
        <section class="card card-profile" aria-labelledby="profile-section-title">
          <h3 id="profile-section-title">个人资料</h3>
      <form @submit.prevent="saveProfile" class="form-stack" novalidate>
        <div class="form-group">
          <label>登录用户名</label>
          <input type="text" :value="auth.user?.username" disabled aria-disabled="true" />
          <span class="hint">用于系统登录，创建后不可更改</span>
        </div>

        <div class="form-row">
          <div class="form-group" :class="{'invalid': firstNameError}">
            <label>名（First Name）</label>
            <input type="text" v-model.trim="firstName" maxlength="30" placeholder="例如：三" @input="validateProfile" aria-describedby="firstNameHint" />
            <span class="hint error-hint" v-if="firstNameError">{{ firstNameError }}</span>
          </div>
          <div class="form-group" :class="{'invalid': lastNameError}">
            <label>姓（Last Name）</label>
            <input type="text" v-model.trim="lastName" maxlength="150" placeholder="例如：张" @input="validateProfile" aria-describedby="lastNameHint" />
            <span class="hint error-hint" v-if="lastNameError">{{ lastNameError }}</span>
          </div>
        </div>

        <div class="form-group" :class="{'invalid': emailError}">
          <label>联系邮箱</label>
          <input type="email" v-model.trim="email" placeholder="your@email.com" @input="validateProfile" aria-describedby="emailHint" />
          <span class="hint error-hint" v-if="emailError">{{ emailError }}</span>
        </div>

        <div class="actions actions-inline">
          <button type="submit" class="btn-primary btn-full" :disabled="!profileDirty || profileLoading || hasProfileErrors" :aria-disabled="(!profileDirty || profileLoading || hasProfileErrors).toString()">
            <span v-if="profileLoading" class="spinner" aria-hidden="true"></span>
            {{ profileLoading ? '保存中...' : '保存资料' }}
          </button>
          <button type="button" class="btn-secondary btn-full" :disabled="!profileDirty || profileLoading" @click="resetProfile" v-if="profileDirty">重置</button>
        </div>

        <transition name="fade-msg">
          <p v-if="profileError" class="message error" aria-live="assertive">{{ profileError }}</p>
        </transition>
        <transition name="fade-msg">
          <p v-if="profileSuccess" class="message success" aria-live="polite">{{ profileSuccess }}</p>
        </transition>
      </form>
        </section>
      </div>

      <div class="account-column">
        <section class="card card-password" aria-labelledby="password-section-title">
          <h3 id="password-section-title">密码安全</h3>
      <div v-if="auth.mustChangePassword" class="alert warning">
        <strong>⚠️ 首次登录必须修改密码</strong>
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
          <button type="submit" class="btn-primary btn-full" :disabled="passwordLoading" :aria-disabled="passwordLoading.toString()">
            <span v-if="passwordLoading" class="spinner" aria-hidden="true"></span>
            {{ passwordLoading ? '处理中...' : '修改密码' }}
          </button>
          <button type="button" class="btn-secondary btn-full" :disabled="passwordLoading || !hasPasswordInput" @click="resetPasswordFields">清空</button>
        </div>

        <transition name="fade-msg">
          <p v-if="passwordError" class="message error" aria-live="assertive">{{ passwordError }}</p>
        </transition>
        <transition name="fade-msg">
          <p v-if="passwordSuccess" class="message success" aria-live="polite">{{ passwordSuccess }}</p>
        </transition>
      </form>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onBeforeUnmount } from 'vue';
import { useAuthStore } from '../../stores/auth';
import { useRouter } from 'vue-router';
import api from '../../utils/api';

const auth = useAuthStore();
const router = useRouter();

// 个人资料
const firstName = ref('');
const lastName = ref('');
const email = ref('');
const profileLoading = ref(false);
const profileError = ref(null);
const profileSuccess = ref(null);
const firstNameError = ref(null);
const lastNameError = ref(null);
const emailError = ref(null);
const profileDirty = ref(false);

// 密码修改
const oldPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const passwordLoading = ref(false);
const passwordError = ref(null);
const passwordSuccess = ref(null);
const canSubmitPassword = computed(()=> {
  if(!oldPassword.value || !newPassword.value || !confirmPassword.value) return false;
  if(newPassword.value.length < 8) return false;
  if(newPassword.value !== confirmPassword.value) return false;
  if(!(/[0-9]/.test(newPassword.value) && /[A-Za-z]/.test(newPassword.value))) return false;
  return true;
});
const hasPasswordInput = computed(()=> oldPassword.value || newPassword.value || confirmPassword.value);

const displayName = computed(()=> {
  if(!auth.user) return '未登录';
  const { first_name, last_name, username } = auth.user;
  if(first_name || last_name){
    return `${last_name || ''}${first_name || ''}`.trim();
  }
  return username;
});

const avatarInitials = computed(()=> {
  if(!auth.user) return '?';
  const first = auth.user.first_name?.charAt(0) || '';
  const last = auth.user.last_name?.charAt(0) || '';
  const combo = `${last}${first}`.trim();
  return combo ? combo.slice(0,2).toUpperCase() : (auth.user.username?.slice(0,2).toUpperCase() || '?');
});

function formatDate(value){
  if(!value) return '--';
  try { return new Date(value).toLocaleString(); }
  catch { return value; }
}

const lastLoginText = computed(()=> formatDate(auth.user?.last_login));
const joinedText = computed(()=> formatDate(auth.user?.date_joined));

const emailBoundText = computed(()=> email.value ? '已绑定' : '未绑定');
const emailBoundClass = computed(()=> email.value ? 'stat-positive' : 'stat-warning');
const emailBoundHint = computed(()=> email.value ? email.value : '绑定邮箱可用于找回密码');

const profileCompletion = computed(()=> {
  let total = 3;
  let filled = 0;
  if(firstName.value) filled++;
  if(lastName.value) filled++;
  if(email.value) filled++;
  return Math.round((filled / total) * 100);
});

const passwordStatus = computed(()=> auth.mustChangePassword ? '需更新' : '安全');
const passwordStatusClass = computed(()=> auth.mustChangePassword ? 'stat-warning' : 'stat-positive');
const passwordStatusHint = computed(()=> auth.mustChangePassword ? '系统要求尽快更新密码' : '建议定期更换密码');

// 控制初始化时不触发 dirty
const isInitializing = ref(true);

onMounted(() => {
  // 加载用户资料
  if (auth.user) {
    firstName.value = auth.user.first_name || '';
    lastName.value = auth.user.last_name || '';
    email.value = auth.user.email || '';
  }
  // 延迟一个 tick 后再允许 dirty
  setTimeout(() => {
    isInitializing.value = false;
    profileDirty.value = false;
  }, 0);
});

function markDirty(){ 
  if (!isInitializing.value) {
    profileDirty.value = true; 
  }
}
watch([firstName,lastName,email], ()=> { markDirty(); validateProfile(); });

function validateProfile(){
  firstNameError.value = firstName.value.length > 30 ? '长度超过 30' : null;
  lastNameError.value = lastName.value.length > 150 ? '长度超过 150' : null;
  if(email.value){
    const emailPattern = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
    emailError.value = emailPattern.test(email.value) ? null : '邮箱格式不正确';
  } else {
    emailError.value = null;
  }
}
const hasProfileErrors = computed(()=> firstNameError.value || lastNameError.value || emailError.value);

function resetProfile(){
  if(!auth.user) return;
  firstName.value = auth.user.first_name || '';
  lastName.value = auth.user.last_name || '';
  email.value = auth.user.email || '';
  profileDirty.value = false; profileError.value = null; profileSuccess.value = null;
  validateProfile();
}

async function saveProfile() {
  profileError.value = null;
  profileSuccess.value = null;
  profileLoading.value = true;
  
  try {
    const resp = await api.post('/auth/update_profile/', {
      first_name: firstName.value,
      last_name: lastName.value,
      email: email.value
    });
    
    if (resp.success) {
      profileSuccess.value = '资料已保存';
      // 有的 store 方法叫 fetchMe，这里确保调用存在的方法
      try { await auth.fetchMe?.(); } catch(_) {}
      // 同步更新本地值，避免用户误以为没有保存
      if (auth.user) {
        isInitializing.value = true;
        firstName.value = auth.user.first_name || '';
        lastName.value = auth.user.last_name || '';
        email.value = auth.user.email || '';
        setTimeout(() => { isInitializing.value = false; }, 0);
      }
      profileDirty.value = false;
      setTimeout(()=> { profileSuccess.value = null; }, 2500);
    } else {
      profileError.value = resp.error?.message || resp.detail || '保存失败';
      setTimeout(()=> { if(profileError.value) profileError.value = null; }, 4000);
    }
  } catch (err) {
    profileError.value = err.response?.data?.error?.message || err.response?.data?.detail || '保存失败';
    setTimeout(()=> { if(profileError.value) profileError.value = null; }, 4000);
  } finally {
    profileLoading.value = false;
  }
}

async function changePassword() {
  // 先清空提示
  passwordError.value = null;
  passwordSuccess.value = null;
  passwordLoading.value = true;

  // 去除首尾空格
  const old = oldPassword.value.trim();
  const nw = newPassword.value.trim();
  const cf = confirmPassword.value.trim();
  oldPassword.value = old; newPassword.value = nw; confirmPassword.value = cf;

  // 前端快速校验，减少不必要请求
  if (!old) {
    passwordLoading.value = false;
    passwordError.value = '请输入旧密码';
    return;
  }
  if (nw.length < 8) {
    passwordLoading.value = false;
    passwordError.value = '新密码至少 8 位';
    return;
  }
  if (nw !== cf) {
    passwordLoading.value = false;
    passwordError.value = '两次输入的新密码不一致';
    return;
  }
  if (!(/[0-9]/.test(nw) && /[A-Za-z]/.test(nw))) {
    passwordLoading.value = false;
    passwordError.value = '新密码需包含字母与数字';
    return;
  }
  
  try {
    const resp = await api.post('/auth/change_password/', {
      old_password: oldPassword.value,
      new_password: newPassword.value,
      confirm_password: confirmPassword.value
    });
    
    if (resp.success) {
      // 成功时仅显示成功信息，确保失败信息清空
      passwordError.value = null;
      passwordSuccess.value = '密码已修改成功，即将跳转到登录页...';
      oldPassword.value = '';
      newPassword.value = '';
      confirmPassword.value = '';
      // 密码修改后旧 token 失效，需要重新登录
      setTimeout(() => {
        auth.forceLogout();
        router.replace('/login');
      }, 1500);
    } else {
      passwordSuccess.value = null; // 明确清空成功提示
      passwordError.value = resp.error?.message || resp.detail || '修改失败';
      setTimeout(()=> { if(passwordError.value) passwordError.value = null; }, 4000);
    }
  } catch (err) {
    passwordSuccess.value = null;
    passwordError.value = err.response?.data?.error?.message || err.response?.data?.detail || '修改失败';
    setTimeout(()=> { if(passwordError.value) passwordError.value = null; }, 4000);
  } finally {
    passwordLoading.value = false;
  }
}

function resetPasswordFields(){
  oldPassword.value=''; newPassword.value=''; confirmPassword.value=''; passwordError.value=null; passwordSuccess.value=null;
}

// 离开页面前未保存提醒
function beforeUnload(e){
  if(profileDirty.value){
    e.preventDefault();
    e.returnValue = '';
  }
}
window.addEventListener('beforeunload', beforeUnload);
onBeforeUnmount(()=> { window.removeEventListener('beforeunload', beforeUnload); });
</script>

<style scoped>
.account-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem 1.25rem;
}

.account-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  align-items: start;
  margin-top: 1.25rem;
}

.account-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.account-column > .card {
  height: auto;
}

.hero-panel {
  margin-bottom: 1.25rem;
  padding: 1.25rem 1.5rem;
  border-radius: 12px;
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  color: #0f172a;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.2rem;
}

.hero-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1 1 0;
}

.avatar-large {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: #4f46e5;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
}

.hero-text-block {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.hero-title-row h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #0f172a;
}

.hero-subtitle,
.hero-meta-line {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  font-size: 13px;
}

.hero-item-label {
  display: block;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 11px;
  color: #94a3b8;
}

.hero-item-value {
  display: block;
  font-size: 14px;
  color: #0f172a;
}

.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:.9rem;margin-bottom:1.1rem;}
.stat-card{background:#fff;border:1px solid rgba(148,163,184,.4);border-radius:10px;padding:.9rem 1.1rem;min-height:100px;display:flex;flex-direction:column;justify-content:center;transition:border-color .2s ease;}
.stat-card:hover{border-color:rgba(148,163,184,.6);}
.stat-label{font-size:12px;color:#64748b;margin-bottom:.35rem;text-transform:uppercase;letter-spacing:.08em;}
.stat-main{display:flex;flex-direction:column;gap:.4rem;}
.stat-value{font-size:22px;font-weight:650;color:#0f172a;line-height:1.1;}
.progress{height:6px;border-radius:999px;background:#f1f5f9;overflow:hidden;}
.progress-bar{height:100%;background:#4f46e5;}
.stat-card small{color:#64748b;font-size:12px;}
.stat-positive{background:#f8fafc;}
.stat-positive .stat-value{color:#0f172a;}
.stat-warning{background:#f8fafc;}
.stat-warning .stat-value{color:#0f172a;}

.badge.admin{padding:.2rem .65rem;border-radius:999px;font-size:12px;line-height:1.2;}
.hero-panel .badge.admin{background:#4f46e5;border:none;color:#fff;}

.card{background:#fff;border:1px solid rgba(148,163,184,.4);border-radius:10px;padding:1.25rem 1.5rem;transition:border-color .2s ease;}
.card:hover{border-color:rgba(148,163,184,.6);}

.card-profile h3,
.card-password h3 {
  margin: 0 0 1.25rem;
  padding-bottom: 0.75rem;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  border-bottom: 1px solid rgba(148,163,184,.3);
}

[data-theme=dark] .hero-panel{background:#1e293b;border-color:rgba(148,163,184,.3);color:#f1f5f9;}
[data-theme=dark] .hero-panel h1{color:#f1f5f9;}
[data-theme=dark] .hero-subtitle,[data-theme=dark] .hero-meta-line{color:#94a3b8;}
[data-theme=dark] .hero-item-value{color:#f1f5f9;}
[data-theme=dark] .avatar-large{background:#6366f1;}
[data-theme=dark] .card{background:#1e293b;border-color:rgba(148,163,184,.3);}
[data-theme=dark] .stat-card{background:#1e293b;border-color:rgba(148,163,184,.3);}
[data-theme=dark] .stat-value{color:#f1f5f9;}
[data-theme=dark] .stat-label{color:#94a3b8;}

.form-stack {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  column-gap: 1rem;
  row-gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.form-group.invalid input{border-color:#ef4444;background:#fef2f2;}
.error-hint{color:#b91c1c;}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}

[data-theme=dark] .form-group label {
  color: #94a3b8;
}

.required {
  color: var(--color-danger);
}

.form-group input {
  box-sizing: border-box;
  height: 38px;
  padding: 0 0.875rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s;
  background: #fff;
  line-height: 1.4;
}

.form-group input:focus {
  outline: none;
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
  box-shadow: none;
}

.form-group input:disabled {
  background: #f8fafc;
  color: #64748b;
  cursor: not-allowed;
}

[data-theme=dark] .form-group input{background:#1e293b;border-color:rgba(148,163,184,.3);color:#f1f5f9;}
[data-theme=dark] .form-group input:focus{background:#334155;border-color:rgba(148,163,184,.5);}
[data-theme=dark] .form-group input:disabled{background:#334155;color:#94a3b8;}

.hint {
  font-size: 12px;
  color: var(--color-text-secondary);
}

[data-theme=dark] .hint {
  color: #94a3b8;
}

.actions {
  margin-top: 0.75rem;
}

.actions-inline {
  display: flex;
  gap: 0.75rem;
}

.btn-full {
  flex: 1 1 0;
  text-align: center;
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 10px;
  background: #4f46e5;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #4338ca;
}
.btn-secondary{padding:0.625rem 1rem;border:1px solid rgba(148,163,184,.4);border-radius:10px;background:#fff;color:#475569;font-size:14px;font-weight:500;cursor:pointer;transition:.2s;}
.btn-secondary:hover:not(:disabled){background:#f8fafc;border-color:rgba(148,163,184,.6);}
.btn-secondary:disabled{opacity:.55;cursor:not-allowed;}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 13px;
  margin: 0;
}

.message.error {
  background: rgba(254,242,242,.8);
  color: #b91c1c;
  border: 1px solid rgba(239,68,68,.4);
}

.message.success {
  background: rgba(240,253,244,.8);
  color: #15803d;
  border: 1px solid rgba(74,222,128,.5);
}
.spinner {width:16px;height:16px;border:3px solid #fff;border-right-color:transparent;border-radius:50%;display:inline-block;animation:spin 0.65s linear infinite;margin-right:6px;vertical-align:middle;}
@keyframes spin {to{transform:rotate(360deg);}}
.fade-msg-enter-active,.fade-msg-leave-active{transition:opacity .35s;}
.fade-msg-enter-from,.fade-msg-leave-to{opacity:0;}

[data-theme=dark] .message.error {
  background: rgba(127,29,29,.3);
  color: #fca5a5;
  border-color: rgba(248,113,113,.35);
}

[data-theme=dark] .message.success {
  background: rgba(20,83,45,.3);
  color: #86efac;
  border-color: rgba(74,222,128,.35);
}

[data-theme=dark] .btn-secondary{background:#1e293b;border-color:rgba(148,163,184,.3);color:#f1f5f9;}
[data-theme=dark] .btn-secondary:hover:not(:disabled){background:#334155;border-color:rgba(148,163,184,.5);}

[data-theme=dark] .alert.warning {
  background: rgba(120,53,15,.3);
  border-color: rgba(251,191,36,.35);
  color: #fcd34d;
}

.alert strong {
  display: block;
  margin-bottom: 0.25rem;
}

.alert p {
  margin: 0;
  font-size: 13px;
}

[data-theme=dark] .alert.warning {
  background: rgba(251,191,36,.14);
  border-color: rgba(251,191,36,.26);
  color: var(--color-warning);
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  .account-main {
    grid-template-columns: 1fr;
  }
}
</style>
