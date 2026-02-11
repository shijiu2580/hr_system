<template>
  <div class="page-container">
    <van-nav-bar title="补签申请" left-arrow @click-left="$router.back()" />

    <!-- 标签页切换 -->
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="申请补签">
        <div class="form-section">
          <van-cell-group inset>
            <!-- 补签类型 -->
            <van-cell title="补签类型" :value="typeText" is-link @click="showTypePicker = true" />
            <!-- 补签日期 -->
            <van-cell title="补签日期" :value="form.date || '请选择'" is-link @click="showDatePicker = true" />
            <!-- 补签时间 -->
            <van-cell title="补签时间" :value="form.time || '请选择'" is-link @click="showTimePicker = true" />
            <!-- 补签原因 -->
            <van-field
              v-model="form.reason"
              type="textarea"
              label="补签原因"
              placeholder="请输入补签原因（必填）"
              rows="3"
              maxlength="200"
              show-word-limit
            />
          </van-cell-group>

          <div class="submit-section">
            <van-button
              type="primary"
              block
              round
              :loading="submitting"
              :disabled="!canSubmit"
              loading-text="提交中..."
              @click="handleSubmit"
            >
              提交申请
            </van-button>
          </div>
        </div>
      </van-tab>

      <van-tab title="申请记录">
        <van-pull-refresh v-model="refreshing" @refresh="fetchList">
          <div v-if="!listLoading && list.length === 0" class="empty-state">
            <van-empty description="暂无补签记录" />
          </div>
          <div v-for="item in list" :key="item.id" class="record-card card">
            <div class="record-header">
              <span class="record-date">{{ item.date }}</span>
              <van-tag :type="statusTagType(item.status)" size="medium">
                {{ statusText(item.status) }}
              </van-tag>
            </div>
            <div class="record-body">
              <div class="record-row">
                <span class="record-label">补签类型</span>
                <span class="record-value">{{ item.type === 'check_in' ? '补签到' : '补签退' }}</span>
              </div>
              <div class="record-row">
                <span class="record-label">补签时间</span>
                <span class="record-value">{{ item.time?.slice(0, 5) || '--' }}</span>
              </div>
              <div class="record-row">
                <span class="record-label">补签原因</span>
                <span class="record-value">{{ item.reason || '--' }}</span>
              </div>
              <div v-if="item.comments" class="record-row">
                <span class="record-label">审批备注</span>
                <span class="record-value">{{ item.comments }}</span>
              </div>
              <div class="record-row">
                <span class="record-label">提交时间</span>
                <span class="record-value">{{ item.created_at }}</span>
              </div>
            </div>
          </div>
        </van-pull-refresh>
        <div v-if="listLoading" class="loading-wrapper">
          <van-loading size="24" />
        </div>
      </van-tab>
    </van-tabs>

    <!-- 类型选择器 -->
    <van-popup v-model:show="showTypePicker" position="bottom">
      <van-picker
        :columns="typeColumns"
        @confirm="onTypeConfirm"
        @cancel="showTypePicker = false"
      />
    </van-popup>

    <!-- 日期选择器 -->
    <van-popup v-model:show="showDatePicker" position="bottom">
      <van-date-picker
        v-model="datePickerValue"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>

    <!-- 时间选择器 -->
    <van-popup v-model:show="showTimePicker" position="bottom">
      <van-time-picker
        v-model="timePickerValue"
        @confirm="onTimeConfirm"
        @cancel="showTimePicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import api from '../utils/api'

const activeTab = ref(0)

// ========== 表单相关 ==========
const form = ref({
  type: 'check_in',
  date: '',
  time: '',
  reason: '',
})

const submitting = ref(false)

const typeColumns = [
  { text: '补签到（上班）', value: 'check_in' },
  { text: '补签退（下班）', value: 'check_out' },
]

const typeText = computed(() => {
  return form.value.type === 'check_in' ? '补签到（上班）' : '补签退（下班）'
})

const canSubmit = computed(() => {
  return form.value.date && form.value.time && form.value.reason.trim()
})

// 类型选择器
const showTypePicker = ref(false)
function onTypeConfirm({ selectedValues }) {
  form.value.type = selectedValues[0]
  showTypePicker.value = false
}

// 日期选择器
const showDatePicker = ref(false)
const now = new Date()
const minDate = new Date(now.getFullYear(), now.getMonth() - 1, 1) // 前一个月开始
const maxDate = new Date() // 今天

// 初始化日期选择器值为今天
const datePickerValue = ref([
  String(now.getFullYear()),
  String(now.getMonth() + 1).padStart(2, '0'),
  String(now.getDate()).padStart(2, '0'),
])

function onDateConfirm({ selectedValues }) {
  form.value.date = selectedValues.join('-')
  showDatePicker.value = false
}

// 时间选择器
const showTimePicker = ref(false)
const timePickerValue = ref(['09', '00'])

function onTimeConfirm({ selectedValues }) {
  form.value.time = selectedValues.join(':')
  showTimePicker.value = false
}

async function handleSubmit() {
  if (!canSubmit.value) return

  submitting.value = true
  try {
    const res = await api.post('/api/attendance/supplement/', {
      date: form.value.date,
      time: form.value.time,
      type: form.value.type,
      reason: form.value.reason.trim(),
    })
    if (res.data.success) {
      showSuccessToast('提交成功')
      // 重置表单
      form.value.reason = ''
      form.value.date = ''
      form.value.time = ''
      // 切换到记录列表并刷新
      activeTab.value = 1
      fetchList()
    } else {
      showToast(res.data.error || '提交失败')
    }
  } catch (e) {
    const msg = e.response?.data?.error || '提交失败，请重试'
    showToast(msg)
  } finally {
    submitting.value = false
  }
}

// ========== 列表相关 ==========
const list = ref([])
const listLoading = ref(false)
const refreshing = ref(false)

async function fetchList() {
  listLoading.value = true
  try {
    const res = await api.get('/api/attendance/supplement/')
    if (res.data.success) {
      list.value = res.data.data || []
    }
  } catch (e) {
    console.error('获取补签记录失败', e)
  } finally {
    listLoading.value = false
    refreshing.value = false
  }
}

function statusTagType(status) {
  const map = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
  }
  return map[status] || 'default'
}

function statusText(status) {
  const map = {
    pending: '待审批',
    approved: '已通过',
    rejected: '已拒绝',
  }
  return map[status] || status
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f5f6fa;
}

.form-section {
  padding: 16px 0;
}

.submit-section {
  padding: 24px 16px;
}

.record-card {
  margin: 12px 16px;
  padding: 16px;
  border-radius: 12px;
  background: #fff;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.record-date {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.record-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.record-row {
  display: flex;
  font-size: 14px;
}

.record-label {
  color: #969799;
  min-width: 72px;
  flex-shrink: 0;
}

.record-value {
  color: #323233;
  flex: 1;
  word-break: break-all;
}

.empty-state {
  padding: 40px 0;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.card {
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
</style>
