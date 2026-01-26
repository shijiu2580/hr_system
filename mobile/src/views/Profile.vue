<template>
  <div class="page-container">
    <van-nav-bar title="完善资料" left-arrow @click-left="$router.back()" />

    <div class="form-container">
      <van-notice-bar
        v-if="rejectReason"
        color="#ee0a24"
        background="#ffece8"
        left-icon="info-o"
        :text="`审核未通过：${rejectReason}，请修改后重新提交`"
      />

      <van-form @submit="handleSubmit" ref="formRef">
        <!-- 基本信息 -->
        <div class="section-title">基本信息</div>
        <van-cell-group inset>
          <van-field v-model="form.name" label="姓名" placeholder="请输入" required
            :rules="[{ required: true, message: '请输入姓名' }]" />
          <van-field v-model="form.english_name" label="英文名" placeholder="请输入" />
          <van-field v-model="form.gender" is-link readonly label="性别" placeholder="请选择"
            @click="showGenderPicker = true" />
          <van-field v-model="form.birth_date" is-link readonly label="出生日期" placeholder="请选择"
            @click="showDatePicker = true" />
          <van-field v-model="form.id_card" label="证件号码" placeholder="身份证号" />

          <van-field v-model="form.phone" label="手机号码" type="tel" placeholder="请输入" required
            :rules="[{ required: true, message: '请输入手机号码' }, { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' }]" />
          <van-field v-model="form.email" label="电子邮箱" placeholder="请输入" readonly required
            :rules="[{ required: true, message: '请输入电子邮箱' }]" />
        </van-cell-group>

        <!-- 户籍信息 -->
        <div class="section-title">户籍信息</div>
        <van-cell-group inset>
          <van-field v-model="form.nationality" label="国籍(地区)" placeholder="请输入" />
          <van-field v-model="form.hukou_location" label="户籍所在地" placeholder="请输入" />
          <van-field v-model="form.hukou_type" is-link readonly label="户籍性质" placeholder="请选择"
            @click="showHukouTypePicker = true" />
          <van-field v-model="form.native_place" label="籍贯" placeholder="如：四川省/宜宾市" />
          <van-field v-model="form.hukou_address" label="户籍地址" type="textarea" rows="2" placeholder="请输入" />
          <van-field v-model="form.ethnicity" label="民族" placeholder="请输入" />
          <van-field v-model="form.blood_type" is-link readonly label="血型" placeholder="请选择"
            @click="showBloodTypePicker = true" />
          <van-field v-model="form.marital_status" is-link readonly label="婚姻状况" placeholder="请选择"
            @click="showMaritalPicker = true" />
          <van-field v-model="form.political_status" is-link readonly label="政治面貌" placeholder="请选择"
            @click="showPoliticalPicker = true" />
          <van-field v-model="form.party_date" is-link readonly label="入党/团日期" placeholder="请选择"
            @click="showPartyDatePicker = true" />
        </van-cell-group>

        <!-- 联系信息 -->
        <div class="section-title">联系信息</div>
        <van-cell-group inset>
          <van-field v-model="form.address" label="联系地址" type="textarea" rows="2" placeholder="请输入详细地址" />
        </van-cell-group>

        <!-- 紧急联系人 -->
        <div class="section-title">紧急联系人</div>
        <van-cell-group inset>
          <van-field v-model="form.emergency_contact" label="联系人姓名" placeholder="请输入" />
          <van-field v-model="form.emergency_relation" label="与本人关系" placeholder="如：父亲" />
          <van-field v-model="form.emergency_phone" label="联系电话" type="tel" placeholder="请输入" />
        </van-cell-group>

        <!-- 教育信息 -->
        <div class="section-title">教育信息</div>
        <van-cell-group inset>
          <van-field v-model="form.school_type" is-link readonly label="学校分类" placeholder="请选择"
            @click="showSchoolTypePicker = true" />
          <van-field v-model="form.school_name" label="毕业学校" placeholder="请输入" />
          <van-field v-model="form.major" label="专业" placeholder="请输入" />
          <van-field v-model="form.graduation_date" is-link readonly label="毕业时间" placeholder="请选择"
            @click="showGraduationDatePicker = true" />
          <van-field v-model="form.education" is-link readonly label="学历" placeholder="请选择"
            @click="showEducationPicker = true" />
        </van-cell-group>

        <!-- 银行信息 -->
        <div class="section-title">银行信息</div>
        <van-cell-group inset>
          <van-field v-model="form.bank_card_no" label="工资卡账号" placeholder="请输入" />
          <van-field v-model="form.expense_card_no" label="报销卡账号" placeholder="请输入" />
        </van-cell-group>

        <!-- 设备信息 -->
        <div class="section-title">设备信息</div>
        <van-cell-group inset>
          <van-field v-model="form.computer_info" is-link readonly label="电脑信息" placeholder="请选择"
            @click="showComputerInfoPicker = true" />
          <van-field v-model="form.computer_brand" label="电脑品牌" placeholder="请输入" />
        </van-cell-group>

        <!-- 证件上传 -->
        <div class="section-title">证件上传</div>
        <van-cell-group inset>
          <van-cell title="照片" required>
            <template #value>
              <van-uploader v-model="avatarList" :max-count="1"
                :after-read="(file) => uploadFile(file, 'avatar')" />
            </template>
          </van-cell>
          <van-cell title="身份证人像面">
            <template #value>
              <van-uploader v-model="idCardFrontList" :max-count="1"
                :after-read="(file) => uploadFile(file, 'id_card_front')" />
            </template>
          </van-cell>
          <van-cell title="身份证国徽面">
            <template #value>
              <van-uploader v-model="idCardBackList" :max-count="1"
                :after-read="(file) => uploadFile(file, 'id_card_back')" />
            </template>
          </van-cell>
        </van-cell-group>

        <div style="margin: 24px 16px;">
          <van-button round block type="primary" native-type="submit" :loading="loading">
            {{ rejectReason ? '重新提交' : '提交资料' }}
          </van-button>
        </div>
      </van-form>
    </div>

    <!-- 性别选择器 -->
    <van-popup v-model:show="showGenderPicker" position="bottom">
      <van-picker :columns="genderOptions" @confirm="onPickerConfirm('gender', $event)" @cancel="showGenderPicker = false" />
    </van-popup>

    <!-- 出生日期选择器 -->
    <van-popup v-model:show="showDatePicker" position="bottom">
      <van-date-picker v-model="birthDateValue" :min-date="new Date(1950, 0, 1)" :max-date="new Date(2010, 11, 31)"
        @confirm="onDateConfirm('birth_date', $event)" @cancel="showDatePicker = false" />
    </van-popup>

    <!-- 户籍性质选择器 -->
    <van-popup v-model:show="showHukouTypePicker" position="bottom">
      <van-picker :columns="hukouTypeOptions" @confirm="onPickerConfirm('hukou_type', $event)" @cancel="showHukouTypePicker = false" />
    </van-popup>

    <!-- 血型选择器 -->
    <van-popup v-model:show="showBloodTypePicker" position="bottom">
      <van-picker :columns="bloodTypeOptions" @confirm="onPickerConfirm('blood_type', $event)" @cancel="showBloodTypePicker = false" />
    </van-popup>

    <!-- 婚姻状况选择器 -->
    <van-popup v-model:show="showMaritalPicker" position="bottom">
      <van-picker :columns="maritalOptions" @confirm="onPickerConfirm('marital_status', $event)" @cancel="showMaritalPicker = false" />
    </van-popup>

    <!-- 政治面貌选择器 -->
    <van-popup v-model:show="showPoliticalPicker" position="bottom">
      <van-picker :columns="politicalOptions" @confirm="onPickerConfirm('political_status', $event)" @cancel="showPoliticalPicker = false" />
    </van-popup>

    <!-- 入党/团日期选择器 -->
    <van-popup v-model:show="showPartyDatePicker" position="bottom">
      <van-date-picker v-model="partyDateValue" :min-date="new Date(1950, 0, 1)" :max-date="new Date()"
        @confirm="onDateConfirm('party_date', $event)" @cancel="showPartyDatePicker = false" />
    </van-popup>

    <!-- 学校分类选择器 -->
    <van-popup v-model:show="showSchoolTypePicker" position="bottom">
      <van-picker :columns="schoolTypeOptions" @confirm="onPickerConfirm('school_type', $event)" @cancel="showSchoolTypePicker = false" />
    </van-popup>

    <!-- 毕业时间选择器 -->
    <van-popup v-model:show="showGraduationDatePicker" position="bottom">
      <van-date-picker v-model="graduationDateValue" :min-date="new Date(1980, 0, 1)" :max-date="new Date(2030, 11, 31)"
        @confirm="onDateConfirm('graduation_date', $event)" @cancel="showGraduationDatePicker = false" />
    </van-popup>

    <!-- 学历选择器 -->
    <van-popup v-model:show="showEducationPicker" position="bottom">
      <van-picker :columns="educationOptions" @confirm="onPickerConfirm('education', $event)" @cancel="showEducationPicker = false" />
    </van-popup>

    <!-- 电脑信息选择器 -->
    <van-popup v-model:show="showComputerInfoPicker" position="bottom">
      <van-picker :columns="computerInfoOptions" @confirm="onPickerConfirm('computer_info', $event)" @cancel="showComputerInfoPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast, showLoadingToast, closeToast } from 'vant'
