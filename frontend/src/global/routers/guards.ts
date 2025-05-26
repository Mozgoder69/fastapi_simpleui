// frontend/src/global/router/guards.ts

import { useAuthStore } from "@/core/auth/useAuthStore";
import type { Router } from "vue-router";

export function setupGuards(router: Router) {
	const auth = useAuthStore();
	router.beforeEach((to, from, next) => {
		const needs = !to.meta.public;
		if (needs && !auth.isAuthenticated) {
			next({ name: "Login", query: { redirect: to.fullPath } });
		} else if (to.name === "Login" && auth.isAuthenticated) {
			next({ name: "Home" });
		} else {
			next();
		}
	});
}
