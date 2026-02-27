<template>
  <div class="page-grid attendance-page">
    <div class="card attendance-card">
      <!-- 顶部标签栏 -->
      <div class="tab-header">
        <div class="tab-left">
          <div class="tab-icon">
            <img src="/icons/attendance.svg" alt="" />
          </div>
          <span class="tab-title">今日考勤</span>
        </div>
        <button class="btn-refresh" @click="loadToday" :disabled="loading" title="刷新">
          <img src="/icons/refresh.svg" alt="" class="refresh-icon" />
        </button>
      </div>

      <!-- 签到签退操作区 -->
      <div class="punch-section">
        <div class="punch-info">
          <div class="current-time">{{ currentTime }}</div>
          <div class="current-date">{{ currentDateStr }}</div>
        </div>
        <div class="punch-actions">
          <button
            class="btn-punch btn-checkin"
            @click="handleCheckIn"
            :disabled="punching || (todayRecord && todayRecord.check_in_time)"
          >签到</button>
          <button
            class="btn-punch btn-checkout"
            @click="handleCheckOut"
            :disabled="punching || !todayRecord || !todayRecord.check_in_time"
          >{{ todayRecord && todayRecord.check_out_time ? '更新签退' : '签退' }}</button>
        </div>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-date">考勤日期</th>
              <th class="col-time">首打卡</th>
              <th class="col-time">末打卡</th>
              <th class="col-absent">缺勤时长</th>
              <th class="col-status">考勤状态</th>
              <th class="col-reason">异常原因</th>
            </tr>
          </thead>
          <tbody v-if="!loading && todayRecord">
            <tr class="data-row">
              <td class="col-date">
                <a href="javascript:;" class="date-link">{{ formatDateWithWeek(todayRecord.date) }}</a>
              </td>
              <td class="col-time">{{ todayRecord.check_in_time ? formatDateTime(todayRecord.date, todayRecord.check_in_time) : '--' }}</td>
              <td class="col-time">{{ todayRecord.check_out_time ? formatDateTime(todayRecord.date, todayRecord.check_out_time) : '--' }}</td>
              <td class="col-absent">{{ calcAbsentTime(todayRecord) }}</td>
              <td class="col-status">
                <span class="status-text" :class="'status-' + getStatus(todayRecord)">{{ getStatusLabel(todayRecord) }}</span>
              </td>
              <td class="col-reason">
                <template v-if="isWorkday && todayRecord.notes && formatReasonLines(todayRecord.notes).length">
                  <div v-for="(line, idx) in formatReasonLines(todayRecord.notes)" :key="idx" class="reason-line">{{ line }}</div>
                </template>
                <template v-else>--</template>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && !todayRecord" class="empty-state">
          今日暂无考勤记录
        </div>
      </div>

      <!-- 底部统计 -->
      <div class="table-footer">
        <span class="total-count">共{{ todayRecord ? 1 : 0 }}条</span>
      </div>
    </div>

    <!-- 原因输入弹窗 -->
    <div v-if="showReasonModal" class="modal-overlay" @click.self="cancelReason">
      <div class="modal-box">
        <div class="modal-header">
          <span class="modal-title">{{ reasonModalTitle }}</span>
          <button class="modal-close" @click="cancelReason">×</button>
        </div>
        <div class="modal-body">
          <p class="reason-hint">{{ reasonModalHint }}</p>
          <textarea
            v-model="reasonText"
            class="reason-input"
            placeholder="请输入原因..."
            rows="3"
          ></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="cancelReason">取消</button>
          <button class="btn-confirm" @click="confirmReason" :disabled="!reasonText.trim()">确认</button>
        </div>
      </div>
    </div>

    <!-- 消息弹窗 -->
    <div v-if="showMessageModal" class="message-modal-overlay" @click.self="closeMessageModal">
      <div class="message-modal-box">
        <div class="message-modal-text">{{ messageModalText }}</div>
        <button class="message-modal-btn" @click="closeMessageModal">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '../../utils/api';

