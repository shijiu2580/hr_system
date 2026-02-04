<template>
  <div class="layout-shell" :class="{ 'sidebar-open-desktop': !isMobile && !sidebarCollapsed }">
    <aside
      class="layout-sidebar"
      :class="{ collapsed: sidebarCollapsed, open: isMobile && sidebarOpen, 'is-mobile': isMobile }"
      @mouseenter="hoverIn"
      @mouseleave="hoverOut"
    >
      <h1 class="logo-title">
        <span class="logo-hr">HR</span>
        <span class="logo-text"> 系统</span>
      </h1>

      <div class="nav-group">
        <RouterLink to="/" class="nav-item">
          <span class="icon-box">
            <img class="icon" src="/icons/dashboard.svg" alt="" />
          </span>
          <span class="text-box">动态</span>
            </RouterLink>

        <!-- 员工菜单（带子菜单） -->
        <div class="nav-item-group">
          <div
            class="nav-item nav-item-parent"
            :class="{ 'has-active': isEmployeesActive }"
            @mouseenter="preloadSubmenu('employees')"
            @click="toggleSubmenu('employees')"
          >
            <span class="icon-box">
              <img class="icon" src="/icons/employees.svg" alt="" />
            </span>
            <span class="text-box">员工</span>
            <span class="arrow-box" v-show="!collapsed">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                :class="{ rotated: submenuOpen.employees }"
              >
                <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2"/>
              </svg>
            </span>
          </div>
              <transition name="submenu">
            <div class="submenu" v-show="submenuOpen.employees && !collapsed">
              <RouterLink to="/employees/manage" class="submenu-item" v-if="canManageEmployees">
                <span>员工管理</span>
              </RouterLink>
              <RouterLink to="/employees/list" class="submenu-item">
                <span>员工列表</span>
              </RouterLink>
              <RouterLink to="/employees/onboarding" class="submenu-item" v-if="canManageEmployees">
                <span>入职审核</span>
              </RouterLink>
            </div>
          </transition>
        </div>


        <!-- 考勤菜单（带子菜单） -->
        <div class="nav-item-group">
          <div
            class="nav-item nav-item-parent"
            :class="{ 'has-active': isAttendanceActive }"
            @mouseenter="preloadSubmenu('attendance')"
            @click="toggleSubmenu('attendance')"
          >
            <span class="icon-box">
              <img class="icon" src="/icons/attendance.svg" alt="" />
            </span>
            <span class="text-box">考勤</span>
            <span class="arrow-box" v-show="!collapsed">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                :class="{ rotated: submenuOpen.attendance }"
              >
                <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2"/>
              </svg>
            </span>
          </div>
          <transition name="submenu">
            <div class="submenu" v-show="submenuOpen.attendance && !collapsed">
              <RouterLink to="/attendance/records" class="submenu-item">
                <span>考勤记录</span>
              </RouterLink>
              <RouterLink to="/attendance/manage" class="submenu-item">
                <span>考勤管理</span>
              </RouterLink>
              <RouterLink to="/attendance/alerts" class="submenu-item">
                <span>异常提醒</span>
              </RouterLink>
              <RouterLink to="/attendance/locations" class="submenu-item" v-if="canManageLocations">
                <span>考勤地点</span>
              </RouterLink>
              <RouterLink to="/attendance/approval" class="submenu-item" v-if="canApproveAttendance">
                <span>补签审批</span>
              </RouterLink>
            </div>
          </transition>
        </div>


        <!-- 请假菜单（带子菜单） -->
        <div class="nav-item-group">
          <div
            class="nav-item nav-item-parent"
            :class="{ 'has-active': isLeavesActive }"
            @mouseenter="preloadSubmenu('leaves')"
            @click="toggleSubmenu('leaves')"
          >
            <span class="icon-box">
              <img class="icon" src="/icons/leaves.svg" alt="" />
            </span>
            <span class="text-box">请假</span>
            <span class="arrow-box" v-show="!collapsed">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                :class="{ rotated: submenuOpen.leaves }"
              >
                <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2"/>
              </svg>
            </span>
          </div>
          <transition name="submenu">
            <div class="submenu" v-show="submenuOpen.leaves && !collapsed">
              <RouterLink to="/leaves/apply" class="submenu-item">
                <span>请假申请</span>
              </RouterLink>
              <RouterLink to="/leaves/business" class="submenu-item">
                <span>出差申请</span>
              </RouterLink>
              <RouterLink to="/leaves/approval" class="submenu-item" v-if="canApproveLeave">
                <span>审批流程</span>
              </RouterLink>
            </div>
          </transition>
        </div>


        <!-- 薪资菜单（带子菜单） -->
        <div class="nav-item-group">
          <div
            class="nav-item nav-item-parent"
            :class="{ 'has-active': isSalariesActive }"
            @mouseenter="preloadSubmenu('salaries')"
            @click="toggleSubmenu('salaries')"
          >
            <span class="icon-box">
              <img class="icon" src="/icons/salaries.svg" alt="" />
            </span>
            <span class="text-box">薪资</span>
            <span class="arrow-box" v-show="!collapsed">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                :class="{ rotated: submenuOpen.salaries }"
              >
                <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2"/>
              </svg>
            </span>
          </div>
          <transition name="submenu">
            <div class="submenu" v-show="submenuOpen.salaries && !collapsed">
              <RouterLink to="/salaries" class="submenu-item" v-if="canViewAllSalary">
                <span>薪资管理</span>
              </RouterLink>
              <RouterLink to="/salaries/records" class="submenu-item">
                <span>薪资记录</span>
              </RouterLink>
              <RouterLink to="/salaries/travel-expense" class="submenu-item">
                <span>差旅报销</span>
              </RouterLink>
              <RouterLink to="/salaries/expense-approval" class="submenu-item" v-if="canApproveExpense">
                <span>报销审批</span>
              </RouterLink>
            </div>
          </transition>
        </div>

        <RouterLink to="/positions" class="nav-item">
          <span class="icon-box">
            <img class="icon" src="/icons/positions.svg" alt="" />
          </span>
          <span class="text-box">职位</span>
        </RouterLink>

        <RouterLink to="/departments" class="nav-item">
          <span class="icon-box">
            <img class="icon" src="/icons/departments.svg" alt="" />
          </span>
          <span class="text-box">部门</span>
        </RouterLink>

        <RouterLink to="/documents" class="nav-item">
          <span class="icon-box">
            <img class="icon" src="/icons/documents.svg" alt="" />
          </span>
          <span class="text-box">文档中心</span>
        </RouterLink>

        <RouterLink to="/reports" class="nav-item" v-if="canViewReports">
          <span class="icon-box">
            <img class="icon" src="/icons/reports.svg" alt="" />
          </span>
          <span class="text-box">大数据报表</span>
        </RouterLink>


        <!-- 离职申请（带子菜单） -->
        <div class="nav-item-group">
          <div
            class="nav-item nav-item-parent"
            :class="{ 'has-active': isResignationActive }"
            @mouseenter="preloadSubmenu('resignation')"
            @click="toggleSubmenu('resignation')"
          >
            <span class="icon-box">
              <img class="icon" src="/icons/resignation.svg" alt="" />
            </span>
            <span class="text-box">离职申请</span>
            <span class="arrow-box" v-show="!collapsed">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                :class="{ rotated: submenuOpen.resignation }"
              >
                <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2"/>
              </svg>
            </span>
          </div>
          <transition name="submenu">
            <div class="submenu" v-show="submenuOpen.resignation && !collapsed">
              <RouterLink to="/resignation/progress" class="submenu-item">
                <span>离职进度</span>
              </RouterLink>
              <RouterLink to="/resignation/apply" class="submenu-item">
                <span>发起申请</span>
              </RouterLink>
              <RouterLink to="/resignation/approval" class="submenu-item" v-if="canApproveLeave">
                <span>离职审批</span>
              </RouterLink>
            </div>
          </transition>
        </div>


        <RouterLink v-if="canViewSystem" to="/system" class="nav-item">
          <span class="icon-box">
            <img class="icon" src="/icons/system.svg" alt="" />
          </span>
          <span class="text-box">系统</span>
        </RouterLink>

        <RouterLink v-if="canViewRbac" to="/rbac" class="nav-item">
          <span class="icon-box">
            <img class="icon" src="/icons/rbac.svg" alt="" />
          </span>
          <span class="text-box">权限管理</span>
        </RouterLink>

        <RouterLink v-if="canViewUsers" to="/users" class="nav-item">
          <span class="icon-box">
            <img class="icon" src="/icons/users.svg" alt="" />
          </span>
          <span class="text-box">用户管理</span>
        </RouterLink>

        <RouterLink to="/account" class="nav-item">
          <span class="icon-box">
            <img class="icon" src="/icons/account.svg" alt="" />
          </span>
          <span class="text-box">账号设置</span>
        </RouterLink>
      </div>
    </aside>

    <div class="sidebar-backdrop" v-if="isMobile && sidebarOpen" @click="closeSidebar"></div>

    <div class="layout-main">
      <div class="top-bar">
        <div class="top-left">
          <button v-if="isMobile" class="menu-toggle" @click="toggleSidebar" aria-label="切换菜单">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>

        <div class="user-box" v-if="auth.ready">
          <!-- 通知铃铛 -->
          <div v-if="auth.user" class="notification-bell" @click="toggleNotifications">
            <img src="/icons/Remind.svg" alt="通知" class="bell-icon" />
            <span v-if="pendingCount > 0" class="badge-dot">{{ pendingCount }}</span>
          </div>

          <span v-if="auth.user" class="user-info">
            <img
              v-if="auth.user.avatar"
              :src="auth.user.avatar"
              alt=""
              class="user-avatar"
            />
            <span v-else class="user-avatar-placeholder">
              {{ userInitials }}
            </span>
            <span class="user-name">
              {{ auth.user.employee_name || auth.user.username }}
            </span>
          </span>
          <button v-if="auth.user" @click="logout">退出</button>
          <button v-else @click="goLogin">登录</button>
          <button class="theme-toggle" @click="toggleTheme">
            {{ themeLabel }}
          </button>

          <!-- 通知下拉菜单 -->
          <div v-if="showNotifications" class="notification-dropdown">
            <div class="notification-header">
              <h3>待审批</h3>
              <button @click="showNotifications = false" class="close-btn">✕</button>
            </div>
            <div v-if="pendingCount === 0" class="notification-empty">
              <p>暂无待审批项</p>
            </div>
            <div v-else class="notification-list">
              <router-link v-if="pendingItems.attendance > 0" to="/attendance/approval" class="notification-item" @click="showNotifications = false">
                <span class="item-text">
                  补签审批
                  <span class="item-count">{{ pendingItems.attendance }}</span>
                </span>
              </router-link>
              <router-link v-if="pendingItems.leave > 0" to="/leaves/approval" class="notification-item" @click="showNotifications = false">
                <span class="item-text">
                  请假审批
                  <span class="item-count">{{ pendingItems.leave }}</span>
                </span>
              </router-link>
              <router-link v-if="pendingItems.resignation > 0" to="/resignation/approval" class="notification-item" @click="showNotifications = false">
                <span class="item-text">
                  离职审批
                  <span class="item-count">{{ pendingItems.resignation }}</span>
                </span>
              </router-link>
              <router-link v-if="pendingItems.businessTrip > 0" to="/leaves/business" class="notification-item" @click="showNotifications = false">
                <span class="item-text">
                  出差审批
                  <span class="item-count">{{ pendingItems.businessTrip }}</span>
                </span>
              </router-link>
              <router-link v-if="pendingItems.expense > 0" to="/salaries/travel-expense" class="notification-item" @click="showNotifications = false">
                <span class="item-text">
                  差旅报销
                  <span class="item-count">{{ pendingItems.expense }}</span>
                </span>
              </router-link>
              <router-link v-if="pendingItems.onboarding > 0" to="/employees/onboarding" class="notification-item" @click="showNotifications = false">
                <span class="item-text">
                  入职审批
                  <span class="item-count">{{ pendingItems.onboarding }}</span>
                </span>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <div class="page-wrapper">
        <div
          v-if="globalError"
          style="background:#fee2e2;color:#991b1b;padding:.6rem .75rem;border:1px solid #fecaca;border-radius:6px;font-size:13px;margin-bottom:1rem;"
        >
          发生脚本错误：{{ globalError }}
        </div>
        <slot />
      </div>

      <!-- ICP备案号 -->
      <footer class="icp-footer">
        <a href="https://beian.miit.gov.cn/#/Integrated/recordQuery" target="_blank" rel="noopener">
          <svg
            class="icp-icon"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>蜀ICP备2026004175号-1</span>
        </a>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter, useRoute } from 'vue-router';
