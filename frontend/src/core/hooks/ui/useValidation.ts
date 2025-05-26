// frontend/src/core/hooks/ui/useValidation.ts

import type { Field, JsonSchema, Value } from "@/core/types";
import {
	extractPrimaryKeys,
	extractProperties,
} from "@/core/utils/schemaUtils";
import { ref, watch } from "vue";
import * as yup from "yup";

const MESSAGES = {
	REQUIRED: (l: string) => `${l} is required`,
	NUMBER: (l: string) => `${l} must be a number`,
	INTEGER: (l: string) => `${l} must be an integer`,
	EMAIL: (l: string) => `${l} must be a valid email`,
	DATE: (l: string) => `${l} must be a valid date`,
	DATE_TIME: (l: string) => `${l} must be a valid date/time`,
	TIME: (l: string) => `${l} must be a valid time`,
	MAX_LENGTH: (l: string, m: number) => `${l} ≤ ${m} chars`,
	MIN_LENGTH: (l: string, m: number) => `${l} ≥ ${m} chars`,
	MIN_VALUE: (l: string, m: number) => `${l} ≥ ${m}`,
	MAX_VALUE: (l: string, m: number) => `${l} ≤ ${m}`,
	ONE_OF: (l: string, vs: Value[]) => `${l} ∈ {${vs.join(", ")}}`,
	PATTERN: (l: string) => `${l} has bad format`,
};

function baseValidator(field: Field, name: string) {
	const lbl = field.label || name;
	switch (field.format) {
		case "date-time":
			return yup.date().typeError(MESSAGES.DATE_TIME(lbl));
		case "date":
			return yup.date().typeError(MESSAGES.DATE(lbl));
		case "time":
			return yup.string().matches(/^([01]\d|2[0-3]):([0-5]\d)(:[0-5]\d)?$/, {
				message: MESSAGES.TIME(lbl),
				excludeEmptyString: true,
			});
		case "email":
			return yup.string().email(MESSAGES.EMAIL(lbl));
	}
	switch (field.type) {
		case "string":
			return yup.string();
		case "number":
			return yup.number().typeError(MESSAGES.NUMBER(lbl));
		case "integer":
			return yup
				.number()
				.integer(MESSAGES.INTEGER(lbl))
				.typeError(MESSAGES.NUMBER(lbl));
		case "boolean":
			return yup.boolean();
		case "array":
			return yup.array();
		case "object":
			return yup.object();
		default:
			return yup.mixed();
	}
}

function addConstraints(v: yup.AnySchema, field: Field, name: string) {
	const lbl = field.label || name;
	let result = v;
	if (field.type === "string") {
		if (field.maxLength != null)
			result = (v as yup.StringSchema).max(
				field.maxLength,
				MESSAGES.MAX_LENGTH(lbl, field.maxLength),
			);
		if (field.minLength != null)
			result = (v as yup.StringSchema).min(
				field.minLength,
				MESSAGES.MIN_LENGTH(lbl, field.minLength),
			);
		if (field.pattern)
			result = (v as yup.StringSchema).matches(
				new RegExp(String(field.pattern)),
				{
					message: MESSAGES.PATTERN(lbl),
					excludeEmptyString: true,
				},
			);
	}
	if (["number", "integer"].includes(field.type)) {
		if (field.minimum != null)
			result = (v as yup.NumberSchema).min(
				field.minimum,
				MESSAGES.MIN_VALUE(lbl, field.minimum),
			);
		if (field.maximum != null)
			result = (v as yup.NumberSchema).max(
				field.maximum,
				MESSAGES.MAX_VALUE(lbl, field.maximum),
			);
	}
	if (Array.isArray(field.enum) && field.enum.length)
		result = yup.mixed().oneOf(field.enum, MESSAGES.ONE_OF(lbl, field.enum));
	return result;
}

function addRequirement(
	v: yup.AnySchema,
	field: Field,
	name: string,
	mode: string,
	primary: string[],
	requiredList?: string[],
) {
	const lbl = field.label || name;
	let req = requiredList?.includes(name) ?? false;
	if (primary.includes(name)) {
		req = mode !== "insert";
	}
	if (
		field.is_enabled === false &&
		!(primary.includes(name) && mode !== "insert")
	) {
		req = false;
	}
	if (req) {
		if (v instanceof yup.StringSchema)
			return v.trim().required(MESSAGES.REQUIRED(lbl));
		if (v instanceof yup.ArraySchema)
			return v.min(1, MESSAGES.REQUIRED(lbl)).required(MESSAGES.REQUIRED(lbl));
		return v.required(MESSAGES.REQUIRED(lbl));
	}
	return v.nullable().optional();
}

export function useValidation(
	schemaRef: Ref<JsonSchema | undefined>,
	modeRef: Ref<string>,
	stepRef?: Ref<number | undefined>,
) {
	const validationSchema = ref<yup.ObjectSchema>(yup.object({}));

	function build(sch?: JsonSchema, mode?: string, step?: number) {
		if (!sch || !mode) return yup.object({});
		const props = extractProperties(sch, mode, step);
		const primary = extractPrimaryKeys(sch);
		let reqList: string[] | undefined;
		// определяем reqList из sch.required / modes.required / steps.required
		if ("steps" in sch && step != null) {
			const st = sch.steps.find((s) => s.step === step);
			const md = st?.modes.find((m) => m.mode === mode);
			reqList = md?.required || st?.required;
		} else if ("modes" in sch) {
			const md = sch.modes.find((m) => m.mode === mode);
			reqList = md?.required || sch.required;
		} else {
			reqList = sch.required;
		}

		const shape: Record<string, yup.AnySchema> = {};
		for (const [k, f] of Object.entries(props)) {
			if (!f) continue;
			let v = baseValidator(f, k);
			v = addConstraints(v, f, k);
			v = addRequirement(v, f, k, mode, primary, reqList);
			shape[k] = v;
		}
		return yup.object(shape);
	}

	watch(
		[schemaRef, modeRef, ...(stepRef ? [stepRef] : [])],
		([sch, mode, step]) => {
			validationSchema.value = build(sch, mode, step);
		},
		{ deep: true, immediate: true },
	);

	return { validationSchema };
}
