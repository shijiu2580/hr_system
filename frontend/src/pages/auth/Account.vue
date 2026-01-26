<template>
  <div class="account-page">
    <section class="hero-panel">
      <div class="hero-main">
        <div class="avatar-large" v-if="!avatarUrl">{{ avatarInitials }}</div>
        <img v-else :src="avatarUrl" alt="头像" class="avatar-large-img" />
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
                    <CustomSelect v-model="profile.gender" :options="genderOptions" placeholder="未选择" />
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
                    <label>婚姻状况</label>
                    <CustomSelect v-model="profile.marital_status" :options="maritalOptions" placeholder="未选择" />
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
                      <CustomSelect v-model="profile.blood_type" :options="bloodTypeOptions" placeholder="未选择" />
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
                <div class="assets-grid is-horizontal">
                  <!-- 头像 -->
                  <div class="asset-item">
                    <div class="asset-info-row">
                      <label class="asset-label">头像</label>
                    </div>
                    <div class="asset-info-row">
                      <a v-if="profile.avatar" :href="profile.avatar" target="_blank" class="link-view">查看</a>
                      <span v-else class="text-muted">未上传</span>
                    </div>
                    <div class="file-upload-wrapper">
                      <label class="btn-upload">
                        选择文件
                        <input type="file" accept="image/*" @change="onFileChange('avatar', $event)" />
                      </label>
                      <span class="file-name" :title="selectedFiles.avatar?.name">{{ selectedFiles.avatar?.name || '未选择任何文件' }}</span>
                    </div>
                  </div>

                  <!-- 身份证人像面 -->
                  <div class="asset-item">
                    <div class="asset-info-row">
                      <label class="asset-label">身份证人像面</label>
                    </div>
                    <div class="asset-info-row">
                      <a v-if="profile.id_card_front" :href="profile.id_card_front" target="_blank" class="link-view">查看</a>
                      <span v-else class="text-muted">未上传</span>
                    </div>
                    <div class="file-upload-wrapper">
                      <label class="btn-upload">
                        选择文件
                        <input type="file" accept="image/*" @change="onFileChange('id_card_front', $event)" />
                      </label>
                      <span class="file-name" :title="selectedFiles.id_card_front?.name">{{ selectedFiles.id_card_front?.name || '未选择任何文件' }}</span>
                    </div>
                  </div>

                  <!-- 身份证国徽面 -->
                  <div class="asset-item">
                    <div class="asset-info-row">
                      <label class="asset-label">身份证国徽面</label>
                    </div>
                    <div class="asset-info-row">
                      <a v-if="profile.id_card_back" :href="profile.id_card_back" target="_blank" class="link-view">查看</a>
                      <span v-else class="text-muted">未上传</span>
                    </div>
                    <div class="file-upload-wrapper">
                      <label class="btn-upload">
                        选择文件
                        <input type="file" accept="image/*" @change="onFileChange('id_card_back', $event)" />
                      </label>
                      <span class="file-name" :title="selectedFiles.id_card_back?.name">{{ selectedFiles.id_card_back?.name || '未选择任何文件' }}</span>
                    </div>
                  </div>
                </div>
              </template>

              <div class="actions actions-inline">
                <button
                  type="submit"
                  class="btn-primary btn-full"
                  :disabled="!profileDirty || profileLoading || hasProfileErrors"
                  :aria-disabled="!profileDirty || profileLoading || hasProfileErrors"
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
import CustomSelect from '../../components/CustomSelect.vue';

const auth = useAuthStore();
const router = useRouter();

const activeTab = ref('basic'); // 'basic', 'detail', 'assets', 'security'
const tabs = [
  { id: 'basic', label: '基础资料' },
  { id: 'detail', label: '详细档案' },
  { id: 'assets', label: '资产/证件' },
  { id: 'security', label: '安全设置' }
];

const genderOptions = [
  { value: '', label: '未选择' },
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'other', label: '其他' }
];

const maritalOptions = [
  { value: '', label: '未选择' },
  { value: 'single', label: '未婚' },
  { value: 'married', label: '已婚' },
  { value: 'divorced', label: '离异' }
];