import { hasPermission, isAdmin, Permissions } from '../utils/permissions';
import { preloadSubmenu } from '../router';
import api from '../utils/api';

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const dark = ref(false);
const globalError = ref(null);
const isMobile = ref(false);
const sidebarOpen = ref(false);
const collapsed = ref(true);
const showNotifications = ref(false);
const pendingItems = ref({
  attendance: 0,      // 补签审批
  leave: 0,           // 请假审批
  resignation: 0,     // 离职审批
  businessTrip: 0,    // 出差审批
  expense: 0,         // 差旅报销审批
  onboarding: 0       // 入职审批
});

// 用户头像首字母
const userInitials = computed(() => {
  const name = auth.user?.employee_name || auth.user?.username || '';
  if (!name) return '?';
  return name.charAt(0).toUpperCase();
});

// 计算待审批总数
const pendingCount = computed(() => {
  return pendingItems.value.attendance +
         pendingItems.value.leave +
         pendingItems.value.resignation +
         pendingItems.value.businessTrip +
         pendingItems.value.expense +
         pendingItems.value.onboarding;
});

// 切换通知面板
function toggleNotifications() {
  showNotifications.value = !showNotifications.value;
  if (showNotifications.value) {
    fetchPendingApprovals();
  }
}

// 获取待审批数量
async function fetchPendingApprovals() {
  try {
    const promises = [
      // 1. 补签审批
      api.get('/attendance/supplement/pending/', { params: { page_size: 1 } })
        .then(res => { pendingItems.value.attendance = res.data?.count || 0; })
        .catch(() => { pendingItems.value.attendance = 0; }),

      // 2. 请假审批 - 统计非离职类型的待审批请假
      api.get('/leaves/', { params: { status: 'pending', page_size: 100 } })
        .then(res => {
          const results = res.data?.results || [];
          pendingItems.value.leave = results.filter(item => item.leave_type !== 'resignation').length;
        })
        .catch(() => { pendingItems.value.leave = 0; }),

      // 3. 离职审批 - 只统计离职类型
      api.get('/leaves/', { params: { status: 'pending', leave_type: 'resignation', page_size: 1 } })
        .then(res => { pendingItems.value.resignation = res.data?.count || 0; })
        .catch(() => { pendingItems.value.resignation = 0; }),

      // 4. 出差审批
      api.get('/business-trips/', { params: { status: 'pending', page_size: 1 } })
        .then(res => { pendingItems.value.businessTrip = res.data?.count || 0; })
        .catch(() => { pendingItems.value.businessTrip = 0; }),

      // 5. 差旅报销审批
      api.get('/travel-expenses/', { params: { status: 'pending', page_size: 1 } })
        .then(res => { pendingItems.value.expense = res.data?.count || 0; })
        .catch(() => { pendingItems.value.expense = 0; }),

      // 6. 入职审批
      api.get('/onboarding/pending/', { params: { page_size: 1 } })
        .then(res => { pendingItems.value.onboarding = res.data?.count || 0; })
        .catch(() => { pendingItems.value.onboarding = 0; })
    ];

    await Promise.all(promises);
  } catch (err) {
    // 静默处理错误
  }
}

