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

    <div class="tabs-header" role="tablist">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        :aria-selected="(activeTab === tab.id).toString()"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="account-container">
      <div class="account-content">
        <transition name="fade-tab" mode="out-in">
          <div :key="activeTab">
            <form v-if="activeTab !== 'security'" class="card card-profile" @submit.prevent="saveProfile" novalidate>
              <h3>{{ tabs.find(t => t.id === activeTab)?.label || '资料设置' }}</h3>

              <template v-if="activeTab === 'basic'">
                <div class="grid">
                  <div class="form-group">
                    <label>姓名</label>
                    <input v-model.trim="profile.name" disabled />
                  </div>
                  <div class="form-group">
                    <label>英文名</label>
                    <input v-model.trim="profile.english_name" maxlength="50" placeholder="例如：John Doe" />
                  </div>
                  <div class="form-group">
                    <label>性别</label>
                    <select v-model="profile.gender">
                      <option value="">未选择</option>
                      <option value="male">男</option>
                      <option value="female">女</option>
                      <option value="other">其他</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>出生日期</label>
                    <input type="date" v-model="profile.birth_date" />
                  </div>
                  <div class="form-group">
                    <label>手机号</label>
                    <input type="tel" v-model.trim="profile.phone" disabled />
                  </div>
                  <div class="form-group">
                    <label>联系邮箱</label>
                    <input type="email" v-model.trim="profile.email" disabled />
                  </div>
                  <div class="form-group" :class="{ invalid: !!idCardError }">
                    <label>身份证号</label>
                    <input v-model.trim="profile.id_card" maxlength="18" placeholder="18位身份证号" @input="validateProfile" />
                    <span v-if="idCardError" class="hint error-hint">{{ idCardError }}</span>
                  </div>
                  <div class="form-group">
                    <label>护照号</label>
                    <input v-model.trim="profile.passport_no" maxlength="30" />
                  </div>
                  <div class="form-group">
                    <label>婚姻状况</label>
                    <select v-model="profile.marital_status">
                      <option value="">未选择</option>
                      <option value="single">未婚</option>
                      <option value="married">已婚</option>
                      <option value="divorced">离异</option>
                    </select>
                  </div>
                  <div class="form-group address-group" :class="{ invalid: !!addressError }">
                    <label>联系地址</label>
                    <input v-model.trim="profile.address" placeholder="居住地址" @input="validateProfile" />
                    <span v-if="addressError" class="hint error-hint">{{ addressError }}</span>
                  </div>
                </div>
              </template>

              <template v-else-if="activeTab === 'detail'">
                <fieldset class="fieldset">
                  <legend>户籍与个人</legend>
                  <div class="grid">
                    <div class="form-group">
                      <label>国籍</label>
                      <input v-model.trim="profile.nationality" />
                    </div>
                    <div class="form-group">
                      <label>籍贯</label>
                      <input v-model.trim="profile.native_place" />
                    </div>
                    <div class="form-group">
                      <label>户口所在地</label>
                      <input v-model.trim="profile.hukou_location" />
                    </div>
                    <div class="form-group">
                      <label>户口类型</label>
                      <input v-model.trim="profile.hukou_type" />
                    </div>
                    <div class="form-group address-group">
                      <label>户口地址</label>
                      <input v-model.trim="profile.hukou_address" />
                    </div>
                    <div class="form-group">
                      <label>民族</label>
                      <input v-model.trim="profile.ethnicity" />
                    </div>
                    <div class="form-group">
                      <label>政治面貌</label>
                      <input v-model.trim="profile.political_status" />
                    </div>
                    <div class="form-group">
                      <label>入党/团时间</label>
                      <input type="date" v-model="profile.party_date" />
                    </div>
                    <div class="form-group">
                      <label>血型</label>
                      <select v-model="profile.blood_type">
                        <option value="">未选择</option>
                        <option value="A">A</option>
                        <option value="B">B</option>
                        <option value="O">O</option>
                        <option value="AB">AB</option>
                        <option value="other">其他</option>
                      </select>
                    </div>
                  </div>
                </fieldset>

                <fieldset class="fieldset">
                  <legend>紧急联系人</legend>
                  <div class="grid">
                    <div class="form-group">
                      <label>联系人</label>
                      <input v-model.trim="profile.emergency_contact" />
                    </div>
                    <div class="form-group">
                      <label>关系</label>
                      <input v-model.trim="profile.emergency_relation" />
                    </div>
                    <div class="form-group" :class="{ invalid: !!emergencyPhoneError }">
                      <label>联系电话</label>
                      <input v-model.trim="profile.emergency_phone" placeholder="11位手机号" @input="validateProfile" />
                      <span v-if="emergencyPhoneError" class="hint error-hint">{{ emergencyPhoneError }}</span>
                    </div>
                  </div>
                </fieldset>

                <fieldset class="fieldset">
                  <legend>教育与银行</legend>
                  <div class="grid">
                    <div class="form-group">
                      <label>学历</label>
                      <input v-model.trim="profile.education" />
                    </div>
                    <div class="form-group">
                      <label>学校类型</label>
                      <input v-model.trim="profile.school_type" />
                    </div>
                    <div class="form-group">
                      <label>学校名称</label>
                      <input v-model.trim="profile.school_name" />
                    </div>
                    <div class="form-group">
                      <label>专业</label>
                      <input v-model.trim="profile.major" />
                    </div>
                    <div class="form-group">
                      <label>毕业时间</label>
                      <input type="date" v-model="profile.graduation_date" />
                    </div>
                    <div class="form-group">
                      <label>工资卡</label>
                      <input v-model.trim="profile.bank_card_no" />
                    </div>
                    <div class="form-group">
                      <label>报销卡</label>
                      <input v-model.trim="profile.expense_card_no" />
                    </div>
                  </div>
                </fieldset>

                <fieldset class="fieldset">
                  <legend>设备与任职</legend>
                  <div class="grid">
                    <div class="form-group">
                      <label>设备信息</label>
                      <input v-model.trim="profile.computer_info" placeholder="设备型号/配置" />
                    </div>
                    <div class="form-group">
                      <label>设备品牌</label>
                      <input v-model.trim="profile.computer_brand" />
                    </div>
                    <div class="form-group" aria-live="polite">
                      <label>部门</label>
                      <input :value="profile.department_name" disabled />
                    </div>
                    <div class="form-group" aria-live="polite">
                      <label>职位</label>
                      <input :value="profile.position_name" disabled />
                    </div>
                    <div class="form-group" aria-live="polite">
                      <label>入职时间</label>
                      <input :value="profile.hire_date" disabled />
                    </div>
                    <div class="form-group" aria-live="polite">
                      <label>在职状态</label>
                      <input :value="profile.onboard_status" disabled />
                    </div>
                  </div>
                </fieldset>
              </template>

              <template v-else>
                <div class="grid">
                  <div class="form-group">
                    <label>头像</label>
                    <div class="file-row">
                      <a v-if="profile.avatar" :href="profile.avatar" target="_blank" rel="noreferrer">查看</a>
                      <span v-else class="muted">未上传</span>
                      <input type="file" accept="image/*" @change="onFileChange('avatar', $event)" disabled />
                    </div>
                    <small class="hint" v-if="selectedFiles.avatar">已选择：{{ selectedFiles.avatar.name }}</small>
                  </div>
                  <div class="form-group">
                    <label>身份证人像面</label>
                    <div class="file-row">
                      <a v-if="profile.id_card_front" :href="profile.id_card_front" target="_blank" rel="noreferrer">查看</a>
                      <span v-else class="muted">未上传</span>
                      <input type="file" accept="image/*" @change="onFileChange('id_card_front', $event)" disabled />
                    </div>
                    <small class="hint" v-if="selectedFiles.id_card_front">已选择：{{ selectedFiles.id_card_front.name }}</small>
                  </div>
                  <div class="form-group">
                    <label>身份证国徽面</label>
                    <div class="file-row">
                      <a v-if="profile.id_card_back" :href="profile.id_card_back" target="_blank" rel="noreferrer">查看</a>
                      <span v-else class="muted">未上传</span>
                      <input type="file" accept="image/*" @change="onFileChange('id_card_back', $event)" disabled />
                    </div>
                    <small class="hint" v-if="selectedFiles.id_card_back">已选择：{{ selectedFiles.id_card_back.name }}</small>
                  </div>
                </div>
              </template>

              <div class="actions actions-inline">
                <button
                  type="submit"
                  class="btn-primary btn-full"
                  :disabled="!profileDirty || profileLoading || hasProfileErrors"
                  :aria-disabled="(!profileDirty || profileLoading || hasProfileErrors).toString()"
                >
                  <span v-if="profileLoading" class="spinner" aria-hidden="true"></span>
                  {{ profileLoading ? '保存中...' : '保存资料' }}
                </button>
                <button
                  type="button"
                  class="btn-secondary btn-full"
                  :disabled="!profileDirty || profileLoading"
                  v-if="profileDirty"
                  @click="resetProfile"
                >重置</button>
              </div>

              <transition name="fade-msg">
                <p v-if="profileError" class="message error" aria-live="assertive">{{ profileError }}</p>
              </transition>
              <transition name="fade-msg">
                <p v-if="profileSuccess" class="message success" aria-live="polite">{{ profileSuccess }}</p>
              </transition>
            </form>

            <section v-else class="card card-password">
              <h3>密码安全</h3>
              <div v-if="auth.mustChangePassword" class="alert warning">
                <strong>首次登录必须修改密码</strong>
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
                  <button type="submit" class="btn-primary btn-full" :disabled="passwordLoading">
                    <span v-if="passwordLoading" class="spinner"></span>
                    {{ passwordLoading ? '处理中...' : '修改密码' }}
                  </button>
                  <button type="button" class="btn-secondary btn-full" :disabled="passwordLoading || !hasPasswordInput" @click="resetPasswordFields">清空</button>
                </div>

                <transition name="fade-msg">
                  <p v-if="passwordError" class="message error">{{ passwordError }}</p>
                </transition>
                <transition name="fade-msg">
                  <p v-if="passwordSuccess" class="message success">{{ passwordSuccess }}</p>
                </transition>
              </form>
            </section>
          </div>
        </transition>
      </div>

      <div class="account-sidebar">
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
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, computed, reactive, onBeforeUnmount } from 'vue';
import { useAuthStore } from '../../stores/auth';
import { useRouter } from 'vue-router';
import api from '../../utils/api';

