<!-- frontend/src/ui/molecules/DynamicField.vue -->

<template>
<div>
<v-row align="center">
<v-col v-if="localIsInput" cols="auto">
<v-icon color="grey">{{ fieldIcon }}</v-icon>
</v-col>
<v-col>
<component v-if="localIsInput" :is="fieldComponent" v-model="modelSync" :label="fieldLabel" :schema="schema" :fieldName="field.name" v-bind="mergedProps" :disabled="!isEnabled" />
<span v-else class="static-label">{{ formattedValue }}</span>
</v-col>
</v-row>
</div>
</template>

<script setup lang="ts">
import type { DynamicFieldProps } from "@/core/types";
import { parseDefaultValue } from "@/core/utils/dataUtils";
import {
	formatField,
	getFieldComponent,
	getFieldIcon,
} from "@/core/utils/fieldMapping";
import { extractProperties } from "@/core/utils/schemaUtils";
import { computed, ref, resolveComponent, watch } from "vue";
const props = defineProps<DynamicFieldProps>();
const emit = defineEmits(["update:modelValue", "edit-mode-changed"]);
const localIsInput = ref(props.isInput ?? false);
watch(
	() => props.isInput,
	(newValue) => {
		localIsInput.value = newValue ?? false;
	},
);
const modelSync = computed({
	get: () => {
		const value = props.modelValue ?? parseDefaultValue(props.field);
		return value === undefined ? null : value;
	},
	set: (newValue) => {
		emit("update:modelValue", newValue === undefined ? null : newValue);
	},
});
const fieldComponent = computed(() => {
	const hintComponent = props.field.uiHints?.component;
	if (typeof hintComponent === "object" && hintComponent !== null) {
		return hintComponent;
	}
	const defaultComponent = getFieldComponent(props.field);
	if (typeof defaultComponent === "string") {
		return defaultComponent;
	}
	return defaultComponent;
});
const fieldIcon = computed(() => {
	return props.field.uiHints?.icon || getFieldIcon(props.field);
});
const fieldLabel = computed(() => {
	return props.field.uiHints?.label || props.field.label || props.field.name;
});
const fieldProperties = computed(
	() =>
		extractProperties(props.schema, props.modeType || "insert")[
			props.field.name
		] || {},
);
const isEnabled = computed(() => fieldProperties.value.is_enabled !== false);
const formattedValue = computed(() =>
	formatField(props.field, props.modelValue),
);
const enumItems = computed(
	() =>
		fieldProperties.value.enum?.map((item) => ({
			value: item,
			label:
				String(item).charAt(0).toUpperCase() +
				String(item).slice(1).replace(/_/g, " "),
		})) || [],
);
const mergedProps = computed(() => {
	const commonProps = {
		clearable: true,
		hint: props.field.hint,
		"persistent-hint": !!props.field.hint,
		multiple: props.field.multiple,
	};
	if (
		fieldProperties.value.enum ||
		props.field.foreign_keys ||
		props.field.primary_key
	) {
		if (fieldComponent.value === "v-select" && enumItems.value.length > 0) {
			Object.assign(commonProps, {
				items: enumItems.value,
				"item-title": "label",
				"item-value": "value",
			});
		}
	}
	const { type, format } = props.field;
	if (type === "number" || type === "integer") {
		Object.assign(commonProps, {
			type: "number",
			step: type === "integer" ? "1" : "any",
		});
	} else if (format === "date") commonProps.type = "date";
	else if (format === "time") commonProps.type = "time";
	else if (format === "date-time") commonProps.type = "datetime-local";
	return commonProps;
});
</script>