// 权限计算属性
const canManageEmployees = computed(() =>
  isAdmin() || hasPermission(Permissions.EMPLOYEE_VIEW)
);
const canViewAllAttendance = computed(() =>
  isAdmin() || hasPermission(Permissions.ATTENDANCE_VIEW_ALL)
);
const canManageLocations = computed(() =>
  isAdmin() || hasPermission(Permissions.ATTENDANCE_LOCATION)
);
const canApproveAttendance = computed(() =>
  isAdmin() || hasPermission(Permissions.ATTENDANCE_APPROVE)
);
const canApproveLeave = computed(() =>
  isAdmin() || hasPermission(Permissions.LEAVE_APPROVE)
);
const canViewAllSalary = computed(() =>
  isAdmin() || hasPermission(Permissions.SALARY_VIEW_ALL)
);
const canApproveExpense = computed(() =>
  isAdmin() || hasPermission(Permissions.EXPENSE_APPROVE)
);
const canViewReports = computed(() =>
  isAdmin() || hasPermission(Permissions.REPORT_VIEW)
);
const canViewSystem = computed(() =>
  isAdmin() || hasPermission(Permissions.SYSTEM_VIEW)
);
const canViewRbac = computed(() =>
  isAdmin() || hasPermission(Permissions.RBAC_VIEW)
);
const canViewUsers = computed(() =>
  isAdmin() || hasPermission(Permissions.USER_VIEW)
);

