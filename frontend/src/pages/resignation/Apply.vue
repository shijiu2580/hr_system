<template>
  <div class="resign-apply-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1>离职申请</h1>
        <p class="header-subtitle">{{ employee?.name || '—' }} · {{ employee?.department?.name || '未分配部门' }}</p>
      </div>
      <div class="header-actions">
        <router-link to="/resignation/progress" class="btn btn-ghost">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回进度
        </router-link>
      </div>
    </header>

    <!-- 已有申请提示 -->
    <div v-if="hasPendingRequest" class="alert alert-warning">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <div>
        <p class="alert-title">您已有进行中的离职申请</p>
        <p class="alert-desc">当前申请审批完成后才能发起新申请。</p>
      </div>
      <router-link to="/resignation/progress" class="btn btn-sm">查看进度</router-link>
    </div>

    <!-- 申请表单 -->
    <section class="content-area" v-if="!hasPendingRequest">
      <article class="card form-card">
        <header class="card-header">
          <div>
            <h2>提交离职申请</h2>
            <p class="card-subtitle">请填写离职相关信息，提交后将进入审批流程</p>
          </div>
        </header>
        <form class="form-body" @submit.prevent="submitForm">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label required">交接开始日</label>
              <CustomDateInput v-model="form.startDate" placeholder="选择交接开始日期" />
            </div>
            <div class="form-group">
              <label class="form-label required">最后工作日</label>
              <CustomDateInput v-model="form.endDate" placeholder="选择最后工作日" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label required">离职原因</label>
            <textarea v-model="form.reason" class="form-textarea" placeholder="请详细说明离职原因..." rows="4" required></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">附件（可选）</label>
            <div class="upload-area" @click="triggerUpload" @dragover.prevent @drop.prevent="handleDrop">
              <input type="file" ref="fileInput" class="file-input" @change="handleFileChange" />
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              <p v-if="!form.file">点击或拖拽文件到此处上传</p>
              <p v-else class="file-name">{{ form.file.name }}</p>
              <span>支持 PDF、Word、图片等常见格式</span>
            </div>
          </div>
          <div class="form-actions">
            <router-link to="/resignation/progress" class="btn btn-ghost">取消</router-link>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting">提交中...</span>
              <span v-else>提交申请</span>
            </button>
          </div>
        </form>
      </article>

      <!-- 申请须知 -->
      <article class="card notice-card">
        <header class="card-header">
          <h2>申请须知</h2>
        </header>
        <div class="notice-body">
          <div class="notice-item">
            <div class="notice-icon">1</div>
            <div class="notice-content">
              <h4>提前通知</h4>
              <p>根据公司规定，普通员工需提前30天提交离职申请，管理层需提前60天。</p>
            </div>
          </div>
          <div class="notice-item">
            <div class="notice-icon">2</div>
            <div class="notice-content">
              <h4>审批流程</h4>
              <p>申请将依次经过直属上级审批和人事部门终审，请保持通讯畅通。</p>
            </div>
          </div>
          <div class="notice-item">
            <div class="notice-icon">3</div>
            <div class="notice-content">
              <h4>工作交接</h4>
              <p>审批通过后请及时完成工作交接，确保各项事务顺利移交。</p>
            </div>
          </div>
          <div class="notice-item">
            <div class="notice-icon">4</div>
            <div class="notice-content">
              <h4>离职结算</h4>
              <p>最后工作日后，人事部门将在5个工作日内完成工资结算和离职手续。</p>
            </div>
          </div>
        </div>
      </article>
    </section>

    <!-- 成功提示弹框 -->
    <Teleport to="body">
      <div v-if="showSuccessModal" class="modal-overlay" @click.self="goToProgress">
        <div class="modal-box success-modal">
          <div class="success-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M9 12l2 2 4-4" />
            </svg>
          </div>
          <h3>提交成功</h3>
          <p>您的离职申请已提交，请等待审批</p>
          <button class="btn btn-primary" @click="goToProgress">查看进度</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../utils/api';
import CustomDateInput from '../../components/CustomDateInput.vue';

const router = useRouter();

const employee = ref(null);
const resignations = ref([]);
const showSuccessModal = ref(false);
const submitting = ref(false);
const fileInput = ref(null);

