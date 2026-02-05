<template>
  <div class="page-container">
    <van-nav-bar title="考勤记录" left-arrow @click-left="$router.back()" />

    <!-- 月份选择 -->
    <div class="month-selector">
      <van-icon name="arrow-left" @click="prevMonth" />
      <span class="month-text" @click="showMonthPicker = true">
        {{ currentYear }}年{{ currentMonth }}月
      </span>
      <van-icon name="arrow" @click="nextMonth" />
    </div>

    <!-- 统计卡片 -->
    <div class="stats-card card">
      <div class="stat-item">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">出勤天数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value late">{{ stats.late }}</div>
        <div class="stat-label">迟到</div>
      </div>
      <div class="stat-item">
        <div class="stat-value early">{{ stats.early }}</div>
        <div class="stat-label">早退</div>
      </div>
      <div class="stat-item">
        <div class="stat-value absent">{{ stats.absent }}</div>
        <div class="stat-label">缺勤</div>
      </div>
    </div>

    <!-- 考勤列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="listLoading"
        :finished="finished"
        finished-text="没有更多了"
        @load="loadMore"
      >
        <div v-for="item in records" :key="item.id" class="record-item card">
          <div class="record-date">
            <div class="date-day">{{ getDay(item.date) }}</div>
            <div class="date-week">{{ getWeekDay(item.date) }}</div>
          </div>
          <div class="record-info">
            <div class="time-row">
              <span class="time-label">签到</span>
              <span class="time-value">
                {{ item.check_in_time?.slice(0, 5) || '--:--' }}
                <van-tag v-if="item.notes && item.notes.includes('补签到')" type="primary" size="mini" style="margin-left: 4px;">补</van-tag>
              </span>
            </div>
            <div class="time-row">
              <span class="time-label">签退</span>
              <span class="time-value">
                {{ item.check_out_time?.slice(0, 5) || '--:--' }}
                <van-tag v-if="item.notes && item.notes.includes('补签退')" type="primary" size="mini" style="margin-left: 4px;">补</van-tag>
              </span>
            </div>
          </div>
          <div class="record-status">
            <van-tag :type="getStatusType(getStatus(item))">
              {{ getStatusText(getStatus(item)) }}
            </van-tag>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 月份选择弹窗 -->
    <van-popup v-model:show="showMonthPicker" position="bottom">
      <van-date-picker
        v-model="pickerValue"
        type="year-month"
        :min-date="new Date(2020, 0)"
        :max-date="new Date()"
        @confirm="onMonthConfirm"
        @cancel="showMonthPicker = false"
      />
    </van-popup>

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
import api from '../utils/api'

const activeTab = ref(0)

const now = new Date()
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth() + 1)
const showMonthPicker = ref(false)
const pickerValue = ref([String(currentYear.value), String(currentMonth.value).padStart(2, '0')])

const records = ref([])
const stats = ref({ total: 0, late: 0, early: 0, absent: 0 })
const refreshing = ref(false)
const listLoading = ref(false)
const finished = ref(false)

const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

onMounted(() => {
  fetchRecords()
})

async function fetchRecords() {
  const startDate = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-01`
  // 计算该月的最后一天
  const lastDay = new Date(currentYear.value, currentMonth.value, 0).getDate()
  const endDate = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`

  try {
    const res = await api.get('/api/attendance/my/', {
      params: { date_from: startDate, date_to: endDate }
    })
    if (res.data.success) {
      records.value = res.data.data || []
      calculateStats()
    }
  } catch (e) {
    console.error(e)
  }

  refreshing.value = false
  listLoading.value = false
  finished.value = true
}

function calculateStats() {
  const s = { total: 0, late: 0, early: 0, absent: 0 }
  records.value.forEach(r => {
    if (r.check_in_time || r.check_out_time) s.total++
    if (r.attendance_type === 'late') s.late++
    if (r.attendance_type === 'early_leave') s.early++
    if (r.attendance_type === 'absent') s.absent++
  })
  stats.value = s
}

function prevMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  fetchRecords()
}

function nextMonth() {
  const now = new Date()
  if (currentYear.value === now.getFullYear() && currentMonth.value === now.getMonth() + 1) {
    return
  }
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  fetchRecords()
}

function onMonthConfirm({ selectedValues }) {
  currentYear.value = parseInt(selectedValues[0])
  currentMonth.value = parseInt(selectedValues[1])
  showMonthPicker.value = false
  fetchRecords()
}

function onRefresh() {
  fetchRecords()
}

function loadMore() {
  finished.value = true
}

function getDay(dateStr) {
  return parseInt(dateStr.split('-')[2])
}

function getWeekDay(dateStr) {
  return weekDays[new Date(dateStr).getDay()]
}

// 根据签到签退时间判断考勤状态
function getStatus(item) {
  if (!item.check_in_time && !item.check_out_time) {
    return 'absent'
  }

  let isLate = false
  let isEarlyLeave = false

  // 判断迟到（9:00后签到）
  if (item.check_in_time) {
    const parts = item.check_in_time.split(':')
    const checkInMinutes = parseInt(parts[0]) * 60 + parseInt(parts[1])
    isLate = checkInMinutes > 9 * 60
  }

  // 判断早退（没签退 或 18:00前签退）
  if (!item.check_out_time && item.check_in_time) {
    // 有签到但没签退，视为早退
    isEarlyLeave = true
  } else if (item.check_out_time) {
    const parts = item.check_out_time.split(':')
    const checkOutMinutes = parseInt(parts[0]) * 60 + parseInt(parts[1])
    isEarlyLeave = checkOutMinutes < 18 * 60
  }

  if (isLate && isEarlyLeave) return 'late_and_early'
  if (isLate) return 'late'
  if (isEarlyLeave) return 'early_leave'

  return 'normal'
}

function getStatusType(type) {
  const map = {
    'normal': 'success',
    'check_in': 'primary',
    'check_out': 'success',
    'late': 'warning',
    'early_leave': 'danger',
    'late_and_early': 'danger',
    'absent': 'danger',
    'leave': 'primary',
  }
  return map[type] || 'default'
}

function getStatusText(type) {
  const map = {
    'normal': '正常',
    'check_in': '已签到',
    'check_out': '正常',
    'late': '迟到',
    'early_leave': '早退',
    'late_and_early': '迟到/早退',
    'absent': '缺勤',
    'leave': '请假',
  }
  return map[type] || type
}
</script>

<style scoped>
.page-container {
  padding-bottom: 70px;
}

.month-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 16px;
  background: #fff;
}

.month-text {
  font-size: 16px;
  font-weight: 500;
}

.stats-card {
  margin: 0 16px 16px;
  padding: 16px;
  display: flex;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #323233;
}

.stat-value.late { color: #ff976a; }
.stat-value.early { color: #ee0a24; }
.stat-value.absent { color: #ee0a24; }

.stat-label {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}

.record-item {
  margin: 0 16px 12px;
  padding: 16px;
  display: flex;
  align-items: center;
}

.record-date {
  text-align: center;
  min-width: 50px;
}

.date-day {
  font-size: 20px;
  font-weight: 600;
}

.date-week {
  font-size: 12px;
  color: #969799;
}

.record-info {
  flex: 1;
  padding: 0 16px;
}

.time-row {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.time-row:not(:last-child) {
  margin-bottom: 4px;
}

.time-label {
  color: #969799;
}

.time-value {
  color: #323233;
}
</style>
