from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenVerifyView
)
from .api.views import (
    # Auth
    LogoutAPIView, ChangePasswordAPIView, AdminResetPasswordAPIView,
    UserProfileUpdateAPIView, CurrentUserAPIView, CustomTokenObtainView,
    send_verification_code, verify_code_and_reset_password, HealthAPIView,
    # Onboarding (员工自助入职)
    SelfRegisterAPIView, send_register_code, OnboardProfileAPIView, OnboardStatusAPIView,
    OnboardPendingListAPIView, OnboardApproveAPIView,
    # Dashboard
    SystemSummaryAPIView, AttendanceTrendAPIView, LeaveTypeStatsAPIView,
    LogTypeStatsAPIView, LogCalendarStatsAPIView, EmployeeChurnStatsAPIView,
    MyTodoSummaryAPIView,
    # Reports
    DepartmentDistributionAPIView, MonthlySalaryAPIView, AttendanceRateAPIView,
    LeaveAnalysisAPIView, EmployeeGrowthAPIView, PositionDistributionAPIView,
    ReportOverviewAPIView,
    # BI
    BIDepartmentCostAPIView, BIAttendanceHeatmapAPIView, BITurnoverAPIView,
    BISalaryRangeAPIView, BILeaveBalanceAPIView, BIDailyAttendanceAPIView,
    # Employees
    EmployeeListCreateAPIView, EmployeeDetailAPIView, CurrentEmployeeAPIView,
    # Attendance
    AttendanceListCreateAPIView, AttendanceDetailAPIView, AttendanceCheckAPIView, attendance_today, attendance_my,
    attendance_supplement_list, attendance_supplement_pending, attendance_supplement_approve,
    attendance_workday,
    CheckInLocationListCreateAPIView, CheckInLocationDetailAPIView, checkin_locations_active,
    attendance_alerts,
    # Leaves
    LeaveListCreateAPIView, LeaveApproveAPIView, LeaveCancelAPIView, LeaveUpdateAPIView,
    BusinessTripListCreateAPIView, BusinessTripDetailAPIView, BusinessTripApproveAPIView, BusinessTripCancelAPIView,
    TravelExpenseListCreateAPIView, TravelExpenseDetailAPIView, TravelExpenseApproveAPIView, TravelExpensePayAPIView,
    # Salaries
    SalaryListCreateAPIView, SalaryDetailAPIView, salary_disburse, salary_pending,
    # System
    SystemLogListAPIView, system_log_clear,
    CompanyDocumentListCreateAPIView, CompanyDocumentDetailAPIView,
    backups_list, backup_create, backup_clean, backup_restore,
    health_check, health_report, system_metrics,
    # RBAC
    RoleListAPIView, RoleListCreateAPIView, RoleDetailAPIView,
    PermissionListAPIView, PermissionListCreateAPIView, PermissionDetailAPIView,
    PermissionGroupsAPIView,
    # Users

    UserListAPIView, UserListCreateAPIView, UserDetailAPIView,
    # Organization
    DepartmentListCreateAPIView, DepartmentDetailAPIView,
    PositionListCreateAPIView, PositionDetailAPIView,
    # Export
    export_employees, export_salaries, export_attendance, export_leaves, export_my_salary_slip,
    export_salary_template,
    # Import
    EmployeeImportAPIView, AttendanceImportAPIView, SalaryImportAPIView,
    ImportTemplateAPIView,
    # Notifications
    notification_list, notification_unread_count,
    notification_mark_read, notification_mark_all_read, notification_clear,
)
from .api.versioning import api_versions, api_changelog