import { useUserStore } from '../stores/user'
import api from '../utils/api'

const router = useRouter()
const userStore = useUserStore()

const form = ref({
  name: '',
  english_name: '',
  gender: '',
  birth_date: '',
  id_card: '',
  phone: '',
  email: '',
  nationality: '中国',
  hukou_location: '',
  hukou_type: '',
  native_place: '',
  hukou_address: '',
  ethnicity: '汉族',
  blood_type: '',
  marital_status: '',
  political_status: '',
  party_date: '',
  address: '',
  emergency_contact: '',
  emergency_relation: '',
  emergency_phone: '',
  school_type: '',
  school_name: '',
  major: '',
  graduation_date: '',
  education: '',
  bank_card_no: '',
  expense_card_no: '',
  computer_info: '',
  computer_brand: '',
})

const loading = ref(false)
const rejectReason = ref('')

// 文件列表
const avatarList = ref([])
const idCardFrontList = ref([])
const idCardBackList = ref([])

// 选择器显示状态
const showGenderPicker = ref(false)
const showDatePicker = ref(false)
const showHukouTypePicker = ref(false)
const showBloodTypePicker = ref(false)
const showMaritalPicker = ref(false)
const showPoliticalPicker = ref(false)
const showPartyDatePicker = ref(false)
const showSchoolTypePicker = ref(false)
const showGraduationDatePicker = ref(false)
const showEducationPicker = ref(false)
const showComputerInfoPicker = ref(false)

