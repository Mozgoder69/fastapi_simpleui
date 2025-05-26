<!-- frontend/src/ui/organisms/GridCrud.vue -->

<template>
<v-card v-if="showHead" class="mb-4">
<v-toolbar flat>
<ViewJSONButton v-if="schema" :schema="schema" />
<v-toolbar-title v-if="title">
<span v-if="schema" class="material-symbols-outlined mr-2" >{{ schema.icon }}</span>
 {{ title }}
</v-toolbar-title>
<slot name="toolbar-actions" />
<v-text-field v-if="showSearch" v-model="internalSearchQuery" label="Search" prepend-icon="mdi-magnify" single-line hide-details class="mx-4" style="max-width: 300px" />
</v-toolbar>
<v-card-text>
<v-btn v-for="action in actions" :key="action.name" :color="action.color" :disabled="!action.isEnabled" @click="handleAction(action.name)" class="mr-2" >
<v-icon left>{{ action.icon }}</v-icon>
 {{ action.label }}
</v-btn>
</v-card-text>
</v-card>
</template>

<script setup lang="ts">
import { useSelectionStore } from "@/core/hooks/ui/useSelectionStore";
import type { Action, GridViewSchema } from "@/core/types";
import ViewJSONButton from "@/ui/atoms/ViewJSONButton.vue";
import { computed, ref, watch } from "vue";
interface Props {
	tableName: string;
	schema?: GridViewSchema;
	title?: string;
	defaultIcon?: string;
	showSearch?: boolean;
	modelValue?: string;
	showHead: boolean;
	hasEditing?: boolean;
}
const props = defineProps<Props>();
const emit = defineEmits<{
	(e: "action-clicked", name: string): void;
	(e: "update:modelValue", value: string): void;
}>();
const selectionStore = useSelectionStore();
const selectedCount = computed(() =>
	selectionStore.selectedCount(props.tableName),
);
const internalSearchQuery = ref(props.modelValue);
watch(internalSearchQuery, (newVal) => emit("update:modelValue", newVal));
const handleAction = (actionName: string) => emit("action-clicked", actionName);
const actions = computed<Action[]>(() => {
	let result = [];
	if (props.hasEditing) {
		result = [
			{
				name: "saveAll",
				label: "Save All",
				isEnabled: true,
				color: "pass",
				icon: "mdi-content-save",
			},
			{
				name: "cancelAll",
				label: "Cancel All",
				isEnabled: true,
				color: "grey",
				icon: "mdi-close",
			},
		];
	} else {
		result = [
			{
				name: "newOne",
				label: "Insert One",
				isEnabled: true,
				color: "info",
				icon: "mdi-plus",
			},
			{
				name: "updMany",
				label: "Update Many",
				isEnabled: selectedCount.value > 0,
				color: "warn",
				icon: "mdi-pencil-circle",
			},
			{
				name: "trimMany",
				label: "Delete Many",
				isEnabled: selectedCount.value > 0,
				color: "fail",
				icon: "mdi-delete-circle",
			},
		];
	}
	return result;
});
</script>