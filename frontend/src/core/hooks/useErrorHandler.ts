// frontend/src/core/hooks/useErrorHandler.ts

import type { AxiosError } from "axios";
import { useToast } from "vue-toastification";

/**
 * Оборачивает async-функцию, показывает toast’ы об ошибках/успехе,
 * логирует в dev.
 */
export function useErrorHandler(
	fn: (...args: Args) => Promise<R>,
	context = "Operation",
	showSuccess = false,
): (...args: Args) => Promise<R> {
	const toast = useToast();
	return async (...args: Args): Promise<R> => {
		try {
			const res = await fn(...args);
			if (showSuccess) toast.success(`${context} succeeded.`);
			return res;
		} catch (err) {
			let msg = "Unexpected error.";
			if ((err as AxiosError).isAxiosError) {
				msg =
					err.response?.data?.detail ||
					err.response?.data?.message ||
					err.message;
			} else if (err instanceof Error) {
				msg = err.message;
			}
			if (import.meta.env.DEV) console.error(`[${context}]`, err);
			toast.error(`${context} failed: ${msg}`);
			throw err;
		}
	};
}