// 日期选择器值
const birthDateValue = ref(['1995', '01', '01'])
const partyDateValue = ref(['2020', '01', '01'])
const graduationDateValue = ref(['2020', '06', '01'])

// 选项配置
const genderOptions = ['男', '女']
const hukouTypeOptions = ['农村', '城镇']
const bloodTypeOptions = ['A型', 'B型', 'O型', 'AB型', '未知']
const maritalOptions = ['未婚', '已婚', '离异', '丧偶']
const politicalOptions = ['群众', '共青团员', '中共党员', '民主党派', '其他']
const schoolTypeOptions = ['普通本科', '211', '985', '双一流', '大专', '高中/中专', '其他']
const educationOptions = ['高中/中专', '大专', '本科', '硕士', '博士']
const computerInfoOptions = ['自带', '公司配发']

// 字段映射
const genderMap = { M: '男', F: '女' }
const maritalMap = { single: '未婚', married: '已婚', divorced: '离异', widowed: '丧偶' }

onMounted(async () => {
  // 先刷新用户信息获取最新邮箱
  await userStore.checkAuth()
  await loadProfile()
})

async function loadProfile() {
  try {
    const res = await userStore.fetchProfile()
    if (res.success) {
      const data = res.data
      form.value = {
        name: data.name || '',
        english_name: data.english_name || '',
        gender: genderMap[data.gender] || '',
        birth_date: data.birth_date || '',
        id_card: data.id_card || '',
        phone: data.phone || '',
        email: data.email || userStore.userInfo?.email || '',
        nationality: data.nationality || '中国',
        hukou_location: data.hukou_location || '',
        hukou_type: data.hukou_type || '',
        native_place: data.native_place || '',
        hukou_address: data.hukou_address || '',
        ethnicity: data.ethnicity || '汉族',
        blood_type: data.blood_type || '',
        marital_status: maritalMap[data.marital_status] || '',
        political_status: data.political_status || '',
        party_date: data.party_date || '',
        address: data.address || '',
        emergency_contact: data.emergency_contact || '',
        emergency_relation: data.emergency_relation || '',
        emergency_phone: data.emergency_phone || '',
        school_type: data.school_type || '',
        school_name: data.school_name || '',
        major: data.major || '',
        graduation_date: data.graduation_date || '',
        education: data.education || '',
        bank_card_no: data.bank_card_no || '',
        expense_card_no: data.expense_card_no || '',
        computer_info: data.computer_info || '',
        computer_brand: data.computer_brand || '',
      }
      rejectReason.value = data.onboard_reject_reason || ''

      // 已有图片
      if (data.avatar) avatarList.value = [{ url: data.avatar, isImage: true }]
      if (data.id_card_front) idCardFrontList.value = [{ url: data.id_card_front, isImage: true }]
      if (data.id_card_back) idCardBackList.value = [{ url: data.id_card_back, isImage: true }]
    }
  } catch (e) {
    console.error(e)
  }
}

