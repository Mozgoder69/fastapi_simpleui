// frontend/src/global/plugins/errorHandler.ts

import type { AxiosError } from "axios";
import type { App } from "vue";
import { useToast } from "vue-toastification";

export function setupErrorHandler(app: App) {
	app.config.errorHandler = (err, instance, info) => {
		const toast = useToast();
		let msg = "Unhandled error.";
		if ((err as AxiosError).isAxiosError) {
			msg =
				err.response?.data?.detail ||
				err.response?.data?.message ||
				err.message;
		} else if (err instanceof Error) {
			msg = err.message;
		}
		const comp =
			instance?.$?.type?.name || instance?.$options?.name || "Anonymous";
		console.error(`Error in ${comp} (${info}):`, err);
		toast.error(`Error in ${comp}: ${msg}`);
	};
}
