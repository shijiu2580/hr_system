<template>
	<div class="documents-page">
		<!-- 顶部导航区 -->
		<header class="page-header">
			<div class="header-left">
				<div class="header-icon">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
						<path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
				<div>
					<h1>文档中心</h1>
					<p class="header-desc">制度、流程、模板与公告的集中管理平台</p>
				</div>
			</div>
			<div class="header-actions">
				<button v-if="canManage" class="btn-primary" @click="router.push('/documents/upload')">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M12 5v14m-7-7h14" />
					</svg>
					上传文档
				</button>
			</div>
		</header>

		<!-- 统计概览 -->
		<section class="stats-row">
			<div class="stat-item">
				<div class="stat-icon">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
						<path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
					</svg>
				</div>
				<div class="stat-content">
					<span class="stat-value">{{ totalCount }}</span>
					<span class="stat-label">文档总数</span>
				</div>
			</div>
			<div class="stat-item">
				<div class="stat-icon active">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
						<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<div class="stat-content">
					<span class="stat-value">{{ activeCount }}</span>
					<span class="stat-label">已启用</span>
				</div>
			</div>
			<div class="stat-item">
				<div class="stat-icon">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
						<path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<div class="stat-content">
					<span class="stat-value">{{ latestUpdate }}</span>
					<span class="stat-label">最近更新</span>
				</div>
			</div>
		</section>

		<!-- 筛选工具栏 -->
		<section class="filter-bar">
			<div class="filter-row">
				<div class="search-wrapper">
					<img class="search-icon" src="/icons/search.svg" alt="" />
					<input
						v-model.trim="filters.search"
						type="text"
						placeholder="搜索文档标题或上传人..."
						class="search-input"
					/>
				</div>
				<div class="filter-toggle">
					<label class="toggle-switch">
						<input type="checkbox" v-model="filters.onlyActive" />
						<span class="toggle-slider"></span>
					</label>
					<span class="toggle-label">仅显示启用</span>
				</div>
			</div>
			<div class="filter-chips">
				<button
					v-for="chip in typeChips"
					:key="chip.value"
					class="filter-chip"
					:class="{ active: filters.type === chip.value }"
					@click="filters.type = chip.value"
				>
					<span>{{ chip.label }}</span>
					<span class="chip-count">{{ chip.count }}</span>
				</button>
			</div>
		</section>

		<!-- 加载骨架 -->
		<section v-if="loading" class="doc-grid">
			<div v-for="n in 6" :key="n" class="doc-skeleton">
				<div class="skeleton-header"></div>
				<div class="skeleton-title"></div>
				<div class="skeleton-desc"></div>
				<div class="skeleton-footer"></div>
			</div>
		</section>

		<!-- 文档列表 -->
		<section v-else>
			<div v-if="filteredDocs.length" class="doc-grid">
				<article v-for="doc in filteredDocs" :key="doc.id" class="doc-card">
					<div class="doc-card-header">
						<div class="doc-type-badge" :class="doc.document_type">
							<span class="type-name">{{ typeMeta[doc.document_type]?.label || '其他' }}</span>
						</div>
						<div class="doc-version">v{{ doc.version }}</div>
						<span v-if="!doc.is_active" class="doc-status inactive">已停用</span>
					</div>

					<h3 class="doc-title">{{ doc.title }}</h3>
					<p class="doc-desc">{{ doc.description || '暂无描述信息' }}</p>

					<div class="doc-meta">
						<div class="meta-item">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
							<span>{{ doc.uploaded_by?.username || '未知' }}</span>
						</div>
						<div class="meta-item">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<rect x="3" y="4" width="18" height="18" rx="2" />
								<path d="M16 2v4M8 2v4M3 10h18" />
							</svg>
							<span>{{ formatDate(doc.updated_at) }}</span>
						</div>
					</div>

					<div class="doc-actions">
						<button class="action-btn download" @click="downloadDoc(doc)">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
							</svg>
							下载
						</button>
						<template v-if="canManage">
							<button class="action-btn" @click="router.push(`/documents/${doc.id}/edit`)">
								<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
									<path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
								</svg>
								编辑
							</button>
							<button class="action-btn" @click="toggleActive(doc)">
								<svg v-if="doc.is_active" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<circle cx="12" cy="12" r="10" />
									<path d="M4.93 4.93l14.14 14.14" />
								</svg>
								<svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								{{ doc.is_active ? '停用' : '启用' }}
							</button>
							<button class="action-btn danger" @click="deleteDoc(doc)">
								<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
								</svg>
								删除
							</button>
						</template>
					</div>
				</article>
			</div>

			<!-- 空状态 -->
			<div v-else class="empty-state">
				<div class="empty-icon">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
						<path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
				<h3>暂无符合条件的文档</h3>
				<p>尝试调整筛选条件，或上传新的文档</p>
				<button v-if="canManage" class="btn-primary" @click="router.push('/documents/upload')">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M12 5v14m-7-7h14" />
					</svg>
					上传文档
				</button>
			</div>
		</section>

		<!-- Toast 提示 -->
		<transition name="toast">
			<div v-if="toast" class="toast-message" :class="toast.type">
				<svg v-if="toast.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				<svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="12" cy="12" r="10" />
					<path d="M12 8v4m0 4h.01" />
				</svg>
				<span>{{ toast.message }}</span>
				<button @click="toast = null">×</button>
			</div>
		</transition>
	</div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(true)