function onPickerConfirm(field, { selectedOptions }) {
  form.value[field] = selectedOptions[0]
  // 关闭对应的picker
  if (field === 'gender') showGenderPicker.value = false
  if (field === 'hukou_type') showHukouTypePicker.value = false
  if (field === 'blood_type') showBloodTypePicker.value = false
  if (field === 'marital_status') showMaritalPicker.value = false
  if (field === 'political_status') showPoliticalPicker.value = false
  if (field === 'school_type') showSchoolTypePicker.value = false
  if (field === 'education') showEducationPicker.value = false
  if (field === 'computer_info') showComputerInfoPicker.value = false
}

function onDateConfirm(field, { selectedValues }) {
  form.value[field] = selectedValues.join('-')
  if (field === 'birth_date') showDatePicker.value = false
  if (field === 'party_date') showPartyDatePicker.value = false
  if (field === 'graduation_date') showGraduationDatePicker.value = false
}

async function uploadFile(file, fieldName) {
  const formData = new FormData()
  formData.append(fieldName, file.file)

  showLoadingToast({ message: '上传中...', forbidClick: true })

  try {
    const res = await api.post('/api/onboarding/profile/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    closeToast()
    if (res.data.success) {
      showSuccessToast('上传成功')
      // 刷新用户信息以更新头像
      await userStore.fetchProfile()
    } else {
      showToast(res.data.error?.message || '上传失败')
    }
  } catch (e) {
    closeToast()
    showToast(e.response?.data?.error?.message || '上传失败')
    if (fieldName === 'avatar') avatarList.value = []
    if (fieldName === 'id_card_front') idCardFrontList.value = []
    if (fieldName === 'id_card_back') idCardBackList.value = []
  }
}

async function handleSubmit() {
  // 校验头像是否上传
  if (avatarList.value.length === 0) {
    showToast('请上传照片')
    return
  }

  loading.value = true

  // 转换性别和婚姻状况为后端值
  const genderValue = Object.entries(genderMap).find(([k, v]) => v === form.value.gender)?.[0] || ''
  const maritalValue = Object.entries(maritalMap).find(([k, v]) => v === form.value.marital_status)?.[0] || ''

  try {
    const res = await userStore.updateProfile({
      ...form.value,
      gender: genderValue,
      marital_status: maritalValue,
    })

    if (res.success) {
      showSuccessToast('提交成功')
      router.push('/status')
    } else {
      showToast(res.error?.message || '提交失败')
    }
  } catch (e) {
    showToast(e.response?.data?.error?.message || '提交失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form-container {
  padding-bottom: 20px;
}

.section-title {
  font-size: 14px;
  color: #969799;
  padding: 16px 16px 8px;
}

:deep(.van-cell-group) {
  margin-bottom: 0;
}

:deep(.required-title::before) {
  content: '*';
  color: #ee0a24;
  margin-right: 2px;
}
</style>
