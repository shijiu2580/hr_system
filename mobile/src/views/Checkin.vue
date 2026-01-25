<template>
  <div class="page-container">
    <van-nav-bar title="签到打卡" left-arrow @click-left="$router.back()" />

    <div class="checkin-content">
      <!-- 加载中 -->
      <div v-if="pageLoading" class="loading-wrapper">
        <van-loading size="32" />
      </div>

      <template v-else>
      <!-- 时间显示 -->
      <div class="time-display">
        <div class="current-time">{{ currentTime }}</div>
        <div class="current-date">{{ currentDate }}</div>
      </div>

      <!-- 休息日显示 -->
      <div v-if="!isWorkday && !hasCheckedIn" class="rest-day">
        <div class="rest-image">
          <van-icon name="smile-o" size="80" color="#a0cfff" />
        </div>
        <div class="rest-text">今日休息</div>
        <div class="rest-hint">{{ holidayName || '周末愉快' }}</div>
        <van-button 
          type="primary" 
          plain 
          round 
          size="small"
          style="margin-top: 20px;"
          @click="showOvertimeConfirm"
        >
          加班打卡
        </van-button>
      </div>

      <!-- 工作日打卡（或已加班打卡）-->
      <template v-else-if="isWorkday || hasCheckedIn">
      <div class="checkin-button-wrapper">
        <div 
          class="checkin-button"
          :class="{ 'checked': hasCheckedIn && hasCheckedOut }"
          @click="handleCheckin"
        >
          <van-loading v-if="loading" color="#fff" size="32" />
          <template v-else>
            <van-icon :name="buttonIcon" size="40" />
            <span>{{ buttonText }}</span>
          </template>
        </div>
      </div>

      <!-- 今日签到状态 -->
      <div class="today-status card">
        <div class="status-row">
          <div class="status-item">
            <div class="status-label">上班签到</div>
            <div class="status-value" :class="{ 'has-value': checkInTime }">
              {{ checkInTime || '--:--' }}
            </div>
            <div v-if="isLate" class="status-tag late">迟到</div>
          </div>
          <div class="status-divider"></div>
          <div class="status-item">
            <div class="status-label">下班签退</div>
            <div class="status-value" :class="{ 'has-value': checkOutTime }">
              {{ checkOutTime || '--:--' }}
            </div>
            <div v-if="isEarlyLeave" class="status-tag early">早退</div>
          </div>
        </div>
      </div>

      <!-- 位置信息 -->
      <div class="location-info card">
        <van-icon name="location-o" color="#1989fa" />
        <span v-if="locationLoading">正在获取位置...</span>
        <span v-else-if="locationError" class="error">{{ locationError }}</span>
        <span v-else>{{ locationName || '已获取位置' }}</span>
      </div>

      <!-- 备注输入（迟到/早退时显示） -->
      <van-cell-group v-if="showNotesInput" inset style="margin-top: 16px;">
        <van-field
          v-model="notes"
          type="textarea"
          :label="notesLabel"
          :placeholder="notesPlaceholder"
          rows="2"
          maxlength="200"
          show-word-limit
        />
      </van-cell-group>
      </template>
      </template>
    </div>

    <!-- 底部导航 -->
    <van-tabbar v-model="activeTab" fixed>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="location-o" to="/checkin">打卡</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/me">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import api from '../utils/api'

const activeTab = ref(1)

// 时间
const currentTime = ref('')
const currentDate = ref('')
let timer = null

// 位置
const latitude = ref(null)
const longitude = ref(null)
const locationName = ref('')
const locationLoading = ref(true)
const locationError = ref('')

// 签到状态
const loading = ref(false)
const todayRecord = ref(null)
const notes = ref('')

// 工作日判断
const pageLoading = ref(true)
const isWorkday = ref(true)
const holidayName = ref('')

const hasCheckedIn = computed(() => !!todayRecord.value?.check_in_time)
const hasCheckedOut = computed(() => !!todayRecord.value?.check_out_time)
const checkInTime = computed(() => todayRecord.value?.check_in_time?.slice(0, 5) || '')
const checkOutTime = computed(() => todayRecord.value?.check_out_time?.slice(0, 5) || '')
const isLate = computed(() => todayRecord.value?.attendance_type === 'late')
const isEarlyLeave = computed(() => todayRecord.value?.attendance_type === 'early_leave')

const buttonIcon = computed(() => {
  if (hasCheckedIn.value && hasCheckedOut.value) return 'clock-o'
  if (hasCheckedIn.value) return 'clock-o'
  return 'location-o'
})

const buttonText = computed(() => {
  if (hasCheckedIn.value && hasCheckedOut.value) return '更新签退'
  if (hasCheckedIn.value) return '下班签退'
  return '上班签到'
})

// 是否需要填写备注
const showNotesInput = computed(() => {
  const now = new Date()
  const hours = now.getHours()
  const minutes = now.getMinutes()
  
  if (!hasCheckedIn.value) {
    // 9点后签到需要填写迟到原因
    return hours > 9 || (hours === 9 && minutes > 0)
  }
  if (!hasCheckedOut.value) {
    // 18点前签退需要填写早退原因
    return hours < 18
  }
  return false
})

const notesLabel = computed(() => !hasCheckedIn.value ? '迟到原因' : '早退原因')
const notesPlaceholder = computed(() => !hasCheckedIn.value ? '请填写迟到原因' : '请填写早退原因')

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  getLocation()
  checkWorkday()
  fetchTodayRecord()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

// 检查今天是否工作日
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
  } finally {
    pageLoading.value = false
  }
}

