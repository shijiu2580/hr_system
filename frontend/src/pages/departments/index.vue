<template>
  <div class="page-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <img src="/icons/departments.svg" alt="" />
        </div>
        <span class="header-title">部门管理</span>
      </div>
      <div class="header-right">
        <div class="stat-badges">
          <span class="stat-badge">
            <span class="stat-value">{{ items.length }}</span>
            <span class="stat-label">部门总数</span>
          </span>
          <span class="stat-badge active">
            <span class="stat-value">{{ treeData.length }}</span>
            <span class="stat-label">顶级部门</span>
          </span>
        </div>
        <button class="btn-primary" @click="showCreateModal = true">
          <img src="/icons/add.svg" alt="" style="width: 16px; height: 16px; filter: brightness(0) invert(1);" />
          新建部门
        </button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filters-bar">
      <div class="filter-item search-item">
        <img src="/icons/search.svg" class="search-icon" alt="" />
        <input v-model="searchKeyword" type="text" placeholder="搜索部门名称..." class="filter-input" />
      </div>
      <div class="filter-actions">
        <button class="btn-outline" @click="expandAll">
          展开全部
        </button>
        <button class="btn-outline" @click="collapseAll">
          折叠全部
        </button>
      </div>
    </div>

    <!-- 树形表格 -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-name">部门名称</th>
            <th class="col-desc">描述</th>
            <th class="col-supervisors">主管</th>
            <th class="col-employees">员工数</th>
            <th class="col-actions">
              <div class="action-header">
                <span>操作</span>
                <img src="/icons/setting.svg" class="settings-icon" alt="设置" />
              </div>
            </th>
          </tr>
        </thead>
        <tbody v-if="!loading && treeData.length">
          <template v-for="item in treeData" :key="item.id">
            <!-- 顶级部门 -->
            <tr class="data-row root-row" :data-dept-id="item.id">
              <td class="col-name">
                <div class="dept-info">
                  <button
                    v-if="item.children?.length"
                    class="expand-btn"
                    @click="toggleExpand(item.id)"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ rotated: expandedIds.has(item.id) }">
                      <polyline points="9 18 15 12 9 6"/>
                    </svg>
                  </button>
                  <span v-else class="expand-placeholder"></span>
                  <div class="dept-icon" :style="{ background: getDeptColor(item.id) }">
                    {{ item.name?.charAt(0) }}
                  </div>
                  <div class="dept-text">
                    <span class="dept-name">{{ item.name }}</span>
                    <span v-if="item.children?.length" class="children-hint">{{ item.children.length }}个子部门</span>
                  </div>
                </div>
              </td>
              <td class="col-desc">
                <span class="desc-text" :title="item.description">{{ item.description || '-' }}</span>
              </td>
              <td class="col-supervisors">
                <span class="supervisor-count" @click="showSupervisors(item)">
                  {{ item.supervisors?.length || 0 }}人
                </span>
              </td>
              <td class="col-employees">
                <span class="employee-count">{{ item.employee_count || 0 }}人</span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <button class="btn-icon" title="编辑" @click="openEdit(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  </button>
                  <button class="btn-icon" title="设置主管" @click="showAssignSupervisor(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                  </button>
                  <button class="btn-icon" title="添加子部门" @click="openAddChild(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  </button>
                  <button class="btn-icon danger" title="删除" @click="remove(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                  </button>
                </div>
              </td>
            </tr>
            <!-- 子部门（展开时显示） -->
            <template v-if="expandedIds.has(item.id) && item.children?.length">
              <template v-for="(child, index) in item.children" :key="child.id">
                <tr class="data-row child-row" :data-dept-id="child.id">
                  <td class="col-name">
                    <div class="dept-info" style="padding-left: 32px;">
                      <button
                        v-if="child.children?.length"
                        class="expand-btn"
                        @click="toggleExpand(child.id)"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ rotated: expandedIds.has(child.id) }">
                          <polyline points="9 18 15 12 9 6"/>
                        </svg>
                      </button>
                      <span v-else class="expand-placeholder"></span>
                      <div class="tree-line" :class="{ 'last-child': index === item.children.length - 1 }"></div>
                      <div class="dept-icon small" :style="{ background: getDeptColor(child.id) }">
                        {{ child.name?.charAt(0) }}
                      </div>
                      <div class="dept-text">
                        <span class="dept-name">{{ child.name }}</span>
                        <span v-if="child.children?.length" class="children-hint">{{ child.children.length }}个子部门</span>
                      </div>
                    </div>
                  </td>
                  <td class="col-desc">
                    <span class="desc-text" :title="child.description">{{ child.description || '-' }}</span>
                  </td>
                  <td class="col-supervisors">
                    <span class="supervisor-count" @click="showSupervisors(child)">
                      {{ child.supervisors?.length || 0 }}人
                    </span>
                  </td>
                  <td class="col-employees">
                    <span class="employee-count">{{ child.employee_count || 0 }}人</span>
                  </td>
                  <td class="col-actions">
                    <div class="action-buttons">
                      <button class="btn-icon" title="编辑" @click="openEdit(child)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                      </button>
                      <button class="btn-icon" title="设置主管" @click="showAssignSupervisor(child)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                      </button>
                      <button class="btn-icon" title="添加子部门" @click="openAddChild(child)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                      </button>
                      <button class="btn-icon danger" title="删除" @click="remove(child)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <!-- 第三级子部门 -->
                <template v-if="expandedIds.has(child.id) && child.children?.length">
                  <tr v-for="(grandChild, gIndex) in child.children" :key="grandChild.id" class="data-row grandchild-row" :data-dept-id="grandChild.id">
                    <td class="col-name">
                      <div class="dept-info" style="padding-left: 64px;">
                        <span class="expand-placeholder"></span>
                        <div class="tree-line level2" :class="{ 'last-child': gIndex === child.children.length - 1 }"></div>
                        <div class="dept-icon tiny" :style="{ background: getDeptColor(grandChild.id) }">
                          {{ grandChild.name?.charAt(0) }}
                        </div>
                        <span class="dept-name">{{ grandChild.name }}</span>
                      </div>
                    </td>
                    <td class="col-desc">
                      <span class="desc-text" :title="grandChild.description">{{ grandChild.description || '-' }}</span>
                    </td>
                    <td class="col-supervisors">
                      <span class="supervisor-count" @click="showSupervisors(grandChild)">
                        {{ grandChild.supervisors?.length || 0 }}人
                      </span>
                    </td>
                    <td class="col-employees">
                      <span class="employee-count">{{ grandChild.employee_count || 0 }}人</span>
                    </td>
                    <td class="col-actions">
                      <div class="action-buttons">
                        <button class="btn-icon" title="编辑" @click="openEdit(grandChild)">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                        </button>
                        <button class="btn-icon" title="设置主管" @click="showAssignSupervisor(grandChild)">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                        </button>
                        <button class="btn-icon danger" title="删除" @click="remove(grandChild)">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                </template>
              </template>
            </template>
          </template>
        </tbody>
      </table>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && !treeData.length" class="empty-state">
        暂无部门数据
      </div>
    </div>

    <!-- 底部统计 -->
    <div class="table-footer">
      <span class="total-count">共{{ items.length }}个部门，{{ treeData.length }}个顶级部门</span>
    </div>

    <!-- Toast 提示 -->
    <teleport to="body">
      <transition name="toast">
        <div v-if="message" class="toast" :class="`toast-${message.type}`">
          <span>{{ message.text }}</span>
          <button @click="message = null" class="toast-close">×</button>
        </div>
      </transition>
    </teleport>

    <!-- 新建/编辑部门弹窗 -->
    <div v-if="showCreateModal || editItem" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editItem ? '编辑部门' : '新建部门' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label>部门名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" placeholder="请输入部门名称" />
          </div>
          <div class="form-row">
            <label>上级部门</label>
            <CustomSelect
              v-model="form.parent_id"
              :options="[{ value: '', label: '无（顶级部门）' }, ...parentOptions]"
              placeholder="选择上级部门"
              searchable
            />
          </div>
          <div class="form-row">
            <label>部门描述</label>
            <textarea v-model="form.description" rows="3" placeholder="请输入部门描述..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModal">取消</button>
          <button class="btn-submit" :disabled="saving" @click="handleSubmit">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 关联职位弹窗 -->
    <div v-if="assignItem" class="modal-overlay" @click.self="assignItem = null">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>关联职位 - {{ assignItem.name }}</h3>
          <button class="modal-close" @click="assignItem = null">×</button>
        </div>
        <div class="modal-body">
          <div class="assign-section">
            <h4>当前关联的职位 ({{ assignedPositions.length }}个)</h4>
            <div v-if="assignedPositions.length" class="position-tags">
              <span v-for="pos in assignedPositions" :key="pos.id" class="position-tag">
                {{ pos.name }}
                <button class="tag-remove" @click="unassignPosition(pos)">×</button>
              </span>
            </div>
            <div v-else class="empty-hint">暂无关联职位</div>
          </div>
          <div class="assign-section">
            <h4>添加职位</h4>
            <div class="assign-search">
              <CustomSelect
                v-model="selectedPosition"
                :options="[{ value: '', label: '搜索并选择职位' }, ...availablePositions.map(p => ({ value: p.id, label: p.name }))]"
                placeholder="搜索并选择职位"
                searchable
              />
              <button class="btn-add" :disabled="!selectedPosition" @click="assignPosition">添加</button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="assignItem = null">关闭</button>
        </div>
      </div>
    </div>

    <!-- 查看职位列表弹窗 -->
    <div v-if="viewPositionsItem" class="modal-overlay" @click.self="viewPositionsItem = null">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ viewPositionsItem.name }} - 关联职位</h3>
          <button class="modal-close" @click="viewPositionsItem = null">×</button>
        </div>
        <div class="modal-body">
          <div v-if="viewPositionsList.length" class="position-list">
            <div v-for="pos in viewPositionsList" :key="pos.id" class="position-item">
              <div class="pos-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 7h-9M14 17H5"/>
                  <circle cx="17" cy="17" r="3"/>
                  <circle cx="7" cy="7" r="3"/>
                </svg>
              </div>
              <div class="pos-info">
                <span class="pos-name">{{ pos.name }}</span>
                <span class="pos-salary" v-if="pos.salary_range_min || pos.salary_range_max">
                  薪资: ¥{{ pos.salary_range_min || '?' }} - ¥{{ pos.salary_range_max || '?' }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="empty-hint">暂无关联职位</div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="viewPositionsItem = null">关闭</button>
        </div>
      </div>
    </div>

    <!-- 设置主管弹窗 -->
    <div v-if="supervisorItem" class="modal-overlay" @click.self="supervisorItem = null">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>设置主管 - {{ supervisorItem.name }}</h3>
          <button class="modal-close" @click="supervisorItem = null">×</button>
        </div>
        <div class="modal-body">
          <div class="assign-section">
            <h4>当前主管 ({{ currentSupervisors.length }}人)</h4>
            <div v-if="currentSupervisors.length" class="supervisor-tags">
              <span v-for="sup in currentSupervisors" :key="sup.id" class="supervisor-tag">
                <span class="sup-avatar">{{ sup.name?.charAt(0) }}</span>
                {{ sup.name }}
                <button class="tag-remove" @click="removeSupervisor(sup)">×</button>
              </span>
            </div>
            <div v-else class="empty-hint">暂无主管</div>
          </div>
          <div class="assign-section">
            <h4>添加主管</h4>
            <div class="assign-search">
              <CustomSelect
                v-model="selectedSupervisor"
                :options="[{ value: '', label: '搜索并选择员工' }, ...availableSupervisors.map(e => ({ value: e.id, label: `${e.name} (${e.department?.name || '无部门'})` }))]"
                placeholder="搜索并选择员工"
                searchable
              />
              <button class="btn-add" :disabled="!selectedSupervisor" @click="addSupervisor">添加</button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="supervisorItem = null">关闭</button>
        </div>
      </div>
    </div>

    <!-- 查看主管列表弹窗 -->
    <div v-if="viewSupervisorsItem" class="modal-overlay" @click.self="viewSupervisorsItem = null">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ viewSupervisorsItem.name }} - 主管列表</h3>
          <button class="modal-close" @click="viewSupervisorsItem = null">×</button>
        </div>
        <div class="modal-body">
          <div v-if="viewSupervisorsItem.supervisors?.length" class="supervisor-list">
            <div v-for="sup in viewSupervisorsItem.supervisors" :key="sup.id" class="supervisor-item">
              <div class="sup-avatar-lg">{{ sup.name?.charAt(0) }}</div>
              <div class="sup-info">
                <span class="sup-name">{{ sup.name }}</span>
                <span class="sup-id">工号: {{ sup.employee_id }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-hint">暂无主管</div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="viewSupervisorsItem = null">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../utils/api'
import CustomSelect from '../../components/CustomSelect.vue'

const loading = ref(false)
const saving = ref(false)
const message = ref(null)

const items = ref([])
const allPositions = ref([])
const allEmployees = ref([])

const searchKeyword = ref('')
const expandedIds = ref(new Set())

const showCreateModal = ref(false)
const editItem = ref(null)
const assignItem = ref(null)
const viewPositionsItem = ref(null)
const viewPositionsList = ref([])
const assignedPositions = ref([])
const selectedPosition = ref('')

// 主管相关
const supervisorItem = ref(null)
const viewSupervisorsItem = ref(null)
const currentSupervisors = ref([])
const selectedSupervisor = ref('')

// 用于"添加子部门"时预选父部门
const presetParentId = ref('')

const form = ref({
  name: '',
  description: '',
  parent_id: ''
})

// 部门颜色
const deptColors = [
  'linear-gradient(135deg, #38bdf8, #0ea5e9)',
  'linear-gradient(135deg, #a78bfa, #8b5cf6)',
  'linear-gradient(135deg, #34d399, #10b981)',
  'linear-gradient(135deg, #fbbf24, #f59e0b)',
  'linear-gradient(135deg, #f87171, #ef4444)',
  'linear-gradient(135deg, #60a5fa, #3b82f6)',
]

function getDeptColor(id) {
  return deptColors[id % deptColors.length]
}

// 构建树形数据
const treeData = computed(() => {
  let list = items.value

  // 搜索过滤
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    const matchIds = new Set()

    // 找到匹配的部门及其父级
    list.forEach(d => {
      if (d.name?.toLowerCase().includes(kw)) {
        matchIds.add(d.id)
        // 添加所有父级
        let current = d
        while (current.parent) {
          matchIds.add(current.parent.id)
          current = list.find(p => p.id === current.parent.id) || { parent: null }
        }
      }
    })

    list = list.filter(d => matchIds.has(d.id))

    // 搜索时自动展开所有匹配的父级
    matchIds.forEach(id => expandedIds.value.add(id))
  }

  // 构建 id -> 部门 映射
  const deptMap = {}
  list.forEach(d => {
    deptMap[d.id] = { ...d, children: [] }
  })

  // 构建树形结构
  const roots = []
  list.forEach(d => {
    if (d.parent?.id && deptMap[d.parent.id]) {
      deptMap[d.parent.id].children.push(deptMap[d.id])
    } else if (!d.parent) {
      roots.push(deptMap[d.id])
    }
  })

  // 按名称排序
  const sortChildren = (nodes) => {
    nodes.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))
    nodes.forEach(n => {
      if (n.children?.length) sortChildren(n.children)
    })
  }
  sortChildren(roots)

  return roots
})