const form = ref({
  startDate: '',
  endDate: '',
  reason: '',
  file: null,
});

const hasPendingRequest = computed(() => {
  return resignations.value.some(r => r.status === 'pending');
});

function triggerUpload() {
  fileInput.value?.click();
}

function handleFileChange(e) {
  const file = e.target.files?.[0];
  if (file) {
    form.value.file = file;
  }
}

function handleDrop(e) {
  const file = e.dataTransfer.files?.[0];
  if (file) {
    form.value.file = file;
  }
}

async function submitForm() {
  if (!form.value.startDate || !form.value.endDate || !form.value.reason) {
    alert('请填写所有必填项');
    return;
  }

  submitting.value = true;
  try {
    const formData = new FormData();
    formData.append('leave_type', 'resignation');
    formData.append('start_date', form.value.startDate);
    formData.append('end_date', form.value.endDate);
    formData.append('reason', form.value.reason);
    if (form.value.file) {
      formData.append('attachment', form.value.file);
    }

    const resp = await api.post('/leaves/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    if (resp.success) {
      showSuccessModal.value = true;
    } else {
      alert(resp.error?.message || '提交失败，请稍后重试');
    }
  } catch (e) {
    console.error(e);
    alert('提交失败，请稍后重试');
  } finally {
    submitting.value = false;
  }
}

async function fetchData() {
  try {
    const [empRes, resignRes] = await Promise.all([
      api.get('/employees/me/'),
      api.get('/leaves/?leave_type=resignation')
    ]);
    employee.value = empRes.data?.data || empRes.data;
    resignations.value = resignRes.data?.results || resignRes.data || [];
  } catch (e) {
    console.error(e);
  }
}

function goToProgress() {
  showSuccessModal.value = false;
  router.push('/resignation/progress');
}

onMounted(fetchData);
</script>

<style scoped>
.resign-apply-page {
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.header-left h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem;
}

.header-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.btn-ghost {
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-ghost:hover:not(:disabled) {
  background: #f3f4f6;
}

.btn-primary {
  background: #2563eb;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}

/* Alert */
.alert {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.alert-warning {
  background: #fffbeb;
  border: 1px solid #fcd34d;
}

.alert svg {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  stroke: #d97706;
}

.alert-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #92400e;
  margin: 0 0 0.25rem;
}

.alert-desc {
  font-size: 0.8125rem;
  color: #b45309;
  margin: 0;
}

.alert .btn {
  margin-left: auto;
  background: #f59e0b;
  color: #fff;
}

.alert .btn:hover {
  background: #d97706;
}

/* Content */
.content-area {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.card-header {
  padding: 1.25rem;
  border-bottom: 1px solid #f3f4f6;
}

.card-header h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem;
}

.card-subtitle {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0;
}

/* Form */
.form-body {
  padding: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1f2937;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1f2937;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: none;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

/* Upload */
.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #2563eb;
  background: #f8fafc;
}

.upload-area .file-input {
  display: none;
}

.upload-area svg {
  width: 40px;
  height: 40px;
  stroke: #9ca3af;
  margin-bottom: 0.75rem;
}

.upload-area p {
  font-size: 0.9375rem;
  color: #374151;
  margin: 0 0 0.25rem;
}

.upload-area span {
  font-size: 0.8125rem;
  color: #6b7280;
}

.upload-area .file-name {
  color: #2563eb;
  font-weight: 500;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
}

/* Notice */
.notice-body {
  padding: 1.25rem;
}

.notice-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 0;
}

.notice-item:not(:last-child) {
  border-bottom: 1px solid #f3f4f6;
}

.notice-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #eff6ff;
  color: #2563eb;
  font-size: 0.875rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notice-content h4 {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem;
}

.notice-content p {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0;
  line-height: 1.5;
}

/* Success Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-box {
  background: #fff;
  border-radius: 16px;
  padding: 2rem;
  max-width: 360px;
  width: 90%;
  text-align: center;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.success-modal .success-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  background: #d1fae5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-modal .success-icon svg {
  width: 32px;
  height: 32px;
  stroke: #059669;
}

.success-modal h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem;
}

.success-modal p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 1.5rem;
}

.success-modal .btn {
  width: 100%;
}
</style>