const loading = ref(false);
const punching = ref(false);
const todayRecord = ref(null);
const currentTime = ref('');
const currentDateStr = ref('');

// 原因弹窗相关
const showReasonModal = ref(false);
const reasonModalTitle = ref('');
const reasonModalHint = ref('');
const reasonText = ref('');
const pendingAction = ref(null); // 'check_in' 或 'check_out'

// 消息弹窗相关
const showMessageModal = ref(false);
const messageModalText = ref('');

function showMessage(type, text) {
  messageModalText.value = text;
  showMessageModal.value = true;
}

function closeMessageModal() {
  showMessageModal.value = false;
}

let timer = null;

const weekDays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];

function formatDateWithWeek(dateStr) {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  const weekDay = weekDays[d.getDay()];
  return `${dateStr} ${weekDay}`;
}

// 格式化异常原因（迟到/早退原因分行显示）
function formatReasonLines(notes) {
  if (!notes) return [];
  const lines = [];
  const lateMatch = notes.match(/迟到原因[：:]\s*([^\s早]+)/);
  const earlyMatch = notes.match(/早退原因[：:]\s*(.+?)(?:\s*迟到|$)/);
  if (lateMatch) lines.push(`迟到原因：${lateMatch[1]}`);
  if (earlyMatch) lines.push(`早退原因：${earlyMatch[1].trim()}`);
  if (lines.length === 0 && notes.trim()) lines.push(notes);
  return lines;
}

function formatDateTime(dateStr, timeStr) {
  if (!timeStr) return '--';
  if (timeStr.includes('T') || timeStr.includes(' ')) {
    const d = new Date(timeStr);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }
  const parts = timeStr.split(':');
  const hh = String(parts[0]).padStart(2, '0');
  const mm = String(parts[1]).padStart(2, '0');
  const ss = parts[2] ? String(Math.floor(parseFloat(parts[2]))).padStart(2, '0') : '00';
  return `${dateStr} ${hh}:${mm}:${ss}`;
}

// 解析时间字符串，返回小时和分钟
function parseTime(timeStr) {
  if (!timeStr) return null;
  let hours, minutes;
  if (timeStr.includes('T') || timeStr.includes(' ')) {
    const d = new Date(timeStr);
    hours = d.getHours();
    minutes = d.getMinutes();
  } else {
    const parts = timeStr.split(':');
    hours = parseInt(parts[0]);
    minutes = parseInt(parts[1]);
  }
  return { hours, minutes, totalMinutes: hours * 60 + minutes };
}

// 是否为工作日（从后端获取）
const isWorkday = ref(true);

async function checkWorkday() {
  try {
    const resp = await api.get('/attendance/workday/');
    if (resp.success) {
      isWorkday.value = resp.data?.is_workday ?? true;
    }
  } catch {
    // 默认为工作日
    isWorkday.value = true;
  }
}

function getStatus(item) {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  const todayStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
  const dateStr = item?.date || todayStr;

  if (!item) {
    if (isWorkday.value && dateStr === todayStr) {
      const currentMinutes = now.getHours() * 60 + now.getMinutes();
      return currentMinutes > 9 * 60 ? 'late' : 'not_checked_in';
    }
    return isWorkday.value ? 'not_checked_in' : 'normal';
  }
  if (item.attendance_type === 'absent') return 'absent';

  // 非工作日（节假日/周末）签到统一视为加班
  if (!isWorkday.value) return 'overtime';

  // 检查是否迟到（9:00后签到）
  const checkIn = parseTime(item.check_in_time);

  // 工作日：仅当天没签到且当前时间超过9点，视为迟到
  if (dateStr === todayStr && !checkIn) {
    const currentMinutes = now.getHours() * 60 + now.getMinutes();
    if (currentMinutes > 9 * 60) {
      return 'late';
    }
    return 'not_checked_in';
  }

  const isLate = checkIn && checkIn.totalMinutes > 9 * 60;

  // 检查是否早退（没签退 或 18:00前签退）
  const checkOut = parseTime(item.check_out_time);
  // 工作日：有签到但没签退，且当前时间超过18点，视为早退
  let isEarlyLeave = false;
  if (checkIn && !checkOut) {
    const now = new Date();
    const currentMinutes = now.getHours() * 60 + now.getMinutes();
    // 超过18点还没签退，判定为早退
    if (currentMinutes >= 18 * 60) {
      isEarlyLeave = true;
    }
  } else if (checkOut) {
    isEarlyLeave = checkOut.totalMinutes < 18 * 60;
  }

  if (isLate && isEarlyLeave) return 'late_and_early';
  if (isLate) return 'late';
  if (isEarlyLeave) return 'early_leave';

  return 'normal';
}