// 展开/收起
function toggleExpand(id) {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
  expandedIds.value = new Set(expandedIds.value) // 触发响应
}

function expandAll() {
  items.value.forEach(d => {
    if (d.children_count > 0) {
      expandedIds.value.add(d.id)
    }
  })
  expandedIds.value = new Set(expandedIds.value)
}

function collapseAll() {
  expandedIds.value.clear()
  expandedIds.value = new Set()
}

// 可选的上级部门（排除自己和自己的子部门）
const parentOptions = computed(() => {
  if (!editItem.value) {
    return items.value.map(d => ({ value: d.id, label: d.full_path || d.name }))
  }
  // 编辑时排除自己和子部门
  const excludeIds = new Set([editItem.value.id])
  // 递归获取所有子部门ID
  const getChildIds = (parentId) => {
    items.value.forEach(d => {
      if (d.parent?.id === parentId && !excludeIds.has(d.id)) {
        excludeIds.add(d.id)
        getChildIds(d.id)
      }
    })
  }
  getChildIds(editItem.value.id)

  return items.value
    .filter(d => !excludeIds.has(d.id))
    .map(d => ({ value: d.id, label: d.full_path || d.name }))
})

// 可用于关联的职位（未分配到当前部门的）
const availablePositions = computed(() => {
  if (!assignItem.value) return []
  const assignedIds = new Set(assignedPositions.value.map(p => p.id))
  return allPositions.value.filter(p => !assignedIds.has(p.id))
})

