<!-- frontend/src/ui/pages/APITestPage.vue -->

<template>
<v-container>
<v-row>
<v-col cols="12">
<TableSelector @table-selected="onTableSelect" />
</v-col>
</v-row>
<v-row v-if="selectedTable">
<v-col cols="12">
<ViewSelector :tableName="selectedTable" @change-view="setSchemaView" />
</v-col>
</v-row>
<v-row v-if="selectedTable && schemaView && viewComponent">
<v-col cols="12">
<component :is="viewComponent" :key="dataDisplayKey" :tableName="selectedTable" :schema="currentSchema" :showHead="true" />
</v-col>
</v-row>
<v-row v-else-if="selectedTable && schemaView">
<v-col cols="12"><v-progress-circular indeterminate/> Loading View...</v-col>
</v-row>
</v-container>
</template>

<script setup lang="ts">
import { useSchemas } from "@/core/hooks/data/useSchemas";
import { useViewLoader } from "@/core/hooks/ui/useViewLoader";
import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import type { Dict, JsonSchema } from "@/core/types";
import TableSelector from "@/ui/molecules/TableSelector.vue";
import ViewSelector from "@/ui/molecules/ViewSelector.vue";
import { ref, shallowRef, watch } from "vue";
import { useToast } from "vue-toastification";
const toast = useToast();
const { getSchemaView } = useSchemas();
const { loadView } = useViewLoader();
const selectedTable = ref<string>("");
const schemaView = ref<string>("");
const dataDisplayKey = ref<number>(0);
const currentSchema = shallowRef<JsonSchema | null>(null);
const viewComponent = shallowRef(null);
const dataDisplayRef = ref(null);
const loadSchemaAndComponent = useErrorHandler(async () => {
	if (!selectedTable.value || !schemaView.value) {
		currentSchema.value = null;
		viewComponent.value = null;
		return;
	}
	try {
		currentSchema.value = await getSchemaView(
			selectedTable.value,
			schemaView.value,
		);
		viewComponent.value = await loadView(schemaView.value);
	} catch (error) {
		toast.error(
			`Ошибка загрузки представления ${schemaView.value}: ${error.message}`,
		);
		currentSchema.value = null;
		viewComponent.value = null;
	}
}, "Load Schema & View");
async function onTableSelect(table: string) {
	selectedTable.value = table;
	if (
		schemaView.value !== "" &&
		currentSchema.value !== null &&
		viewComponent.value !== null
	)
		await loadSchemaAndComponent();
	dataDisplayKey.value += 1;
}
async function setSchemaView(view: string) {
	schemaView.value = view;
	viewComponent.value = null;
	currentSchema.value = null; // Также очистим схему
	await loadSchemaAndComponent();
	dataDisplayKey.value += 1;
}
watch(selectedTable, (newTable) => {
	if (!newTable) {
		currentSchema.value = null;
	}
});
</script>