const documents = ref([])
const toast = ref(null)
const filters = reactive({ search: '', type: 'all', onlyActive: true })

const typeOptions = [
	{ value: 'policy', label: '政策文件' },
	{ value: 'procedure', label: '流程文件' },
	{ value: 'template', label: '模板文件' },
	{ value: 'announcement', label: '公告通知' },
	{ value: 'training', label: '培训资料' },
	{ value: 'other', label: '其他' }
]

const typeMeta = typeOptions.reduce((acc, cur) => {
	acc[cur.value] = cur
	return acc
}, {})

const canManage = computed(() => !!auth.user?.is_staff)

const typeChips = computed(() => {
	const base = [{ value: 'all', label: '全部类型' }, ...typeOptions]
	return base.map(item => ({
		...item,
		count: item.value === 'all' ? documents.value.length : documents.value.filter(doc => doc.document_type === item.value).length
	}))
})

const filteredDocs = computed(() => {
	const keyword = filters.search.toLowerCase()
	return documents.value.filter(doc => {
		if (filters.onlyActive && !doc.is_active) return false
		if (filters.type !== 'all' && doc.document_type !== filters.type) return false
		if (!keyword) return true
		return [doc.title, doc.description, doc.uploaded_by?.username]
			.filter(Boolean)
			.some(text => String(text).toLowerCase().includes(keyword))
	})
})

const totalCount = computed(() => documents.value.length)
const activeCount = computed(() => documents.value.filter(d => d.is_active).length)
const latestUpdate = computed(() => {
	if (!documents.value.length) return '--'
	const sorted = [...documents.value].sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
	return formatDate(sorted[0]?.updated_at)
})

function formatDate(value) {
	if (!value) return '--'
	const d = new Date(value)
	if (Number.isNaN(d.getTime())) return value
	return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function loadDocuments() {
	loading.value = true
	const resp = await api.get('/documents/')
	if (resp.success) {
		const payload = resp.data
		if (Array.isArray(payload)) documents.value = payload
		else if (Array.isArray(payload?.results)) documents.value = payload.results
		else documents.value = []
	} else {
		showToast(resp.error?.message || '加载失败', 'error')
		documents.value = []
	}
	loading.value = false
}

function showToast(message, type = 'info') {
	toast.value = { message, type }
	setTimeout(() => {
		if (toast.value && toast.value.message === message) {
			toast.value = null
		}
	}, 3200)
}

async function toggleActive(doc) {
	const resp = await api.patch(`/documents/${doc.id}/`, { is_active: !doc.is_active })
	if (resp.success) {
		doc.is_active = !doc.is_active
		showToast(doc.is_active ? '已启用文档' : '已停用文档', 'success')
	} else {
		showToast(resp.error?.message || '切换失败', 'error')
	}
}

async function deleteDoc(doc) {
	if (!confirm(`确定删除「${doc.title}」吗？`)) return
	const resp = await api.delete(`/documents/${doc.id}/`)
	if (resp.success) {
		showToast('文档已删除', 'success')
		documents.value = documents.value.filter(item => item.id !== doc.id)
	} else {
		showToast(resp.error?.message || '删除失败', 'error')
	}
}

function downloadDoc(doc) {
	if (!doc.file_url) {
		showToast('该文档附件不存在或已被删除', 'error')
		return
	}
	// 使用 fetch + blob 下载，正确处理 404 等错误
	fetch(doc.file_url)
		.then(resp => {
			if (!resp.ok) {
				throw new Error(`HTTP ${resp.status}`)
			}
			return resp.blob()
		})
		.then(blob => {
			const url = URL.createObjectURL(blob)
			const a = document.createElement('a')
			a.href = url
			// 从 file_url 中提取文件名
			const fileName = decodeURIComponent(doc.file_url.split('/').pop()) || doc.title
			a.download = fileName
			document.body.appendChild(a)
			a.click()
			document.body.removeChild(a)
			URL.revokeObjectURL(url)
		})
		.catch(() => {
			showToast('文件下载失败，文件可能已被删除', 'error')
		})
}

onMounted(() => loadDocuments())
</script>

<style scoped>
.documents-page {
	max-width: 1400px;
	margin: 0 auto;
	padding: 0 1.5rem 3rem;
}

/* 页面头部 */
.page-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 1.5rem;
	padding: 1.5rem 1.75rem;
	background: #fff;
	border: 1px solid rgba(148, 163, 184, 0.4);
	border-radius: 12px;
	margin-bottom: 1.25rem;
}

