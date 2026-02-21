import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { canAccessRoute, Permissions } from '../utils/permissions';

// 模块化页面导入
const Dashboard = () => import('../pages/dashboard/index.vue');
const Employees = () => import('../pages/employees/index.vue');
const EmployeeList = () => import('../pages/employees/List.vue');
const EmployeeDetail = () => import('../pages/employees/Detail.vue');
const EmployeeCreate = () => import('../pages/employees/Create.vue');
const EmployeeEdit = () => import('../pages/employees/Edit.vue');
const EmployeeOnboarding = () => import('../pages/employees/Onboarding.vue');
const AttendanceRecords = () => import('../pages/attendance/Records.vue');
const AttendanceManage = () => import('../pages/attendance/Manage.vue');
const AttendanceForm = () => import('../pages/attendance/Form.vue');
const AttendanceApproval = () => import('../pages/attendance/Approval.vue');
const AttendanceLocations = () => import('../pages/attendance/Locations.vue');
const AttendanceAlerts = () => import('../pages/attendance/Alerts.vue');
const LeaveApply = () => import('../pages/leaves/Apply.vue');
const LeaveApproval = () => import('../pages/leaves/Approval.vue');
const LeaveCreate = () => import('../pages/leaves/Create.vue');
const BusinessTrip = () => import('../pages/leaves/BusinessTrip.vue');
const BusinessTripCreate = () => import('../pages/leaves/BusinessTripCreate.vue');
const Salaries = () => import('../pages/salaries/index.vue');
const SalaryCreate = () => import('../pages/salaries/Create.vue');
const SalaryRecords = () => import('../pages/salaries/Records.vue');
const TravelExpense = () => import('../pages/salaries/TravelExpense.vue');
const ExpenseApproval = () => import('../pages/salaries/ExpenseApproval.vue');
const System = () => import('../pages/system/index.vue');
const Reports = () => import('../pages/reports/index.vue');
const BIReports = () => import('../pages/bi/index.vue');
const Documents = () => import('../pages/documents/index.vue');
const DocumentForm = () => import('../pages/documents/Form.vue');
const Departments = () => import('../pages/departments/index.vue');
const DepartmentForm = () => import('../pages/departments/Form.vue');
const Positions = () => import('../pages/positions/index.vue');
const PositionForm = () => import('../pages/positions/Form.vue');
const RolePermission = () => import('../pages/rbac/index.vue');
const Users = () => import('../pages/users/index.vue');
const UserCreate = () => import('../pages/users/Create.vue');
const UserEdit = () => import('../pages/users/Edit.vue');
const Login = () => import('../pages/auth/Login.vue');
const ForgotPassword = () => import('../pages/auth/ForgotPassword.vue');
const AdminResetPassword = () => import('../pages/auth/AdminResetPassword.vue');
const Account = () => import('../pages/auth/Account.vue');
const ResignationProgress = () => import('../pages/resignation/Progress.vue');
const ResignationApply = () => import('../pages/resignation/Apply.vue');
const ResignationApproval = () => import('../pages/resignation/Approval.vue');

// 预加载：用于侧边栏二级菜单展开时提前加载对应页面模块，减少点击后的首开等待。
const SUBMENU_PRELOADERS = {
  employees: [Employees, EmployeeList, EmployeeOnboarding, EmployeeCreate, EmployeeEdit, EmployeeDetail],
  attendance: [AttendanceRecords, AttendanceManage, AttendanceApproval, AttendanceLocations, AttendanceAlerts, AttendanceForm],
  leaves: [LeaveApply, LeaveApproval, LeaveCreate, BusinessTrip, BusinessTripCreate],
  salaries: [Salaries, SalaryCreate, SalaryRecords, TravelExpense, ExpenseApproval],
  reports: [Reports, BIReports],
  resignation: [ResignationProgress, ResignationApply, ResignationApproval],
};