// 可用于设置为主管的员工（未在当前部门主管列表中的）
const availableSupervisors = computed(() => {
  if (!supervisorItem.value) return []
  const supervisorIds = new Set(currentSupervisors.value.map(s => s.id))
  return allEmployees.value.filter(e => !supervisorIds.has(e.id))
})

async function loadData() {
  loading.value = true
  try {
    const [deptRes, posRes, empRes] = await Promise.all([
      api.get('/departments/'),
      api.get('/positions/'),
      api.get('/employees/')
    ])

    const deptList = deptRes.data?.results || deptRes.data || []
    const posList = posRes.data?.results || posRes.data || []
    const empList = empRes.data?.results || empRes.data || []

    // 计算每个部门关联的职位数和员工数
    const posCountMap = {}
    const empCountMap = {}

    posList.forEach(pos => {
      if (pos.department?.id) {
        posCountMap[pos.department.id] = (posCountMap[pos.department.id] || 0) + 1
      }
    })

    empList.forEach(emp => {
      if (emp.department?.id) {
        empCountMap[emp.department.id] = (empCountMap[emp.department.id] || 0) + 1
      }
    })

    items.value = deptList.map(d => ({
      ...d,
      position_count: posCountMap[d.id] || 0,
      employee_count: empCountMap[d.id] || 0
    }))

    allPositions.value = posList
    allEmployees.value = empList
  } catch (e) {
    message.value = { type: 'error', text: '加载数据失败' }
  } finally {
    loading.value = false
  }
}

