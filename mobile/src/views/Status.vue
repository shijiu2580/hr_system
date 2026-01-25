<template>
  <div class="page-container">
    <van-nav-bar title="入职进度" />

    <div class="status-content">
      <!-- 用户不存在提示 -->
      <template v-if="userNotFound">
        <div class="status-card status-not-found">
          <van-icon name="warning-o" size="48" />
          <div class="status-text">账号已失效</div>
          <div class="status-desc">您的账号信息不存在或已被删除，请联系HR</div>
        </div>
        <div style="padding: 16px;">
          <van-button type="primary" block round @click="handleLogout">
            重新登录
          </van-button>
        </div>
      </template>
      
      <template v-else>
        <!-- 状态卡片 -->
        <div class="status-card" :class="statusClass">
          <van-icon :name="statusIcon" size="48" />
          <div class="status-text">{{ statusText }}</div>
          <div class="status-desc">{{ statusDesc }}</div>
        </div>

        <!-- 进度步骤 -->
        <div class="steps-card card">
          <van-steps :active="activeStep" direction="vertical">
            <van-step>
              <template #active-icon><van-icon name="checked" /></template>
              <h3>提交申请</h3>
              <p>已完成注册，资料已提交</p>
            </van-step>
            <van-step>
              <template #active-icon><van-icon name="checked" /></template>
              <h3>HR审核中</h3>
              <p>{{ reviewingText }}</p>
            </van-step>
            <van-step>
              <h3>审核通过</h3>
              <p>{{ approvedText }}</p>
            </van-step>
            <van-step>
              <h3>正式入职</h3>
              <p>开始签到打卡</p>
            </van-step>
          </van-steps>
        </div>

        <!-- 拒绝原因 -->
        <div v-if="rejectReason" class="reject-card card">
          <div class="reject-title">
            <van-icon name="warning-o" color="#ee0a24" />
            <span>审核意见</span>
          </div>
          <div class="reject-content">{{ rejectReason }}</div>
          <van-button 
            type="primary" 
            size="small" 
            round 
            @click="$router.push('/profile')"
          >
            修改资料重新提交
          </van-button>
        </div>

        <!-- 入职信息 -->
        <div v-if="status === 'onboarded'" class="info-card card">
          <van-cell-group :border="false">
            <van-cell title="员工编号" :value="employeeId" />
            <van-cell title="入职日期" :value="hireDate" />
            <van-cell title="所属部门" :value="department" />
            <van-cell title="职位" :value="position" />
          </van-cell-group>
          
          <div style="padding: 16px;">
            <van-button 
              type="primary" 
              block 
              round 
              @click="goToHome"
            >
              进入首页
            </van-button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const userNotFound = computed(() => userStore.userNotFound)
const status = computed(() => userStore.employeeInfo?.onboard_status || 'pending')
const rejectReason = computed(() => userStore.employeeInfo?.reject_reason || '')
const isRejected = computed(() => status.value === 'rejected' || rejectReason.value)
const employeeId = computed(() => userStore.employeeInfo?.employee_id || '-')
const hireDate = computed(() => userStore.employeeInfo?.hire_date || '-')
const department = computed(() => userStore.employeeInfo?.department || '-')
const position = computed(() => userStore.employeeInfo?.position || '-')

const statusClass = computed(() => ({
  'status-pending': status.value === 'pending' && !isRejected.value,
  'status-approved': status.value === 'onboarded',
  'status-rejected': isRejected.value,
}))

const statusIcon = computed(() => {
  if (isRejected.value) return 'cross'
  if (status.value === 'onboarded') return 'checked'
  return 'clock-o'
})

const statusText = computed(() => {
  if (isRejected.value) return '审核未通过'
  if (status.value === 'onboarded') return '已入职'
  return '审核中'
})

const statusDesc = computed(() => {
  if (isRejected.value) return '请根据审核意见修改后重新提交'
  if (status.value === 'onboarded') return '恭喜您，已成功入职！'
  return '您的入职申请正在审核中，请耐心等待'
})

const activeStep = computed(() => {
  if (status.value === 'onboarded') return 3
  if (isRejected.value) return 1
  return 1
})

const reviewingText = computed(() => {
  if (isRejected.value) return '审核未通过，请修改后重新提交'
  if (status.value === 'onboarded') return '审核已通过'
  return 'HR正在审核您的资料...'
})

const approvedText = computed(() => {
  if (status.value === 'onboarded') return `入职日期：${hireDate.value}`
  return '等待审核通过'
})

function handleLogout() {
  userStore.logout()
  router.replace('/login')
}

function goToHome() {
  router.push('/home')
}

onMounted(async () => {
  await userStore.fetchOnboardStatus()
  // 已入职员工自动跳转首页
  if (userStore.employeeInfo?.onboard_status === 'onboarded') {
    router.replace('/home')
  }
})
</script>

<style scoped>
.status-content {
  padding: 16px;
}

.status-card {
  text-align: center;
  padding: 40px 20px;
  border-radius: 12px;
  margin-bottom: 16px;
  color: #fff;
}

.status-pending {
  background: linear-gradient(135deg, #ff9a44 0%, #fc6076 100%);
}

.status-approved {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.status-rejected {
  background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
}

.status-text {
  font-size: 24px;
  font-weight: 600;
  margin: 16px 0 8px;
}

.status-desc {
  font-size: 14px;
  opacity: 0.9;
}

.steps-card :deep(h3) {
  font-size: 14px;
  margin: 0 0 4px;
}

.steps-card :deep(p) {
  font-size: 12px;
  color: #969799;
  margin: 0;
}

.reject-card {
  padding: 16px;
}

.reject-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  margin-bottom: 8px;
}

.reject-content {
  background: #fff7f7;
  padding: 12px;
  border-radius: 8px;
  color: #ee0a24;
  font-size: 14px;
  margin-bottom: 16px;
}

.info-card :deep(.van-cell) {
  padding: 12px 0;
}

.status-not-found {
  background: linear-gradient(135deg, #666 0%, #999 100%);
}
</style>
