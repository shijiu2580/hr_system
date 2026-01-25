<template>
  <div class="page-container">
    <van-nav-bar title="请假申请" left-arrow @click-left="$router.back()" />

    <!-- 新建请假按钮 -->
    <div class="action-bar">
      <van-button type="primary" size="small" icon="plus" @click="showForm = true">
        新建请假
      </van-button>
    </div>

    <!-- 请假列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
      >
        <div v-for="item in leaves" :key="item.id" class="leave-item card">
          <div class="leave-header">
            <van-tag :type="getTypeTag(item.leave_type)">{{ item.leave_type_display }}</van-tag>
            <van-tag :type="getStatusTag(item.status)">{{ item.status_display }}</van-tag>
          </div>
          <div class="leave-body">
            <div class="leave-dates">
              {{ item.start_date }} 至 {{ item.end_date }}
              <span class="days">（{{ item.days }}天）</span>
            </div>
            <div class="leave-reason">{{ item.reason }}</div>
          </div>
          <div v-if="item.comments" class="leave-comments">
            <van-icon name="comment-o" />
            <span>{{ item.comments }}</span>
          </div>
        </div>
        
        <van-empty v-if="!loading && leaves.length === 0" description="暂无请假记录" />
      </van-list>
    </van-pull-refresh>

    <!-- 新建请假表单 -->
    <van-popup v-model:show="showForm" position="bottom" round style="height: 80%;">
      <div class="form-popup">
        <div class="form-header">
          <span @click="showForm = false">取消</span>
          <span class="title">新建请假</span>
          <span class="submit" @click="handleSubmit">提交</span>
        </div>
        
        <van-form ref="formRef">
          <van-cell-group inset>
            <van-field
              v-model="form.leave_type"
              is-link
              readonly
              label="请假类型"
              placeholder="请选择"
              @click="showTypePicker = true"
              :rules="[{ required: true, message: '请选择请假类型' }]"
            />
            <van-field
              v-model="form.dateRange"
              is-link
              readonly
              label="请假日期"
              placeholder="请选择"
              @click="showDatePicker = true"
              :rules="[{ required: true, message: '请选择请假日期' }]"
            />
            <van-field
              v-model="form.days"
              label="请假天数"
              readonly
            />
            <van-field
              v-model="form.reason"
              type="textarea"
              label="请假原因"
              placeholder="请输入请假原因"
              rows="3"
              maxlength="500"
              show-word-limit
              :rules="[{ required: true, message: '请输入请假原因' }]"
            />
          </van-cell-group>
        </van-form>
      </div>
    </van-popup>

    <!-- 类型选择器 -->
    <van-popup v-model:show="showTypePicker" position="bottom">
      <van-picker
        :columns="leaveTypes"
        @confirm="onTypeConfirm"
        @cancel="showTypePicker = false"
      />
    </van-popup>

    <!-- 日期选择器 -->
    <van-calendar
      v-model:show="showDatePicker"
      type="range"
      :show-confirm="true"
      @confirm="onDateConfirm"
      :min-date="minDate"
      :max-date="maxDate"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import api from '../utils/api'

const leaves = ref([])
const refreshing = ref(false)
const loading = ref(false)
const finished = ref(true)

const showForm = ref(false)
const showTypePicker = ref(false)
const showDatePicker = ref(false)
const formRef = ref(null)

const form = ref({
  leave_type: '',
  leave_type_value: '',
  dateRange: '',
  start_date: '',
  end_date: '',
  days: '',
  reason: '',
})

const leaveTypes = [
  { text: '病假', value: 'sick' },
  { text: '事假', value: 'personal' },
  { text: '年假', value: 'annual' },
  { text: '产假', value: 'maternity' },
  { text: '陪产假', value: 'paternity' },
  { text: '其他', value: 'other' },
]

// 日期范围限制
const minDate = new Date()
const maxDate = new Date()
maxDate.setFullYear(maxDate.getFullYear() + 1)

onMounted(() => {
  fetchLeaves()
})

async function fetchLeaves() {
  loading.value = true
  try {
    const res = await api.get('/api/leaves/')
    if (res.data.success) {
      leaves.value = res.data.data || []
    }
  } catch (e) {
    console.error(e)
  }
  loading.value = false
  refreshing.value = false
}

function onRefresh() {
  fetchLeaves()
}

function onTypeConfirm({ selectedOptions }) {
  form.value.leave_type = selectedOptions[0].text
  form.value.leave_type_value = selectedOptions[0].value
  showTypePicker.value = false
}

function onDateConfirm(dates) {
  const [start, end] = dates
  form.value.start_date = formatDate(start)
  form.value.end_date = formatDate(end)
  form.value.dateRange = `${form.value.start_date} 至 ${form.value.end_date}`
  form.value.days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
  showDatePicker.value = false
}

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

async function handleSubmit() {
  if (!form.value.leave_type_value) {
    showToast('请选择请假类型')
    return
  }
  if (!form.value.start_date) {
    showToast('请选择请假日期')
    return
  }
  if (!form.value.reason.trim()) {
    showToast('请输入请假原因')
    return
  }
  
  try {
    const res = await api.post('/api/leaves/', {
      leave_type: form.value.leave_type_value,
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      days: form.value.days,
      reason: form.value.reason,
    })
    
    if (res.data.success) {
      showSuccessToast('提交成功')
      showForm.value = false
      resetForm()
      fetchLeaves()
    } else {
      showToast(res.data.error?.message || '提交失败')
    }
  } catch (e) {
    showToast(e.response?.data?.error?.message || '提交失败')
  }
}

function resetForm() {
  form.value = {
    leave_type: '',
    leave_type_value: '',
    dateRange: '',
    start_date: '',
    end_date: '',
    days: '',
    reason: '',
  }
}

function getTypeTag(type) {
  const map = { sick: 'danger', personal: 'warning', annual: 'success' }
  return map[type] || 'primary'
}

function getStatusTag(status) {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'default'
}
</script>

<style scoped>
.action-bar {
  padding: 12px 16px;
  background: #fff;
}

.leave-item {
  margin: 12px 16px;
  padding: 16px;
}

.leave-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.leave-dates {
  font-size: 14px;
  color: #323233;
}

.days {
  color: #969799;
}

.leave-reason {
  font-size: 13px;
  color: #646566;
  margin-top: 8px;
  line-height: 1.5;
}

.leave-comments {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebedf0;
  font-size: 13px;
  color: #969799;
}

.form-popup {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ebedf0;
}

.form-header .title {
  font-size: 16px;
  font-weight: 500;
}

.form-header .submit {
  color: #1989fa;
}
</style>
