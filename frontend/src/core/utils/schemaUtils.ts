// frontend/src/core/utils/schemaUtils.ts

import type {
	JsonSchema,
	ModeViewSchema,
	WizardViewSchema,
} from "@/core/types";

/**
 *  Вернёт свойства для переданного режима/шага.
 */
export function extractProperties(
	schema: JsonSchema | ModeViewSchema | WizardViewSchema,
	mode: "insert" | "select" | "update" = "insert",
	step?: number,
): Record {
	if ("steps" in schema) {
		const st =
			step != null
				? schema.steps.find((s) => s.step === step)
				: schema.steps[0];
		return (
			st?.modes.find((m) => m.mode === mode)?.properties || st?.properties || {}
		);
	}
	if ("modes" in schema) {
		return (
			schema.modes.find((m) => m.mode === mode)?.properties ||
			schema.properties ||
			{}
		);
	}
	return schema.properties || {};
}

/**
 *  Список ключевых полей (primary_key=true).
 */
export function extractPrimaryKeys(schema: JsonSchema): string[] {
	return Object.entries(extractProperties(schema, "select"))
		.filter(([, f]) => f.primary_key)
		.map(([k]) => k);
}

/**
 *  Инициализация данных по дефолту + встраивание existing.
 */
export function getDefaultData(
	schema: JsonSchema | ModeViewSchema,
	mode: "insert" | "select" | "update" = "insert",
	existing: Record = {},
): Record {
	const props = extractProperties(schema, mode);
	return Object.keys(props).reduce((out, key) => {
		out[key] = existing[key] ?? props[key].default ?? null;
		return out;
	}, {} as Record);
}
