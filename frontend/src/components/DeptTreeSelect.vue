<template>
  <div class="dept-tree-select" :class="{ open: isOpen }" ref="selectRef">
    <div class="select-trigger" @click="toggle" tabindex="0">
      <span class="select-value">{{ displayValue }}</span>
      <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M6 9l6 6 6-6" />
      </svg>
    </div>
    <Teleport to="body">
      <Transition name="dropdown">
        <div v-if="isOpen" class="select-dropdown" :style="dropdownStyle" ref="dropdownRef">
          <div class="options-list">
            <!-- 全部/空选项 -->
            <div
              v-if="showEmpty"
              class="select-option"
              :class="{ selected: modelValue === '' }"
              @click="selectDept('')"
            >
              {{ emptyLabel }}
            </div>
            <!-- 树形部门 -->
            <template v-for="dept in treeData" :key="dept.id">
              <div
                class="select-option"
                :class="{
                  selected: modelValue === dept.id,
                  'dept-parent': dept.children && dept.children.length
                }"
                @click="selectDept(dept.id)"
              >
                <span
                  v-if="dept.children && dept.children.length"
                  class="expand-icon"
                  @click.stop="toggleExpand(dept.id)"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ rotated: expanded[dept.id] }">
                    <path d="M9 18l6-6-6-6" />
                  </svg>
                </span>
                <span class="dept-name">{{ dept.name }}</span>
                <span v-if="dept.children && dept.children.length" class="child-count">({{ dept.children.length }})</span>
              </div>
              <!-- 子部门 -->
              <template v-if="expanded[dept.id] && dept.children">
                <div
                  v-for="child in dept.children"
                  :key="child.id"
                  class="select-option dept-child"
                  :class="{ selected: modelValue === child.id }"
                  @click="selectDept(child.id)"
                >
                  <span class="child-indent"></span>
                  <span class="dept-name">{{ child.name }}</span>
                </div>
              </template>
            </template>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  departments: { type: Array, default: () => [] },
  placeholder: { type: String, default: '全部部门' },
  emptyLabel: { type: String, default: '全部部门' },
  showEmpty: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const selectRef = ref(null)
const dropdownRef = ref(null)
const dropdownStyle = ref({})
const expanded = ref({})

// 构建树形结构
const treeData = computed(() => {
  const depts = props.departments
  const map = {}
  const roots = []

  // 先建立 id -> dept 映射
  depts.forEach(d => {
    map[d.id] = { ...d, children: [] }
  })

  // 建立父子关系
  depts.forEach(d => {
    const parentId = d.parent?.id || d.parent
    if (parentId && map[parentId]) {
      map[parentId].children.push(map[d.id])
    } else {
      roots.push(map[d.id])
    }
  })

  // 排序：没有子部门的排前面，有子部门的排后面
  roots.sort((a, b) => {
    const aHasChildren = a.children && a.children.length > 0
    const bHasChildren = b.children && b.children.length > 0
    if (aHasChildren === bHasChildren) return 0
    return aHasChildren ? 1 : -1
  })

  return roots
})

// 显示值
const displayValue = computed(() => {
  if (!props.modelValue) return props.placeholder
  const findDept = (list) => {
    for (const d of list) {
      if (d.id === props.modelValue) return d.name
      if (d.children) {
        const found = findDept(d.children)
        if (found) return found
      }
    }
    return null
  }
  return findDept(treeData.value) || props.placeholder
})

function updateDropdownPosition() {
  if (!selectRef.value) return
  const rect = selectRef.value.getBoundingClientRect()
  dropdownStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`,
    width: `${Math.max(rect.width, 200)}px`,
    zIndex: 9999
  }
}

function toggle() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    updateDropdownPosition()
  }
}

function selectDept(id) {
  emit('update:modelValue', id)
  emit('change', id)
  isOpen.value = false
}

function toggleExpand(id) {
  expanded.value[id] = !expanded.value[id]
}

// 点击外部关闭
function handleClickOutside(e) {
  if (selectRef.value && !selectRef.value.contains(e.target) &&
      dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.dept-tree-select {
  position: relative;
  min-width: 140px;
}

.select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 0 12px;
  height: 38px;
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s;
}

.select-trigger:hover {
  border-color: rgba(148, 163, 184, 0.6);
}

.dept-tree-select.open .select-trigger {
  border-color: rgba(148, 163, 184, 0.6);
  background: #f8fafc;
}

.select-value {
  flex: 1;
  font-size: 13px;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.select-arrow {
  width: 16px;
  height: 16px;
  color: #94a3b8;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.dept-tree-select.open .select-arrow {
  transform: rotate(180deg);
}

.select-dropdown {
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  max-height: 320px;
  overflow: hidden;
}

.options-list {
  max-height: 320px;
  overflow-y: auto;
  padding: 4px;
}

.select-option {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  font-size: 13px;
  color: #334155;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s;
}

.select-option:hover {
  background: #f1f5f9;
}

.select-option.selected {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

.dept-parent {
  font-weight: 500;
}

.dept-child {
  padding-left: 12px;
  font-weight: 400;
  color: #64748b;
}

.dept-child:hover {
  color: #334155;
}

.dept-child.selected {
  color: #2563eb;
}

.expand-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 18px;
  cursor: pointer;
  border-radius: 4px;
  flex-shrink: 0;
}

.expand-icon:hover {
  background: #e2e8f0;
}

.expand-icon svg {
  width: 14px;
  height: 14px;
  color: #64748b;
  transition: transform 0.2s;
}

.expand-icon svg.rotated {
  transform: rotate(90deg);
}

.expand-placeholder {
  width: 20px;
  flex-shrink: 0;
}

.child-indent {
  width: 20px;
  flex-shrink: 0;
}

.dept-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.child-count {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 400;
}

/* 动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
