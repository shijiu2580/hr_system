<template>
  <div class="layout-shell">
  <aside class="layout-sidebar" :class="{collapsed}" @mouseenter="hoverIn" @mouseleave="hoverOut">
  <h1 class="logo-title"><span class="logo-hr">HR</span><span class="logo-text"> 系统</span></h1>
      <div class="nav-group">
    <RouterLink to="/" class="nav-item">
      <span class="icon-box"><img class="icon" src="/icons/dashboard.svg" alt="" /></span><span class="text-box">动态</span>
    </RouterLink>

    <!-- 员工菜单（带子菜单） -->
    <div class="nav-item-group">
      <div class="nav-item nav-item-parent" :class="{ 'has-active': isEmployeesActive }" @click="toggleSubmenu('employees')">
        <span class="icon-box"><img class="icon" src="/icons/employees.svg" alt="" /></span>
        <span class="text-box">员工</span>
        <span class="arrow-box" v-show="!collapsed">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" :class="{ rotated: submenuOpen.employees }">
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
      <div class="nav-item nav-item-parent" :class="{ 'has-active': isAttendanceActive }" @click="toggleSubmenu('attendance')">
        <span class="icon-box"><img class="icon" src="/icons/attendance.svg" alt="" /></span>
        <span class="text-box">考勤</span>
        <span class="arrow-box" v-show="!collapsed">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" :class="{ rotated: submenuOpen.attendance }">
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
      <div class="nav-item nav-item-parent" :class="{ 'has-active': isLeavesActive }" @click="toggleSubmenu('leaves')">
        <span class="icon-box"><img class="icon" src="/icons/leaves.svg" alt="" /></span>
        <span class="text-box">请假</span>
        <span class="arrow-box" v-show="!collapsed">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" :class="{ rotated: submenuOpen.leaves }">
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
      <div class="nav-item nav-item-parent" :class="{ 'has-active': isSalariesActive }" @click="toggleSubmenu('salaries')">
        <span class="icon-box"><img class="icon" src="/icons/salaries.svg" alt="" /></span>
        <span class="text-box">薪资</span>
        <span class="arrow-box" v-show="!collapsed">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" :class="{ rotated: submenuOpen.salaries }">
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
      <span class="icon-box"><img class="icon" src="/icons/positions.svg" alt="" /></span><span class="text-box">职位</span>
    </RouterLink>
    <RouterLink to="/departments" class="nav-item">
      <span class="icon-box"><img class="icon" src="/icons/departments.svg" alt="" /></span><span class="text-box">部门</span>
    </RouterLink>
    <RouterLink to="/documents" class="nav-item">
      <span class="icon-box"><img class="icon" src="/icons/documents.svg" alt="" /></span><span class="text-box">文档中心</span>
    </RouterLink>
    <RouterLink to="/reports" class="nav-item" v-if="canViewReports">
      <span class="icon-box"><img class="icon" src="/icons/reports.svg" alt="" /></span><span class="text-box">大数据报表</span>
    </RouterLink>

    <!-- 离职申请（带子菜单） -->
    <div class="nav-item-group">
      <div class="nav-item nav-item-parent" :class="{ 'has-active': isResignationActive }" @click="toggleSubmenu('resignation')">
        <span class="icon-box"><img class="icon" src="/icons/resignation.svg" alt="" /></span>
        <span class="text-box">离职申请</span>
        <span class="arrow-box" v-show="!collapsed">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" :class="{ rotated: submenuOpen.resignation }">
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
      <span class="icon-box"><img class="icon" src="/icons/system.svg" alt="" /></span><span class="text-box">系统</span>
    </RouterLink>
    <RouterLink v-if="canViewRbac" to="/rbac" class="nav-item">
      <span class="icon-box"><img class="icon" src="/icons/rbac.svg" alt="" /></span><span class="text-box">权限管理</span>
    </RouterLink>
    <RouterLink v-if="canViewUsers" to="/users" class="nav-item">
      <span class="icon-box"><img class="icon" src="/icons/users.svg" alt="" /></span><span class="text-box">用户管理</span>
    </RouterLink>
    <RouterLink to="/account" class="nav-item">
      <span class="icon-box"><img class="icon" src="/icons/account.svg" alt="" /></span><span class="text-box">账号设置</span>
    </RouterLink>
      </div>
    </aside>
  <div class="layout-main">
      <div class="top-bar">
        <div class="user-box" v-if="auth.ready">
          <span v-if="auth.user" class="user-info">
            <img v-if="auth.user.avatar" :src="auth.user.avatar" alt="" class="user-avatar" />
            <span v-else class="user-avatar-placeholder">{{ userInitials }}</span>
            <span class="user-name">{{ auth.user.employee_name || auth.user.username }}</span>
          </span>
          <button v-if="auth.user" @click="logout">退出</button>
          <button v-else @click="goLogin">登录</button>
          <button class="theme-toggle" @click="toggleTheme">{{ themeLabel }}</button>
        </div>
      </div>
      <div class="page-wrapper">
        <div v-if="globalError" style="background:#fee2e2;color:#991b1b;padding:.6rem .75rem;border:1px solid #fecaca;border-radius:6px;font-size:13px;margin-bottom:1rem;">发生脚本错误：{{ globalError }}</div>
        <slot />
      </div>
      <!-- ICP备案号 -->
      <footer class="icp-footer">
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">
          <svg class="icp-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
          <span>蜀ICP备2026004175号-1</span>
        </a>
      </footer>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter, useRoute } from 'vue-router';
