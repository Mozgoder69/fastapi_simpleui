<!-- frontend/src/ui/templates/WizardView.vue -->

<template>
<div class="wizard-wrapper">
  <v-stepper
    v-model="activeStepIndex"
    :items="stepItems"
    color="primary"
    editable
  >
    <!-- your step content -->
    <div
      v-for="(step, idx) in steps"
      :key="step.step"
      v-show="activeStepIndex === idx + 1 && isStepSchemaValid(step.step)"
      class="wizard-step-container"
    >
      <FormMode
        :schema="getStep(idx + 1)"
        :isWizard="true"
        :mode="wizardData[step.step].mode"
        :isSearching="isStepSearching[step.step] || false"
        :title="step.title"
        :defaultIcon="step.icon"
        :showHead="showHead"
        @update:mode="m => onModeChange(step.step, m)"
        @search="() => onSearch(step.step)"
      />
      <FormData
        :schema="getStep(idx + 1)"
        :mode="wizardData[step.step].mode"
        :formData="wizardData[step.step].data"
        :isInput="true"
        @update="d => onFormDataChange(step.step, d)"
      />
    </div>

    <!-- bottom-of-wizard “Submit” button (only on last step) -->
    <v-row
      v-if="activeStepIndex === steps.length"
      class="mt-6"
      justify="end"
    >
  <!-- абсолютный хак: поверх правого нижнего угла степпера -->
  <v-btn
    v-if="activeStepIndex === steps.length"
    color="primary"
    class="submit-overlay"
    @click="onSubmitWizard"
  >
    Submit
  </v-btn>
    </v-row>
  </v-stepper>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import * as yup from "yup";

import FormData from "@/ui/organisms/FormData.vue";
import FormMode from "@/ui/organisms/FormMode.vue";

import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { api } from "@/core/services/api";
import type {
	Dict,
	StepSchema,
	WizardData,
	WizardViewSchema,
} from "@/core/types";
import { initFormData, initStepData } from "@/core/utils/dataUtils";
import {
	extractPrimaryKeys,
	extractProperties,
} from "@/core/utils/schemaUtils";

interface Props {
	schema: WizardViewSchema;
	showHead: boolean;
}
const props = defineProps<Props>();

const router = useRouter();
const toast = useToast();

// 1. steps & nav items
const steps = computed(() => props.schema.steps || []);
const stepItems = computed(() =>
	steps.value.map((s, i) => ({
		title: s.title,
		value: i + 1,
		complete: wizardData[s.step]?.__completed === true,
	})),
);

// 2. wizard state
const activeStepIndex = ref(1);
const wizardData = reactive<WizardData>({});
const isStepSearching = reactive<Record<number, boolean>>({});

// 3. Helpers
const getStep = (index: number): StepSchema => {
	// index is 1-based
	return steps.value[index - 1];
};

const initializeWizardData = () => {
	for (const s of steps.value) {
		if (!wizardData[s.step]) {
			wizardData[s.step] = {
				mode: "insert",
				data: initFormData(
					getStep(steps.value.indexOf(s) + 1).modes[0].properties,
				),
				recordId: null,
				__completed: false,
			};
		}
	}
};
watch(() => props.schema, initializeWizardData, {
	immediate: true,
	deep: true,
});

const isStepSchemaValid = (stepNumber: number): boolean => {
	const schema = steps.value.find((s) => s.step === stepNumber);
	const propsMode = extractProperties(schema, wizardData[stepNumber].mode);
	return Object.keys(propsMode).length > 0;
};

// 4. Mode switch / data update / search
const onModeChange = (step: number, mode: "insert" | "select") => {
	wizardData[step].mode = mode;
	if (mode === "insert") {
		wizardData[step].data = initFormData(
			extractProperties(
				steps.value.find((s) => s.step === step),
				mode,
			),
		);
		wizardData[step].recordId = null;
		wizardData[step].__completed = false;
	}
};

const onFormDataChange = (step: number, data: Dict) => {
	wizardData[step].data = { ...data };
};

