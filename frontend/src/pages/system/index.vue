<template>
  <div class="system-page">
    <section class="hero-panel">
      <div class="hero-info">
        <div class="hero-icon">
          <img src="/icons/system.svg" alt="" style="width:100%;height:100%;" />
        </div>
        <div>
          <h1>系统维护</h1>
          <p class="hero-text">数据备份与日志管理</p>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn-primary icon-btn" @click="createBackup" :disabled="creating">
          <img src="/icons/add.svg" alt="" class="btn-icon" />
          <span>{{ creating ? '创建中...' : '一键备份' }}</span>
        </button>
        <button class="btn-secondary icon-btn" @click="reloadAll" :disabled="loadingBackups || loadingLogs">
          <img src="/icons/refresh.svg" alt="" class="btn-icon" />
          <span>刷新</span>
        </button>
      </div>
    </section>

    <section class="card metrics-card">
      <header class="card-header">
        <div class="section-title">
          <img src="/icons/stats.svg" alt="" class="section-icon" />
          <h2>运行概览</h2>
        </div>
      </header>
      <div class="metrics-grid">
        <div class="metric-card">
          <span class="metric-label">备份数量</span>
          <strong class="metric-value">{{ backupStats.count }}</strong>
          <span class="metric-desc">累计占用 {{ formatSize(backupStats.totalSize) }}</span>
        </div>
        <div class="metric-card highlight">
          <span class="metric-label">最近备份</span>
          <strong class="metric-value text-sm">{{ backupStats.latestName || '暂无' }}</strong>
          <span class="metric-desc">{{ backupStats.latestSize ? formatSize(backupStats.latestSize) : '等待首次备份' }}</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">日志总量</span>
          <strong class="metric-value">{{ logStats.total }}</strong>
          <span class="metric-desc">窗口内已加载记录</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">异常告警</span>
          <strong class="metric-value">{{ logStats.errorCount }}</strong>
          <span class="metric-desc">WARNING {{ logStats.warningCount }} 条</span>
        </div>
      </div>
    </section>

    <!-- 系统信息卡片 -->
    <section class="card system-info-card">
      <header class="card-header">
        <div class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 16v-4M12 8h.01" />
          </svg>
          <h2>系统信息</h2>
        </div>
        <div class="card-actions">
          <span class="status-indicator" :class="healthStatus">
            <span class="status-dot"></span>
            {{ healthStatus === 'ok' ? '运行正常' : healthStatus === 'loading' ? '检测中...' : '异常' }}
          </span>
          <button class="btn-secondary btn-sm" @click="loadHealth" :disabled="loadingHealth">
            {{ loadingHealth ? '检测中...' : '刷新状态' }}
          </button>
        </div>
      </header>
      <div v-if="loadingHealth" class="info-loading">
        <div class="spinner-small"></div>
        <span>正在获取系统信息...</span>
      </div>
      <div v-else-if="healthData" class="system-info-grid">
        <div class="info-group">
          <h4>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2" />
              <path d="M8 21h8M12 17v4" />
            </svg>
            运行环境
          </h4>
          <div class="info-items">
            <div class="info-item">
              <span class="info-label">Python 版本</span>
              <span class="info-value">{{ healthData.system_info?.python_version || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Django 版本</span>
              <span class="info-value">{{ healthData.system_info?.django_version || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">调试模式</span>
              <span class="info-value" :class="healthData.system_info?.debug_mode ? 'warn' : ''">
                {{ healthData.system_info?.debug_mode ? '开启' : '关闭' }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">时区</span>
              <span class="info-value">{{ healthData.system_info?.timezone || '-' }}</span>
            </div>
          </div>
        </div>
        <div class="info-group">
          <h4>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16v6H4zM4 14h16v6H4z" />
              <path d="M8 8h.01M8 18h.01" />
            </svg>
            存储空间
          </h4>
          <div class="info-items">
            <div class="info-item">
              <span class="info-label">数据库大小</span>
              <span class="info-value highlight">{{ formatSize(healthData.storage?.database_size) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">媒体文件</span>
              <span class="info-value">{{ formatSize(healthData.storage?.media_size) }}</span>
            </div>
          </div>
        </div>
        <div class="info-group">
          <h4>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 3v18h18" />
              <path d="M18 9l-5 5-4-4-3 3" />
            </svg>
            数据统计
          </h4>
          <div class="info-items stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ healthData.statistics?.total_employees || 0 }}</span>
              <span class="stat-label">员工总数</span>
            </div>
            <div class="stat-item active">
              <span class="stat-value">{{ healthData.statistics?.active_employees || 0 }}</span>
              <span class="stat-label">在职员工</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ healthData.statistics?.total_departments || 0 }}</span>
              <span class="stat-label">部门数量</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ healthData.statistics?.total_attendance || 0 }}</span>
              <span class="stat-label">考勤记录</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ healthData.statistics?.total_leaves || 0 }}</span>
              <span class="stat-label">请假申请</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ healthData.statistics?.total_salaries || 0 }}</span>
              <span class="stat-label">薪资记录</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="info-empty">
        <p>点击"刷新状态"获取系统详细信息</p>
      </div>
    </section>

    <section class="card backup-card">
      <header class="card-header">
        <div class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 4h16v6H4z" />
            <path d="M4 14h16v6H4z" />
            <path d="M10 8v8" />
            <path d="M14 8v8" />
          </svg>
          <h2>备份文件</h2>
        </div>
        <div class="card-actions">
          <button class="btn-secondary btn-sm" @click="cleanBackups" :disabled="cleaning">{{ cleaning ? '清理中...' : '清理旧备份' }}</button>
        </div>
      </header>
      <p class="section-hint">备份文件按时间倒序排列，恢复操作会自动创建安全副本。</p>
      <div class="alert-stack">
        <transition name="fade">
          <div v-if="errorBackup" class="alert alert-error">
            <span>{{ errorBackup }}</span>
            <button class="alert-close" @click="errorBackup = ''">×</button>
          </div>
        </transition>
        <transition name="fade">
          <div v-if="successBackup" class="alert alert-success">
            <span>{{ successBackup }}</span>
            <button class="alert-close" @click="successBackup = ''">×</button>
          </div>
        </transition>
      </div>
      <div class="table-wrapper">
        <div v-if="loadingBackups" class="table-skeleton">
          <div class="skeleton-row" v-for="n in 5" :key="n"></div>
        </div>
        <table v-else-if="backups.length" class="data-table">
          <thead>
            <tr>
              <th>文件名</th>
              <th>大小</th>
              <th class="col-compact">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in backups" :key="b.name">
              <td>
                <div class="file-name">{{ b.name }}</div>
                <small class="file-meta">自动保留最近 5 个</small>
              </td>
              <td>{{ formatSize(b.size) }}</td>
              <td>
                <button class="btn-ghost btn-xs" @click="restore(b)" :disabled="restoringName === b.name">
                  {{ restoringName === b.name ? '恢复中...' : '恢复' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty">暂无备份文件，建议立即创建第一份备份。</p>
      </div>
    </section>

    <section class="card logs-card">
      <header class="card-header">
        <div class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 4h14" />
            <path d="M5 8h14" />
            <path d="M5 12h14" />
            <path d="M5 16h8" />
          </svg>
          <h2>系统日志</h2>
        </div>
        <div class="card-actions">
          <button class="btn-secondary btn-sm" @click="reloadLogs" :disabled="loadingLogs">{{ loadingLogs ? '刷新中...' : '刷新' }}</button>
          <button class="btn-danger btn-sm" @click="clearLogs" :disabled="clearingLogs">{{ clearingLogs ? '清空中...' : '清空筛选结果' }}</button>
        </div>
      </header>
      <div class="filter-bar">
        <div class="filter-row">
          <div class="filter-field">
            <span class="filter-label">日志级别</span>
            <CustomSelect
              v-model="levelFilter"
              :options="[
                { value: '', label: '全部级别' },
                { value: 'INFO', label: 'INFO' },
                { value: 'WARNING', label: 'WARNING' },
                { value: 'ERROR', label: 'ERROR' },
                { value: 'DEBUG', label: 'DEBUG' }
              ]"
              placeholder="全部级别"
              @change="reloadLogs"
            />
          </div>
          <div class="filter-field">
            <span class="filter-label">操作用户</span>
            <CustomSelect
              v-model="userFilter"
              :options="userOptions"
              placeholder="全部用户"
              @change="reloadLogs"
            />
          </div>
          <div class="filter-field">
            <span class="filter-label">关键字搜索</span>
            <div class="search-input-wrapper">
              <img class="search-icon" src="/icons/search.svg" alt="" />
              <input v-model.trim="logKeyword" placeholder="搜索动作或详情..." class="search-input" />
            </div>
          </div>
        </div>
        <div class="filter-summary" v-if="levelFilter || userFilter || logKeyword">
          <span class="summary-text">
            筛选条件：
            <span v-if="levelFilter" class="filter-tag">{{ levelFilter }} <button @click="levelFilter='';reloadLogs()">×</button></span>
            <span v-if="userFilter" class="filter-tag">{{ userFilter === 'system' ? '系统' : userFilter }} <button @click="userFilter='';reloadLogs()">×</button></span>
            <span v-if="logKeyword" class="filter-tag">"{{ logKeyword }}" <button @click="logKeyword=''">×</button></span>
          </span>
          <button class="clear-all-btn" @click="clearFilters">清除全部</button>
        </div>
      </div>
      <div class="alert-stack">
        <transition name="fade">
          <div v-if="errorLogs" class="alert alert-error">
            <span>{{ errorLogs }}</span>
            <button class="alert-close" @click="errorLogs = ''">×</button>
          </div>
        </transition>
        <transition name="fade">
          <div v-if="successLogs" class="alert alert-success">
            <span>{{ successLogs }}</span>
            <button class="alert-close" @click="successLogs = ''">×</button>
          </div>
        </transition>
      </div>
      <div class="log-panel">
        <div v-if="loadingLogs" class="table-skeleton">
          <div class="skeleton-row" v-for="n in 6" :key="`log-${n}`"></div>
        </div>
        <table v-else-if="filteredLogs.length" class="data-table logs-table">
          <thead>
            <tr>
              <th style="width:160px;">时间</th>
              <th style="width:90px;">级别</th>
              <th style="width:100px;">用户</th>
              <th>动作 / 详情</th>
              <th style="width:120px;">IP地址</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in filteredLogs" :key="l.id">
              <td class="time-cell">{{ formatTs(l.timestamp) }}</td>
              <td><span class="status-pill" :class="levelClass(l.level)">{{ l.level }}</span></td>
              <td class="user-cell">{{ l.user?.username || '系统' }}</td>
              <td>
                <div class="log-text">
                  <strong>{{ l.action }}</strong>
                  <span v-if="l.detail">{{ l.detail }}</span>
                </div>
              </td>
              <td class="ip-cell">{{ l.ip_address || '-' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p>未查询到相关日志</p>
          <span>尝试放宽筛选条件或刷新</span>
        </div>
      </div>
      <div class="log-footer" v-if="filteredLogs.length">
        <span class="log-count">共 {{ filteredLogs.length }} 条日志</span>
      </div>
    </section>

    <!-- 清理备份确认弹窗 -->
    <div v-if="showCleanBackupModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>确认清理旧备份</h3>
          <button class="modal-close" @click="showCleanBackupModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-message">
            <p>确定要清理旧的备份文件吗？</p>
          </div>
          <p class="confirm-hint">
            系统将保留最近的 <strong>5</strong> 个备份文件，其余旧文件将被永久删除以释放空间。
          </p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showCleanBackupModal = false">取消</button>
          <button class="btn-danger" @click="confirmCleanBackups">确认清理</button>
        </div>
      </div>
    </div>

    <!-- 清空日志确认弹窗 -->
    <div v-if="showClearLogModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>确认清空日志</h3>
          <button class="modal-close" @click="showClearLogModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-message">
            <p>确定要清空符合当前筛选条件的日志吗？</p>
          </div>
          <p class="confirm-hint" v-if="levelFilter || userFilter || logKeyword">
            当前筛选：
            <span v-if="levelFilter">级别:{{ levelFilter }} </span>
            <span v-if="userFilter">用户:{{ userFilter }} </span>
            <span v-if="logKeyword">关键词:{{ logKeyword }}</span>
          </p>
          <p class="confirm-hint" v-else>
            这将清空 <strong>所有</strong> 系统日志，此操作不可恢复！
          </p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showClearLogModal = false">取消</button>
          <button class="btn-danger" @click="confirmClearLogs">确认清空</button>
        </div>
      </div>
    </div>

    <!-- 无备份提示弹窗 -->
    <div v-if="showNoBackupsModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>提示</h3>
          <button class="modal-close" @click="showNoBackupsModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-message">
            <p>暂时没有旧备份文件需要清理。</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="showNoBackupsModal = false">知道了</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'

// ==================== 备份管理 ====================
const backups = ref([])
const loadingBackups = ref(false)
const creating = ref(false)
const cleaning = ref(false)
const restoringName = ref(null)
const errorBackup = ref('')
const successBackup = ref('')

const backupStats = computed(() => {
  const list = backups.value || []
  const totalSize = list.reduce((sum, item) => sum + (item.size || 0), 0)
  const latest = list[0] || null

  return {
    count: list.length,
    totalSize,
    latestName: latest?.name || '',
    latestSize: latest?.size || 0,
  }
})

async function loadBackups() {
  loadingBackups.value = true
  errorBackup.value = ''

  try {
    const resp = await api.get('/backups/')
    if (resp.success) {
      backups.value = resp.data?.backups || []
    } else {
      errorBackup.value = resp.error?.message || '加载备份失败'
    }
  } catch (e) {
    errorBackup.value = '加载备份失败'
  } finally {
    loadingBackups.value = false
  }
}

async function createBackup() {
  creating.value = true
  errorBackup.value = ''
  successBackup.value = ''

  try {
    const resp = await api.post('/backups/create/')
    if (resp.success) {
      successBackup.value = resp.data?.detail || '创建成功'
      await loadBackups()
    } else {
      errorBackup.value = resp.error?.message || '创建失败'
    }
  } catch (e) {
    errorBackup.value = '创建失败'
  } finally {
    creating.value = false
  }
}

const showCleanBackupModal = ref(false)
const showNoBackupsModal = ref(false)

async function cleanBackups() {
  if (backups.value.length === 0) {
    showNoBackupsModal.value = true
    return
  }
  // Open the confirmation modal instead of using confirm()
  showCleanBackupModal.value = true
}

async function confirmCleanBackups() {
  showCleanBackupModal.value = false
  cleaning.value = true
  errorBackup.value = ''
  successBackup.value = ''

  try {
    const resp = await api.post('/backups/clean/', { keep: 5 })
    if (resp.success) {
      successBackup.value = resp.data?.detail || '清理完成'
      await loadBackups()
    } else {
      errorBackup.value = resp.error?.message || '清理失败'
    }
  } catch (e) {
    errorBackup.value = '清理失败'
  } finally {
    cleaning.value = false
  }
}

async function restore(b) {
  if (!confirm(`确认将 ${b.name} 恢复？将生成自动备份副本。`)) return

  restoringName.value = b.name
  errorBackup.value = ''
  successBackup.value = ''

  try {
    const resp = await api.post('/backups/restore/', { filename: b.name })
    if (resp.success) {
      successBackup.value = resp.data?.detail || '恢复成功'
    } else {
      errorBackup.value = resp.error?.message || '恢复失败'
    }
  } catch (e) {
    errorBackup.value = '恢复失败'
  } finally {
    restoringName.value = null
  }
}

// ==================== 日志管理 ====================
const logs = ref([])
const loadingLogs = ref(false)
const clearingLogs = ref(false)
const errorLogs = ref('')
const successLogs = ref('')
const levelFilter = ref('')
const userFilter = ref('')
const logKeyword = ref('')

// 用户列表选项（从日志中提取）
const userOptions = computed(() => {
  const users = new Set()

  logs.value.forEach(l => {
    if (l.user?.username) users.add(l.user.username)
  })

  const options = [
    { value: '', label: '全部用户' },
    { value: 'system', label: '系统' }
  ]

  users.forEach(u => options.push({ value: u, label: u }))

  return options
})

// 清除所有筛选条件
function clearFilters() {
  levelFilter.value = ''
  userFilter.value = ''
  logKeyword.value = ''
  reloadLogs()
}

const logStats = computed(() => {
  const list = logs.value || []

  return {
    total: list.length,
    errorCount: list.filter(item => item.level === 'ERROR').length,
    warningCount: list.filter(item => item.level === 'WARNING').length,
  }
})

async function reloadLogs() {
  loadingLogs.value = true
  errorLogs.value = ''

  try {
    const params = levelFilter.value ? { level: levelFilter.value } : {}
    const resp = await api.get('/logs/', { params })
    if (resp.success) {
      logs.value = resp.data?.results || resp.data || []
    } else {
      errorLogs.value = resp.error?.message || '加载日志失败'
    }
  } catch (e) {
    errorLogs.value = '加载日志失败'
  } finally {
    loadingLogs.value = false
  }
}

const showClearLogModal = ref(false)

function openClearLogModal() {
  if (filteredLogs.value.length === 0) return
  showClearLogModal.value = true
}

async function confirmClearLogs() {
  showClearLogModal.value = false
  clearingLogs.value = true
  errorLogs.value = ''
  successLogs.value = ''

  try {
    const payload = levelFilter.value ? { level: levelFilter.value } : {}
    const resp = await api.post('/logs/clear/', payload)
    if (resp.success) {
      successLogs.value = resp.data?.detail || '已清空'
      await reloadLogs()
    } else {
      errorLogs.value = resp.error?.message || '清空失败'
    }
  } catch (e) {
    errorLogs.value = '清空失败'
  } finally {
    clearingLogs.value = false
  }
}

async function clearLogs() {
  // Deprecated direct call, use openClearLogModal instead
  openClearLogModal()
}

const filteredLogs = computed(() => {
  let result = logs.value

  // 用户筛选
  if (userFilter.value) {
    if (userFilter.value === 'system') {
      result = result.filter(l => !l.user)
    } else {
      result = result.filter(l => l.user?.username === userFilter.value)
    }
  }

  // 关键字筛选
  const kw = logKeyword.value.trim().toLowerCase()
  if (kw) {
    result = result.filter(l =>
      (l.action && l.action.toLowerCase().includes(kw)) ||
      (l.detail && l.detail.toLowerCase().includes(kw))
    )
  }

  return result
})

function levelClass(l) {
  if (l === 'ERROR') return 'danger'
  if (l === 'WARNING') return 'warning'
  if (l === 'INFO') return 'success'
  if (l === 'DEBUG') return 'debug'
  return ''
}

function formatTs(ts) {
  try {
    return new Date(ts).toLocaleString()
  } catch {
    return ts
  }
}

function formatSize(bytes = 0) {
  if (!bytes) return '0 MB'

  const mb = bytes / 1024 / 1024
  if (mb < 1) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }
  return `${mb.toFixed(2)} MB`
}

function reloadAll() {
  loadBackups()
  reloadLogs()
  loadHealth()
}

// ==================== 系统健康监控 ====================
// 系统健康信息
const healthData = ref(null)
const loadingHealth = ref(false)

const healthStatus = computed(() => {
  if (loadingHealth.value) return 'loading'
  if (!healthData.value) return 'unknown'
  return healthData.value.status === 'ok' && healthData.value.db ? 'ok' : 'error'
})

async function loadHealth() {
  loadingHealth.value = true

  try {
    const resp = await api.get('/health/')
    if (resp.success) {
      healthData.value = resp.data
    } else {
      healthData.value = { status: 'error', db: false }
    }
  } catch (e) {
    healthData.value = { status: 'error', db: false }
  } finally {
    loadingHealth.value = false
  }
}

onMounted(() => {
  loadBackups()
  reloadLogs()
  loadHealth()
})
</script>

<style scoped>
/* ==================== 页面布局 ==================== */
.system-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding-bottom: 2rem;
}

/* ==================== 顶部面板 ==================== */
.hero-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.2rem;
  flex-wrap: wrap;
  padding: 1.6rem 1.8rem;
  border-radius: 10px;
  background: #fff;
  border: 1px solid #e5e7eb;
}

