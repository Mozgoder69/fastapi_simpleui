// frontend/src/core/services/extra.ts
/* API-клиент для взаимодействия с серверными эндпоинтами: получение метаданных (например, схемы таблиц) и выполнение CRUD операций */

import { client } from "./client";

export const api = {
	// Custom API routes
	// Activity endpoints
	acceptRequest: (requestId: number) =>
		client.post(`/api/request/${requestId}/accept/`),
	rejectRequest: (requestId: number) =>
		client.post(`/api/request/${requestId}/reject/`),

	validateUniqueContact: (contact: string) =>
		client.get("/api/contact/validate/", { params: { contact } }),

	// Internal Registration endpoints
	resetPassword: (employeeId: number, password: string) =>
		client.post(`/api/employee/${employeeId}/reset_password/`, { password }),

	// Sales Order endpoints
	cancelSalesOrder: (salesOrderId: number) =>
		client.post(`/api/salesorder/${salesOrderId}/cancel/`),
	acceptSalesOrder: (salesOrderId: number) =>
		client.post(`/api/salesorder/${salesOrderId}/accept/`),
	executeSalesOrder: (salesOrderId: number) =>
		client.post(`/api/salesorder/${salesOrderId}/execute/`),
	finishSalesOrder: (salesOrderId: number) =>
		client.post(`/api/salesorder/${salesOrderId}/finish/`),
	returnSalesOrder: (salesOrderId: number) =>
		client.post(`/api/salesorder/${salesOrderId}/return/`),

	// Scenario endpoints
	updateScenarioOffsiteRooms: (
		addressId: number,
		scenarioId: number,
		roomsLeft: number,
	) =>
		client.put(`/api/scenario_offsite/${addressId}/${scenarioId}/`, {
			rooms_left: roomsLeft,
		}),
	updateScenarioOnsiteStage: (
		productId: number,
		scenarioId: number,
		currentStage: string,
	) =>
		client.put(`/api/scenario_onsite/${productId}/${scenarioId}/`, {
			current_stage: currentStage,
		}),

	// Report endpoints
	generateEmployeeTaskPerformanceReport: (startDate: string, endDate: string) =>
		client.get("/api/reports/employee-task-performance", {
			params: { start_date: startDate, end_date: endDate },
		}),
	generateEmployeeOrderPerformanceReport: (
		startDate: string,
		endDate: string,
	) =>
		client.get("/api/reports/employee-order-performance", {
			params: { start_date: startDate, end_date: endDate },
		}),
	generateServiceUsageReport: (startDate: string, endDate: string) =>
		client.get("/api/reports/service-usage", {
			params: { start_date: startDate, end_date: endDate },
		}),
	generateServiceSatisfactionReport: (startDate: string, endDate: string) =>
		client.get("/api/reports/service-satisfaction", {
			params: { start_date: startDate, end_date: endDate },
		}),
	generateCatalogChangeReport: (startDate: string, endDate: string) =>
		client.get("/api/reports/catalog-change", {
			params: { start_date: startDate, end_date: endDate },
		}),
	generateOrderTimingReport: (startDate: string, endDate: string) =>
		client.get("/api/reports/order-timing", {
			params: { start_date: startDate, end_date: endDate },
		}),
	generateCatalogUsageReport: (startDate: string, endDate: string) =>
		client.get("/api/reports/catalog-usage", {
			params: { start_date: startDate, end_date: endDate },
		}),
};
