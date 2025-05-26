// frontend/src/core/hooks/data/useSchemas.ts

import { api } from "@/core/services/api";

export const useSchemas = () => ({
	getTables: api.getTables,
	getSchemas: api.getSchemas,
	getSchema: api.getSchema,
	getSchemaView: (table: string, view = "WizardView") =>
		view === "WizardView"
			? api.getWizardSchemaView(table)
			: api.getSimpleSchemaView(table, view),
});
