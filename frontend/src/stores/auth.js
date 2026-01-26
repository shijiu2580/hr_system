import { defineStore } from 'pinia';
import api from '../utils/api';

const LS_ACCESS = 'hr_access_token';
const LS_REFRESH = 'hr_refresh_token';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    roles: [],
    permissions: [],
    mustChangePassword: false,
    accessToken: null,
    refreshToken: null,
    ready: false,
    loading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.user && !!s.accessToken,
  },
  actions: {
    hydrateFromStorage(){
      if(!this.accessToken){
        this.accessToken = localStorage.getItem(LS_ACCESS);
        this.refreshToken = localStorage.getItem(LS_REFRESH);
      }
    },
    persistTokens(){
      if(this.accessToken){ localStorage.setItem(LS_ACCESS, this.accessToken); }
      else { localStorage.removeItem(LS_ACCESS); }
      if(this.refreshToken){ localStorage.setItem(LS_REFRESH, this.refreshToken); }
      else { localStorage.removeItem(LS_REFRESH); }
    },
    async fetchMe(){
      this.hydrateFromStorage();
      // 没有 token 直接标记为未登录，避免在登录页又被拉回首页
      if(!this.accessToken){
        this.user = null;
        this.roles = [];
        this.permissions = [];
        this.mustChangePassword = false;
        this.ready = true;
        return;
      }
      try {
        const resp = await api.get('/auth/me/', { noCache: true, skipDuplicateCheck: true });
        const data = resp?.data;
        if(resp?.success && data?.authenticated){
          this.user = data.user;
          this.roles = data.roles || [];
          this.permissions = data.permissions || [];
          this.mustChangePassword = !!(data.must_change_password || data.user?.must_change_password);
        } else {
          this.user = null; this.roles = []; this.permissions = [];
          this.mustChangePassword = false;
        }
      } catch(e){
        // 若 401 则保持未登录状态
        this.user = null;
        this.roles = [];
        this.permissions = [];
        this.mustChangePassword = false;
      } finally {
        this.ready = true;
      }
    },
    async login(username, password){
      this.loading = true; this.error = null;
      try {
        // 获取 JWT（SimpleJWT 默认字段 access / refresh）
        const resp = await api.post('/auth/token/', { username, password });
        if (!resp.success) {
          // 401 时 detail 通常是 "No active account found with the given credentials"
          const msg = resp.error?.message || resp.detail || '登录失败';
          this.error = msg.includes('credentials') || msg.includes('active account')
            ? '账号或密码错误'
            : msg;
          throw new Error(this.error);
        }
        this.accessToken = resp.data.access;
        this.refreshToken = resp.data.refresh;
        this.persistTokens();
        await this.fetchMe();
        if(!this.user){
          throw new Error('登录失败');
        }
      } catch(e){
        if (!this.error) {
          this.error = '账号或密码错误';
        }
        this.forceLogout();
        throw e;
      } finally { this.loading = false; }
    },
    async refresh(){
      if(!this.refreshToken) throw new Error('无刷新令牌');
      try {
        const resp = await api.post('/auth/token/refresh/', { refresh: this.refreshToken }, { skipDuplicateCheck: true });
        if (!resp.success) throw new Error(resp.error?.message || resp.detail || '刷新失败');
        const data = resp.data;
        this.accessToken = data.access;
        if (data.refresh) this.refreshToken = data.refresh;
        this.persistTokens();
      } catch(e){
        this.forceLogout();
        throw e;
      }
    },
    forceLogout(){
      this.accessToken = null; this.refreshToken = null; this.user = null; this.roles = []; this.permissions = []; this.persistTokens();
      this.mustChangePassword = false;
    },
    async logout(){
      try { await api.post('/auth/logout/'); } catch(_) {}
      this.forceLogout(); this.ready = true;
    },
    hasPermissionKey(key){
      if(!key) return false;
      if(this.roles.some(r => r.code === 'admin')) return true;
      return this.permissions.includes(key);
    }
  }
});