function openEdit(item) {
  editItem.value = item
  presetParentId.value = ''
  form.value = {
    name: item.name || '',
    description: item.description || '',
    parent_id: item.parent?.id || ''
  }
}

// 添加子部门（预设父部门）
function openAddChild(parent) {
  editItem.value = null
  presetParentId.value = parent.id
  form.value = {
    name: '',
    description: '',
    parent_id: parent.id
  }
  showCreateModal.value = true
  // 展开父部门以便看到新添加的子部门
  expandedIds.value.add(parent.id)
  expandedIds.value = new Set(expandedIds.value)
}

function closeModal() {
  showCreateModal.value = false
  editItem.value = null
  presetParentId.value = ''
  form.value = { name: '', description: '', parent_id: '' }
}

async function handleSubmit() {
  if (!form.value.name?.trim()) {
    message.value = { type: 'error', text: '请输入部门名称' }
    return
  }

  saving.value = true
  try {
    const parentId = form.value.parent_id ? parseInt(form.value.parent_id) : null
    const payload = {
      name: form.value.name,
      description: form.value.description || '',
      parent_id: parentId
    }

    if (editItem.value) {
      await api.put(`/departments/${editItem.value.id}/`, payload)
      message.value = { type: 'success', text: '部门已更新' }
    } else {
      await api.post('/departments/', payload)
      message.value = { type: 'success', text: '部门已创建' }
    }

    closeModal()
    await loadData()
  } catch (e) {
    message.value = { type: 'error', text: e.response?.data?.detail || '操作失败' }
  } finally {
    saving.value = false
  }
}