function getStatusLabel(item) {
  if (!item) return isWorkday.value ? '未签到' : '休息日';
  const status = getStatus(item);
  const map = {
    normal: '正常',
    overtime: '加班',
    late: '迟到',
    early_leave: '早退',
    late_and_early: '迟到/早退',
    absent: '缺勤',
    not_checked_in: '未签到'
  };
  const statusText = map[status] || '正常';
  // 判断是否是补签数据
  const isSupplement = item.notes && (item.notes.includes('补签到') || item.notes.includes('补签退'));
  return isSupplement ? `补签:${statusText}` : statusText;
}

// 计算缺勤时长（午休12:00-13:00不计算）
function calcAbsentTime(item) {
  // 休息日/节假日：加班，缺勤为0
  if (!isWorkday.value) return '0 分钟';
  if (!item || !item.check_out_time) return '--';

  const WORK_START = 9 * 60;     // 上班 9:00
  const LUNCH_START = 12 * 60;   // 午休开始 12:00
  const LUNCH_END = 13 * 60;     // 午休结束 13:00
  const WORK_END = 18 * 60;      // 下班 18:00
  const TOTAL_WORK = 8 * 60;     // 总工作时长 480分钟（不含午休）

  const parseMinutes = (timeStr) => {
    if (!timeStr) return null;
    if (timeStr.includes('T') || timeStr.includes(' ')) {
      const d = new Date(timeStr);
      return d.getHours() * 60 + d.getMinutes();
    }
    const parts = timeStr.split(':');
    return parseInt(parts[0]) * 60 + parseInt(parts[1]);
  };

  // 计算某个时间段内的有效工作分钟数（排除午休 12:00-13:00）
  const calcWorkMinutes = (from, to) => {
    if (from >= to) return 0;
    let minutes = to - from;
    const overlapStart = Math.max(from, LUNCH_START);
    const overlapEnd = Math.min(to, LUNCH_END);
    if (overlapStart < overlapEnd) {
      minutes -= (overlapEnd - overlapStart);
    }
    return Math.max(0, minutes);
  };

  const checkIn = parseMinutes(item.check_in_time);
  const checkOut = parseMinutes(item.check_out_time);

  // 实际签到时间（不早于上班时间）
  const effectiveIn = checkIn !== null ? Math.max(checkIn, WORK_START) : WORK_START;
  // 实际签退时间（不晚于下班时间）
  const effectiveOut = Math.min(checkOut, WORK_END);

  const workedMinutes = calcWorkMinutes(effectiveIn, effectiveOut);
  const absentMinutes = Math.max(0, TOTAL_WORK - workedMinutes);

  if (absentMinutes <= 0) {
    return '0 分钟';
  }

  if (absentMinutes >= 60) {
    const hours = Math.floor(absentMinutes / 60);
    const mins = absentMinutes % 60;
    return mins > 0 ? `${hours} 小时 ${mins} 分钟` : `${hours} 小时`;
  }
  return `${absentMinutes} 分钟`;
}

