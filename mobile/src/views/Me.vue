<template>
  <div class="page-container">
    <van-nav-bar title="我的" />

    <!-- 用户信息卡片 -->
    <div class="user-card">
      <van-image
        v-if="avatar"
        round
        width="60"
        height="60"
        :src="avatar"
        fit="cover"
      >
        <template #error>
          <div class="avatar-placeholder">{{ nameInitial }}</div>
        </template>
      </van-image>
      <div v-else class="avatar-placeholder-wrapper">
        <div class="avatar-placeholder">{{ nameInitial }}</div>
      </div>
      <div class="user-info">
        <div class="user-name">{{ userName }}</div>
        <div class="user-id">{{ employeeId }}</div>
        <div class="user-dept">{{ department }} · {{ position }}</div>
      </div>
    </div>

    <!-- 功能菜单 -->
    <van-cell-group inset>
      <van-cell title="个人资料" icon="user-o" is-link @click="$router.push('/profile')" />
      <van-cell title="考勤记录" icon="calendar-o" is-link @click="$router.push('/attendance')" />
      <van-cell title="请假记录" icon="edit" is-link @click="$router.push('/leave')" />
    </van-cell-group>

    <van-cell-group inset style="margin-top: 12px;">
      <van-cell title="入职进度" icon="clock-o" is-link @click="$router.push('/status')" />
      <van-cell title="修改密码" icon="lock" is-link @click="showPasswordDialog = true" />
      <van-cell title="关于" icon="info-o" is-link @click="showAbout = true" />
    </van-cell-group>

    <div style="padding: 20px 16px;">
      <van-button type="danger" block round plain @click="handleLogout">
        退出登录
      </van-button>
    </div>

    <!-- 修改密码弹窗 -->
    <van-dialog
      v-model:show="showPasswordDialog"
      title="修改密码"
      show-cancel-button
      :before-close="handlePasswordDialogClose"
    >
      <van-form ref="passwordFormRef">
        <van-cell-group>
          <van-field
            v-model="passwordForm.old_password"
            type="password"
            label="旧密码"
            placeholder="请输入旧密码"
          />
          <van-field
            v-model="passwordForm.new_password"
            type="password"
            label="新密码"
            placeholder="请输入新密码（至少8位）"
          />
          <van-field
            v-model="passwordForm.confirm_password"
            type="password"
            label="确认密码"
            placeholder="请再次输入新密码"
          />
        </van-cell-group>
      </van-form>
    </van-dialog>

    <!-- 关于弹窗 -->
    <van-dialog v-model:show="showAbout" title="关于" confirm-button-text="知道了">
      <div style="padding: 20px; text-align: center;">
        <div style="font-size: 18px; font-weight: 500;">HR员工自助系统</div>
        <div style="color: #969799; margin-top: 8px;">版本 1.0.0</div>
        <div style="color: #969799; margin-top: 16px; font-size: 13px;">
          提供入职登记、签到打卡、请假申请等自助服务
        </div>
      </div>
    </van-dialog>

    <!-- 底部导航 -->
    <van-tabbar v-model="activeTab" fixed>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="location-o" to="/checkin">打卡</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/me">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast, showConfirmDialog, showDialog } from 'vant'
import { useUserStore } from '../stores/user'
import api from '../utils/api'

const router = useRouter()
const userStore = useUserStore()
const activeTab = ref(2)

// 页面加载时刷新用户信息
onMounted(async () => {
  if (userStore.isLoggedIn) {
    await userStore.fetchProfile()
  }
})

const avatar = computed(() => userStore.employeeInfo?.avatar || '')
const userName = computed(() => userStore.employeeInfo?.name || userStore.userInfo?.username || '用户')
const nameInitial = computed(() => userName.value.charAt(0))
const employeeId = computed(() => userStore.employeeInfo?.employee_id ? `员工编号:${userStore.employeeInfo.employee_id}` : '')
const department = computed(() => userStore.employeeInfo?.department || '未分配')
const position = computed(() => userStore.employeeInfo?.position || '未分配')

const showPasswordDialog = ref(false)
const showAbout = ref(false)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

async function handlePasswordDialogClose(action) {
  if (action === 'cancel') {
    return true  // 允许关闭
  }
  
  // 点击确认按钮
  const { old_password, new_password, confirm_password } = passwordForm.value
  
  if (!old_password || !new_password || !confirm_password) {
    await showDialog({ title: '提示', message: '请填写完整信息' })
    return false  // 不关闭弹窗
  }
  if (new_password.length < 8) {
    await showDialog({ title: '提示', message: '新密码至少8位' })
    return false
  }
  if (new_password !== confirm_password) {
    await showDialog({ title: '提示', message: '两次密码不一致' })
    return false
  }
  
  try {
    const res = await api.post('/api/auth/change_password/', {
      old_password,
      new_password,
      confirm_password,
    })
    if (res.data.success) {
      passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
      // 延迟显示成功提示，等弹窗关闭后再显示
      setTimeout(() => {
        showDialog({ title: '成功', message: '密码修改成功' })
      }, 300)
      return true  // 关闭弹窗
    } else {
      await showDialog({ title: '修改失败', message: res.data.error?.message || '请检查输入' })
      return false
    }
  } catch (e) {
    await showDialog({ title: '修改失败', message: e.response?.data?.error?.message || '请检查输入' })
    return false
  }
}

function handleLogout() {
  showConfirmDialog({
    title: '提示',
    message: '确定要退出登录吗？',
  }).then(() => {
    userStore.logout()
    router.replace('/welcome')
  }).catch(() => {})
}
</script>

<style scoped>
.page-container {
  padding-bottom: 70px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 16px;
  background: linear-gradient(135deg, #409EFF 0%, #53a8ff 100%);
  color: #fff;
}

.avatar-placeholder-wrapper {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
}

.avatar-placeholder {
  width: 60px;
  height: 60px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
}

.user-id {
  font-size: 13px;
  opacity: 0.8;
  margin-top: 4px;
}

.user-dept {
  font-size: 13px;
  opacity: 0.8;
  margin-top: 2px;
}

:deep(.van-cell-group--inset) {
  margin-top: 12px;
}
</style>