function goLogin() {
  router.replace('/login');
}

async function logout() {
  await auth.logout();
  router.replace('/login');
}

function applyTheme() {
  const root = document.documentElement;
  root.setAttribute('data-theme', dark.value ? 'dark' : 'light');
}

function toggleTheme() {
  dark.value = !dark.value;
  applyTheme();
}

const themeLabel = computed(() => dark.value ? '浅色' : '深色');

const sidebarCollapsed = computed(() => {
  if (isMobile.value) return !sidebarOpen.value;
  return collapsed.value;
});

// 悬停折叠逻辑
function hoverIn() {
  if (isMobile.value) return;
  collapsed.value = false;
}

function hoverOut() {
  if (isMobile.value) return;
  collapsed.value = true;
  closeAllSubmenus();
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value;
}

function closeSidebar() {
  sidebarOpen.value = false;
  closeAllSubmenus();
}

// 子菜单状态
const submenuOpen = ref({
  employees: false,
  attendance: false,
  leaves: false,
  salaries: false,
  resignation: false
});

function toggleSubmenu(name) {
  const willOpen = !submenuOpen.value[name];
  // 先关闭其他子菜单
  Object.keys(submenuOpen.value).forEach(key => {
    if (key !== name) {
      submenuOpen.value[key] = false;
    }
  });
  // 切换当前子菜单
  submenuOpen.value[name] = willOpen;

  // 展开时预加载对应子页面，减少点击后的等待
  if (willOpen) {
    preloadSubmenu(name);
  }
}

