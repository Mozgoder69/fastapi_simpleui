// frontend/src/core/services/client.ts

import axios from "axios";
import { LRUCache } from "lru-cache";

export const cache = new LRUCache({
	max: 500,
	maxSize: 5000,
	sizeCalculation: (value) => JSON.stringify(value).length || 1,
	ttl: 1000 * 30,
});

export const client = axios.create({
	baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8173",
	timeout: 10000,
	headers: { "Content-Type": "application/json", Accept: "application/json" },
});

const MUTATING_METHODS = ["post", "put", "delete", "patch"];

const generateCacheKey = (config) =>
	config.method?.toLowerCase() === "get" && config.url
		? `${config.method.toUpperCase()}:${config.url}${config.params ? JSON.stringify(config.params, Object.keys(config.params).sort()) : ""}`
		: null;

client.interceptors.request.use((config) => {
	const cacheKey = generateCacheKey(config);
	if (cacheKey) {
		const cached = cache.get(cacheKey);
		if (cached !== undefined)
			return Promise.reject({
				__fromCache: true,
				config,
				status: 304,
				data: cached,
			});
	}
	return config;
});

client.interceptors.response.use(
	(response) => {
		const { config } = response;
		const method = config.method?.toLowerCase();
		if (method === "get") {
			const cacheKey = generateCacheKey(config);
			if (cacheKey && response.data) cache.set(cacheKey, response.data);
		} else if (method && MUTATING_METHODS.includes(method)) cache.clear();
		return response.data;
	},
	(error) => {
		if (error.__fromCache && error.data) return Promise.resolve(error.data);
		if (error.response)
			console.error("API Error:", {
				status: error.response.status,
				data: error.response.data,
				url: error.config?.url,
			});
		else if (error.request)
			console.error("API No Response:", {
				message: error.message,
				url: error.config?.url,
			});
		else console.error("API Setup Error:", error.message);
		return Promise.reject(error);
	},
);