const onSearch = useErrorHandler(async (step: number) => {
	if (wizardData[step].mode !== "select" || isStepSearching[step]) return;

	const schema = steps.value.find((s) => s.step === step);
	const pks = extractPrimaryKeys(schema);
	const keys: Dict = {};
	const allFilled = pks.every((pk) => {
		const v = wizardData[step].data[pk];
		if (v != null && v !== "") {
			keys[pk] = v;
			return true;
		}
		return false;
	});
	if (!allFilled) {
		return toast.warning("Fill all primary key fields for search.");
	}

	isStepSearching[step] = true;
	try {
		const rec = await api.readOne(schema.entity, keys);
		if (rec?.keys) {
			wizardData[step].data = { ...rec.keys, ...(rec.data || {}) };
			wizardData[step].__completed = true;
			toast.success("Record loaded.");
		} else {
			wizardData[step].__completed = false;
			toast.info("Not found.");
		}
	} finally {
		isStepSearching[step] = false;
	}
}, "Wizard Step Search");

// 5. Per‐step validation
const validateStepData = async (step: number): Promise<boolean> => {
	const schema = steps.value.find((s) => s.step === step);
	const mode = wizardData[step].mode;
	const propsForMode = extractProperties(schema, mode);
	const data = wizardData[step].data;
	const shape: Record<string, yup.AnySchema> = {};

	for (const [key, field] of Object.entries(propsForMode)) {
		if (!field) continue;
		let v: yup.AnySchema = yup.mixed();
		if (field.type === "string") v = yup.string();
		if (["number", "integer"].includes(field.type)) v = yup.number();
		if (field.type === "boolean") v = yup.boolean();
		if (field.required) v = v.required(`${field.label || key} is required`);
		else v = v.nullable();
		shape[key] = v;
	}

	try {
		await yup.object().shape(shape).validate(data, { abortEarly: false });
		return true;
	} catch (err) {
		toast.error(`Step ${step} validation failed: ${err.errors.join(", ")}`);
		return false;
	}
};

interface WizardStepRequest {
	entity: string;
	mode: "insert" | "select";
	data: Dict;
	recordId: Dict | null;
}

const onSubmitWizard = async () => {
	const stepsPayload: WizardStepRequest[] = steps.value.map((s) => ({
		entity: s.entity,
		mode: wizardData[s.step].mode,
		data: wizardData[s.step].data,
		recordId: wizardData[s.step].recordId,
	}));

	try {
		await api.createWizard(props.schema.entity, stepsPayload);
		toast.success("Успешно!");
		router.push("/");
	} catch (err) {
		toast.error(`Ошибка: ${err.message}`);
	}
};
</script>

<style>
.wizard-wrapper {
  position: relative;
}
.submit-overlay {
  position: absolute;
  bottom: 20px; /* поднимите/опустите по вкусу */
  right: 20px; /* сместите влево, чтобы оказаться над Next */
}
</style>

<!-- frontend/src/ui/templates/WizardView.vue -->

<!-- <template>
<v-stepper v-model="activeStepIndex" :items="stepItems" color="primary" editable>
<div v-for="(step, index) in steps" :key="step.step" v-show="activeStepIndex === index + 1 && isStepSchemaValid(step.step)" class="wizard-step-container">
<FormMode :schema="getSchemaForStep(step.step)" :isWizard="true" :mode="wizardData[step.step]?.mode || 'insert'" :isSearching="isStepSearching[step.step] || false" :title="getSchemaForStep(step.step)?.title ?? 'Untitled Step'" :defaultIcon="step.icon" :showHead="showHead" @update:mode="newMode => onModeChange(step.step, newMode)" @search="() => onSearch(step.step)" />
<FormData :key="`${step.step}-${wizardData[step.step]?.mode || 'insert'}`" :schema="getSchemaForStep(step.step)" :mode="wizardData[step.step]?.mode || 'insert'" :recordId="wizardData[step.step]?.recordId" :tableName="getSchemaForStep(step.step).entity" :formData="wizardData[step.step]?.data" :isInput="true" />
</div>
</v-stepper>
</template>