function closeAllSubmenus() {
  Object.keys(submenuOpen.value).forEach(key => {
    submenuOpen.value[key] = false;
  });
}

// 判断各菜单是否有激活项
const isEmployeesActive = computed(() => route.path.startsWith('/employees'));
const isAttendanceActive = computed(() => route.path.startsWith('/attendance'));
const isLeavesActive = computed(() => route.path.startsWith('/leaves'));
const isSalariesActive = computed(() => route.path.startsWith('/salaries'));
const isResignationActive = computed(() => route.path.startsWith('/resignation'));

let pendingInterval = null;

onMounted(() => {
  applyTheme();
  updateIsMobile();
  window.addEventListener('resize', updateIsMobile);

  // 获取待审批数量（如果有审批权限）
  if (auth.user && (canApproveAttendance.value || canApproveLeave.value || canApproveExpense.value)) {
    fetchPendingApprovals();
    // 每5分钟刷新一次
    pendingInterval = setInterval(fetchPendingApprovals, 5 * 60 * 1000);
  }
});

window.addEventListener('error', (e) => {
  globalError.value = e.message;
});

onUnmounted(() => {
  window.removeEventListener('resize', updateIsMobile);
  if (pendingInterval) {
    clearInterval(pendingInterval);
    pendingInterval = null;
  }
});

