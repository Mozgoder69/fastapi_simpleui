<!-- frontend/src/ui/templates/BssEntityMain.vue -->

<template>
<v-card class="mb-4">
<!-- 1) Toolbar с иконкой, заголовком, чипом и кнопками -->
<v-toolbar flat color="primary" density="compact">
<v-icon class="ml-2 mr-2">{{ schema.icon || 'mdi-database' }}</v-icon>
<v-toolbar-title>{{ schema.title }}</v-toolbar-title>
<v-chip size="small" class="ml-2">ID: {{ recordIdString }}</v-chip>
<v-spacer/>
<!-- Селектор вида -->
<v-btn-toggle v-model="viewTypeLocal" mandatory class="mx-4" density="compact" >
<v-btn value="TableView" small>Таблица</v-btn>
<v-btn value="CardView" small>Карточки</v-btn>
</v-btn-toggle>
<!-- Слот для действий; по умолчанию — Edit/Delete -->
<slot name="actions">
<v-btn icon title="Edit"><v-icon>mdi-pencil</v-icon></v-btn>
<v-btn icon title="Delete"><v-icon>mdi-delete</v-icon></v-btn>
</slot>
</v-toolbar>
<!-- 2) Универсальное представление -->
<v-card-text class="pa-0">
<DataDisplay :tableName="schema.entity" :schemaView="viewTypeLocal" :filters="recordId" :showHead="false" />
</v-card-text>
</v-card>
</template>

<script setup lang="ts">
import type { Dict, JsonSchema } from "@/core/types";
import {
	formatField,
	getFieldIcon as getFieldIconUtil,
} from "@/core/utils/fieldMapping";
import DataDisplay from "@/ui/molecules/DataDisplay.vue";
import { computed, ref, watch } from "vue";
const props = withDefaults(
	defineProps<{
		schema: JsonSchema;
		recordId: Dict;
		viewType?: "TableView" | "CardView";
	}>(),
	{
		viewType: "TableView",
	},
);
const emit =
	defineEmits<(e: "update:viewType", v: "TableView" | "CardView") => void>();
// локальная копия viewType для v-model на кнопках
const viewTypeLocal = ref(props.viewType);
// если родитель передаёт новое viewType — синхронизируем
watch(
	() => props.viewType,
	(v) => {
		if (v) viewTypeLocal.value = v;
	},
);
// при изменении локального — эмитим наверх
watch(viewTypeLocal, (v) => {
	emit("update:viewType", v);
});
const recordId = props.recordId;
const recordIdString = computed(
	() =>
		Object.entries(recordId)
			.map(([k, v]) => `${k}=${v}`)
			.join("&") || "N/A",
);
function getFieldIcon(field): string {
	return field.uiHints?.icon || getFieldIconUtil(field);
}
function formatDisplayValue(field, value: unknown): string {
	if (field.uiHints?.formatter) {
		return (field.uiHints.formatter as (v: unknown) => string)(value);
	}
	return formatField(field, value);
}
</script>