<script setup lang="ts">
import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { api } from "@/core/services/api";
import type {
	Dict,
	ModeSchema,
	StepSchema,
	WizardData,
	WizardViewSchema,
} from "@/core/types";
import {
	initFormData,
	initStepData,
	parseDefaultValue,
} from "@/core/utils/dataUtils";
import {
	extractPrimaryKeys,
	extractProperties,
} from "@/core/utils/schemaUtils";
import FormData from "@/ui/organisms/FormData.vue";
import FormMode from "@/ui/organisms/FormMode.vue";
import { computed, reactive, ref, watch } from "vue";
import type { Ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import * as yup from "yup";
interface Props {
	schema: WizardViewSchema;
	showHead: boolean;
}
const props = defineProps<Props>();
const router = useRouter();
const toast = useToast();
const steps = computed(() => props.schema?.steps || []);
const activeStepIndex = ref(1);
const wizardData = reactive<WizardData>({});
const isStepSaving = reactive<Record<number, boolean>>({});
const isStepSearching = reactive<Record<number, boolean>>({});
const getSchemaForStep = (stepNumber: number): StepSchema => {
	const step = steps.value.find((s) => s.step === stepNumber);
	if (!step) {
		return {
			step: stepNumber,
			entity: props.schema.entity,
			title: `Step ${stepNumber}`,
			icon: "mdi-alert-circle-outline",
			modes: [
				{
					mode: "insert",
					title: "Insert",
					properties: {},
				},
			],
		};
	}
	return {
		...step,
		modes: step.modes?.length
			? step.modes
			: [
					{
						mode: "insert",
						title: "Insert",
						properties: step.properties || {},
					},
				],
	};
};
const initializeWizardData = () => {
	for (const step of steps.value) {
		if (!wizardData[step.step]) {
			const stepSchema = getSchemaForStep(step.step);
			wizardData[step.step] = {
				mode: stepSchema.modes[0]?.mode || "insert",
				data: initStepData(stepSchema),
				recordId: null,
				__completed: false,
			};
		}
	}
};
const onModeChange = (stepNumber: number, newMode: "insert" | "select") => {
	if (!wizardData[stepNumber]) return;
	const stepSchema = getSchemaForStep(stepNumber);
	const modeSchema =
		stepSchema.modes.find((m) => m.mode === newMode) || stepSchema.modes[0];
	wizardData[stepNumber].mode = newMode;
	if (newMode === "insert") {
		wizardData[stepNumber].recordId = null;
		wizardData[stepNumber].__completed = false;
		wizardData[stepNumber].data = initFormData(modeSchema.properties);
	}
};
watch(() => props.schema, initializeWizardData, {
	immediate: true,
	deep: true,
});
const isStepSchemaValid = (stepNumber: number): boolean => {
	const schema = getSchemaForStep(stepNumber);
	return (
		schema &&
		schema.modes.length > 0 &&
		(Object.keys(schema.modes[0].properties || {}).length > 0 ||
			Object.keys(schema.properties || {}).length > 0)
	);
};
const stepItems = computed(() =>
	steps.value.map((step, idx) => ({
		title: step.title,
		value: idx + 1,
		complete: wizardData[step.step]?.__completed === true,
	})),
);
const isStepEditable = (stepValue: number): boolean => {
	const stepNumber = steps.value[stepValue - 1]?.step;
	return (
		activeStepIndex.value === stepValue ||
		wizardData[stepNumber]?.__completed === true
	);
};
const isLastStep = (index: number): boolean => index === steps.value.length - 1;
const validateStepData = async (stepNumber: number): Promise<boolean> => {
	if (!wizardData[stepNumber]) return false;
	const stepSchema = getSchemaForStep(stepNumber);
	const mode = wizardData[stepNumber].mode;
	const properties = extractProperties(stepSchema, mode);
	const dataToValidate = wizardData[stepNumber].data;
	const shape: yup.ObjectShape = {};
	for (const [key, field] of Object.entries(properties)) {
		if (!field) continue;
		let validator: yup.AnySchema = yup.mixed(); // Базовый
		if (field.type === "string") validator = yup.string();
		if (field.type === "number" || field.type === "integer")
			validator = yup.number();
		if (field.type === "boolean") validator = yup.boolean();
		if (field.required) {
			validator = validator.required(`${field.label || key} is required`);
		} else {
			validator = validator.nullable();
		}
		shape[key] = validator;
	}
	const validationSchema = yup.object().shape(shape);
	try {
		await validationSchema.validate(dataToValidate, { abortEarly: false });
		return true;
	} catch (err) {
		toast.error(
			`Validation failed for Step ${stepNumber}: ${err.errors.join(", ")}`,
		);
		return false;
	}
};
const onFormDataChange = (stepNumber: number, newData: Dict) => {
	if (wizardData[stepNumber]) wizardData[stepNumber].data = { ...newData };
};
const onFormDataSubmitted = (stepNumber: number, submittedData: Dict) => {
	if (!wizardData[stepNumber]) return;
	const stepSchema = getSchemaForStep(stepNumber);
	const primaryKeys = extractPrimaryKeys(stepSchema);
	const pkObj: Dict = {};
	for (const pk of primaryKeys) {
		if (submittedData[pk] !== undefined) {
			pkObj[pk] = submittedData[pk];
		}
	}
	wizardData[stepNumber].recordId =
		Object.keys(pkObj).length > 0 ? pkObj : null;
	wizardData[stepNumber].data = submittedData;
	wizardData[stepNumber].__completed = true;
	toast.success(`Step ${stepNumber} completed.`);
	goToNextStep();
};
const onSearch = useErrorHandler(async (stepNumber: number) => {
	if (
		!wizardData[stepNumber] ||
		wizardData[stepNumber].mode !== "select" ||
		isStepSearching[stepNumber]
	)
		return;
	const stepSchema = getSchemaForStep(stepNumber);
	const primaryKeys = extractPrimaryKeys(stepSchema);
	const searchKeys: Dict = {};
	const allKeysProvided = primaryKeys.every((pk) => {
		const value = wizardData[stepNumber].data[pk];
		if (value !== undefined && value !== null && value !== "") {
			searchKeys[pk] = value;
			return true;
		}
		return false;
	});
	if (!allKeysProvided) {
		return toast.warning("Please fill in all primary key fields for search.");
	}
	isStepSearching[stepNumber] = true;
	try {
		const record = await api.readOne(stepSchema.entity, searchKeys);
		if (record?.keys) {
			wizardData[stepNumber].recordId = { ...record.keys };
			wizardData[stepNumber].data = initFormData(
				extractProperties(stepSchema, "select"),
				{ ...(record.keys || {}), ...(record.data || {}) },
			);
			wizardData[stepNumber].__completed = true;
			toast.success("Record found and loaded.");
			goToNextStep();
		} else {
			toast.info("Record with these keys not found.");
			wizardData[stepNumber].recordId = null;
			wizardData[stepNumber].__completed = false;
		}
	} catch (error) {
		console.error("Wizard Search Error:", error);
		wizardData[stepNumber].recordId = null;
		wizardData[stepNumber].__completed = false;
	} finally {
		isStepSearching[stepNumber] = false;
	}
}, "Wizard Step Search");
const goToNextStep = () => {
	if (activeStepIndex.value < steps.value.length) {
		activeStepIndex.value++;
	} else {
		handleFinish();
	}
};
const handleFinish = useErrorHandler(async () => {
	if (!steps.value.every((step) => wizardData[step.step]?.__completed)) {
		toast.warning("Please complete all steps before finishing.");
		const firstIncompleteStepIndex = steps.value.findIndex(
			(step) => !wizardData[step.step]?.__completed,
		);
		if (firstIncompleteStepIndex !== -1)
			activeStepIndex.value = firstIncompleteStepIndex + 1;
		return;
	}
	toast.success("Wizard completed successfully!");
	router.push("/");
}, "Wizard Submission");
</script> -->