.header-left {
	display: flex;
	align-items: center;
	gap: 1rem;
}

.header-icon {
	width: 48px;
	height: 48px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: #f8fafc;
	border-radius: 12px;
}

.header-icon svg {
	width: 26px;
	height: 26px;
	color: #475569;
}

.page-header h1 {
	margin: 0 0 0.2rem;
	font-size: 22px;
	font-weight: 600;
	color: #0f172a;
}

.header-desc {
	margin: 0;
	font-size: 13px;
	color: #64748b;
}

.header-actions {
	display: flex;
	gap: 0.75rem;
}

/* 统计行 */
.stats-row {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
	gap: 1rem;
	margin-bottom: 1.25rem;
}

.stat-item {
	display: flex;
	align-items: center;
	gap: 1rem;
	padding: 1.25rem 1.5rem;
	background: #fff;
	border: 1px solid rgba(148, 163, 184, 0.4);
	border-radius: 10px;
	transition: border-color 0.2s ease;
}

.stat-item:hover {
	border-color: rgba(148, 163, 184, 0.6);
}

.stat-icon {
	width: 44px;
	height: 44px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: #f8fafc;
	border-radius: 10px;
	flex-shrink: 0;
}

.stat-icon svg {
	width: 22px;
	height: 22px;
	color: #64748b;
}

.stat-icon.active {
	background: #f0fdf4;
}

.stat-icon.active svg {
	color: #22c55e;
}

.stat-content {
	display: flex;
	flex-direction: column;
	gap: 0.15rem;
}

.stat-value {
	font-size: 22px;
	font-weight: 600;
	color: #0f172a;
	line-height: 1.1;
}

.stat-label {
	font-size: 12px;
	color: #94a3b8;
	text-transform: uppercase;
	letter-spacing: 0.05em;
}

/* 筛选栏 */
.filter-bar {
	display: flex;
	flex-direction: column;
	gap: 1rem;
	padding: 1.25rem 1.5rem;
	background: #fff;
	border: 1px solid rgba(148, 163, 184, 0.4);
	border-radius: 10px;
	margin-bottom: 1.5rem;
}

.filter-row {
	display: flex;
	align-items: center;
	gap: 1rem;
}

.search-wrapper {
	position: relative;
	width: 280px;
	flex-shrink: 0;
}

.search-icon {
	position: absolute;
	left: 12px;
	top: 50%;
	transform: translateY(-50%);
	width: 18px;
	height: 18px;
	color: #94a3b8;
	pointer-events: none;
}

.search-input {
	width: 100%;
	height: 36px;
	padding: 0 1rem 0 2.5rem;
	border: 1px solid rgba(148, 163, 184, 0.4);
	border-radius: 10px;
	font-size: 13px;
	background: #fff;
	transition: border-color 0.2s, background 0.2s;
}

.search-input:focus {
	outline: none;
	border-color: rgba(148, 163, 184, 0.6);
	background: #f8fafc;
}

.search-input::placeholder {
	color: #94a3b8;
}