export function preloadSubmenu(name) {
  const loaders = SUBMENU_PRELOADERS[name];
  if (!loaders || loaders.length === 0) return Promise.resolve();

  return Promise.allSettled(
    loaders.map((loader) => {
      try {
        return loader();
      } catch (e) {
        return Promise.resolve();
      }
    })
  ).then(() => undefined);
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 主页
    { path: '/', component: Dashboard, meta: { requiresAuth: true } },

    // 员工管理
    { path: '/employees', redirect: '/employees/list' },
    { path: '/employees/list', component: EmployeeList, meta: { requiresAuth: true } },
    { path: '/employees/manage', component: Employees, meta: { requiresAuth: true, permissions: [Permissions.EMPLOYEE_VIEW] } },
    { path: '/employees/onboarding', component: EmployeeOnboarding, meta: { requiresAuth: true, permissions: [Permissions.ONBOARDING_VIEW_ALL] } },
    { path: '/employees/create', component: EmployeeCreate, meta: { requiresAuth: true, permissions: [Permissions.EMPLOYEE_CREATE] } },
    { path: '/employees/:id', component: EmployeeDetail, meta: { requiresAuth: true } },
    { path: '/employees/:id/edit', component: EmployeeEdit, meta: { requiresAuth: true, permissions: [Permissions.EMPLOYEE_EDIT] } },

    // 考勤与请假
    { path: '/attendance', redirect: '/attendance/records' },
    { path: '/attendance/records', component: AttendanceRecords, meta: { requiresAuth: true } },
    { path: '/attendance/manage', component: AttendanceManage, meta: { requiresAuth: true } },
    { path: '/attendance/alerts', component: AttendanceAlerts, meta: { requiresAuth: true, permissions: [Permissions.ATTENDANCE_VIEW_ALL] } },
    { path: '/attendance/approval', component: AttendanceApproval, meta: { requiresAuth: true, permissions: [Permissions.ATTENDANCE_APPROVE] } },
    { path: '/attendance/locations', component: AttendanceLocations, meta: { requiresAuth: true, permissions: [Permissions.ATTENDANCE_LOCATION] } },
    { path: '/attendance/create', component: AttendanceForm, meta: { requiresAuth: true } },
    { path: '/attendance/:id/edit', component: AttendanceForm, meta: { requiresAuth: true, permissions: [Permissions.ATTENDANCE_EDIT] } },
    { path: '/leaves', redirect: '/leaves/apply' },
    { path: '/leaves/apply', component: LeaveApply, meta: { requiresAuth: true } },
    { path: '/leaves/approval', component: LeaveApproval, meta: { requiresAuth: true, permissions: [Permissions.LEAVE_APPROVE] } },
    { path: '/leaves/create', component: LeaveCreate, meta: { requiresAuth: true } },
    { path: '/leaves/business', component: BusinessTrip, meta: { requiresAuth: true } },
    { path: '/leaves/business/create', component: BusinessTripCreate, meta: { requiresAuth: true, permissions: [Permissions.TRIP_CREATE] } },
    { path: '/resignation', redirect: '/resignation/progress' },
    { path: '/resignation/progress', component: ResignationProgress, meta: { requiresAuth: true } },
    { path: '/resignation/apply', component: ResignationApply, meta: { requiresAuth: true } },
    { path: '/resignation/approval', component: ResignationApproval, meta: { requiresAuth: true, permissions: [Permissions.RESIGNATION_APPROVE] } },

    // 薪资与组织
    { path: '/salaries', component: Salaries, meta: { requiresAuth: true, permissions: [Permissions.SALARY_VIEW_ALL] } },
    { path: '/salaries/create', component: SalaryCreate, meta: { requiresAuth: true, permissions: [Permissions.SALARY_CREATE] } },
    { path: '/salaries/records', component: SalaryRecords, meta: { requiresAuth: true } },
    { path: '/salaries/travel-expense', component: TravelExpense, meta: { requiresAuth: true, permissions: [Permissions.EXPENSE_VIEW] } },
    { path: '/salaries/expense-approval', component: ExpenseApproval, meta: { requiresAuth: true, permissions: [Permissions.EXPENSE_APPROVE] } },
    { path: '/departments', component: Departments, meta: { requiresAuth: true } },
    { path: '/departments/create', component: DepartmentForm, meta: { requiresAuth: true, permissions: [Permissions.DEPARTMENT_CREATE] } },
    { path: '/departments/:id/edit', component: DepartmentForm, meta: { requiresAuth: true, permissions: [Permissions.DEPARTMENT_EDIT] } },
    { path: '/positions', component: Positions, meta: { requiresAuth: true } },
    { path: '/positions/create', component: PositionForm, meta: { requiresAuth: true, permissions: [Permissions.POSITION_CREATE] } },
    { path: '/positions/:id/edit', component: PositionForm, meta: { requiresAuth: true, permissions: [Permissions.POSITION_EDIT] } },

    // 系统管理（管理员）
    { path: '/system', component: System, meta: { requiresAuth: true, permissions: [Permissions.SYSTEM_VIEW] } },
    { path: '/reports', component: Reports, meta: { requiresAuth: true, permissions: [Permissions.REPORT_VIEW] } },
    { path: '/bi', component: BIReports, meta: { requiresAuth: true, permissions: [Permissions.BI_VIEW] } },
    { path: '/documents', component: Documents, meta: { requiresAuth: true } },
    { path: '/documents/upload', component: DocumentForm, meta: { requiresAuth: true, permissions: [Permissions.DOCUMENT_UPLOAD] } },
    { path: '/documents/:id/edit', component: DocumentForm, meta: { requiresAuth: true, permissions: [Permissions.DOCUMENT_MANAGE] } },
    { path: '/rbac', component: RolePermission, meta: { requiresAuth: true, permissions: [Permissions.RBAC_VIEW] } },
    { path: '/users', component: Users, meta: { requiresAuth: true, permissions: [Permissions.USER_VIEW] } },
    { path: '/users/create', component: UserCreate, meta: { requiresAuth: true, permissions: [Permissions.USER_CREATE] } },
    { path: '/users/:id/edit', component: UserEdit, meta: { requiresAuth: true, permissions: [Permissions.USER_EDIT] } },
    { path: '/admin-reset-password', component: AdminResetPassword, meta: { requiresAuth: true, permissions: [Permissions.USER_RESET_PASSWORD] } },

    // 用户相关
    { path: '/account', component: Account, meta: { requiresAuth: true, skipProfileCheck: true } },
    { path: '/login', component: Login, meta: { plain: true } },
    { path: '/forgot-password', component: ForgotPassword, meta: { plain: true } },

    // 无权限页面
    { path: '/403', component: () => import('../pages/auth/Forbidden.vue'), meta: { requiresAuth: true } },

    // 未匹配路径重定向到首页（导航守卫会处理跳转到登录页）
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ]
});

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();
  const isPlain = to.matched.some(record => record.meta?.plain);

  if (isPlain) {
    if (!auth.ready) {
      auth.ready = true;
    }
    return next();
  }

  if(!auth.ready){
    // 超时保护：最多等3秒，避免白屏
    await Promise.race([
      auth.fetchMe(),
      new Promise(resolve => setTimeout(resolve, 3000))
    ]);
    if (!auth.ready) auth.ready = true;
  }
  if(to.meta.requiresAuth && !auth.isAuthenticated){
    // 未登录时跳转到登录页
    return next({ path: '/login', query: { redirect: to.fullPath } });
  }
  // 强制首次修改密码：除账号设置页面外都重定向
  if(auth.isAuthenticated && auth.mustChangePassword && to.path !== '/account'){
    return next({ path: '/account', query: { redirect: to.fullPath } });
  }

  // 权限检查
  const requiredPermissions = to.meta.permissions;
  if (requiredPermissions && requiredPermissions.length > 0) {
    // 管理员直接放行
    if (auth.user?.is_staff || auth.user?.is_superuser) {
      return next();
    }
    // 检查是否有所需权限
    const hasAllPermissions = requiredPermissions.every(p => auth.hasPermissionKey(p));
    if (!hasAllPermissions) {
      return next({ path: '/403', query: { from: to.fullPath } });
    }
  }

  next();
});

export default router;
