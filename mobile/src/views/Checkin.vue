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
          <svg-icon name="leaves" size="80" color="#a0cfff" />
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
          :class="buttonStatusClass"
          @click="handleCheckin"
        >
          <van-loading v-if="loading" color="#fff" size="32" />
          <template v-else>
            <div class="button-inner">
              <svg-icon :name="buttonIcon" size="48" color="#fff" />
              <span class="button-text">{{ buttonText }}</span>
              <span class="button-time">{{ currentTime.slice(0, 5) }}</span>
            </div>
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
      <div class="location-info card" @click="handleLocationClick">
        <svg-icon name="attendance" color="#1989fa" />
        <span v-if="locationLoading">正在获取位置...</span>
        <span v-else-if="locationError" class="error">{{ locationError }}</span>
        <span v-else-if="isDefaultLocation" class="warning">
          定位失败，点击重试
          <van-icon name="replay" style="margin-left: 4px;" />
        </span>
        <span v-else>
          {{ locationName || '已获取位置' }}
          <span v-if="locationRefreshing" class="location-hint">（更新中）</span>
        </span>
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
      <van-tabbar-item to="/home">
        <span>首页</span>
        <template #icon="{ active }">
          <svg-icon name="dashboard" :color="active ? '#1989fa' : '#646566'" size="20" />
        </template>
      </van-tabbar-item>
      <van-tabbar-item to="/checkin">
        <span>打卡</span>
        <template #icon="{ active }">
          <svg-icon name="attendance" :color="active ? '#1989fa' : '#646566'" size="20" />
        </template>
      </van-tabbar-item>
      <van-tabbar-item to="/me">
        <span>我的</span>
        <template #icon="{ active }">
          <svg-icon name="account" :color="active ? '#1989fa' : '#646566'" size="20" />
        </template>
      </van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
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
const locationRefreshing = ref(false)
const locationError = ref('')

const LOCATION_CACHE_KEY = 'hr_mobile_location_cache_v1'
const LOCATION_CACHE_TTL_MS = 10 * 60 * 1000