async function remove(item) {
  if (!confirm(`确认删除部门「${item.name}」？\n注意：该部门下的职位和员工将解除关联。`)) return

  try {
    await api.delete(`/departments/${item.id}/`)
    message.value = { type: 'success', text: '已删除' }
    await loadData()
  } catch (e) {
    message.value = { type: 'error', text: e.response?.data?.detail || '删除失败' }
  }
}

// 显示关联的职位
function showPositions(item) {
  viewPositionsItem.value = item
  viewPositionsList.value = allPositions.value.filter(p => p.department?.id === item.id)
}

// 打开关联职位弹窗
function showAssign(item) {
  assignItem.value = item
  assignedPositions.value = allPositions.value.filter(p => p.department?.id === item.id)
  selectedPosition.value = ''
}

// 添加职位到部门
async function assignPosition() {
  if (!selectedPosition.value) return

  try {
    await api.patch(`/positions/${selectedPosition.value}/`, {
      department_id: assignItem.value.id
    })
    message.value = { type: 'success', text: '职位已关联到该部门' }
    await loadData()
    assignedPositions.value = allPositions.value.filter(p => p.department?.id === assignItem.value.id)
    selectedPosition.value = ''
  } catch (e) {
    message.value = { type: 'error', text: '关联失败' }
  }
}

