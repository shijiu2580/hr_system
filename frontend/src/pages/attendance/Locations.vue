<template>
  <div class="page-grid">
    <div class="card">
      <div class="header">
        <div class="title">
          <img src="/icons/attendance.svg" alt="" class="icon" />
          <div>
            <h2>考勤地点</h2>
            <p class="sub">配置允许签到的地点与范围（默认 1km）</p>
          </div>
        </div>
        <div class="actions">
          <button class="btn btn-secondary" @click="load" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
          <button class="btn btn-primary" @click="openCreate" v-if="isStaff">
            新增地点
          </button>
        </div>
      </div>

      <div v-if="!isStaff" class="alert warn">
        仅管理员可维护考勤地点。
      </div>

      <div v-if="error" class="alert error">
        {{ error }}
        <button class="x" @click="error = ''">×</button>
      </div>

      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 70px;">默认</th>
              <th>名称</th>
              <th>地址</th>
              <th style="width: 120px;">范围(米)</th>
              <th style="width: 100px;">状态</th>
              <th style="width: 220px;">坐标</th>
              <th v-if="isStaff" style="width: 180px;">操作</th>
            </tr>
          </thead>
          <tbody v-if="!loading">
            <tr v-for="item in pagedLocations" :key="item.id">
              <td>
                <span class="tag" :class="item.is_default ? 'tag-primary' : 'tag-muted'">
                  {{ item.is_default ? '默认' : '—' }}
                </span>
              </td>
              <td>{{ item.name }}</td>
              <td class="muted">{{ item.address }}</td>
              <td>{{ item.radius }}</td>
              <td>
                <span
                  class="tag tag-clickable"
                  :class="item.is_active ? 'tag-success' : 'tag-muted'"
                  @click="isStaff && toggleStatus(item)"
                  :style="isStaff ? 'cursor: pointer;' : ''"
                  :title="isStaff ? '点击切换状态' : ''"
                >
                  {{ item.is_active ? '启用' : '停用' }}
                </span>
              </td>
              <td class="mono">
                {{ fmtCoord(item.longitude) }}, {{ fmtCoord(item.latitude) }}
              </td>
              <td v-if="isStaff">
                <button class="btn-link" @click="openEdit(item)">编辑</button>
                <button class="btn-link danger" @click="remove(item)" :disabled="saving">删除</button>
              </td>
            </tr>
            <tr v-if="locations.length === 0">
              <td :colspan="isStaff ? 7 : 6" class="empty">暂无考勤地点</td>
            </tr>
          </tbody>
        </table>
        <div v-if="loading" class="loading-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>

      <!-- 底部分页 -->
      <div class="table-footer">
        <span class="total-count">共 {{ locations.length }} 条</span>
        <div class="pagination">
          <span class="page-size-label">每页</span>
          <CustomSelect
            v-model="pageSize"
            :options="pageSizeOptions"
            class="page-size-custom-select"
            @change="currentPage = 1"
            :dropUp="true"
          />
          <span class="page-size-label">条</span>
          <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(1)">«</button>
          <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">‹</button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">›</button>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(totalPages)">»</button>
        </div>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>{{ editingId ? '编辑考勤地点' : '新增考勤地点' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>

        <div class="modal-body">
          <!-- 地图放在最上面 -->
          <div class="map-block">
            <AMapPicker v-model="picked" :radius="form.radius" />
          </div>

          <!-- 坐标显示 -->
          <div class="coord-display" v-if="form.latitude != null && form.longitude != null">
            <span class="coord-label">已选坐标：</span>
            <span class="coord-value">{{ fmtCoord(form.longitude) }}, {{ fmtCoord(form.latitude) }}</span>
          </div>
          <div class="coord-display empty-coord" v-else>
            <span class="coord-label">请在地图上点击或搜索选择位置</span>
          </div>

          <div class="form-fields">
            <div class="form-row">
              <label>名称 <span class="required">*</span></label>
              <input v-model.trim="form.name" type="text" placeholder="例如：总部大楼" />
            </div>

            <div class="form-row">
              <label>范围(米) <span class="required">*</span></label>
              <input v-model.number="form.radius" type="number" min="50" max="10000" placeholder="1000" />
            </div>

            <div class="form-row">
              <label>地址 <span class="required">*</span></label>
              <input v-model.trim="form.address" type="text" placeholder="选择地图位置后自动填充" />
            </div>

            <div class="form-row">
              <label>启用状态</label>
              <div class="checkbox-wrap">
                <input type="checkbox" id="is_active" v-model="form.is_active" />
                <label for="is_active">{{ form.is_active ? '已启用' : '已停用' }}</label>
              </div>
            </div>

            <div class="form-row">
              <label>设为默认</label>
              <div class="checkbox-wrap">
                <input type="checkbox" id="is_default" v-model="form.is_default" />
                <label for="is_default">{{ form.is_default ? '是（仅允许一个默认）' : '否' }}</label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModal">取消</button>
          <button class="btn-submit" @click="save" :disabled="saving || !canSave">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import api from '../../utils/api'
import { useAuthStore } from '../../stores/auth'
import AMapPicker from '../../components/AMapPicker.vue'
import CustomSelect from '../../components/CustomSelect.vue'

const auth = useAuthStore()
const isStaff = computed(() => !!auth.user?.is_staff)

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const locations = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

const pageSizeOptions = [
  { value: 5, label: '5' },
  { value: 10, label: '10' },
  { value: 20, label: '20' },
  { value: 50, label: '50' }
]

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(locations.value.length / pageSize.value))
})