const auth = useAuthStore();
const router = useRouter();

const activeTab = ref('basic'); // 'basic', 'detail', 'assets', 'security'
const tabs = [
  { id: 'basic', label: '基础资料' },
  { id: 'detail', label: '详细档案' },
  { id: 'assets', label: '资产/证件' },
  { id: 'security', label: '安全设置' }
];

// 个人资料（员工档案 - 全字段）
const profile = reactive({
  employee_id: '',
  name: '',
  english_name: '',
  gender: '',
  birth_date: '',
  phone: '',
  email: '',
  address: '',
  id_card: '',
  passport_no: '',
  marital_status: 'single',

  // 户籍信息
  nationality: '中国',
  native_place: '',
  hukou_location: '',
  hukou_type: '',
  hukou_address: '',
  ethnicity: '汉族',
  political_status: '',
  party_date: '',
  blood_type: '',

  // 紧急联系人
  emergency_contact: '',
  emergency_relation: '',
  emergency_phone: '',

  // 教育信息
  education: '',
  school_type: '',
  school_name: '',
  major: '',
  graduation_date: '',

  // 银行信息
  bank_card_no: '',
  expense_card_no: '',

  // 设备信息
  computer_info: '',
  computer_brand: '',

  // 任职信息（只读展示）
  department_name: '',
  position_name: '',
  hire_date: '',
  onboard_status: '',

  // 证件/附件（URL）
  avatar: null,
  id_card_front: null,
  id_card_back: null,
});

