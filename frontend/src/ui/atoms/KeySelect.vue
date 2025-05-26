<!-- frontend/src/ui/atoms/KeySelect.vue -->

<template>
<v-select v-model="model" :items="options" :label="label" :item-title="itemTitle" :item-value="itemValue" :item-props="getItemProps" outlined clearable >
<template #item="{ item, props: slotProps }">
<v-list-item v-bind="slotProps">
<template #prepend>
<v-chip small color="primary" class="mr-2">
 {{ fieldName }}: {{ formatKey(item[itemValue]) }}
</v-chip>
</template>
<v-list-item-title>{{ item.label }}</v-list-item-title>
</v-list-item>
</template>
<template #selection="{ item }">
<v-chip small color="primary" class="mr-2">
 {{ fieldName }}: {{ formatKey(item[itemValue]) }}
</v-chip>
 {{ item.label }}
</template>
</v-select>
</template>

<script setup lang="ts">
import type { Value } from "@/core/types";
import { computed } from "vue";
const props = withDefaults(
	defineProps<{
		modelValue?: Value;
		options: Array<{ value: Value; label: string }>;
		label?: string;
		itemTitle?: string;
		itemValue?: string;
		tableName?: string;
		fieldName?: string;
	}>(),
	{
		modelValue: null,
		options: () => [],
		label: "",
		itemTitle: "label",
		itemValue: "value",
		tableName: "",
		fieldName: "",
	},
);
const emit = defineEmits<(e: "update:modelValue", v: Value) => void>();
const model = computed({
	get: () => props.modelValue,
	set: (v) => emit("update:modelValue", v),
});
const options = computed(() => props.options);
const label = computed(() => props.label);
const itemTitle = computed(() => props.itemTitle);
const itemValue = computed(() => props.itemValue);
const fieldName = computed(() => props.fieldName);
const formatKey = (value: Value): string =>
	typeof value === "object" ? Object.values(value).join(" - ") : String(value);
const getItemProps = (item) => {
	const id = [
		props.tableName,
		props.fieldName,
		formatKey(item[props.itemValue]),
	]
		.filter(Boolean)
		.join("::");
	return { id };
};
</script>
<style scoped>
.v-chip {
  font-weight: 500;
}
</style>