watch(() => route.fullPath, () => {
  if (isMobile.value) {
    closeSidebar();
  }
});

function updateIsMobile() {
  isMobile.value = window.innerWidth <= 960;
  if (!isMobile.value) {
    sidebarOpen.value = false;
    collapsed.value = true;
  }
}
</script>

<style scoped>
/* ==================== 全局布局 ==================== */
.layout-shell {
  display: flex;
  min-height: 100vh;
  background: #f8fafc;
}

/* ==================== 侧边栏 ==================== */
.layout-sidebar {
  width: 160px;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  padding: 1rem 0 4rem; /* 底部留出 4rem 空间 */
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  overflow-y: auto;
  overflow-x: hidden;
  z-index: 50;
  transition: width .35s cubic-bezier(.4, 0, .2, 1), box-shadow .35s cubic-bezier(.4, 0, .2, 1), transform .3s cubic-bezier(.4, 0, .2, 1);
  box-shadow: 0 0 0 rgba(0, 0, 0, 0);
  scrollbar-width: none;
  -ms-overflow-style: none;
  will-change: width, box-shadow;
}

.layout-sidebar::-webkit-scrollbar {
  display: none;
}

.layout-sidebar.collapsed {
  width: 64px;
}

.layout-sidebar:not(.collapsed) {
  box-shadow: 0 4px 18px -4px rgba(0, 0, 0, .18), 0 2px 8px -2px rgba(0, 0, 0, .12);
}

/* ==================== Logo ==================== */
.logo-title {
  font-size: 18px;
  margin: 0 0 .8rem;
  font-weight: 600;
  line-height: 1;
  white-space: nowrap;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.logo-hr {
  width: 64px;
  min-width: 64px;
  text-align: center;
  flex-shrink: 0;
}

.logo-text {
  transition: opacity .3s ease, transform .3s ease;
  opacity: 1;
  transform: translateX(0);
}

.layout-sidebar.collapsed .logo-text {
  opacity: 0;
  transform: translateX(-8px);
  pointer-events: none;
}

/* ==================== 导航组 ==================== */
.nav-group {
  display: flex;
  flex-direction: column;
  gap: .25rem;
  margin-top: .4rem;
  flex: 1;
  min-height: 0;
}

.nav-group a.nav-item {
  display: flex;
  align-items: center;
  padding: .55rem 0;
  border-radius: 6px;
  text-decoration: none;
  color: #1e293b;
  font-size: 14px;
  line-height: 1.2;
  white-space: nowrap;
  width: 100%;
  box-sizing: border-box;
}

.nav-group a .icon-box,
.nav-item-parent .icon-box {
  width: 64px;
  min-width: 64px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}

.nav-group a .icon,
.nav-item-parent .icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

.nav-group a .text-box,
.nav-item-parent .text-box {
  flex: 1;
  transition: opacity .3s ease, transform .3s ease;
  overflow: hidden;
  transform: translateX(0);
  opacity: 1;
}

.layout-sidebar.collapsed .nav-group a .text-box,
.layout-sidebar.collapsed .nav-item-parent .text-box {
  opacity: 0;
  transform: translateX(-8px);
  pointer-events: none;
}

/* ==================== 导航项悬停和激活状态 ==================== */
@media (hover: hover) {
  .nav-group a.nav-item:hover,
  .nav-item-parent:hover {
    background: #e2e8f0;
  }
}

.nav-group a.nav-item:active,
.nav-item-parent:active {
  transform: scale(0.96);
}

.nav-group a.router-link-active {
  background: #2563eb;
  color: #fff;
}

/* ==================== 子菜单 ==================== */
.nav-item-group {
  position: relative;
}

.nav-item-parent {
  display: flex;
  align-items: center;
  padding: .55rem 0;
  border-radius: 6px;
  color: #1e293b;
  font-size: 14px;
  line-height: 1.2;
  white-space: nowrap;
  width: 100%;
  box-sizing: border-box;
  cursor: pointer;
  transition: background .2s;
}

.nav-item-parent.has-active {
  background: rgba(37, 99, 235, .1);
  color: #2563eb;
}

.arrow-box {
  width: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 8px;
  transition: transform .2s;
}

.arrow-box svg {
  transition: transform .2s;
}

.arrow-box svg.rotated {
  transform: rotate(180deg);
}

.submenu {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 4px 27px 4px 28px;
  overflow: hidden;
  transition: all .35s ease-out, opacity .35s ease, max-height .35s ease;
  white-space: nowrap;
  max-height: 200px;
  opacity: 1;
}

.layout-sidebar.collapsed .submenu {
  max-height: 0;
  opacity: 0;
  padding: 0 27px 0 28px;
  pointer-events: none;
}

.submenu-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: .5rem .75rem;
  border-radius: 6px;
  text-decoration: none;
  color: #64748b;
  font-size: 13px;
  transition: all .2s;
  white-space: nowrap;
}