const bloodTypeOptions = [
  { value: '', label: '未选择' },
  { value: 'A', label: 'A' },
  { value: 'B', label: 'B' },
  { value: 'O', label: 'O' },
  { value: 'AB', label: 'AB' },
  { value: 'other', label: '其他' }
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

const avatarUrl = computed(() => {
  // 优先使用 profile 中的头像（员工详情接口返回的）
  if (profile.avatar) return profile.avatar;
  // 其次使用 auth.user 中的头像（/auth/me/ 接口返回的）
  if (auth.user?.avatar) return auth.user.avatar;
  return null;
});

const avatarInitials = computed(()=> {
  const base = profile.name || auth.user?.username || '';
  if(!base) return '?';
  const trimmed = String(base).trim();
  if(!trimmed) return '?';
  // 只显示第一个字
  return trimmed.charAt(0).toUpperCase();
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
  'phone','email','address','id_card','marital_status',
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
const hasProfileErrors = computed(()=> !!(nameError.value || phoneError.value || emergencyPhoneError.value || emailError.value || idCardError.value || addressError.value));

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
}

/* Hero Section */
.hero-panel {
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.hero-main {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex: 1;
}

.avatar-large {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  box-shadow: var(--shadow-sm);
}

.avatar-large-img {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  object-fit: cover;
  box-shadow: var(--shadow-sm);
}

.hero-text-block {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.hero-title-row h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.hero-subtitle {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.hero-meta-line {
  margin: 0;
  font-size: 12px;
  color: var(--color-text-secondary);
  opacity: 0.8;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 150px;
  border-left: 1px solid var(--color-border);
  padding-left: 1.5rem;
}

.hero-item-label {
  display: block;
  font-size: 11px;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  letter-spacing: 0.5px;
}

.hero-item-value {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.badge.admin {
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  font-size: 11px;
  background: var(--color-primary);
  color: #fff;
  opacity: 0.9;
}

/* Tabs */
.tabs-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 1px;
}

.tab-btn {
  padding: 0.6rem 1rem;
  background: transparent;
  border: none;
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: var(--transition);
  font-weight: 500;
}

.tab-btn:hover {
  background: var(--color-surface-alt);
  color: var(--color-text);
}

.tab-btn.active {
  background: var(--color-primary);
  color: #fff;
  box-shadow: var(--shadow-sm);
}

/* Layout */
.account-container {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 1.5rem;
  align-items: start;
}

.account-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (max-width: 900px) {
  .account-container {
    grid-template-columns: 1fr;
  }
}

/* Card */
.card-profile h3,
.card-password h3 {
  margin: 0 0 1.25rem;
  padding-bottom: 0.75rem;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
}

/* Forms */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
}

.required {
  color: var(--color-danger);
  margin-left: 2px;
}

.actions {
  margin-top: 1.5rem;
  display: flex;
  gap: 1rem;
}

.btn-primary, .btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  height: 36px;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-surface-alt);
  border-color: var(--color-border-strong);
}

.btn-full {
  width: 100%;
}

/* Stat Card */
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  box-shadow: var(--shadow-sm);
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  text-transform: uppercase;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text);
}

.progress {
  height: 6px;
  background: var(--color-surface-alt);
  border-radius: 99px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.progress-bar {
  height: 100%;
  background: var(--color-success);
}

/* Assets & Documents */
.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.asset-item {
  background: var(--color-surface-alt);
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
}

.asset-info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.asset-label {
  font-weight: 500;
  color: var(--color-text);
  font-size: 14px;
}

.file-upload-wrapper {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: var(--transition);
}

.file-upload-wrapper:hover {
  border-color: var(--color-primary);
}

.btn-upload {
  background: var(--color-surface-alt);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  padding: 0.25rem 0.5rem;
  font-size: 12px;
  border-radius: 4px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.btn-upload:hover {
  background: var(--color-border);
}

/* Input file hidden but clickable via parent label if configured, but here structure is button>input */
.btn-upload input[type="file"] {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.file-name {
  font-size: 12px;
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 150px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.message {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 13px;
  margin: 0;
}

.message.error {
  background: #fef2f2;
  color: var(--color-danger);
  border: 1px solid #fee2e2;
}

.message.success {
  background: #f0fdf4;
  color: var(--color-success);
  border: 1px solid #dcfce7;
}

/* Dark mode tweaks handled by variables automatically */
</style>
