import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router';
import App from './App.vue';
import { setupPermissionDirective } from './utils/directives';
import './style.css';

const app = createApp(App);
app.use(createPinia());
app.use(router);

// 注册权限指令 v-permission
setupPermissionDirective(app);

// 全局处理日期输入框点击 - 自动打开日期选择器
document.addEventListener('click', (e) => {
	const target = e.target;
	if (target && target.tagName === 'INPUT' && target.type === 'date') {
		// 使用 showPicker API（现代浏览器支持）
		if (typeof target.showPicker === 'function') {
			try {
				target.showPicker();
			} catch (err) {
				// 某些情况下可能会抛出错误，忽略即可
			}
		}
	}
});

router.isReady().then(() => {
	app.mount('#app');
});