.hero-info {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  flex: 1;
  min-width: 280px;
}

.hero-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-panel h1 {
  margin: 0 0 0.25rem;
  font-size: 26px;
  color: #1e293b;
}

.hero-text {
  margin: 0;
  color: #475569;
  font-size: 14px;
  max-width: 540px;
}

.hero-actions {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

/* ==================== 按钮样式 ==================== */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 14px;
  background: #2563eb;
  color: #fff;
  border: 1px solid #2563eb;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  line-height: 1.5;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary:not(:disabled):hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2);
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1.1rem;
  border-radius: 10px;
  font-weight: 500;
  letter-spacing: 0.01em;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #fff;
  color: #334155;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1.5;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #f1f5f9;
}

.btn-secondary:not(:disabled):hover {
  background: #f8fafc;
  border-color: #94a3b8;
  color: #0f172a;
}

.btn-sm {
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  font-size: 12px;
}

.btn-xs {
  padding: 0.35rem 0.7rem;
  border-radius: 8px;
  font-size: 12px;
}

.btn-ghost {
  border: 1px solid rgba(148, 163, 184, 0.45);
  background: #fff;
  color: #0f172a;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.btn-ghost:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-ghost:not(:disabled):hover {
  background: rgba(226, 232, 240, 0.6);
}