// 解除职位与部门的关联
async function unassignPosition(pos) {
  if (!confirm(`确认解除职位「${pos.name}」与该部门的关联？`)) return

  try {
    await api.patch(`/positions/${pos.id}/`, {
      department_id: null
    })
    message.value = { type: 'success', text: '已解除关联' }
    await loadData()
    assignedPositions.value = allPositions.value.filter(p => p.department?.id === assignItem.value.id)
  } catch (e) {
    message.value = { type: 'error', text: '操作失败' }
  }
}

// 显示主管列表
function showSupervisors(item) {
  viewSupervisorsItem.value = item
}

// 打开设置主管弹窗
function showAssignSupervisor(item) {
  supervisorItem.value = item
  currentSupervisors.value = item.supervisors || []
  selectedSupervisor.value = ''
}

// 添加主管
async function addSupervisor() {
  if (!selectedSupervisor.value) return

  try {
    const newSupervisorIds = [...currentSupervisors.value.map(s => s.id), selectedSupervisor.value]
    await api.patch(`/departments/${supervisorItem.value.id}/`, {
      supervisor_ids: newSupervisorIds
    })
    message.value = { type: 'success', text: '主管已添加' }
    await loadData()
    // 更新当前主管列表
    const updatedDept = items.value.find(d => d.id === supervisorItem.value.id)
    if (updatedDept) {
      currentSupervisors.value = updatedDept.supervisors || []
      supervisorItem.value = updatedDept
    }
    selectedSupervisor.value = ''
  } catch (e) {
    message.value = { type: 'error', text: '添加主管失败' }
  }
}

// 移除主管
async function removeSupervisor(sup) {
  if (!confirm(`确认移除「${sup.name}」的主管身份？`)) return

  try {
    const newSupervisorIds = currentSupervisors.value.filter(s => s.id !== sup.id).map(s => s.id)
    await api.patch(`/departments/${supervisorItem.value.id}/`, {
      supervisor_ids: newSupervisorIds
    })
    message.value = { type: 'success', text: '已移除主管' }
    await loadData()
    // 更新当前主管列表
    const updatedDept = items.value.find(d => d.id === supervisorItem.value.id)
    if (updatedDept) {
      currentSupervisors.value = updatedDept.supervisors || []
      supervisorItem.value = updatedDept
    }
  } catch (e) {
    message.value = { type: 'error', text: '操作失败' }
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-container {
  padding: 1rem 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  background: #f8fafc;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 顶部标题栏 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  width: 40px;
  height: 40px;
  background: #eff6ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon img {
  width: 24px;
  height: 24px;
}

.header-icon svg {
  width: 20px;
  height: 20px;
  color: #2563eb;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* 统计徽章 */
.stat-badges {
  display: flex;
  gap: 1rem;
}

.stat-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.35rem 0.85rem;
  border-radius: 8px;
  background: #f1f5f9;
  min-width: 90px;
}

.stat-badge.active {
  background: #eff6ff;
}

.stat-badge.active .stat-value {
  color: #2563eb;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #2563eb;
  color: #fff;
  border: 0;
  padding: 0.5rem 1rem;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.18);
}

.btn-primary:hover {
  background: #1d4ed8;
}

/* 筛选栏 */
.filters-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.search-item {
  position: relative;
  max-width: 320px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  opacity: 0.55;
  pointer-events: none;
}

.filter-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.25rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.filter-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  padding: 0.45rem 0.9rem;
  background: #fff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 13px;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: #f8fafc;
  border-color: #94a3b8;
  color: #1e293b;
}

