// frontend/src/core/utils/fieldMapping.ts

import FKSelect from "@/ui/atoms/FKSelect.vue";
import PKSelect from "@/ui/atoms/PKSelect.vue";
import TextBool from "@/ui/atoms/TextBool.vue";

const BASE_TYPES = {
	boolean: { component: TextBool, icon: "mdi-toggle-switch" },
	string: { component: "v-text-field", icon: "mdi-alphabetical" },
	integer: { component: "v-text-field", icon: "mdi-numeric" },
	number: { component: "v-text-field", icon: "mdi-numeric" },
	date: {
		component: "v-text-field",
		icon: "mdi-calendar",
		formatter: (v) => new Date(v).toLocaleDateString(),
	},
	"date-time": {
		component: "v-text-field",
		icon: "mdi-calendar",
		formatter: (v) => new Date(v).toLocaleString(),
	},
};

export function getFieldComponent(field) {
	if (field.foreign_keys) return FKSelect;
	if (field.primary_key) return PKSelect;
	if (field.enum) return "v-select";
	return (
		BASE_TYPES[field.format]?.component ||
		BASE_TYPES[field.type]?.component ||
		"v-text-field"
	);
}

export function getFieldIcon(field) {
	if (field.foreign_keys) return "mdi-link";
	if (field.primary_key) return "mdi-key";
	if (field.enum) return "mdi-format-list-bulleted";
	return (
		BASE_TYPES[field.format]?.icon ||
		BASE_TYPES[field.type]?.icon ||
		"mdi-label"
	);
}

export function formatField(field, value) {
	return BASE_TYPES[field.format]?.formatter?.(value) ?? value;
}
