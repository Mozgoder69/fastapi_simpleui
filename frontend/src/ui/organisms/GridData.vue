<!-- frontend/src/ui/templates/GridData.vue -->

<template>
<v-card>
<slot name="content" v-bind="{ filteredRecords, searchQuery, primaryKeys, formatField, handleAction, selectedCount, isIndeterminate, selectAllState, handleSelectAll, isSelected, toggleItemSelection, isEditing, getItemKey, toggleEdit, updateField, saveRecord, requestDeleteItem }" >
<v-alert type="info" variant="tonal">No content provided.</v-alert>
</slot>
<ModalDialog :tableName="tableName" :schema="schema" :fetchRecords="fetchRecords" ref="dialog" />
</v-card>
</template>

<script setup lang="ts">
import { useGrid } from "@/core/hooks/data/useGrid";
import { useInlineEdit } from "@/core/hooks/ui/useInlineEdit";
import { useSelectionStore } from "@/core/hooks/ui/useSelectionStore";
import type { Dict, GridViewSchema } from "@/core/types";
import { formatField } from "@/core/utils/fieldMapping";
import ModalDialog from "@/ui/molecules/ModalDialog.vue";
import { computed, ref, watch } from "vue";
import { useToast } from "vue-toastification";
interface Props {
	tableName: string;
	schema: GridViewSchema;
	searchQuery?: string;
	filters?: Dict;
}
const props = defineProps<Props>();
const toast = useToast();
const dialog = ref(null);
const {
	fetchRecords,
	searchQuery,
	filteredRecords,
	primaryKeys,
	getRecordKey,
} = useGrid(
	props.tableName,
	props.schema,
	props.searchQuery ? ref(props.searchQuery) : undefined,
	props.filters || {},
);
const {
	isEditing,
	getItemKey,
	toggleEdit,
	updateField,
	saveRecord: saveRecordBase,
} = useInlineEdit(props.tableName, primaryKeys);
const saveRecord = async (item: Dict) => {
	const ok = await saveRecordBase(item);
	if (ok) await fetchRecords();
	return ok;
};
const requestDeleteItem = (item: Dict) => dialog.value.confirmDelete([item]);
const sel = useSelectionStore();
watch(
	() => props.tableName,
	(t) => t && sel.ensureTableExists(t),
	{ immediate: true },
);
const selectedCount = computed(() => sel.selectedCount(props.tableName));
const selectedItems = computed(() =>
	filteredRecords.value.filter((r) =>
		sel.isSelected(props.tableName, r, primaryKeys.value),
	),
);
const isIndeterminate = computed(
	() =>
		sel.selectedCount(props.tableName) > 0 &&
		sel.selectedCount(props.tableName) < filteredRecords.value.length,
);
const selectAllState = ref(false);
const handleSelectAll = (checked: boolean) => {
	selectAllState.value = checked;
	if (checked) {
		sel.selectAllItems(props.tableName, filteredRecords.value);
	} else {
		sel.deselectAllItems(props.tableName);
	}
};
const isSelected = (item: Dict) =>
	sel.isSelected(props.tableName, item, primaryKeys.value);
const toggleItemSelection = (item: Dict) =>
	sel.toggleItemSelection(props.tableName, item, primaryKeys.value);
const handleAction = async (actionName: string, item?: Dict) => {
	switch (actionName) {
		case "newOne":
			dialog.value.openCreateDialog();
			break;
		case "trimMany":
			if (selectedItems.value.length) {
				dialog.value.confirmDelete(selectedItems.value);
			} else {
				toast.info("Выберите одну или несколько записей для удаления.");
			}
			break;
		case "updMany":
			if (selectedItems.value.length) {
				selectedItems.value.forEach(toggleEdit);
			} else {
				toast.info("Выберите одну или несколько записей для редактирования.");
			}
			break;
		case "saveAll":
			for (const rec of filteredRecords.value) {
				if (isEditing.value[getItemKey(rec)]) {
					await saveRecord(rec);
				}
			}
			break;
		case "cancelAll":
			for (const rec of filteredRecords.value) {
				if (isEditing.value[getItemKey(rec)]) {
					toggleEdit(rec);
				}
			}
			break;
	}
};
const hasActiveEdits = computed(() =>
	Object.values(isEditing.value).some((v) => v),
);
defineExpose({
	fetchRecords,
	handleAction,
	hasActiveEdits,
});
</script>