// 加班打卡确认
function showOvertimeConfirm() {
  showConfirmDialog({
    title: '加班打卡',
    message: '今日为休息日，确定要进行加班打卡吗？',
  }).then(() => {
    isWorkday.value = true  // 临时设为工作日以显示打卡界面
  }).catch(() => {})
}

function updateTime() {
  const now = new Date()
  currentTime.value = now.toTimeString().slice(0, 8)
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  currentDate.value = `${now.getMonth() + 1}月${now.getDate()}日 ${weekDays[now.getDay()]}`
}

function getLocation() {
  locationLoading.value = true
  locationError.value = ''
  
  // 检查是否为非安全环境（HTTP 非 localhost）
  const isSecure = window.isSecureContext || 
                   location.protocol === 'https:' || 
                   location.hostname === 'localhost' || 
                   location.hostname === '127.0.0.1'
  
  if (!navigator.geolocation) {
    locationError.value = '浏览器不支持定位'
    locationLoading.value = false
    return
  }
  
  // 非安全环境下尝试用 IP 地理定位或使用默认位置
  if (!isSecure) {
    console.warn('非 HTTPS 环境，无法使用精确定位')
    // 显示提示，让用户知道在HTTP下定位不准确
    locationName.value = '定位不可用（非HTTPS）'
    locationLoading.value = false
    // 设置一个标记，表示位置可能不准确
    latitude.value = 0
    longitude.value = 0
    return
  }
  
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      latitude.value = pos.coords.latitude
      longitude.value = pos.coords.longitude
      locationLoading.value = false
      locationName.value = `${latitude.value.toFixed(4)}, ${longitude.value.toFixed(4)}`
    },
    (err) => {
      locationLoading.value = false
      switch (err.code) {
        case 1:
          locationError.value = '请允许获取位置权限'
          break
        case 2:
          locationError.value = '无法获取位置信息'
          break
        case 3:
          locationError.value = '获取位置超时'
          break
        default:
          locationError.value = '获取位置失败'
      }
      // 定位失败时也使用默认位置
      if (!latitude.value) {
        latitude.value = 22.5431
        longitude.value = 114.0579
        locationName.value = '默认位置'
        locationError.value = ''
      }
    },
    { enableHighAccuracy: true, timeout: 10000 }
  )
}

async function fetchTodayRecord() {
  try {
    const res = await api.get('/api/attendance/today/')
    if (res.data.success) {
      todayRecord.value = res.data.data
    }
  } catch (e) {
    console.error(e)
  }
}

async function handleCheckin() {
  if (locationLoading.value) {
    showToast('正在获取位置，请稍候')
    return
  }
  
  // HTTP 环境下位置可能是 0,0，仍然允许提交，让后端决定
  // 只有明确的错误才阻止
  if (locationError.value && latitude.value === null) {
    showToast('请先允许获取位置')
    getLocation()
    return
  }
  
  // 检查是否需要填写备注
  if (showNotesInput.value && !notes.value.trim()) {
    showToast(notesPlaceholder.value)
    return
  }
  
  // 已签到后都是签退（可以多次更新）
  const action = hasCheckedIn.value ? 'check_out' : 'check_in'
  const actionText = hasCheckedIn.value ? (hasCheckedOut.value ? '更新签退' : '签退') : '签到'
  
  loading.value = true
  try {
    const res = await api.post('/api/attendance/check/', {
      action,
      latitude: latitude.value,
      longitude: longitude.value,
      notes: notes.value.trim(),
    })
    
    if (res.data.success) {
      showSuccessToast(`${actionText}成功`)
      todayRecord.value = res.data.data
      notes.value = ''
    } else {
      showToast(res.data.error?.message || `${actionText}失败`)
    }
  } catch (e) {
    showToast(e.response?.data?.error?.message || `${actionText}失败`)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-container {
  padding-bottom: 70px;
}

.checkin-content {
  padding: 20px 16px;
}

.time-display {
  text-align: center;
  margin-bottom: 30px;
}

.current-time {
  font-size: 48px;
  font-weight: 300;
  color: #323233;
  font-family: 'SF Mono', Monaco, monospace;
}

.current-date {
  font-size: 14px;
  color: #969799;
  margin-top: 8px;
}

.checkin-button-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.checkin-button {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  gap: 8px;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  transition: transform 0.2s;
}

.checkin-button:active {
  transform: scale(0.95);
}

.checkin-button.checked {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  box-shadow: 0 8px 20px rgba(56, 239, 125, 0.4);
}

.checkin-button span {
  font-size: 14px;
}

.today-status {
  padding: 20px;
}

.status-row {
  display: flex;
  align-items: center;
}

.status-item {
  flex: 1;
  text-align: center;
}

.status-divider {
  width: 1px;
  height: 50px;
  background: #ebedf0;
}

.status-label {
  font-size: 12px;
  color: #969799;
  margin-bottom: 8px;
}

.status-value {
  font-size: 24px;
  color: #c8c9cc;
  font-family: 'SF Mono', Monaco, monospace;
}

.status-value.has-value {
  color: #323233;
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  margin-top: 8px;
}

.status-tag.late {
  background: #fff7e8;
  color: #ff976a;
}

.status-tag.early {
  background: #ffece8;
  color: #ee0a24;
}

.location-info {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #646566;
}

.location-info .error {
  color: #ee0a24;
}

/* 休息日样式 */
.rest-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 40px 20px;
}

.rest-image {
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.rest-text {
  font-size: 20px;
  font-weight: 500;
  color: #323233;
  margin-bottom: 8px;
}

.rest-hint {
  font-size: 14px;
  color: #969799;
}

/* 加载中 */
.loading-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>
