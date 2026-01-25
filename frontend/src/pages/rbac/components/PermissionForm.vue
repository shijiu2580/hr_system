<template>
  <Teleport to="body">
    <transition name="modal">
      <div v-if="showPermForm" class="modal-overlay" @click.self="handleCancel">
        <div class="modal-container">
          <!-- 弹窗头部 -->
          <div class="modal-header">
            <div class="modal-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <h3>{{ editingPerm ? '编辑权限' : '新建权限' }}</h3>
            </div>
            <button class="close-btn" @click="handleCancel" type="button">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- 弹窗内容 -->
          <form @submit.prevent="handleSubmit" class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label>权限键 <span class="required">*</span></label>
                <input 
                  v-model.trim="permForm.key" 
                  required 
                  :disabled="!!editingPerm" 
                  placeholder="例如：employee.view" 
                />
                <span class="form-hint">权限的唯一标识符，创建后不可修改</span>
              </div>
              <div class="form-group">
                <label>权限名称 <span class="required">*</span></label>
                <input 
                  v-model.trim="permForm.name" 
                  required 
                  placeholder="例如：查看员工" 
                />
              </div>
            </div>
            <div class="form-group">
              <label>权限描述</label>
              <textarea 
                v-model.trim="permForm.description" 
                rows="3" 
                placeholder="可选，描述此权限的用途"
              ></textarea>
            </div>

            <!-- 弹窗底部 -->
            <div class="modal-footer">
              <button class="btn btn-primary" type="submit" :disabled="savingPerm">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                {{ savingPerm ? '保存中...' : '保存' }}
              </button>
              <button class="btn btn-secondary" type="button" @click="handleCancel">
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { useRbac } from '../composables/useRbac';

const {
  showPermForm,
  editingPerm,
  savingPerm,
  permForm,
  submitPerm,
  cancelPerm
} = useRbac();

function handleSubmit() {
  submitPerm();
}

function handleCancel() {
  cancelPerm();
}
</script>

<style scoped>
/* 弹窗遮罩 */
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
  padding: 1rem;
}

/* 弹窗容器 */
.modal-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 弹窗头部 */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-title svg {
  color: #2563eb;
}

.modal-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: #6b7280;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

/* 弹窗内容 */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
}

/* 表单网格 */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

@media (max-width: 500px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #dc2626;
}

.form-hint {
  font-size: 11px;
  color: #9ca3af;
}

.form-group input,
.form-group textarea {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: none;
}

.form-group input:disabled,
.form-group textarea:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

/* 弹窗底部 */
.modal-footer {
  display: flex;
  gap: 0.5rem;
  padding-top: 1rem;
  margin-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background: #2563eb;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 弹窗动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95) translateY(-20px);
}
</style>