const selectedFiles = reactive({
  avatar: null,
  id_card_front: null,
  id_card_back: null,
});

const profileLoading = ref(false);
const profileError = ref(null);
const profileSuccess = ref(null);
const nameError = ref(null);
const phoneError = ref(null);
const emailError = ref(null);
const addressError = ref(null);
const idCardError = ref(null);
const emergencyPhoneError = ref(null);

const profileSnapshot = ref(null);

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
  if(profile.name) return profile.name;
  if(!auth.user) return '未登录';
  const { first_name, last_name, username } = auth.user;
  if(first_name || last_name){
    return `${last_name || ''}${first_name || ''}`.trim();
  }
  return username;
});

const avatarInitials = computed(()=> {
  const base = profile.name || auth.user?.username || '';
  if(!base) return '?';
  const trimmed = String(base).trim();
  if(!trimmed) return '?';
  // 中文优先取前 2 字；英文取前 2 个字母
  return trimmed.slice(0,2).toUpperCase();
});

function formatDate(value){
  if(!value) return '--';
  try { return new Date(value).toLocaleString(); }
  catch { return value; }
}

const lastLoginText = computed(()=> formatDate(auth.user?.last_login));
const joinedText = computed(()=> formatDate(auth.user?.date_joined));

const emailBoundText = computed(()=> profile.email ? '已绑定' : '未绑定');
const emailBoundClass = computed(()=> profile.email ? 'stat-positive' : 'stat-warning');
const emailBoundHint = computed(()=> profile.email ? profile.email : '绑定邮箱可用于找回密码');

