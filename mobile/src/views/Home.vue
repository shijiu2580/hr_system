<template>
  <div class="page-container">
    <!-- 顶部用户信息 -->
    <div class="header">
      <div class="user-info">
        <van-image
          round
          width="50"
          height="50"
          :src="avatar"
          fit="cover"
        >
          <template #error>
            <div class="avatar-placeholder">{{ nameInitial }}</div>
          </template>
        </van-image>
        <div class="user-text">
          <div class="user-name">{{ userName }}</div>
          <div class="user-dept">{{ department }} · {{ position }}</div>
        </div>
      </div>
    </div>

    <!-- 今日签到状态 -->
    <div class="checkin-card card" @click="$router.push('/checkin')">
      <div class="checkin-status">
        <van-loading v-if="checkinLoading" size="24" />
        <van-icon 
          v-else
          :name="checkinIcon" 
          :color="checkinIconColor"
          size="32"
        />
        <div class="checkin-text">
          <div class="checkin-title">{{ checkinLoading ? '加载中...' : checkinTitle }}</div>
          <div class="checkin-time">{{ checkinLoading ? '' : checkinTime }}</div>
        </div>
      </div>
      <van-icon name="arrow" color="#969799" />
    </div>

    <!-- 功能菜单 -->
    <div class="menu-grid">
      <div class="menu-item" @click="$router.push('/checkin')">
        <div class="menu-icon" style="background: #e8f4ff;">
          <van-icon name="location-o" color="#1989fa" size="24" />
        </div>
        <span>签到打卡</span>
      </div>
      <div class="menu-item" @click="$router.push('/attendance')">
        <div class="menu-icon" style="background: #e8f7e8;">
          <van-icon name="calendar-o" color="#07c160" size="24" />
        </div>
        <span>考勤记录</span>
      </div>
      <div class="menu-item" @click="$router.push('/leave')">
        <div class="menu-icon" style="background: #fff7e8;">
          <van-icon name="edit" color="#ff976a" size="24" />
        </div>
        <span>请假申请</span>
      </div>
      <div class="menu-item" @click="$router.push('/me')">
        <div class="menu-icon" style="background: #f7e8ff;">
          <van-icon name="user-o" color="#b37feb" size="24" />
        </div>
        <span>个人中心</span>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="section-title">快捷服务</div>
    <van-cell-group inset>
      <van-cell title="补签申请" is-link icon="edit" to="/attendance" />
      <van-cell title="公司通知" is-link icon="bullhorn-o" />
    </van-cell-group>

    <!-- 底部导航 -->
    <van-tabbar v-model="activeTab" fixed>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="location-o" to="/checkin">打卡</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/me">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import api from '../utils/api'

const userStore = useUserStore()
const activeTab = ref(0)

const avatar = computed(() => userStore.employeeInfo?.avatar || '')
const userName = computed(() => userStore.employeeInfo?.name || userStore.userInfo?.username || '用户')
const nameInitial = computed(() => userName.value.charAt(0))
const department = computed(() => userStore.employeeInfo?.department || '未分配')
const position = computed(() => userStore.employeeInfo?.position || '未分配')

// 今日签到
const todayAttendance = ref(null)
const isWorkday = ref(true)
const holidayName = ref('')
const checkinLoading = ref(true)

const todayCheckedIn = computed(() => !!todayAttendance.value?.check_in_time)
const checkinTitle = computed(() => {
  // 休息日
  if (!isWorkday.value) return '今日休息'
  // 工作日
  if (!todayAttendance.value) return '今日未签到'
  if (todayAttendance.value.check_out_time) return '今日已签退'
  return '今日已签到'
})
const checkinTime = computed(() => {
  // 休息日
  if (!isWorkday.value) return holidayName.value || '周末愉快'
  // 工作日
  if (!todayAttendance.value) return '点击进行签到'
  if (todayAttendance.value.check_out_time) {
    return `签退时间 ${todayAttendance.value.check_out_time.slice(0, 5)}`
  }
  return `签到时间 ${todayAttendance.value.check_in_time.slice(0, 5)}`
})

// 签到卡片图标
const checkinIcon = computed(() => {
  if (!isWorkday.value) return 'smile-o'
  if (todayCheckedIn.value) return 'checked'
  return 'clock-o'
})
const checkinIconColor = computed(() => {
  if (!isWorkday.value) return '#1989fa'
  if (todayCheckedIn.value) return '#07c160'
  return '#969799'
})

onMounted(async () => {
  await Promise.all([fetchTodayAttendance(), checkWorkday()])
  checkinLoading.value = false
})

async function checkWorkday() {
  try {
    const res = await api.get('/api/attendance/workday/')
    if (res.data.success) {
      isWorkday.value = res.data.data.is_workday
      holidayName.value = res.data.data.holiday_name || ''
    }
  } catch (e) {
    // 请求失败时，简单判断周末
    const day = new Date().getDay()
    isWorkday.value = day !== 0 && day !== 6
  }
}

async function fetchTodayAttendance() {
  try {
    const res = await api.get('/api/attendance/today/')
    if (res.data.success) {
      todayAttendance.value = res.data.data
    }
  } catch (e) {
    console.error(e)
  }
}
</script>

<style scoped>
.page-container {
  padding-bottom: 70px;
}

.header {
  background: linear-gradient(135deg, #409EFF 0%, #53a8ff 100%);
  padding: 20px 16px 30px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-placeholder {
  width: 50px;
  height: 50px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

.user-text {
  color: #fff;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
}

.user-dept {
  font-size: 13px;
  opacity: 0.8;
  margin-top: 4px;
}

.checkin-card {
  margin: -20px 16px 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkin-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.checkin-title {
  font-size: 16px;
  font-weight: 500;
}

.checkin-time {
  font-size: 13px;
  color: #969799;
  margin-top: 4px;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 0 16px;
  margin-bottom: 20px;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.menu-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-item span {
  font-size: 12px;
  color: #323233;
}

.section-title {
  font-size: 14px;
  color: #969799;
  padding: 0 16px 8px;
}
</style>