/* 表格容器 */
.table-container {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.data-table th {
  text-align: left;
  padding: 0.75rem 1rem;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
  font-size: 14px;
  vertical-align: middle;
}

.data-row:hover td {
  background: #f8fafc;
}

.col-name { min-width: 280px; width: 35%; }
.col-desc { width: 25%; }
.col-supervisors { width: 15%; }
.col-employees { width: 10%; }
.col-actions { width: 15%; min-width: 140px; }

/* 描述文本 */
.desc-text {
  color: #64748b;
  font-size: 13px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 树形结构样式 */
.expand-btn {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 0;
  cursor: pointer;
  color: #94a3b8;
  margin-right: 4px;
  transition: color 0.2s;
}

.expand-btn:hover {
  color: #475569;
}

.expand-btn svg {
  width: 14px;
  height: 14px;
  transition: transform 0.2s;
}

.expand-btn svg.rotated {
  transform: rotate(90deg);
}

.expand-placeholder {
  width: 24px;
  display: inline-block;
}

/* 树线 */
.tree-line {
  position: absolute;
  left: 21px;
  top: -50%;
  width: 1px;
  height: 100%;
  border-left: 1px dashed #cbd5e1;
}

.tree-line::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  width: 12px;
  border-top: 1px dashed #cbd5e1;
}

.tree-line.last-child {
  height: 50%;
}

/* 行样式 */
.root-row td {
  background: #fff;
}

.child-row td {
  background: #f8fafc;
}

.grandchild-row td {
  background: #f1f5f9;
}

.data-row:hover td {
  background: #e0f2fe !important;
}

/* 子部门提示 */
.children-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 0.125rem;
}

/* 筛选下拉框 */
.filter-dropdown {
  min-width: 200px;
}

/* 完整路径显示 */
.full-path {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 0.125rem;
}

/* 无数据 */
.text-muted {
  color: #94a3b8;
  font-size: 13px;
}

/* 高亮行动画 */
.highlight-row td {
  animation: highlight-pulse 0.5s ease-out 3;
}

@keyframes highlight-pulse {
  0%, 100% { background-color: transparent; }
  50% { background-color: #dbeafe; }
}

.dept-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.dept-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.dept-icon.small {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  font-size: 14px;
}

.dept-icon.tiny {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  font-size: 12px;
}

.dept-name {
  font-weight: 500;
  color: #1e293b;
}

.dept-text {
  display: flex;
  flex-direction: column;
}

.dept-path {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 0.125rem;
}

.desc-ellipsis {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: #64748b;
}

.position-count {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.6rem;
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.position-count:hover {
  background: rgba(14, 165, 233, 0.2);
}

.supervisor-count {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.6rem;
  background: rgba(139, 92, 246, 0.1);
  color: #7c3aed;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.supervisor-count:hover {
  background: rgba(139, 92, 246, 0.2);
}

.employee-count {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.6rem;
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.action-link {
  color: #0ea5e9;
  text-decoration: none;
  font-size: 13px;
  margin-right: 0.75rem;
}

.action-link:hover {
  text-decoration: underline;
}

.action-link.danger {
  color: #ef4444;
}

/* 加载状态 */
.loading-state {
  padding: 2rem;
}

.progress-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  width: 30%;
  background: linear-gradient(90deg, #38bdf8, #0ea5e9);
  animation: loading 1s ease-in-out infinite;
}

@keyframes loading {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #94a3b8;
}

/* 底部分页 */
.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.total-count {
  font-size: 13px;
  color: #64748b;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-size-label {
  font-size: 13px;
  color: #64748b;
}

.page-size-select {
  width: 70px;
}

.page-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #64748b;
}

.page-btn:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #475569;
  min-width: 60px;
  text-align: center;
}

/* Toast */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-width: 400px;
}