const completionFields = [
  'name','phone','email','address',
  'id_card','emergency_contact','emergency_phone',
  'education','school_name','major',
  'bank_card_no','computer_info'
];
const profileCompletion = computed(()=> {
  const total = completionFields.length;
  const filled = completionFields.reduce((acc, k) => acc + (profile[k] ? 1 : 0), 0);
  return Math.round((filled / total) * 100);
});

const passwordStatus = computed(()=> auth.mustChangePassword ? '需更新' : '安全');
const passwordStatusClass = computed(()=> auth.mustChangePassword ? 'stat-warning' : 'stat-positive');
const passwordStatusHint = computed(()=> auth.mustChangePassword ? '系统要求尽快更新密码' : '建议定期更换密码');

// 控制初始化时不触发 dirty
const isInitializing = ref(true);

const hasSelectedFiles = computed(()=> {
  return Boolean(
    selectedFiles.avatar ||
    selectedFiles.id_card_front ||
    selectedFiles.id_card_back
  );
});

const editableFields = [
  'name','english_name','gender','birth_date',
  'phone','email','address','id_card','passport_no','marital_status',
  'nationality','native_place','hukou_location','hukou_type','hukou_address',
  'ethnicity','political_status','party_date','blood_type',
  'emergency_contact','emergency_relation','emergency_phone',
  'education','school_type','school_name','major','graduation_date',
  'bank_card_no','expense_card_no',
  'computer_info','computer_brand',
];

function buildEditableSnapshot(){
  const obj = {};
  editableFields.forEach((k) => { obj[k] = profile[k] ?? ''; });
  return obj;
}

const profileDirty = computed(()=> {
  if(isInitializing.value) return false;
  if(!profileSnapshot.value) return false;
  const now = JSON.stringify(buildEditableSnapshot());
  const old = JSON.stringify(profileSnapshot.value);
  return now !== old || hasSelectedFiles.value;
});

onMounted(() => {
  loadMyEmployee();
});

async function loadMyEmployee(){
  // 先用 auth 的 email 兜底
  profile.email = auth.user?.email || '';
  try {
    const resp = await api.get('/employees/me/', { noCache: true, skipDuplicateCheck: true });
    if(resp.success && resp.data){
      const emp = resp.data;
      profile.employee_id = emp.employee_id || '';
      profile.name = emp.name || '';
      profile.english_name = emp.english_name || '';
      profile.gender = emp.gender || '';
      profile.birth_date = emp.birth_date || '';
      profile.phone = emp.phone || '';
      profile.email = emp.email || profile.email;
      profile.address = emp.address || '';
      profile.id_card = emp.id_card || '';
      profile.passport_no = emp.passport_no || '';
      profile.marital_status = emp.marital_status || 'single';

      profile.nationality = emp.nationality || '中国';
      profile.native_place = emp.native_place || '';
      profile.hukou_location = emp.hukou_location || '';
      profile.hukou_type = emp.hukou_type || '';
      profile.hukou_address = emp.hukou_address || '';
      profile.ethnicity = emp.ethnicity || '汉族';
      profile.political_status = emp.political_status || '';
      profile.party_date = emp.party_date || '';
      profile.blood_type = emp.blood_type || '';

      profile.emergency_contact = emp.emergency_contact || '';
      profile.emergency_relation = emp.emergency_relation || '';
      profile.emergency_phone = emp.emergency_phone || '';

      profile.education = emp.education || '';
      profile.school_type = emp.school_type || '';
      profile.school_name = emp.school_name || '';
      profile.major = emp.major || '';
      profile.graduation_date = emp.graduation_date || '';

      profile.bank_card_no = emp.bank_card_no || '';
      profile.expense_card_no = emp.expense_card_no || '';
      profile.computer_info = emp.computer_info || '';
      profile.computer_brand = emp.computer_brand || '';

      profile.department_name = emp.department?.name || '';
      profile.position_name = emp.position?.name || '';
      profile.hire_date = emp.hire_date || '';
      profile.onboard_status = emp.onboard_status || '';

      profile.avatar = emp.avatar || null;
      profile.id_card_front = emp.id_card_front || null;
      profile.id_card_back = emp.id_card_back || null;

      profileSnapshot.value = buildEditableSnapshot();
    }
  } finally {
    setTimeout(() => {
      isInitializing.value = false;
      validateProfile();
    }, 0);
  }
}