import { hasPermission, isAdmin, Permissions } from '../utils/permissions';

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const dark = ref(false);
const globalError = ref(null);

// 用户头像首字母
const userInitials = computed(() => {
  const name = auth.user?.employee_name || auth.user?.username || '';
  if (!name) return '?';
  return name.charAt(0).toUpperCase();
});

// 权限计算属性
const canManageEmployees = computed(() => isAdmin() || hasPermission(Permissions.EMPLOYEE_VIEW));
const canViewAllAttendance = computed(() => isAdmin() || hasPermission(Permissions.ATTENDANCE_VIEW_ALL));
const canManageLocations = computed(() => isAdmin() || hasPermission(Permissions.ATTENDANCE_LOCATION));
const canApproveAttendance = computed(() => isAdmin() || hasPermission(Permissions.ATTENDANCE_APPROVE));
const canApproveLeave = computed(() => isAdmin() || hasPermission(Permissions.LEAVE_APPROVE));
const canViewAllSalary = computed(() => isAdmin() || hasPermission(Permissions.SALARY_VIEW_ALL));
const canApproveExpense = computed(() => isAdmin() || hasPermission(Permissions.EXPENSE_APPROVE));
const canViewReports = computed(() => isAdmin() || hasPermission(Permissions.REPORT_VIEW));
const canViewSystem = computed(() => isAdmin() || hasPermission(Permissions.SYSTEM_VIEW));
const canViewRbac = computed(() => isAdmin() || hasPermission(Permissions.RBAC_VIEW));
const canViewUsers = computed(() => isAdmin() || hasPermission(Permissions.USER_VIEW));

function goLogin(){ router.replace('/login'); }
async function logout(){
  await auth.logout();
  router.replace('/login');
}
function applyTheme(){
  const root = document.documentElement;
  root.setAttribute('data-theme', dark.value ? 'dark' : 'light');
}
function toggleTheme(){ dark.value = !dark.value; applyTheme(); }
const themeLabel = computed(()=> dark.value ? '浅色' : '深色');
// 悬停折叠逻辑
const collapsed = ref(true);
function hoverIn(){ collapsed.value=false; }
function hoverOut(){ collapsed.value=true; closeAllSubmenus(); }

// 子菜单状态
const submenuOpen = ref({
  employees: false,
  attendance: false,
  leaves: false,
  salaries: false,
  resignation: false
});

function toggleSubmenu(name) {
  // 先关闭其他子菜单
  Object.keys(submenuOpen.value).forEach(key => {
    if (key !== name) {
      submenuOpen.value[key] = false;
    }
  });
  // 切换当前子菜单
  submenuOpen.value[name] = !submenuOpen.value[name];
}

function closeAllSubmenus() {
  Object.keys(submenuOpen.value).forEach(key => {
    submenuOpen.value[key] = false;
  });
}

// 判断员工子菜单是否有激活项
const isEmployeesActive = computed(() => {
  return route.path.startsWith('/employees');
});