.filter-chips {
	display: flex;
	flex-wrap: wrap;
	gap: 0.5rem;
	flex: 1;
}

.filter-chip {
	display: inline-flex;
	align-items: center;
	gap: 0.4rem;
	padding: 0.45rem 0.85rem;
	border: 1px solid rgba(148, 163, 184, 0.4);
	border-radius: 20px;
	background: #fff;
	font-size: 13px;
	color: #475569;
	cursor: pointer;
	transition: all 0.2s ease;
}

.filter-chip:hover {
	border-color: rgba(148, 163, 184, 0.6);
	background: #f8fafc;
}

.filter-chip.active {
	background: #0f172a;
	border-color: #0f172a;
	color: #fff;
}

.chip-icon {
	font-size: 14px;
}

.chip-count {
	font-size: 11px;
	opacity: 0.7;
	padding: 0.1rem 0.4rem;
	background: rgba(0, 0, 0, 0.06);
	border-radius: 10px;
}

.filter-chip.active .chip-count {
	background: rgba(255, 255, 255, 0.2);
}

.filter-toggle {
	display: flex;
	align-items: center;
	gap: 0.6rem;
	margin-left: auto;
}

.toggle-label {
	font-size: 13px;
	color: #64748b;
}

.toggle-switch {
	position: relative;
	width: 40px;
	height: 22px;
	cursor: pointer;
}

.toggle-switch input {
	opacity: 0;
	width: 0;
	height: 0;
}

.toggle-slider {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: #e2e8f0;
	border-radius: 22px;
	transition: 0.2s;
}

.toggle-slider::before {
	content: '';
	position: absolute;
	width: 16px;
	height: 16px;
	left: 3px;
	bottom: 3px;
	background: #fff;
	border-radius: 50%;
	transition: 0.2s;
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.toggle-switch input:checked + .toggle-slider {
	background: #0f172a;
}

.toggle-switch input:checked + .toggle-slider::before {
	transform: translateX(18px);
}

/* 文档网格 */
.doc-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
	gap: 1rem;
}

/* 骨架屏 */
.doc-skeleton {
	background: #fff;
	border: 1px solid rgba(148, 163, 184, 0.4);
	border-radius: 10px;
	padding: 1.25rem;
	display: flex;
	flex-direction: column;
	gap: 0.85rem;
}