function validateProfile(){
  // 修正：不可编辑字段（姓名/身份证）不再前端强制阻断，假设服务端已有数据
  nameError.value = null; // !profile.name ? '必填' : (profile.name.length > 50 ? '长度超过 50' : null);

  if(profile.phone){
    phoneError.value = /^1[3-9]\d{9}$/.test(profile.phone) ? null : '请输入有效的11位手机号';
  } else {
    phoneError.value = null;
  }
  if(profile.emergency_phone){
    emergencyPhoneError.value = /^1[3-9]\d{9}$/.test(profile.emergency_phone) ? null : '请输入有效的11位手机号';
  } else {
    emergencyPhoneError.value = null;
  }
  if(profile.email){
    const emailPattern = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
    emailError.value = emailPattern.test(profile.email) ? null : '邮箱格式不正确';
  } else {
    emailError.value = null;
  }

  idCardError.value = null; // 不再校验不可编辑的身份证

  addressError.value = profile.address && profile.address.length > 200 ? '长度超过 200' : null;
}
const hasProfileErrors = computed(()=> nameError.value || phoneError.value || emergencyPhoneError.value || emailError.value || idCardError.value || addressError.value);

function onFileChange(key, evt){
  const file = evt?.target?.files?.[0] || null;
  selectedFiles[key] = file;
}

function resetProfile(){
  if(profileSnapshot.value){
    editableFields.forEach((k) => {
      profile[k] = profileSnapshot.value[k] ?? '';
    });
  }
  selectedFiles.avatar = null;
  selectedFiles.id_card_front = null;
  selectedFiles.id_card_back = null;
  profileError.value = null; profileSuccess.value = null;
  validateProfile();
}