// 判断考勤子菜单是否有激活项
const isAttendanceActive = computed(() => {
  return route.path.startsWith('/attendance');
});

// 判断请假子菜单是否有激活项
const isLeavesActive = computed(() => {
  return route.path.startsWith('/leaves');
});

// 判断薪资子菜单是否有激活项
const isSalariesActive = computed(() => {
  return route.path.startsWith('/salaries');
});

// 判断离职子菜单是否有激活项
const isResignationActive = computed(() => {
  return route.path.startsWith('/resignation');
});

onMounted(()=>{ applyTheme(); });
window.addEventListener('error', (e) => { globalError.value = e.message; });
</script>
<style scoped>
.layout-shell{display:flex;min-height:100vh;background:#f8fafc;}
.layout-sidebar{width:160px;background:#ffffff;border-right:1px solid #e2e8f0;padding:1rem 0 2rem;display:flex;flex-direction:column;position:fixed;left:0;top:0;bottom:0;height:100vh;overflow-y:auto;overflow-x:hidden;z-index:50;transition:width .4s cubic-bezier(.25,.8,.25,1),box-shadow .4s ease;box-shadow:0 0 0 rgba(0,0,0,0);scrollbar-width:none;-ms-overflow-style:none;}
.layout-sidebar::-webkit-scrollbar{display:none;}
.layout-sidebar.collapsed{width:64px;}
.layout-sidebar:not(.collapsed){box-shadow:0 4px 18px -4px rgba(0,0,0,.18),0 2px 8px -2px rgba(0,0,0,.12);}
.logo-title{font-size:18px;margin:0 0 .8rem;font-weight:600;line-height:1;white-space:nowrap;display:flex;align-items:center;}
.logo-hr{width:64px;min-width:64px;text-align:center;flex-shrink:0;}
.logo-text{transition:opacity .3s ease,transform .3s ease;opacity:1;transform:translateX(0);}
.layout-sidebar.collapsed .logo-text{opacity:0;transform:translateX(-8px);pointer-events:none;}
.layout-sidebar.collapsed .logo-title{font-size:18px;}
[data-theme=dark] .layout-sidebar{background:linear-gradient(180deg,#0f172a 0%,#1e293b 100%);border-right-color:#334155;color:#e2e8f0;}
.nav-group{display:flex;flex-direction:column;gap:.25rem;margin-top:.4rem;flex:1;}
.nav-group a.nav-item{display:flex;align-items:center;padding:.55rem 0;border-radius:6px;text-decoration:none;color:#1e293b;font-size:14px;line-height:1.2;white-space:nowrap;width:100%;box-sizing:border-box;}
.nav-group a .icon-box,.nav-item-parent .icon-box{width:64px;min-width:64px;display:flex;justify-content:center;align-items:center;flex-shrink:0;}
.nav-group a .icon,.nav-item-parent .icon{width:20px;height:20px;object-fit:contain;}
.nav-group a .text-box,.nav-item-parent .text-box{flex:1;transition:opacity .3s ease,transform .3s ease;overflow:hidden;transform:translateX(0);opacity:1;}
.layout-sidebar.collapsed .nav-group a .text-box,.layout-sidebar.collapsed .nav-item-parent .text-box{opacity:0;transform:translateX(-8px);pointer-events:none;}
.nav-group a .text{transition:opacity .35s ease,transform .35s ease;}
.layout-sidebar.collapsed .nav-group a .text{opacity:0;transform:translateX(-6px);pointer-events:none;}
.layout-sidebar:not(.collapsed) .nav-group a .text{opacity:1;transform:translateX(0);}
@media (hover:hover){.nav-group a.nav-item:hover,.nav-item-parent:hover{background:#e2e8f0;}}
.nav-group a.router-link-active{background:#2563eb;color:#fff;}
[data-theme=dark] .nav-group a.nav-item{color:#94a3b8;}
[data-theme=dark] .nav-group a.nav-item:hover,[data-theme=dark] .nav-item-parent:hover{background:rgba(148,163,184,.15);color:#e2e8f0;}
[data-theme=dark] .nav-group a.router-link-active{background:linear-gradient(135deg,#3b82f6,#60a5fa);color:#fff;box-shadow:0 4px 12px rgba(59,130,246,.35);}

/* 子菜单样式 */
.nav-item-group{position:relative;}
.nav-item-parent{display:flex;align-items:center;padding:.55rem 0;border-radius:6px;color:#1e293b;font-size:14px;line-height:1.2;white-space:nowrap;width:100%;box-sizing:border-box;cursor:pointer;transition:background .2s;}
.nav-item-parent.has-active{background:rgba(37,99,235,.1);color:#2563eb;}
[data-theme=dark] .nav-item-parent{color:#94a3b8;}
[data-theme=dark] .nav-item-parent.has-active{background:rgba(59,130,246,.2);color:#60a5fa;}
.arrow-box{width:24px;display:flex;justify-content:center;align-items:center;margin-right:8px;transition:transform .2s;}
.arrow-box svg{transition:transform .2s;}
.arrow-box svg.rotated{transform:rotate(180deg);}
.submenu{display:flex;flex-direction:column;gap:2px;padding:4px 27px 4px 28px;overflow:hidden;transition:all .5s ease-out,opacity .3s ease,max-height .5s ease;white-space:nowrap;max-height:200px;opacity:1;}
.layout-sidebar.collapsed .submenu{max-height:0;opacity:0;padding:0 27px 0 28px;pointer-events:none;}
.submenu-item{display:flex;align-items:center;gap:8px;padding:.5rem .75rem;border-radius:6px;text-decoration:none;color:#64748b;font-size:13px;transition:all .2s;white-space:nowrap;}
.submenu-item:hover{background:#f1f5f9;color:#1e293b;}
.submenu-item.router-link-active{background:#2563eb;color:#fff;}
.submenu-dot{width:6px;height:6px;border-radius:50%;background:currentColor;opacity:.5;}
.submenu-item.router-link-active .submenu-dot{opacity:1;}
[data-theme=dark] .submenu-item{color:#94a3b8;}
[data-theme=dark] .submenu-item:hover{background:rgba(148,163,184,.1);color:#e2e8f0;}
[data-theme=dark] .submenu-item.router-link-active{background:linear-gradient(135deg,#3b82f6,#60a5fa);color:#fff;}

/* 子菜单动画 */
.submenu-enter-active{transition:all 1s ease-out;max-height:200px;}
.submenu-leave-active{transition:all .4s ease-in;max-height:200px;}
.submenu-enter-from,.submenu-leave-to{opacity:0;max-height:0;}

.layout-main{flex:1;display:flex;flex-direction:column;min-width:0;margin-left:64px;}
.top-bar{height:52px;display:flex;align-items:center;justify-content:flex-end;padding:0 1rem;background:#fff;border-bottom:1px solid #e2e8f0;}
[data-theme=dark] .top-bar{background:#1e293b;border-bottom-color:#334155;}
[data-theme=dark] .user-box{color:#e2e8f0;}
[data-theme=dark] .theme-toggle,.user-box button{background:linear-gradient(135deg,#3b82f6,#60a5fa);}
.user-box{display:flex;align-items:center;gap:.65rem;font-size:14px;}
.user-info{display:flex;align-items:center;gap:.5rem;}
.user-avatar{width:28px;height:28px;border-radius:50%;object-fit:cover;}
.user-avatar-placeholder{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#60a5fa);color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;}
.user-name{max-width:100px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.theme-toggle, .user-box button{padding:.45rem .75rem;background:#2563eb;color:#fff;border:none;border-radius:6px;font-size:13px;cursor:pointer;}
.user-box button:hover,.theme-toggle:hover{filter:brightness(.95);}
.page-wrapper{padding:1rem 1.5rem;overflow:auto;flex:1;}
.icp-footer{text-align:center;padding:1.5rem 0 .5rem;font-size:12px;color:#94a3b8;}
.icp-footer a{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:99px;color:#94a3b8;text-decoration:none;transition:all .2s;}
.icp-footer a:hover{color:#3b82f6;background:#eff6ff;}
[data-theme=dark] .layout-shell{background:#0f172a;}
[data-theme=dark] .page-wrapper{background:#0f172a;}
[data-theme=dark] .icp-footer a:hover{background:#1e293b;color:#60a5fa;}
[data-theme=dark] .logo-title{color:#f8fafc;}
[data-theme=dark] .nav-group a .icon{filter:brightness(0) invert(1) opacity(.85);}
</style>