.submenu-item:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.submenu-item:active {
  transform: scale(0.96);
}

.submenu-item.router-link-active {
  background: #2563eb;
  color: #fff;
}

/* ==================== 子菜单动画 ==================== */
.submenu-enter-active {
  transition: all 0.6s ease-out;
  max-height: 200px;
}

.submenu-leave-active {
  transition: all 0.4s ease-in;
  max-height: 200px;
}

.submenu-enter-from,
.submenu-leave-to {
  opacity: 0;
  max-height: 0;
}

/* ==================== 主内容区 ==================== */
.layout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  margin-left: 64px;
}

.top-bar {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
}

.top-left {
  display: flex;
  align-items: center;
  gap: .75rem;
}

.menu-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 10px;
  cursor: pointer;
  color: #1f2937;
  transition: all .2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .08);
}

.menu-toggle:hover {
  background: #f1f5f9;
}

.user-box {
  display: flex;
  align-items: center;
  gap: .65rem;
  font-size: 14px;
  position: relative;
}

/* ==================== 通知铃铛 ==================== */
.notification-bell {
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 8px;
  transition: all .2s;
  color: #64748b;
}

.notification-bell .bell-icon {
  width: 20px;
  height: 20px;
  transition: transform .2s;
  filter: invert(42%) sepia(8%) saturate(926%) hue-rotate(180deg) brightness(93%) contrast(87%);
}

.notification-bell:hover {
  background: #f1f5f9;
}

.notification-bell:hover .bell-icon {
  transform: scale(1.1) rotate(15deg);
  filter: invert(39%) sepia(93%) saturate(1757%) hue-rotate(205deg) brightness(96%) contrast(91%);
}

.badge-dot {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  font-weight: 600;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,.2);
}

/* ==================== 通知下拉菜单 ==================== */
.notification-dropdown {
  position: absolute;
  top: 54px;
  right: 12px;
  width: 280px;
  max-height: 500px;
  background: #ffffff;
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 12px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(0,0,0,0.02);
  z-index: 1000;
  overflow: hidden;
  transform-origin: top right;
  animation: slideDown .2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-5px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  background: #fff;
}

.notification-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
}

.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 16px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all .2s;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #64748b;
}

.notification-empty {
  padding: 40px 20px;
  text-align: center;
  color: #94a3b8;
  background: #f8fafc;
}

.notification-empty p {
  margin: 0;
  font-size: 13px;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
  background: #f8fafc;
  padding: 8px;
}