async function saveProfile() {
  profileError.value = null;
  profileSuccess.value = null;
  profileLoading.value = true;

  try {
    validateProfile();
    if(hasProfileErrors.value){
      profileError.value = '请先修正表单错误';
      return;
    }

    const payload = buildEditableSnapshot();

    let resp;
    if(hasSelectedFiles.value){
      const form = new FormData();
      Object.entries(payload).forEach(([k, v]) => {
        if(v === null || v === undefined) return;
        form.append(k, String(v));
      });
      if(selectedFiles.avatar) form.append('avatar', selectedFiles.avatar);
      if(selectedFiles.id_card_front) form.append('id_card_front', selectedFiles.id_card_front);
      if(selectedFiles.id_card_back) form.append('id_card_back', selectedFiles.id_card_back);

      resp = await api.patch('/employees/me/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
        skipDuplicateCheck: true,
      });
    } else {
      // 更新员工档案（JSON）
      resp = await api.patch('/employees/me/', payload);
    }

    if (resp.success) {
      profileSuccess.value = '资料已保存';
      // 同步快照
      profileSnapshot.value = buildEditableSnapshot();

      // 更新页面展示用的 URL（上传后服务端会返回新 URL）
      if(resp.data){
        const emp = resp.data;
        profile.avatar = emp.avatar || profile.avatar;
        profile.id_card_front = emp.id_card_front || profile.id_card_front;
        profile.id_card_back = emp.id_card_back || profile.id_card_back;
      }

      selectedFiles.avatar = null;
      selectedFiles.id_card_front = null;
      selectedFiles.id_card_back = null;

      // 同步更新 User.email（用于登录/通知等），不强制写入 first_name/last_name
      try {
        await api.post('/auth/update_profile/', { email: profile.email });
      } catch(_){ }

      try { await auth.fetchMe?.(); } catch(_) {}
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
  background: radial-gradient(circle at 10% 20%, rgba(79, 70, 229, 0.08), transparent 30%),
              radial-gradient(circle at 80% 0%, rgba(14, 165, 233, 0.08), transparent 30%),
              #f8fafc;
  border-radius: 18px;
}

.hero-panel {
  margin-bottom: 1.25rem;
  padding: 1.35rem 1.6rem;
  border-radius: 14px;
  background: linear-gradient(135deg, #eef2ff, #e0f2fe);
  border: 1px solid rgba(99, 102, 241, 0.35);
  color: #0f172a;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.2rem;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.12);
}

.hero-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1 1 0;
}

.avatar-large {
  width: 64px;
  height: 64px;
  border-radius: 14px;
  background: #4f46e5;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 700;
  box-shadow: 0 10px 25px rgba(79, 70, 229, 0.35);
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
  font-weight: 700;
  color: #0f172a;
}

.hero-subtitle,
.hero-meta-line {
  margin: 0;
  font-size: 13px;
  color: #475569;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  font-size: 13px;
  min-width: 140px;
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

.tabs-header {
  display: flex;
  gap: 0.5rem;
  margin: 0 0 1rem;
  padding: 0.35rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
  backdrop-filter: blur(6px);
  overflow-x: auto;
}

.tab-btn {
  padding: 0.65rem 1.4rem;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  color: #475569;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  color: #312e81;
  background: #eef2ff;
}

.tab-btn.active {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: #fff;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.35);
}

.account-container {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 1.25rem;
  align-items: start;
}

.account-content {
  min-width: 0;
}

.account-sidebar {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

@media (max-width: 900px) {
  .account-container {
    grid-template-columns: 1fr;
  }
  .account-sidebar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

.card {
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 12px;
  padding: 1.35rem 1.5rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

.card:hover {
  border-color: rgba(99, 102, 241, 0.35);
  box-shadow: 0 12px 36px rgba(15, 23, 42, 0.12);
}

.card-profile h3,
.card-password h3 {
  margin: 0 0 1.25rem;
  padding-bottom: 0.75rem;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  border-bottom: 1px solid rgba(148, 163, 184, 0.3);
}

.stat-card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 12px;
  padding: 1rem 1.15rem;
  min-height: 110px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.35rem;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(4px);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.12);
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.stat-main {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.1;
}

.progress {
  height: 7px;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(135deg, #22c55e, #16a34a);
}

.stat-card small {
  color: #64748b;
  font-size: 12px;
}

.stat-positive {
  background: #f8fafc;
}

.stat-warning {
  background: #fff7ed;
}

.badge.admin {
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 12px;
  line-height: 1.2;
  background: rgba(79, 70, 229, 0.12);
  color: #4338ca;
  border: 1px solid rgba(79, 70, 229, 0.3);
}

.hero-panel .badge.admin {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: #fff;
}

.form-stack {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  align-items: start;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group.invalid input,
.form-group.invalid select {
  border-color: #ef4444;
  background: #fef2f2;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}

.required {
  color: var(--color-danger);
}

.hint {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.error-hint {
  color: #b91c1c;
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
  transition: background 0.2s, box-shadow 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #4338ca;
  box-shadow: 0 10px 20px rgba(67, 56, 202, 0.25);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.625rem 1rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  background: #fff;
  color: #475569;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background: #f8fafc;
  border-color: rgba(148, 163, 184, 0.6);
}

.btn-secondary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.message {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 13px;
  margin: 0;
}

.message.error {
  background: rgba(254, 242, 242, 0.8);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.message.success {
  background: rgba(240, 253, 244, 0.8);
  color: #15803d;
  border: 1px solid rgba(74, 222, 128, 0.5);
}

.spinner {
  width: 16px;
  height: 16px;
  border: 3px solid #fff;
  border-right-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.65s linear infinite;
  margin-right: 6px;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-msg-enter-active,
.fade-msg-leave-active {
  transition: opacity 0.35s;
}

.fade-msg-enter-from,
.fade-msg-leave-to {
  opacity: 0;
}

.fade-tab-enter-active,
.fade-tab-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-tab-enter-from,
.fade-tab-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.fieldset {
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 12px;
  padding: 1rem;
  margin: 0 0 1rem;
  background: rgba(248, 250, 252, 0.75);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.fieldset legend {
  padding: 0 0.5rem;
  font-size: 12px;
  color: #64748b;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.file-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.muted {
  font-size: 12px;
  color: #94a3b8;
}

.alert {
  padding: 0.85rem 1rem;
  border-radius: 10px;
  border: 1px solid rgba(251, 191, 36, 0.3);
  background: rgba(251, 191, 36, 0.12);
  color: #92400e;
}

.alert strong {
  display: block;
  margin-bottom: 0.25rem;
}

.alert p {
  margin: 0;
  font-size: 13px;
}

@media (max-width: 640px) {
  .tabs-header { flex-wrap: wrap; }
  .account-container { grid-template-columns: 1fr; }
}

[data-theme="dark"] .account-page {
  background: radial-gradient(circle at 10% 20%, rgba(79, 70, 229, 0.12), transparent 30%),
              radial-gradient(circle at 80% 0%, rgba(14, 165, 233, 0.12), transparent 30%),
              #0f172a;
}

[data-theme="dark"] .hero-panel {
  background: linear-gradient(135deg, #0f172a, #111827);
  border-color: rgba(99, 102, 241, 0.25);
  color: #e2e8f0;
}

[data-theme="dark"] .hero-title-row h1 { color: #e2e8f0; }
[data-theme="dark"] .hero-subtitle,
[data-theme="dark"] .hero-meta-line { color: #cbd5e1; }
[data-theme="dark"] .hero-item-value { color: #e2e8f0; }
[data-theme="dark"] .avatar-large { background: #6366f1; }

[data-theme="dark"] .tabs-header {
  background: rgba(30, 41, 59, 0.8);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

[data-theme="dark"] .tab-btn { color: #cbd5e1; }
[data-theme="dark"] .tab-btn:hover {
  color: #e2e8f0;
  background: rgba(99, 102, 241, 0.15);
}
[data-theme="dark"] .tab-btn.active {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff;
}

[data-theme="dark"] .card,
[data-theme="dark"] .stat-card {
  background: rgba(30, 41, 59, 0.9);
  border-color: rgba(148, 163, 184, 0.3);
  color: #e2e8f0;
}

[data-theme="dark"] .stat-label { color: #cbd5e1; }
[data-theme="dark"] .stat-value { color: #f1f5f9; }

[data-theme="dark"] .form-group label { color: #cbd5e1; }
[data-theme="dark"] .form-group input,
[data-theme="dark"] .form-group select {
  background: #1e293b;
  border-color: rgba(148, 163, 184, 0.3);
  color: #f1f5f9;
}

[data-theme="dark"] .form-group input:focus,
[data-theme="dark"] .form-group select:focus {
  background: #334155;
  border-color: rgba(148, 163, 184, 0.5);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

[data-theme="dark"] .hint,
[data-theme="dark"] .muted { color: #94a3b8; }

[data-theme="dark"] .btn-secondary {
  background: #1e293b;
  border-color: rgba(148, 163, 184, 0.3);
  color: #f1f5f9;
}

[data-theme="dark"] .btn-secondary:hover:not(:disabled) {
  background: #334155;
  border-color: rgba(148, 163, 184, 0.5);
}

[data-theme="dark"] .message.error {
  background: rgba(127, 29, 29, 0.3);
  color: #fca5a5;
  border-color: rgba(248, 113, 113, 0.35);
}

[data-theme="dark"] .message.success {
  background: rgba(20, 83, 45, 0.3);
  color: #86efac;
  border-color: rgba(74, 222, 128, 0.35);
}

[data-theme="dark"] .alert {
  background: rgba(251, 191, 36, 0.14);
  border-color: rgba(251, 191, 36, 0.26);
  color: #fcd34d;
}
</style>
