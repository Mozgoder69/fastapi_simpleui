// frontend/src/core/utils/dataUtils.ts

import type { Dict, Field, Value } from "@/core/types";

/** Обрезает строку посередине, вставляя "..." */
export function truncateValue(value: Value, maxLength = 15): string {
	const str = String(value ?? "");
	if (str.length <= maxLength) return str;
	const half = Math.floor((maxLength - 3) / 2);
	return `${str.slice(0, half + ((maxLength - 3) % 2))}...${str.slice(-half)}`;
}

/** Парсит default из JSON-схемы, поддерживает now() и числовые/boolean */
export function parseDefaultValue(field: Field): Value {
	const def = field.default;
	if (def == null) return field.type === "boolean" ? false : null;
	if (typeof def !== "string") return def;
	if (def.includes("now()")) {
		const dt = new Date();
		const m = /'(\d+)\s*years'/.exec(def);
		if (m) dt.setFullYear(dt.getFullYear() - +m[1]);
		if (field.format === "date") return dt.toISOString().slice(0, 10);
		if (field.format === "time") return dt.toTimeString().slice(0, 5);
		if (field.format === "date-time") return dt.toISOString().slice(0, 16);
	}
	if (field.type === "boolean") return def.toLowerCase() === "true";
	if (["integer", "number"].includes(field.type))
		return Number.parseFloat(def) || null;
	return def.replace(/'::\w+/, "");
}

/** Собирает объект formData из properties и existing */
export function initFormData(
	properties: Record<string, Field>,
	existing: Dict = {},
): Dict {
	return Object.fromEntries(
		Object.entries(properties).map(([k, f]) => [
			k,
			k in existing ? existing[k] : parseDefaultValue(f),
		]),
	);
}

export function resetFormDataForMode(
	modeSchema: ModeSchema,
	existingData: Dict = {},
): Dict {
	return initFormData(modeSchema.properties, existingData);
}

export function initStepData(step: StepSchema): Dict {
	const firstMode = step.modes[0];
	return initFormData(firstMode.properties);
}
