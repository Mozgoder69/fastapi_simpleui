import App from "@/App.vue";
import { createPinia } from "pinia";
import createLogger from "pinia-logger";
// frontend/src/main.ts
import "@mdi/font/css/materialdesignicons.css";
import { createApp } from "vue";
import Toast, { POSITION } from "vue-toastification";
import "vue-toastification/dist/index.css";

import { setupErrorHandler } from "@/global/plugins/errorHandler";
import vuetify from "@/global/plugins/vuetify";
import router from "@/global/routers";
import { setupGuards } from "@/global/routers/guards";

import { useAuthInterceptors } from "@/core/auth/useAuthInterceptors";
import { useAuthStore } from "@/core/auth/useAuthStore";
import { useErrorHandler } from "@/core/hooks/useErrorHandler";

async function bootstrap() {
	const app = createApp(App);

	// Pinia + dev-logger
	const pinia = createPinia();
	if (import.meta.env.DEV) {
		pinia.use(
			createLogger({
				expanded: false,
				logActions: true,
				logMutations: true,
				showStoreName: true,
			}),
		);
	}
	app.use(pinia);

	// глобальный Vue.errorHandler → toast
	setupErrorHandler(app);

	// auth
	const authStore = useAuthStore();
	useAuthInterceptors();
	await authStore.checkToken();

	// маршруты
	setupGuards(router);
	app.use(router);

	// UI
	app.use(vuetify);
	app.use(Toast, {
		position: POSITION.BOTTOM_RIGHT,
		timeout: 4000,
		draggable: false,
		closeOnClick: false,
	});

	app.mount("#app");
}

useErrorHandler(bootstrap, "Initialize App")();