urlpatterns = [
    path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('auth/change_password/', ChangePasswordAPIView.as_view(), name='api_change_password'),
    path('auth/admin_reset_password/', AdminResetPasswordAPIView.as_view(), name='api_admin_reset_password'),
    path('auth/update_profile/', UserProfileUpdateAPIView.as_view(), name='api_update_profile'),
    path('auth/send_code/', send_verification_code, name='api_send_verification_code'),
    path('auth/reset_password/', verify_code_and_reset_password, name='api_reset_password'),
    path('health/', HealthAPIView.as_view(), name='api_health'),
    path('auth/me/', CurrentUserAPIView.as_view(), name='api_me'),
    # JWT token endpoints - 使用自定义视图支持手机号登录
    path('auth/token/', CustomTokenObtainView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('summary/', SystemSummaryAPIView.as_view(), name='api_system_summary'),
    path('todos/', MyTodoSummaryAPIView.as_view(), name='api_my_todos'),
    path('stats/attendance_trend/', AttendanceTrendAPIView.as_view(), name='api_attendance_trend'),
    path('stats/leave_type/', LeaveTypeStatsAPIView.as_view(), name='api_leave_type_stats'),
    path('stats/log_types/', LogTypeStatsAPIView.as_view(), name='api_log_type_stats'),
    path('stats/log_calendar/', LogCalendarStatsAPIView.as_view(), name='api_log_calendar_stats'),
    path('stats/employee_churn/', EmployeeChurnStatsAPIView.as_view(), name='api_employee_churn_stats'),

    # Reports (大数据报表)
    path('reports/overview/', ReportOverviewAPIView.as_view(), name='api_report_overview'),
    path('reports/department_distribution/', DepartmentDistributionAPIView.as_view(), name='api_dept_distribution'),
    path('reports/monthly_salary/', MonthlySalaryAPIView.as_view(), name='api_monthly_salary'),
    path('reports/attendance_rate/', AttendanceRateAPIView.as_view(), name='api_attendance_rate'),
    path('reports/leave_analysis/', LeaveAnalysisAPIView.as_view(), name='api_leave_analysis'),
    path('reports/employee_growth/', EmployeeGrowthAPIView.as_view(), name='api_employee_growth'),
    path('reports/position_distribution/', PositionDistributionAPIView.as_view(), name='api_position_distribution'),

    # BI 报表
    path('bi/department-cost/', BIDepartmentCostAPIView.as_view(), name='api_bi_dept_cost'),
    path('bi/attendance-heatmap/', BIAttendanceHeatmapAPIView.as_view(), name='api_bi_attendance_heatmap'),
    path('bi/turnover/', BITurnoverAPIView.as_view(), name='api_bi_turnover'),
    path('bi/salary-range/', BISalaryRangeAPIView.as_view(), name='api_bi_salary_range'),
    path('bi/leave-balance/', BILeaveBalanceAPIView.as_view(), name='api_bi_leave_balance'),
    path('bi/daily-attendance/', BIDailyAttendanceAPIView.as_view(), name='api_bi_daily_attendance'),

    path('employees/', EmployeeListCreateAPIView.as_view(), name='api_employees'),
    path('employees/me/', CurrentEmployeeAPIView.as_view(), name='api_employee_me'),
    path('employees/<int:pk>/', EmployeeDetailAPIView.as_view(), name='api_employee_detail'),

    path('attendance/', AttendanceListCreateAPIView.as_view(), name='api_attendance'),
    path('attendance/<int:pk>/', AttendanceDetailAPIView.as_view(), name='api_attendance_detail'),
    path('attendance/today/', attendance_today, name='api_attendance_today'),
    path('attendance/my/', attendance_my, name='api_attendance_my'),
    path('attendance/workday/', attendance_workday, name='api_attendance_workday'),
    path('attendance/check/', AttendanceCheckAPIView.as_view(), name='api_attendance_check'),
    path('attendance/supplement/', attendance_supplement_list, name='api_attendance_supplement'),
    path('attendance/supplement/pending/', attendance_supplement_pending, name='api_attendance_supplement_pending'),
    path('attendance/supplement/<int:pk>/approve/', attendance_supplement_approve, name='api_attendance_supplement_approve'),

    # 签到地点管理
    path('checkin-locations/', CheckInLocationListCreateAPIView.as_view(), name='api_checkin_locations'),
    path('checkin-locations/active/', checkin_locations_active, name='api_checkin_locations_active'),
    path('checkin-locations/<int:pk>/', CheckInLocationDetailAPIView.as_view(), name='api_checkin_location_detail'),

    # 考勤异常提醒
    path('attendance/alerts/', attendance_alerts, name='api_attendance_alerts'),

    path('leaves/', LeaveListCreateAPIView.as_view(), name='api_leaves'),
    path('leaves/<int:pk>/', LeaveUpdateAPIView.as_view(), name='api_leave_update'),
    path('leaves/<int:pk>/approve/', LeaveApproveAPIView.as_view(), name='api_leave_approve'),
    path('leaves/<int:pk>/cancel/', LeaveCancelAPIView.as_view(), name='api_leave_cancel'),

    # Business Trips (出差)
    path('business-trips/', BusinessTripListCreateAPIView.as_view(), name='api_business_trips'),
    path('business-trips/<int:pk>/', BusinessTripDetailAPIView.as_view(), name='api_business_trip_detail'),
    path('business-trips/<int:pk>/approve/', BusinessTripApproveAPIView.as_view(), name='api_business_trip_approve'),
    path('business-trips/<int:pk>/cancel/', BusinessTripCancelAPIView.as_view(), name='api_business_trip_cancel'),

    # Travel Expenses (差旅报销)
    path('travel-expenses/', TravelExpenseListCreateAPIView.as_view(), name='api_travel_expenses'),
    path('travel-expenses/<int:pk>/', TravelExpenseDetailAPIView.as_view(), name='api_travel_expense_detail'),
    path('travel-expenses/<int:pk>/approve/', TravelExpenseApproveAPIView.as_view(), name='api_travel_expense_approve'),
    path('travel-expenses/<int:pk>/pay/', TravelExpensePayAPIView.as_view(), name='api_travel_expense_pay'),

    path('salaries/', SalaryListCreateAPIView.as_view(), name='api_salaries'),
    path('salaries/<int:pk>/', SalaryDetailAPIView.as_view(), name='api_salary_detail'),
    path('salaries/disburse/', salary_disburse, name='api_salary_disburse'),
    path('salaries/pending/', salary_pending, name='api_salary_pending'),
    path('logs/', SystemLogListAPIView.as_view(), name='api_system_logs'),
    path('logs/clear/', system_log_clear, name='api_system_log_clear'),

    # RBAC (read-only legacy + new CRUD)
    path('roles/', RoleListAPIView.as_view(), name='api_roles'),
    path('roles/manage/', RoleListCreateAPIView.as_view(), name='api_roles_manage'),
    path('roles/manage/<int:pk>/', RoleDetailAPIView.as_view(), name='api_role_detail'),
    path('permissions/', PermissionListAPIView.as_view(), name='api_permissions'),
    path('permissions/groups/', PermissionGroupsAPIView.as_view(), name='api_permission_groups'),
    path('permissions/manage/', PermissionListCreateAPIView.as_view(), name='api_permissions_manage'),
    path('permissions/manage/<int:pk>/', PermissionDetailAPIView.as_view(), name='api_permission_detail'),
    path('users/', UserListAPIView.as_view(), name='api_users'),
    path('users/manage/', UserListCreateAPIView.as_view(), name='api_users_manage'),
    path('users/manage/<int:pk>/', UserDetailAPIView.as_view(), name='api_user_detail'),

    path('departments/', DepartmentListCreateAPIView.as_view(), name='api_departments'),
    path('departments/<int:pk>/', DepartmentDetailAPIView.as_view(), name='api_department_detail'),
    path('positions/', PositionListCreateAPIView.as_view(), name='api_positions'),
    path('positions/<int:pk>/', PositionDetailAPIView.as_view(), name='api_position_detail'),

    path('backups/', backups_list, name='api_backups_list'),
    path('backups/create/', backup_create, name='api_backup_create'),
    path('backups/clean/', backup_clean, name='api_backup_clean'),
    path('backups/restore/', backup_restore, name='api_backup_restore'),

    # System Monitoring
    path('system/health/', health_check, name='api_health_check'),
    path('system/health/report/', health_report, name='api_health_report'),
    path('system/metrics/', system_metrics, name='api_system_metrics'),

    # Company Documents
    path('documents/', CompanyDocumentListCreateAPIView.as_view(), name='api_company_documents'),
    path('documents/<int:pk>/', CompanyDocumentDetailAPIView.as_view(), name='api_company_document_detail'),

    # Export
    path('export/employees/', export_employees, name='api_export_employees'),
    path('export/salaries/', export_salaries, name='api_export_salaries'),
    path('export/salary-slip/', export_my_salary_slip, name='api_export_my_salary_slip'),
    path('export/salary-template/', export_salary_template, name='api_export_salary_template'),
    path('export/attendance/', export_attendance, name='api_export_attendance'),
    path('export/leaves/', export_leaves, name='api_export_leaves'),

    # Import
    path('import/employees/', EmployeeImportAPIView.as_view(), name='api_import_employees'),
    path('import/attendance/', AttendanceImportAPIView.as_view(), name='api_import_attendance'),
    path('import/salaries/', SalaryImportAPIView.as_view(), name='api_import_salaries'),
    path('import/template/<str:template_type>/', ImportTemplateAPIView.as_view(), name='api_import_template'),

    # Notifications
    path('notifications/', notification_list, name='api_notifications'),
    path('notifications/unread-count/', notification_unread_count, name='api_notification_unread_count'),
    path('notifications/<str:notification_id>/read/', notification_mark_read, name='api_notification_mark_read'),
    path('notifications/read-all/', notification_mark_all_read, name='api_notification_mark_all_read'),
    path('notifications/clear/', notification_clear, name='api_notification_clear'),

    # API Version Info
    path('versions/', api_versions, name='api_versions'),
    path('changelog/', api_changelog, name='api_changelog'),

    # Onboarding (员工自助入职 - H5端使用)
    path('onboarding/register/', SelfRegisterAPIView.as_view(), name='api_self_register'),
    path('onboarding/send-code/', send_register_code, name='api_send_register_code'),
    path('onboarding/profile/', OnboardProfileAPIView.as_view(), name='api_onboard_profile'),
    path('onboarding/status/', OnboardStatusAPIView.as_view(), name='api_onboard_status'),
    # HR审核入职
    path('onboarding/pending/', OnboardPendingListAPIView.as_view(), name='api_onboard_pending'),
    path('onboarding/<int:pk>/approve/', OnboardApproveAPIView.as_view(), name='api_onboard_approve'),
]
