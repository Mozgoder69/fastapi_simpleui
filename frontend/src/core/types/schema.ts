// frontend/src/core/types/schema.ts

import type { Component } from "vue"; // Для прямого указания компонента
import type { Value } from "./data";

// export type FieldState

export type UIHints = {
	label?: string;
	icon?: string;
	state?: "edit" | "read" | "text" | "none"; // RW input, RO input, RO label, hidden field
	component?: string | Component;
	formatter?: (value: Value) => string;
};

export type Field = {
	type?: string;
	format?: string;
	default?: Value;
	enum?: Value[];
	primary_key?: boolean;
	foreign_key?: ForeignKey;
	required?: boolean;
	is_enabled?: boolean;
	uiHints?: UIHints;
	[key: string]: Value;
};

export type ForeignKey = {
	ref_schema: string;
	ref_table: string;
	ref_column: string;
	label_fields: string[];
};

export type BaseJsonSchema = {
	$schema: string;
	entity: string;
	title: string;
	icon: string;
	properties: Record<string, Field>;
	additionalProperties: boolean;
	[key: string]: Value;
};

export type ModeSchema = {
	mode: "insert" | "select" | "update";
	title: string;
	properties: Record<string, Field>;
};

export type FormViewSchema = BaseJsonSchema & {
	view: "FormView";
	modes: ModeSchema[];
};
export type StepSchema = {
	step: number;
	entity: string;
	title: string;
	icon: string;
	modes: ModeSchema[];
};
export type WizardViewSchema = BaseJsonSchema & {
	view: "WizardView";
	steps: StepSchema[];
};
export type GridViewSchema = BaseJsonSchema & {
	view: "TableView" | "CardView";
};
export type ModeViewSchema = FormViewSchema | WizardViewSchema;
export type ViewJsonSchema = GridViewSchema | ModeViewSchema;
export type JsonSchema = BaseJsonSchema | ViewJsonSchema;

export interface StepData {
	mode: "insert" | "select";
	data: Record<string, Value>;
	recordId: Record<string, Value> | null;
	__completed: boolean;
}

export interface WizardData {
	[step: number]: StepData;
}
