// frontend/vite.config.ts

import vue from "@vitejs/plugin-vue";
import path from "node:path";

import { defineConfig } from "vite";

export default defineConfig({
	root: "src",
	plugins: [vue()],
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
		},
	},
	server: {
		port: 5173,
		proxy: {
			"/api": {
				target: import.meta.env.VITE_API_URL || "http://localhost:8173",
				changeOrigin: true,
				rewrite: (path: string) => path.replace(/^\/api\/?/, ""),
			},
		},
	},
	build: {
		minify: false,
		outDir: path.resolve(__dirname, "../dist"),
		rollupOptions: {
			input: path.resolve(__dirname, "src/index.html"),
		},
	},
});