.skeleton-header,
.skeleton-title,
.skeleton-desc,
.skeleton-footer {
	background: linear-gradient(90deg, #f1f5f9 0%, #e2e8f0 50%, #f1f5f9 100%);
	background-size: 200% 100%;
	border-radius: 6px;
	animation: shimmer 1.5s infinite;
}

.skeleton-header {
	height: 32px;
	width: 45%;
}

.skeleton-title {
	height: 22px;
	width: 80%;
}

.skeleton-desc {
	height: 40px;
	width: 100%;
}

.skeleton-footer {
	height: 36px;
	width: 100%;
	margin-top: auto;
}

@keyframes shimmer {
	0% { background-position: 200% 0; }
	100% { background-position: -200% 0; }
}

/* 文档卡片 */
.doc-card {
	background: #fff;
	border: 1px solid rgba(148, 163, 184, 0.4);
	border-radius: 10px;
	padding: 1.25rem;
	display: flex;
	flex-direction: column;
	gap: 0.85rem;
	transition: border-color 0.2s ease;
}

.doc-card:hover {
	border-color: rgba(148, 163, 184, 0.6);
}

.doc-card-header {
	display: flex;
	align-items: center;
	gap: 0.75rem;
}

.doc-type-badge {
	display: inline-flex;
	align-items: center;
	gap: 0.4rem;
	padding: 0.35rem 0.75rem;
	background: #f8fafc;
	border-radius: 8px;
	font-size: 12px;
}

.type-icon {
	font-size: 14px;
}

.type-name {
	color: #475569;
	font-weight: 500;
}

.doc-version {
	font-size: 11px;
	color: #94a3b8;
	padding: 0.2rem 0.5rem;
	background: #f8fafc;
	border-radius: 4px;
}

.doc-status {
	margin-left: auto;
	font-size: 11px;
	padding: 0.25rem 0.6rem;
	border-radius: 4px;
	font-weight: 500;
}

.doc-status.inactive {
	background: #fef2f2;
	color: #dc2626;
}

.doc-title {
	margin: 0;
	font-size: 16px;
	font-weight: 600;
	color: #0f172a;
	line-height: 1.4;
}

.doc-desc {
	margin: 0;
	font-size: 13px;
	color: #64748b;
	line-height: 1.5;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
	min-height: 39px;
}

.doc-meta {
	display: flex;
	gap: 1.5rem;
	padding-top: 0.5rem;
	border-top: 1px solid rgba(148, 163, 184, 0.2);
}

.meta-item {
	display: flex;
	align-items: center;
	gap: 0.4rem;
	font-size: 12px;
	color: #64748b;
}

.meta-item svg {
	width: 14px;
	height: 14px;
	color: #94a3b8;
}

.doc-actions {
	display: flex;
	flex-wrap: wrap;
	gap: 0.5rem;
	margin-top: auto;
	padding-top: 0.75rem;
}

.action-btn {
	display: inline-flex;
	align-items: center;
	gap: 0.35rem;
	padding: 0.45rem 0.75rem;
	border: 1px solid rgba(148, 163, 184, 0.4);
	border-radius: 8px;
	background: #fff;
	font-size: 12px;
	color: #475569;
	cursor: pointer;
	transition: all 0.2s ease;
}

.action-btn svg {
	width: 14px;
	height: 14px;
}

.action-btn:hover {
	background: #f8fafc;
	border-color: rgba(148, 163, 184, 0.6);
}

.action-btn.download {
	background: #0f172a;
	border-color: #0f172a;
	color: #fff;
}

.action-btn.download:hover {
	background: #1e293b;
}

.action-btn.danger:hover {
	background: #fef2f2;
	border-color: rgba(239, 68, 68, 0.4);
	color: #dc2626;
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 4rem 2rem;
	background: #fff;
	border: 1px solid rgba(148, 163, 184, 0.4);
	border-radius: 10px;
	text-align: center;
}

.empty-icon {
	width: 80px;
	height: 80px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: #f8fafc;
	border-radius: 50%;
	margin-bottom: 1.5rem;
}

.empty-icon svg {
	width: 40px;
	height: 40px;
	color: #94a3b8;
}

.empty-state h3 {
	margin: 0 0 0.5rem;
	font-size: 18px;
	font-weight: 600;
	color: #0f172a;
}

.empty-state p {
	margin: 0 0 1.5rem;
	font-size: 14px;
	color: #64748b;
}

/* 主按钮 */
.btn-primary {
	display: inline-flex;
	align-items: center;
	gap: 0.5rem;
	padding: 0.6rem 1.1rem;
	background: #0f172a;
	border: none;
	border-radius: 10px;
	font-size: 13px;
	font-weight: 500;
	color: #fff;
	cursor: pointer;
	transition: background 0.2s ease;
}

.btn-primary svg {
	width: 16px;
	height: 16px;
}

.btn-primary:hover {
	background: #1e293b;
}

/* Toast 消息 */
.toast-message {
	position: fixed;
	bottom: 2rem;
	right: 2rem;
	display: flex;
	align-items: center;
	gap: 0.75rem;
	padding: 0.85rem 1.25rem;
	background: #0f172a;
	border-radius: 10px;
	color: #fff;
	font-size: 13px;
	box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
	z-index: 1000;
}

.toast-message svg {
	width: 18px;
	height: 18px;
	flex-shrink: 0;
}

.toast-message.success {
	background: #059669;
}

.toast-message.error {
	background: #dc2626;
}

.toast-message button {
	background: none;
	border: none;
	color: inherit;
	font-size: 18px;
	cursor: pointer;
	opacity: 0.7;
	margin-left: 0.5rem;
}

.toast-message button:hover {
	opacity: 1;
}

.toast-enter-active,
.toast-leave-active {
	transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
	opacity: 0;
	transform: translateY(10px);
}

/* 响应式 */
@media (max-width: 768px) {
	.page-header {
		flex-direction: column;
		align-items: flex-start;
	}

	.filter-row {
		flex-direction: column;
		align-items: stretch;
		gap: 0.75rem;
	}

	.search-wrapper {
		width: 100%;
	}

	.filter-toggle {
		margin-left: 0;
	}

	.doc-grid {
		grid-template-columns: 1fr;
	}

	.doc-actions {
		flex-direction: column;
	}

	.action-btn {
		justify-content: center;
	}
}
</style>

