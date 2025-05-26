// frontend/src/core/auth/useAuthStore.ts

import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { cache, client } from "@/core/services/client";
import { defineStore } from "pinia";
import { computed, reactive } from "vue";

function decodeJWT(token: string) {
	try {
		const [, payload] = token.split(".");
		return JSON.parse(
			atob(
				payload
					.replace(/-/g, "+")
					.replace(/_/g, "/")
					.padEnd(payload.length + ((4 - (payload.length % 4)) % 4), "="),
			),
		);
	} catch {
		return {};
	}
}

export const useAuthStore = defineStore("auth", () => {
	const state = reactive({
		access_token: localStorage.getItem("access_token") as string | null,
		refresh_token: localStorage.getItem("refresh_token") as string | null,
		uname: "" as string,
		isRefreshing: false,
		refreshSubscribers: [] as Array<(token: string | null) => void>,
	});

	// сразу выставляем заголовок для любых запросов, отправленных до interceptors
	if (state.access_token) {
		client.defaults.headers.common.Authorization = `Bearer ${state.access_token}`;
		state.uname = decodeJWT(state.access_token).uname || "";
	}

	const isAuthenticated = computed(() => !!state.access_token);

	function setTokens(access: string, refresh: string) {
		state.access_token = access;
		state.refresh_token = refresh;
		localStorage.setItem("access_token", access);
		localStorage.setItem("refresh_token", refresh);
		client.defaults.headers.common.Authorization = `Bearer ${access}`;
		state.uname = decodeJWT(access).uname || "";
	}

	function clearTokens() {
		state.access_token = null;
		state.refresh_token = null;
		state.uname = "";
		localStorage.removeItem("access_token");
		localStorage.removeItem("refresh_token");
		client.defaults.headers.common.Authorization = undefined;
		cache.clear();
	}

	const logout = useErrorHandler(async () => {
		clearTokens();
	}, "Logout");

	const login = useErrorHandler(async (username: string, password: string) => {
		clearTokens();
		const resp = await client.post(
			"/api/token",
			new URLSearchParams({ username, password }),
			{ headers: { "Content-Type": "application/x-www-form-urlencoded" } },
		);
		setTokens(resp.access_token, resp.refresh_token);
		return true;
	}, "Login");

	const loginAsGuest = () => login("customer", "customer");

	const refreshToken = useErrorHandler(async (): Promise<string> => {
		if (!state.refresh_token) throw new Error("No refresh token");

		if (state.isRefreshing) {
			return new Promise((resolve) => {
				state.refreshSubscribers.push(resolve);
			});
		}

		state.isRefreshing = true;
		try {
			const resp = await client.post(
				"/api/token/refresh",
				new URLSearchParams({ refresh_token: state.refresh_token }),
				{ headers: { "Content-Type": "application/x-www-form-urlencoded" } },
			);
			const newAccess = resp.access_token;
			const newRefresh = resp.refresh_token || state.refresh_token;
			setTokens(newAccess, newRefresh);

			for (const cb of state.refreshSubscribers) {
				cb(newAccess);
			}

			state.refreshSubscribers = [];
			return newAccess;
		} catch (e) {
			for (const cb of state.refreshSubscribers) {
				cb(null);
			}
			state.refreshSubscribers = [];
			await logout();
			throw new Error("Refresh failed");
		} finally {
			state.isRefreshing = false;
		}
	}, "Refresh Token");

	const checkToken = useErrorHandler(async () => {
		if (!state.access_token) return;
		const { exp } = decodeJWT(state.access_token);
		if (!exp || exp * 1000 < Date.now()) {
			state.refresh_token ? await refreshToken() : await logout();
		}
	}, "Check Token");

	return {
		access_token: computed(() => state.access_token),
		refresh_token: computed(() => state.refresh_token),
		uname: computed(() => state.uname),
		isAuthenticated,
		login,
		loginAsGuest,
		refreshToken,
		logout,
		checkToken,
	};
});
