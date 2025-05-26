// frontend/src/global/router/index.ts

import { createRouter, createWebHistory } from "vue-router";

const routes = [
	{
		path: "/login",
		name: "Login",
		component: () => import("@/ui/pages/LoginPage.vue"),
		meta: { public: true },
	},
	{
		path: "/bssentity/:tableName",
		name: "BssEntity",
		component: () => import("@/ui/pages/BssEntityPage.vue"),
		props: true,
	},
	{
		path: "/apiroutes",
		name: "API Routes",
		component: () => import("@/ui/pages/APIRoutesPage.vue"),
		meta: { public: true },
	},
	{
		path: "/apitest",
		name: "API Test",
		component: () => import("@/ui/pages/APITestPage.vue"),
	},
	{
		path: "/otp",
		name: "OTP",
		component: () => import("@/ui/pages/OTPPage.vue"),
	},
	{
		path: "/",
		name: "Home",
		component: () => import("@/ui/pages/HomePage.vue"),
	},
];

export default createRouter({
	history: createWebHistory(),
	routes,
});
