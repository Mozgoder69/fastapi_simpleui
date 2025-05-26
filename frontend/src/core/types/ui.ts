// frontend/src/core/types/ui.ts
import type { Dict, Field, ModeViewSchema, Value } from "."; // Import necessary types

// Basic Toast notification structure (if needed internally, vue-toastification handles its own)
// export type Toast = { id: number; message: string; type: string; show: boolean; position: "top" | "bottom"; };

// Action button definition
export type Action = {
	name: string; // Internal identifier (e.g., "newOne")
	label: string; // Button text
	isEnabled: boolean; // Whether the button is clickable
	icon?: string; // Optional icon
	color?: string; // Optional color
};

// Dynamic frame definition (if FramesBox is used)
export type Frame = {
	id: string; // Unique identifier
	component: string; // Component name to render
	[key: string]: Value; // Additional props for the component
};

// Generic props for components accepting v-model and schema (example)
// export type ComponentProps<T> = { modelValue?: T; label?: string; schema?: JsonSchema; [key: string]: any; };

// Props specifically for a component rendering a single field based on schema (might not be needed if DynamicField covers it)
// export type FieldProps = { field: Field; modelValue: Dict; label: string; validationSchema: yup.ObjectSchema<Dict>; loadForeignKeyOptions?: () => Promise<{ value: Value; label: string }[]>; formatField?: (field: Field, value: Value) => Value; readonly?: boolean; };

// Props for the DynamicField component
export type DynamicFieldProps = {
	schema: ModeViewSchema | GridViewSchema; // Schema context (can be Form, Wizard step, or Grid)
	field: Field & { name: string }; // Field definition including its key name
	modelValue: Value; // Current value (for v-model)
	label: string; // Field label
	modeType?: "insert" | "select" | "update"; // Current mode (influences behavior/read-only state)
	isInput?: boolean; // Explicitly control if it should be an input or static text
	// allowToggle?: boolean; // Removed, handled by parent logic (e.g., inline edit)
	disabled?: boolean; // Explicitly disable the field
};

// Props for the FormData component
export type FormDataProps = {
	schema: ModeViewSchema; // Expects FormView or WizardStep schema
	mode: "insert" | "select" | "update"; // Current operational mode
	formData: Dict; // The reactive form data object (managed by useForm)
	recordId?: Dict | null; // Current record's primary key (for update/select)
	tableName: string; // Table name for API calls
	isInput: boolean; // Usually true for FormData, controls underlying DynamicFields
	disabledAll?: boolean;
	// isWizard?: boolean; // Removed, schema type implies this
};

// Props for GridCrud component
export type GridCrudProps = {
	tableName: string;
	schema?: GridViewSchema; // Schema for title, icon etc.
	title?: string; // Optional override title
	defaultIcon?: string; // Optional override icon
	showSearch?: boolean; // Show search input?
	modelValue?: string; // v-model for search query
	showHead: boolean; // Show the header card?
};

// Props for GridData component
export type GridDataProps = {
	tableName: string;
	schema: GridViewSchema; // Grid schema is required
	searchQuery?: string; // External search query (optional)
	// Removed title, defaultIcon, showSearch as they belong in GridCrud
};

// Props for FormMode component
export type FormModeProps = {
	isWizard: boolean; // Is this part of a wizard?
	mode: string; // Current mode ('insert', 'select', 'update')
	schema: ModeViewSchema; // Form or Wizard schema
	isSearching?: boolean; // Loading state for search button
	title: string; // Title to display
	defaultIcon: string; // Icon to display
	showHead: boolean; // Render the header?
};

// Props for TableView/CardView components
export type GridViewTemplateProps = {
	schema: GridViewSchema;
	tableName: string;
	showHead: boolean; // Show the GridCrud header?
	// Data is handled internally by GridData
};

// Props for FormView component
export type FormViewProps = {
	schema: ModeViewSchema; // Form or Wizard schema
	defaultMode?: "insert" | "select" | "update";
	recordId?: Dict | null; // Initial record ID
	showHead: boolean; // Show the FormMode header?
	tableName: string; // Target table
	// isWizard is implicitly handled by schema type/context
};

// Props for WizardView component
export type WizardViewProps = {
	schema: WizardViewSchema;
	showHead: boolean; // Show headers within each step's FormMode?
	// tableName is derived from schema.entity or step.entity
};