.toast-success { color: #059669; }
.toast-error { color: #dc2626; }
.toast-warning { color: #d97706; }

.toast-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #999;
}

.toast-enter-active { animation: toastIn 0.3s ease; }
.toast-leave-active { animation: toastOut 0.2s ease; }

@keyframes toastIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes toastOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-large {
  max-width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1e293b;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f1f5f9;
  border-radius: 8px;
  font-size: 20px;
  cursor: pointer;
  color: #64748b;
}

.modal-close:hover {
  background: #e2e8f0;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e2e8f0;
}

/* 表单 */
.form-row {
  margin-bottom: 1rem;
}

.form-row label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.4rem;
}

.required {
  color: #ef4444;
}

.form-row input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-row textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-row input:focus,
.form-row textarea:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: none;
}

.btn-cancel {
  padding: 0.6rem 1.2rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  color: #475569;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-submit {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  color: #fff;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 关联职位 */
.assign-section {
  margin-bottom: 1.5rem;
}

.assign-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 0.75rem;
}

.position-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.position-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.65rem;
  background: rgba(14, 165, 233, 0.1);
  color: #0284c7;
  border-radius: 20px;
  font-size: 13px;
}

.tag-remove {
  width: 18px;
  height: 18px;
  border: none;
  background: rgba(14, 165, 233, 0.2);
  border-radius: 50%;
  font-size: 14px;
  cursor: pointer;
  color: #0284c7;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-remove:hover {
  background: rgba(14, 165, 233, 0.3);
}

.empty-hint {
  font-size: 13px;
  color: #94a3b8;
  padding: 0.5rem 0;
}

.assign-search {
  display: flex;
  gap: 0.5rem;
}

.btn-add {
  padding: 0 1rem;
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
}

.btn-add:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 职位列表 */
.position-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.position-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem;
  background: #f8fafc;
  border-radius: 8px;
}

.pos-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pos-icon svg {
  width: 18px;
  height: 18px;
  color: #fff;
}

.pos-info {
  display: flex;
  flex-direction: column;
}

.pos-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.pos-salary {
  font-size: 12px;
  color: #64748b;
}

/* 主管样式 */
.supervisor-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.supervisor-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.65rem;
  background: rgba(139, 92, 246, 0.1);
  color: #7c3aed;
  border-radius: 20px;
  font-size: 13px;
}

.supervisor-tag .sup-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a78bfa, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 500;
}

.supervisor-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.supervisor-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem;
  background: #f8fafc;
  border-radius: 8px;
}

.sup-avatar-lg {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a78bfa, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 500;
}

.sup-info {
  display: flex;
  flex-direction: column;
}

.sup-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.sup-id {
  font-size: 12px;
  color: #64748b;
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .filters-bar {
    flex-direction: column;
  }

  .search-box {
    max-width: none;
  }

  .table-container {
    overflow-x: auto;
  }

  .data-table {
    min-width: 800px;
  }
}
.action-header {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.data-table th .settings-icon {
  width: 18px;
  height: 18px;
  color: #9ca3af;
  cursor: pointer;
  vertical-align: middle;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #fff;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
  color: #0f172a;
}

.btn-icon.danger:hover {
  border-color: #fecaca;
  background: #fef2f2;
  color: #ef4444;
}

.btn-icon svg {
  width: 16px;
  height: 16px;
}

</style>