function readLocationCache() {
  try {
    const raw = localStorage.getItem(LOCATION_CACHE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') return null
    if (typeof parsed.lat !== 'number' || typeof parsed.lng !== 'number' || typeof parsed.ts !== 'number') return null
    if (Date.now() - parsed.ts > LOCATION_CACHE_TTL_MS) return null
    return parsed
  } catch {
    return null
  }
}

function writeLocationCache(lat, lng) {
  try {
    localStorage.setItem(
      LOCATION_CACHE_KEY,
      JSON.stringify({ lat, lng, ts: Date.now() })
    )
  } catch {
    // ignore
  }
}

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
const isDefaultLocation = computed(() => locationName.value === '默认位置' || (latitude.value === 22.5431 && longitude.value === 114.0579))

const buttonIcon = computed(() => {
  if (hasCheckedIn.value && hasCheckedOut.value) return 'attendance'
  if (hasCheckedIn.value) return 'attendance'
  return 'attendance'
})

const buttonText = computed(() => {
  if (hasCheckedIn.value && hasCheckedOut.value) return '更新签退'
  if (hasCheckedIn.value) return '下班签退'
  return '上班签到'
})

const buttonStatusClass = computed(() => {
  if (hasCheckedIn.value && hasCheckedOut.value) return 'status-completed'
  if (hasCheckedIn.value) return 'status-working'
  return 'status-start'
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

// 地址缓存
const ADDRESS_CACHE_KEY = 'hr_mobile_address_cache_v1'
function getAddressFromCache(lat, lng) {
  try {
    const raw = localStorage.getItem(ADDRESS_CACHE_KEY)
    if (!raw) return null
    const cache = JSON.parse(raw)
    // 经纬度四舍五入到小数点后3位作为key（约100米精度）
    const key = `${lat.toFixed(3)},${lng.toFixed(3)}`
    return cache[key] || null
  } catch { return null }
}
function saveAddressToCache(lat, lng, address) {
  try {
    const raw = localStorage.getItem(ADDRESS_CACHE_KEY)
    const cache = raw ? JSON.parse(raw) : {}
    const key = `${lat.toFixed(3)},${lng.toFixed(3)}`
    cache[key] = address
    // 只保留最近10个地址
    const keys = Object.keys(cache)
    if (keys.length > 10) delete cache[keys[0]]
    localStorage.setItem(ADDRESS_CACHE_KEY, JSON.stringify(cache))
  } catch { /* ignore */ }
}

// 逆地理编码：将经纬度转换为地址名称（使用 OpenStreetMap）
async function reverseGeocode(lat, lng) {
  // 先检查缓存
  const cached = getAddressFromCache(lat, lng)
  if (cached) return cached

  try {
    // 使用 AbortController 设置超时
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000)

    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
      { 
        headers: { 'Accept-Language': 'zh-CN,zh' },
        signal: controller.signal 
      }
    )
    clearTimeout(timeoutId)

    const data = await res.json()
    if (data && data.address) {
      const addr = data.address
      // 优先显示：区/街道 + 道路/建筑
      const parts = []
      if (addr.suburb || addr.district) parts.push(addr.suburb || addr.district)
      if (addr.road) parts.push(addr.road)
      if (addr.building || addr.amenity) parts.push(addr.building || addr.amenity)
      
      let result = parts.length > 0 ? parts.join(' ') : null
      if (!result) {
        result = data.display_name?.split(',').slice(0, 3).join(' ') || null
      }
      // 保存到缓存
      if (result) saveAddressToCache(lat, lng, result)
      return result
    }
  } catch (e) {
    if (e.name === 'AbortError') {
      console.warn('逆地理编码超时')
    } else {
      console.warn('逆地理编码失败:', e)
    }
  }
  // 返回坐标作为备选
  return `${lat.toFixed(4)}, ${lng.toFixed(4)}`
}

function getLocation() {
  locationLoading.value = true
  locationError.value = ''
  locationRefreshing.value = false

  // 先使用缓存位置（提升“体感速度”），再后台刷新真实位置
  const cached = readLocationCache()
  const hasCached = !!cached
  if (cached) {
    latitude.value = cached.lat
    longitude.value = cached.lng
    locationName.value = '使用上次位置...'
    locationLoading.value = false
    locationRefreshing.value = true
    // 异步获取缓存位置的地址
    reverseGeocode(cached.lat, cached.lng).then(addr => {
      if (addr && locationRefreshing.value) {
        locationName.value = addr + '（更新中）'
      }
    })
  }

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

  // 定位成功回调
  const onSuccess = async (pos) => {
    latitude.value = pos.coords.latitude
    longitude.value = pos.coords.longitude
    locationLoading.value = false
    locationRefreshing.value = false
    writeLocationCache(latitude.value, longitude.value)

    // 先显示"定位成功"，然后异步获取地址
    locationName.value = '定位成功'
    const address = await reverseGeocode(latitude.value, longitude.value)
    if (address) {
      locationName.value = address
    }
  }

  // 定位失败回调
  const onError = (err) => {
    locationLoading.value = false
    locationRefreshing.value = false

    // 如果已有缓存位置，则不显示错误，避免“位置更新中”变成红字干扰
    if (hasCached) {
      return
    }

    console.error('定位失败:', err.code, err.message)

    let errorMsg = ''
    switch (err.code) {
      case 1:
        errorMsg = '请在手机设置中开启定位权限'
        break
      case 2:
        errorMsg = '无法获取位置，请检查GPS是否开启'
        break
      case 3:
        errorMsg = '定位超时，请到信号好的地方重试'
        break
      default:
        errorMsg = '获取位置失败'
    }

    // 定位失败时使用默认位置，但保留提示
    if (!latitude.value) {
      latitude.value = 22.5431
      longitude.value = 114.0579
      locationName.value = '默认位置'
      locationError.value = ''
      // 弹出提示引导用户
      showToast({
        message: errorMsg,
        position: 'top',
        duration: 3000,
      })
    }
  }

  // 直接使用高精度GPS定位
  navigator.geolocation.getCurrentPosition(
    onSuccess,
    onError,
    {
      enableHighAccuracy: true,  // 强制使用GPS高精度
      timeout: 15000,            // 15秒超时
      maximumAge: 0              // 不使用缓存，获取实时位置
    }
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
    showToast({
      message: '正在获取位置，请稍候',
      duration: 1500,
    })
    return
  }

  // HTTP 环境下位置可能是 0,0，仍然允许提交，让后端决定
  // 只有明确的错误才阻止
  if (locationError.value && latitude.value === null) {
    showToast({
      message: '请先允许获取位置',
      icon: 'warning-o',
    })
    getLocation()
    return
  }

  // 检查是否需要填写备注
  if (showNotesInput.value && !notes.value.trim()) {
    showToast({
      message: notesPlaceholder.value,
      position: 'top',
    })
    return
  }

  // 计算打卡类型和提示文案
  const isUpdate = hasCheckedIn.value && hasCheckedOut.value
  const action = hasCheckedIn.value ? 'check_out' : 'check_in'
  let actionText = '签到'
  if (hasCheckedIn.value) {
    actionText = isUpdate ? '更新签退' : '签退'
  }

  loading.value = true
  const pendingToast = showToast({
    type: 'loading',
    message: `${actionText}中...`,
    duration: 0,
    forbidClick: true,
  })

  try {
    const res = await api.post('/api/attendance/check/', {
      action,
      latitude: latitude.value,
      longitude: longitude.value,
      notes: notes.value.trim(),
    })

    if (res.data.success) {
      // 先关闭 loading toast，再展示结果 toast，避免“白框无文字”的竞态
      pendingToast?.close?.()
      showToast({
        type: 'success',
        message: `${actionText}成功`,
        duration: 1500,
      })
      todayRecord.value = res.data.data
      notes.value = ''
    } else {
      pendingToast?.close?.()
      showToast(res.data.error?.message || `${actionText}失败`)
    }
  } catch (e) {
    // 避免与 api.js 中的全局错误提示重复
    // api.js 处理了 401, 403, 404, 500 以及网络错误
    const status = e.response?.status
    if (!status || ![401, 403, 404, 500].includes(status)) {
        pendingToast?.close?.()
        showToast(e.response?.data?.error?.message || `${actionText}失败`)
    }
  } finally {
    pendingToast?.close?.()
    loading.value = false
  }
}

// 点击位置卡片
function handleLocationClick() {
  if (isDefaultLocation.value || locationError.value) {
    showToast({
      message: '正在重新获取位置...',
      duration: 1000,
    })
    // 重置并重新获取
    latitude.value = null
    longitude.value = null
    locationName.value = ''
    getLocation()
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
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 40px;
  height: 180px;
}

.checkin-button {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 4px solid rgba(255, 255, 255, 0.25);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  z-index: 10;
  box-sizing: border-box;
}

/* Halo Effect via pseudo-element */
.checkin-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  z-index: -1;
  animation: pulse 2s ease-out infinite;
}

.button-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.button-text {
  font-size: 16px;
  font-weight: 600;
  margin-top: 4px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
  letter-spacing: 1px;
}

.button-time {
  font-size: 13px;
  opacity: 0.9;
  font-family: 'SF Mono', Monaco, monospace;
}

.checkin-button:active {
  transform: scale(0.95);
}

/* Status variants */
.checkin-button.status-start {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  box-shadow: 0 10px 25px rgba(25, 118, 210, 0.4);
}
.checkin-button.status-start::before {
  background: radial-gradient(circle, rgba(33, 150, 243, 0.6) 0%, rgba(33, 150, 243, 0) 70%);
}

.checkin-button.status-working {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
  box-shadow: 0 10px 25px rgba(245, 124, 0, 0.4);
}
.checkin-button.status-working::before {
  background: radial-gradient(circle, rgba(255, 152, 0, 0.6) 0%, rgba(255, 152, 0, 0) 70%);
}

.checkin-button.status-completed {
  background: linear-gradient(135deg, #00C853 0%, #009624 100%);
  box-shadow: 0 10px 25px rgba(0, 150, 36, 0.4);
}
.checkin-button.status-completed::before {
  background: radial-gradient(circle, rgba(0, 200, 83, 0.6) 0%, rgba(0, 200, 83, 0) 70%);
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.3;
  }
  100% {
    transform: scale(1.4);
    opacity: 0;
  }
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

.location-hint {
  color: #969799;
  margin-left: 6px;
  font-size: 12px;
}

.location-info .error {
  color: #ee0a24;
}

.location-info .warning {
  color: #ff976a;
  display: flex;
  align-items: center;
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