.btn-danger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  background: #ef4444;
  border: 1px solid #ef4444;
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1.5;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger:not(:disabled):hover {
  background: #dc2626;
  border-color: #dc2626;
  box-shadow: 0 1px 2px rgba(220, 38, 38, 0.15);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* ==================== 卡片样式 ==================== */
.card {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  padding: 1.5rem 1.6rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.section-title {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: #0f172a;
  font-weight: 600;
  font-size: 16px;
}

.section-title svg {
  width: 18px;
  height: 18px;
  color: #2563eb;
  flex-shrink: 0;
}

.section-title img {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.section-title h2 {
  margin: 0;
  font-size: inherit;
  font-weight: inherit;
  line-height: 1;
}

.section-icon {
  width: 18px;
  height: 18px;
  vertical-align: middle;
}

.section-hint {
  font-size: 12px;
  color: #94a3b8;
}

/* ==================== 指标卡片 ==================== */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metric-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1.1rem 1.2rem;
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  transition: box-shadow 0.2s ease;
}

.metric-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.metric-card.highlight {
  background: #f8fafc;
}

.metric-label {
  font-size: 12px;
  color: #94a3b8;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.metric-value {
  font-size: 24px;
  color: #0f172a;
  font-weight: 700;
  line-height: 1.2;
}

.metric-value.text-sm {
  font-size: 14px;
  word-break: break-all;
}

.metric-desc {
  font-size: 13px;
  color: #64748b;
}

/* ==================== 提示框 ==================== */
.alert-stack {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.alert {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 13px;
}

.alert-error {
  background: rgba(254, 242, 242, 0.8);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #b91c1c;
}

.alert-success {
  background: rgba(240, 253, 244, 0.8);
  border: 1px solid rgba(74, 222, 128, 0.5);
  color: #15803d;
}

.alert-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: inherit;
}

/* ==================== 表格样式 ==================== */
.table-wrapper {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1rem;
  background: #fff;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead th {
  /* 使用全局样式 */
}

.data-table tbody td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  font-size: 14px;
  color: #374151;
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background: #fafafa;
}

.col-compact {
  width: 140px;
  text-align: right;
}

.file-name {
  font-weight: 600;
  color: #0f172a;
}

.file-meta {
  display: block;
  color: #94a3b8;
  font-size: 12px;
  margin-top: 0.2rem;
}

/* ==================== 筛选栏 ==================== */
.filter-bar {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}

.filter-row {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  width: 200px;
}

.filter-label {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.filter-field input,
.filter-field select {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0 0.75rem;
  font-size: 14px;
  background: #fff;
  height: 36px;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.filter-field input:focus,
.filter-field select:focus {
  outline: none;
  border-color: #2563eb;
  background: #fff;
}

.filter-field select {
  appearance: none;
  cursor: pointer;
  padding-right: 2.4rem;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2.5'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
}

.filter-field select:hover {
  border-color: #9ca3af;
  background-color: #f9fafb;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  height: 36px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  width: 16px;
  height: 16px;
  color: #94a3b8;
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 36px;
  padding: 0 0.9rem 0 2.2rem !important;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  line-height: normal;
}

.search-input:focus {
  outline: none;
  border-color: #2563eb;
  background: #fff;
}

.filter-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.85rem;
  padding-top: 0.85rem;
  border-top: 1px dashed rgba(148, 163, 184, 0.4);
}

.summary-text {
  font-size: 12px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.filter-tag button {
  background: none;
  border: none;
  color: #0369a1;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0;
  margin-left: 0.15rem;
}

.filter-tag button:hover {
  color: #0c4a6e;
}

.clear-all-btn {
  background: none;
  border: none;
  color: #dc2626;
  font-size: 12px;
  cursor: pointer;
  text-decoration: underline;
}

.clear-all-btn:hover {
  color: #b91c1c;
}

/* ==================== 日志面板 ==================== */
.log-panel {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #fff;
  padding: 1rem;
  max-height: 500px;
  overflow: auto;
}

.logs-table tbody td {
  vertical-align: middle;
}

.logs-table tbody td strong {
  display: block;
  font-size: 13px;
  color: #0f172a;
  margin-bottom: 0.2rem;
}

.logs-table tbody td span {
  font-size: 12px;
  color: #64748b;
}

.time-cell {
  font-size: 13px;
  color: #475569;
  white-space: nowrap;
}

.user-cell {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
}

.ip-cell {
  font-size: 12px;
  color: #94a3b8;
  font-family: monospace;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.status-pill.success {
  background: rgba(134, 239, 172, 0.35);
  color: #15803d;
}

.status-pill.warning {
  background: rgba(253, 224, 71, 0.4);
  color: #92400e;
}

.status-pill.danger {
  background: rgba(248, 113, 113, 0.4);
  color: #b91c1c;
}

.status-pill.debug {
  background: rgba(148, 163, 184, 0.35);
  color: #475569;
}

.log-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.log-footer {
  display: flex;
  justify-content: flex-end;
  padding: 0.75rem 0 0;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
  margin-top: 1rem;
}

.log-count {
  font-size: 12px;
  color: #64748b;
}

/* ==================== 空状态与加载 ==================== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: #94a3b8;
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 0.75rem;
  opacity: 0.5;
}

.empty-state p {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  margin: 0;
}

.empty-state span {
  font-size: 12px;
  margin-top: 0.25rem;
}

.empty {
  font-size: 13px;
  color: #94a3b8;
  text-align: center;
  padding: 0.5rem 0;
}

.table-skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.skeleton-row {
  height: 44px;
  border-radius: 8px;
  background: linear-gradient(90deg, #f3f4f6, #e5e7eb, #f3f4f6);
  background-size: 200% 100%;
  animation: skeleton 1.2s infinite;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

@keyframes skeleton {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* ==================== 系统信息卡片 ==================== */
.system-info-card .card-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logs-card .card-actions {
  display: flex;
  gap: 1rem;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 13px;
  font-weight: 500;
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
}

.status-indicator.ok {
  background: rgba(134, 239, 172, 0.3);
  color: #15803d;
}

.status-indicator.error {
  background: rgba(248, 113, 113, 0.3);
  color: #b91c1c;
}

.status-indicator.loading,
.status-indicator.unknown {
  background: rgba(148, 163, 184, 0.25);
  color: #64748b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

.status-indicator.ok .status-dot {
  background: #22c55e;
}

.status-indicator.error .status-dot {
  background: #ef4444;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.info-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #64748b;
  font-size: 14px;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(14, 165, 233, 0.2);
  border-top-color: #0ea5e9;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.system-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
}

.info-group {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1.2rem;
  transition: box-shadow 0.2s ease;
}

.info-group:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.info-group h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem;
  font-size: 14px;
  color: #0f172a;
  font-weight: 600;
  line-height: 1;
}

.info-group h4 svg {
  width: 18px;
  height: 18px;
  color: #2563eb;
  flex-shrink: 0;
}

.info-items {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.info-label {
  font-size: 13px;
  color: #64748b;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.info-value.highlight {
  color: #2563eb;
}

.info-value.warn {
  color: #f59e0b;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem 0.5rem;
  background: #f8fafc;
  border-radius: 8px;
  text-align: center;
}

.stat-item.active {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-item.active .stat-value {
  color: #2563eb;
}

.stat-label {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.info-empty {
  text-align: center;
  padding: 2rem;
  color: #94a3b8;
  font-size: 14px;
}

/* ==================== 响应式 ==================== */
@media (max-width: 720px) {
  .card {
    padding: 1.3rem;
  }

  .hero-panel {
    padding: 1.4rem;
  }

  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  }

  .system-info-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Modal Styles */
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
  z-index: 1001; /* Increased z-index to be on top of other content */
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: #fff;
  border-radius: 8px; /* More standard border radius */
  width: 90%;
  max-width: 440px; /* Slightly wider */
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: slideUp 0.2s ease;
  overflow: hidden; /* Ensure content doesn't spill out */
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem; /* Increased horizontal padding */
  border-bottom: 1px solid #e2e8f0; /* Lighter border */
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b; /* Slightly darker text */
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #64748b;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
  color: #334155;
}

.confirm-message {
  display: block;
  text-align: left;
  margin-bottom: 1rem;
}

/* warning-icon definition removed */

.confirm-message p {
  font-size: 14px;
  color: #334155;
  margin: 0;
  line-height: 1.5;
}

.confirm-hint {
  background: #fff1f2; /* Light red background for warning context */
  border: 1px solid #fecdd3;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 13px;
  color: #9f1239;
  margin: 0;
  line-height: 1.5;
}

.confirm-hint strong {
  color: #be123c;
  font-weight: 600;
}

.modal-footer {
  padding: 1rem 1.5rem; /* Match header padding */
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  border-radius: 0; /* Remove bottom radius as it's handled by overflow hidden on content */
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