async function loadToday() {
  loading.value = true;
  const resp = await api.get('/attendance/today/');
  if (resp.success) {
    todayRecord.value = resp.data || null;
  }
  loading.value = false;
}

function updateClock() {
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  currentTime.value = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  const weekDay = weekDays[now.getDay()];
  currentDateStr.value = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} ${weekDay}`;
}

async function handleCheckIn() {
  const now = new Date();
  const hours = now.getHours();
  // 工作日9:00后签到算迟到，需要填原因；休息日/节假日不判断迟到（算加班签到）
  const isLate = isWorkday.value && hours >= 9;

  if (isLate) {
    // 迟到需要填写原因
    reasonModalTitle.value = '迟到签到';
    reasonModalHint.value = '当前时间已超过 09:00，请填写迟到原因：';
    reasonText.value = '';
    pendingAction.value = 'check_in';
    showReasonModal.value = true;
  } else {
    // 正常签到或加班签到
    await doCheckIn('');
  }
}

async function handleCheckOut() {
  const now = new Date();
  const hours = now.getHours();
  // 工作日18:00前签退算早退，需要填原因；休息日/节假日不判断早退（算加班签退）
  const isEarlyLeave = isWorkday.value && hours < 18;
  const isUpdate = todayRecord.value && todayRecord.value.check_out_time;

  if (isEarlyLeave && !isUpdate) {
    // 首次签退且早退需要填写原因
    reasonModalTitle.value = '早退签退';
    reasonModalHint.value = '当前时间早于 18:00，请填写早退原因：';
    reasonText.value = '';
    pendingAction.value = 'check_out';
    showReasonModal.value = true;
  } else if (isUpdate) {
    // 更新签退时间
    await doUpdateCheckOut();
  } else {
    // 正常签退或加班签退
    await doCheckOut('');
  }
}

async function doCheckIn(notes) {
  punching.value = true;
  try {
    const resp = await api.post('/attendance/check/', { action: 'check_in', notes });
    if (resp.success) {
      showMessage('success', '签到成功！');
      await loadToday();
    } else {
      showMessage('error', resp.error?.message || '签到失败');
    }
  } catch (e) {
    const msg = e.response?.data?.error?.message || e.response?.data?.message || e.message || '网络错误';
    showMessage('error', '签到失败：' + msg);
  }
  punching.value = false;
}

async function doCheckOut(notes) {
  punching.value = true;
  try {
    const resp = await api.post('/attendance/check/', { action: 'check_out', notes });
    if (resp.success) {
      showMessage('success', '签退成功！');
      await loadToday();
    } else {
      showMessage('error', resp.error?.message || '签退失败');
    }
  } catch (e) {
    const msg = e.response?.data?.error?.message || e.response?.data?.message || e.message || '网络错误';
    showMessage('error', '签退失败：' + msg);
  }
  punching.value = false;
}

async function doUpdateCheckOut() {
  punching.value = true;
  try {
    const resp = await api.post('/attendance/check/', { action: 'update_check_out' });
    if (resp.success) {
      showMessage('success', '签退时间已更新！');
      await loadToday();
    } else {
      showMessage('error', resp.error?.message || '更新失败');
    }
  } catch (e) {
    const msg = e.response?.data?.error?.message || e.response?.data?.message || e.message || '网络错误';
    showMessage('error', '更新失败：' + msg);
  }
  punching.value = false;
}

function cancelReason() {
  showReasonModal.value = false;
  reasonText.value = '';
  pendingAction.value = null;
}

async function confirmReason() {
  if (!reasonText.value.trim()) return;
  showReasonModal.value = false;

  if (pendingAction.value === 'check_in') {
    await doCheckIn(reasonText.value.trim());
  } else if (pendingAction.value === 'check_out') {
    await doCheckOut(reasonText.value.trim());
  }

  reasonText.value = '';
  pendingAction.value = null;
}

onMounted(() => {
  checkWorkday();
  loadToday();
  updateClock();
  timer = setInterval(updateClock, 1000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.attendance-page {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.attendance-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}

/* 顶部标签栏 */
.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f8fafc;
}

.tab-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.tab-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2563eb;
  border-radius: 8px;
}

.tab-icon img {
  width: 20px;
  height: 20px;
  filter: brightness(0) invert(1);
}

.tab-title {
  font-size: 16px;
  font-weight: 600;
  color: #2563eb;
}

/* 签到签退区域 */
.punch-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 1.25rem;
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  color: white;
  border-radius: 12px;
  margin: 1rem;
}

.punch-info {
  text-align: left;
}

.current-time {
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: 2px;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.current-date {
  font-size: 1rem;
  opacity: 0.9;
}

.punch-actions {
  display: flex;
  gap: 1rem;
}

.btn-punch {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border: none;
  border-radius: 16px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-punch:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-checkin {
  background: white;
  color: #16a34a;
}

.btn-checkin:not(:disabled):hover {
  background: #f0fdf4;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.btn-checkout {
  background: white;
  color: #dc2626;
}

.btn-checkout:not(:disabled):hover {
  background: #fef2f2;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.btn-refresh {
  padding: 0.375rem;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px;
}

.btn-refresh:hover {
  background: #f3f4f6;
}

.refresh-icon {
  width: 16px;
  height: 16px;
  opacity: 0.6;
}

/* 表格 */
.table-wrapper {
  position: relative;
  min-height: 100px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
  vertical-align: middle;
}

.data-row:hover {
  background: #fafafa;
}

.col-date { min-width: 180px; }
.col-time { min-width: 160px; }
.col-absent { min-width: 100px; }
.col-status { min-width: 100px; }
.col-reason { min-width: 120px; color: #9ca3af; }
.reason-line { line-height: 1.5; }
.reason-line + .reason-line { margin-top: 4px; }

.date-link {
  color: #2563eb;
  text-decoration: none;
}

.date-link:hover {
  text-decoration: underline;
}

.status-text {
  font-weight: 500;
}

.status-text.status-normal { color: #059669; }
.status-text.status-overtime { color: #2563eb; }
.status-text.status-late { color: #d97706; }
.status-text.status-early_leave { color: #d97706; }
.status-text.status-late_and_early { color: #dc2626; }
.status-text.status-absent { color: #dc2626; }
.status-text.status-not_checked_in { color: #d97706; }

/* 加载状态 */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #9ca3af;
  font-size: 14px;
}

/* 底部统计 */
.table-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #e5e7eb;
  font-size: 13px;
  color: #6b7280;
}

/* 原因输入弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-box {
  background: white;
  border-radius: 12px;
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  animation: modalIn 0.2s ease-out;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #9ca3af;
  cursor: pointer;
  line-height: 1;
  padding: 0;
}

.modal-close:hover {
  color: #4b5563;
}

.modal-body {
  padding: 1.25rem;
}

.reason-hint {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 0.75rem;
}

.reason-input {
  width: calc(100% - 0.15rem);
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
}

.reason-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: none;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #4b5563;
  font-size: 14px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #f3f4f6;
}

.btn-confirm {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: #2563eb;
  color: white;
  font-size: 14px;
  cursor: pointer;
}

.btn-confirm:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 消息弹窗 */
.message-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 20vh;
  z-index: 9999;
}

.message-modal-box {
  background: white;
  border-radius: 8px;
  padding: 1.5rem 2rem;
  text-align: center;
  min-width: 240px;
  max-width: 320px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  animation: modalIn 0.2s ease-out;
}

.message-modal-text {
  font-size: 15px;
  color: #1f2937;
  margin-bottom: 1.25rem;
  line-height: 1.5;
  text-align: center;
}

.message-modal-btn {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: #2563eb;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.message-modal-btn:hover {
  background: #1d4ed8;
}
</style>