const pagedLocations = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return locations.value.slice(start, end)
})

function goToPage(page) {
  if (page < 1) page = 1
  if (page > totalPages.value) page = totalPages.value
  currentPage.value = page
}

const showModal = ref(false)
const editingId = ref(null)

const form = ref({
  name: '',
  address: '',
  latitude: null,
  longitude: null,
  radius: 1000,
  is_active: true,
  is_default: false,
})

const picked = ref(null)

const canSave = computed(() => {
  return !!form.value.name && !!form.value.address && form.value.latitude != null && form.value.longitude != null
})

function fmtCoord(v) {
  if (v === null || v === undefined) return '--'
  const n = Number(v)
  if (Number.isNaN(n)) return String(v)
  return n.toFixed(6)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const resp = await api.get('/checkin-locations/')
    if (!resp.success) throw new Error(resp.error?.message || '加载失败')
    locations.value = Array.isArray(resp.data) ? resp.data : (resp.data?.results || resp.data || [])
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  picked.value = null
  form.value = {
    name: '',
    address: '',
    latitude: null,
    longitude: null,
    radius: 1000,
    is_active: true,
    is_default: false,
  }
  showModal.value = true
}

function openEdit(item) {
  editingId.value = item.id
  form.value = {
    name: item.name || '',
    address: item.address || '',
    latitude: item.latitude,
    longitude: item.longitude,
    radius: item.radius ?? 1000,
    is_active: !!item.is_active,
    is_default: !!item.is_default,
  }
  picked.value = {
    name: form.value.name,
    address: form.value.address,
    latitude: Number(form.value.latitude),
    longitude: Number(form.value.longitude),
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

watch(picked, (val) => {
  if (!val) return
  form.value.latitude = val.latitude
  form.value.longitude = val.longitude
  if (val.address) form.value.address = val.address
  if (val.name && !form.value.name) form.value.name = val.name
}, { deep: true })

async function save() {
  if (!isStaff.value) return
  saving.value = true
  error.value = ''
  try {
    const payload = {
      name: form.value.name,
      address: form.value.address,
      latitude: form.value.latitude,
      longitude: form.value.longitude,
      radius: form.value.radius,
      is_active: form.value.is_active,
      is_default: form.value.is_default,
    }

    const resp = editingId.value
      ? await api.put(`/checkin-locations/${editingId.value}/`, payload)
      : await api.post('/checkin-locations/', payload)

    if (!resp.success) throw new Error(resp.error?.message || '保存失败')

    showModal.value = false
    await load()
  } catch (e) {
    error.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}

async function remove(item) {
  if (!isStaff.value) return
  if (!confirm(`确定删除考勤地点：${item.name}？`)) return
  saving.value = true
  error.value = ''
  try {
    const resp = await api.delete(`/checkin-locations/${item.id}/`)
    if (!resp.success) throw new Error(resp.error?.message || '删除失败')
    await load()
  } catch (e) {
    error.value = e.message || '删除失败'
  } finally {
    saving.value = false
  }
}

async function toggleStatus(item) {
  if (!isStaff.value || saving.value) return
  saving.value = true
  error.value = ''
  try {
    const resp = await api.patch(`/checkin-locations/${item.id}/`, {
      is_active: !item.is_active
    })
    if (!resp.success) throw new Error(resp.error?.message || '切换失败')
    item.is_active = !item.is_active
  } catch (e) {
    error.value = e.message || '切换状态失败'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.page-grid {
  display: grid;
  gap: 16px;
}

.card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px;
  border-bottom: 1px solid #e5e7eb;
  background: #f8fafc;
}

.title {
  display: flex;
  gap: 10px;
  align-items: center;
}

.icon {
  width: 34px;
  height: 34px;
}

h2 {
  margin: 0;
  font-size: 16px;
}

.sub {
  margin: 2px 0 0;
  color: #64748b;
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  border: none;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-secondary {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-secondary:hover:not(:disabled) {
  background: #cbd5e1;
}

.table-wrapper {
  position: relative;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 12px 14px;
  border-bottom: 1px solid #eef2f7;
  font-size: 13px;
  text-align: left;
}

.data-table th {
  /* 使用全局样式 */
}

.muted {
  color: #64748b;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  color: #334155;
  font-size: 12px;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid transparent;
}

.tag-primary {
  background: #dbeafe;
  color: #1d4ed8;
  border-color: #bfdbfe;
}

.tag-success {
  background: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
}

.tag-muted {
  background: #f1f5f9;
  color: #64748b;
  border-color: #e2e8f0;
}

.tag-clickable:hover {
  opacity: 0.8;
  transform: scale(1.02);
}

.btn-link {
  background: transparent;
  border: none;
  color: #2563eb;
  cursor: pointer;
  padding: 0;
  margin-right: 10px;
  font-size: 13px;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-link.danger {
  color: #dc2626;
}

.loading {
  padding: 20px;
  display: flex;
  justify-content: center;
}

.spinner {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty {
  text-align: center;
  color: #94a3b8;
  padding: 22px 0;
}

.alert {
  margin: 12px 18px 0;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  border: 1px solid;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert.warn {
  background: #fffbeb;
  border-color: #fde68a;
  color: #92400e;
}

.alert.error {
  background: #fee2e2;
  border-color: #fecaca;
  color: #991b1b;
}

.x {
  background: transparent;
  border: none;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  color: inherit;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 16px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-content.modal-large {
  width: min(920px, 96vw);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eef2f7;
  background: #f8fafc;
  flex-shrink: 0;
}

.modal-header h3 {
  font-weight: 600;
  color: #0f172a;
  font-size: 16px;
  margin: 0;
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 22px;
  cursor: pointer;
  color: #64748b;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.map-block {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 16px;
}

.coord-display {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: #f0f9ff;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
  border: 1px solid #bae6fd;
}

.coord-display.empty-coord {
  background: #fefce8;
  border-color: #fde68a;
}

.coord-icon {
  font-size: 16px;
}

.coord-label {
  color: #475569;
}

.coord-value {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: #0f172a;
  font-weight: 600;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.form-row label {
  width: 80px;
  flex-shrink: 0;
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.form-row input[type="text"],
.form-row input[type="number"],
.form-row select {
  flex: 1;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: white;
}

.form-row input[type="text"]:focus,
.form-row input[type="number"]:focus,
.form-row select:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: none;
}

.checkbox-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.checkbox-wrap input[type="checkbox"] {
  appearance: none;
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border: 1.5px solid #1f2937;
  border-radius: 4px;
  background: transparent;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}

.checkbox-wrap input[type="checkbox"]:checked {
  background: #d1d5db;
  border-color: #1f2937;
}

.checkbox-wrap input[type="checkbox"]:focus {
  outline: none;
  box-shadow: none;
}

.checkbox-wrap input[type="checkbox"]:checked::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  color: #1f2937;
  font-weight: bold;
}

.checkbox-wrap label {
  width: auto;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
}

.required {
  color: #ef4444;
  margin-right: 2px;
}

.tip {
  margin-top: 16px;
  font-size: 12px;
  color: #475569;
  padding: 12px 14px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 3px solid #3b82f6;
  line-height: 1.5;
}

.tip strong {
  color: #1e40af;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eef2f7;
  background: #fafafa;
  flex-shrink: 0;
}

.btn-cancel {
  padding: 8px 20px;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-submit {
  padding: 8px 20px;
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-submit:hover {
  background: #1d4ed8;
}

.btn-submit:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

/* 底部分页 */
.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  border-top: 1px solid #eef2f7;
  background: #fafafa;
}

.total-count {
  font-size: 13px;
  color: #64748b;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-size-label {
  font-size: 13px;
  color: #64748b;
}

/* 分页下拉框样式 */
.page-size-custom-select {
  width: 70px;
}

.page-size-custom-select :deep(.select-trigger) {
  padding: 0.3rem 0.5rem;
  padding-right: 1.5rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 6px;
  background: #fff;
  min-height: auto;
}

.page-size-custom-select :deep(.select-trigger:hover) {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}

.page-size-custom-select :deep(.select-trigger:focus),
.page-size-custom-select :deep(.custom-select.open .select-trigger) {
  border-color: rgba(148, 163, 184, 0.6);
  box-shadow: none;
}

.page-size-custom-select :deep(.select-value) {
  font-size: 13px;
  color: #1e293b;
}

.page-size-custom-select :deep(.select-arrow) {
  color: #1e293b;
  width: 12px;
  height: 12px;
  right: 0.4rem;
}

.page-size-custom-select :deep(.select-dropdown) {
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 4px;
  min-width: 70px;
  top: auto;
  bottom: calc(100% + 4px);
}

.page-size-custom-select :deep(.select-option) {
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  text-align: center;
}

.page-size-custom-select :deep(.select-option:hover),
.page-size-custom-select :deep(.select-option.highlighted) {
  background: #f1f5f9;
  color: #1e293b;
}

.page-size-custom-select :deep(.select-option.selected) {
  background: #2563eb;
  color: #fff;
}

.page-size-custom-select :deep(.select-option.selected::before) {
  display: none;
}

.page-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #374151;
  min-width: 60px;
  text-align: center;
}
</style>
