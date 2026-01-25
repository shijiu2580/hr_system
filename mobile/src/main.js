import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import SvgIcon from './components/SvgIcon.vue'
// 导入 svg 图标脚本
import 'virtual:svg-icons-register'

// Vant 组件样式
import 'vant/lib/index.css'
import './styles/index.css'

const app = createApp(App)

app.component('svg-icon', SvgIcon)

app.use(createPinia())
app.use(router)

app.mount('#app')
