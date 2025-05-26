// frontend/src/core/auth/useAuthInterceptors.ts

import { useAuthStore } from "@/core/auth/useAuthStore";
import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { client } from "@/core/services/client";
import type { AxiosRequestConfig } from "axios";
import { useRouter } from "vue-router";

const setAuthHeader = (config: AxiosRequestConfig, token: string) => {
	config.headers = config.headers ?? {};
	config.headers.Authorization = `Bearer ${token}`;
	return config;
};

export function useAuthInterceptors() {
	const store = useAuthStore();
	const router = useRouter();

	// проактивно проверяем и обновляем токен при инициализации
	store.checkToken();

	// 1. request — вшиваем токен, если есть
	client.interceptors.request.use(
		(config: AxiosRequestConfig) => {
			if (store.access_token) {
				console.debug("[Auth] attach token");
				setAuthHeader(config, store.access_token);
			}
			return config;
		},
		useErrorHandler((err) => Promise.reject(err), "Auth Request Error"),
	);

	// 2. response — ловим 400/401, делаем refresh, реинжектим токен и повторяем запрос
	client.interceptors.response.use(
		(response) => response,
		useErrorHandler(async (error) => {
			const status = error.response?.status;
			const req = error.config as AxiosRequestConfig & { _retry?: boolean };

			if ((status === 400 || status === 401) && !req._retry) {
				req._retry = true;

				if (!store.refresh_token) {
					console.warn("[Auth] no refresh token, logging out");
					await store.logout();
					router.push({ name: "Login" });
					throw new Error("No refresh token");
				}

				console.debug("[Auth] refreshing token");
				const newToken = await store.refreshToken();
				setAuthHeader(req, newToken);
				return client(req);
			}

			throw error;
		}, "Auth Response Error"),
	);
}
