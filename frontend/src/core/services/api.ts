// frontend/src/core/services/api.ts

import { client } from "./client";

const serializeParams = (params) => {
	if (!params) return undefined;
	const serialized = {};
	for (const key in params) {
		if (
			Object.prototype.hasOwnProperty.call(params, key) &&
			params[key] !== undefined
		) {
			serialized[key] =
				typeof params[key] === "object" && params[key] !== null
					? JSON.stringify(params[key])
					: params[key];
		}
	}
	return serialized;
};

const filterValidColumns = (columns = []) =>
	columns.filter((col) => typeof col === "string" && col.trim() !== "");

export const api = {
	getTables: () =>
		client.get("/api/tables").then((res) => res.map((t) => t.table_name)),
	getEnumTypes: () => client.get("/api/enums"),
	getEnumValues: (enumType) => client.get(`/api/enums/${enumType}`),
	getSchema: (table) => client.get(`/api/tables/${table}/schema`),
	getWizardSchemaView: (table) =>
		client.get(`/api/tables/${table}/schema/WizardView`),
	getSimpleSchemaView: (table, schemaView) =>
		client.get(`/api/tables/${table}/schema/${schemaView}`),
	getSchemas: () => client.get("/api/tables/schemas"),
	getBackRefs: (table: string) => client.get(`/api/tables/${table}/refs`),
	genMany: (table, data_only_list) =>
		client.post(`/api/tables/${table}/data/bulk`, { records: data_only_list }),
	listMany: (table, filters = {}, columns = [], limit = 20, offset = 0) =>
		client.get(`/api/tables/${table}/data/bulk`, {
			params: serializeParams({
				filters,
				columns: filterValidColumns(columns),
				limit: limit || 1,
				offset,
			}),
		}),
	trimMany: (table, keys_only_list) =>
		client.delete(`/api/tables/${table}/data/bulk`, {
			data: { records: keys_only_list },
		}),
	updMany: (table, keyed_data_list) =>
		client.put(`/api/tables/${table}/data/bulk`, { records: keyed_data_list }),
	newOne: (table, data_only) =>
		client.post(`/api/tables/${table}/data`, data_only),
	readOne: (table, filters, columns = []) =>
		client.get(`/api/tables/${table}/data`, {
			params: serializeParams({
				filters,
				columns: filterValidColumns(columns),
			}),
		}),
	delOne: (table, keys_only) =>
		client.delete(`/api/tables/${table}/data`, { data: keys_only }),
	editOne: (table, keyed_data) =>
		client.put(`/api/tables/${table}/data`, keyed_data),

	createWizard: (table: string, steps: WizardStepRequest[]) =>
		client.post(`/api/tables/${table}/data/wizard`, steps),

	generateOTP: (contact) =>
		client.post("/api/message/generate", { contact, role: "customer" }),
	validateOTP: (customerId, otp) =>
		client.post("/api/message/validate", {
			customer_id: customerId,
			subject: otp,
			uname: "customer",
			role: "customer",
		}),
};