.notification-list::-webkit-scrollbar {
  width: 4px;
}
.notification-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.notification-item {
  display: block;
  text-decoration: none;
  color: inherit;
  margin-bottom: 8px;
  padding: 0;
  border: none;
}

.notification-item:hover {
  background: transparent;
}

.notification-item:last-child {
  margin-bottom: 0;
}

.item-text {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #334155;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.notification-item:hover .item-text {
  border-color: #cbd5e1;
  background: #fff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
  color: #0f172a;
}

.item-count {
  background: #ef4444;
  color: white;
  font-size: 11px;
  font-weight: 700;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  margin-left: auto;
  box-shadow: 0 1px 2px rgba(239, 68, 68, 0.3);
}

.user-box {
  display: flex;
  align-items: center;
  gap: .65rem;
  font-size: 14px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: .5rem;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar-placeholder {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.user-name {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.theme-toggle,
.user-box button {
  padding: .45rem .75rem;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
}

.user-box button:hover,
.theme-toggle:hover {
  filter: brightness(.95);
}

.page-wrapper {
  padding: 1rem 1.5rem;
  overflow: auto;
  flex: 1;
}

.sidebar-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, .35);
  z-index: 40;
}

@media (max-width: 960px) {
  .layout-shell {
    flex-direction: column;
  }

  .layout-sidebar {
    position: fixed;
    width: 240px;
    transform: translateX(-100%);
    box-shadow: 0 10px 40px rgba(0, 0, 0, .18);
  }

  .layout-sidebar.collapsed {
    width: 240px;
  }

  .layout-sidebar.open {
    transform: translateX(0);
  }

  .layout-main {
    margin-left: 0;
    min-height: 100vh;
  }

  .top-bar {
    justify-content: space-between;
  }

  .menu-toggle {
    display: inline-flex;
  }

  .sidebar-backdrop {
    display: block;
  }
}

/* ==================== ICP 备案 ==================== */
.icp-footer {
  text-align: center;
  padding: 1.5rem 0 .5rem;
  font-size: 12px;
  color: #94a3b8;
}

.icp-footer a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 99px;
  color: #94a3b8;
  text-decoration: none;
  transition: all .2s;
}

.icp-footer a:hover {
  color: #3b82f6;
  background: #eff6ff;
}

/* ==================== 暗色主题 ==================== */
[data-theme=dark] .layout-shell {
  background: #0f172a;
}

[data-theme=dark] .layout-sidebar {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  border-right-color: #334155;
  color: #e2e8f0;
}

[data-theme=dark] .logo-title {
  color: #f8fafc;
}

[data-theme=dark] .nav-group a.nav-item {
  color: #94a3b8;
}

[data-theme=dark] .nav-group a .icon {
  filter: brightness(0) invert(1) opacity(.85);
}

[data-theme=dark] .nav-group a.nav-item:hover,
[data-theme=dark] .nav-item-parent:hover {
  background: rgba(148, 163, 184, .15);
  color: #e2e8f0;
}

[data-theme=dark] .nav-group a.router-link-active {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: #fff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, .35);
}

[data-theme=dark] .nav-item-parent {
  color: #94a3b8;
}

[data-theme=dark] .nav-item-parent.has-active {
  background: rgba(59, 130, 246, .2);
  color: #60a5fa;
}

[data-theme=dark] .submenu-item {
  color: #94a3b8;
}

[data-theme=dark] .submenu-item:hover {
  background: rgba(148, 163, 184, .1);
  color: #e2e8f0;
}

[data-theme=dark] .submenu-item.router-link-active {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: #fff;
}

[data-theme=dark] .top-bar {
  background: #1e293b;
  border-bottom-color: #334155;
}

[data-theme=dark] .user-box {
  color: #e2e8f0;
}

[data-theme=dark] .theme-toggle,
[data-theme=dark] .user-box button {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

[data-theme=dark] .page-wrapper {
  background: #0f172a;
}

[data-theme=dark] .icp-footer a:hover {
  background: #1e293b;
  color: #60a5fa;
}
</style>
