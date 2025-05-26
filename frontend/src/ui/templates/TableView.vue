<!-- frontend/src/ui/templates/TableView.vue -->

<template>
<GridCrud :tableName="tableName" :schema="schema" :title="schema.title || tableName" :defaultIcon="schema.icon" :showSearch="true" v-model="searchQuery" :showHead="showHead" :hasEditing="hasEditing" @action-clicked="handleAction" />
<GridData ref="gridDataRef" :tableName="tableName" :schema="schema" :searchQuery="searchQuery" :filters="filters">
<template #content="{ filteredRecords, primaryKeys, isSelected, toggleItemSelection, selectedCount, isIndeterminate, selectAllState, handleSelectAll, isEditing, getItemKey, toggleEdit, updateField, saveRecord, requestDeleteItem }">
<v-data-table v-if="dynamicHeaders && dynamicHeaders.length > 0 && filteredRecords.length"
 :headers="dynamicHeaders"
 :items="filteredRecords"
 :search="searchQuery.value"
 :items-per-page="itemsPerPage"
 :item-key="getItemKey"
 class="elevation-1"
 >
<template #headers="{ columns }">
<tr>
<th style="width: 1%;">
<v-checkbox-btn :model-value="selectAllState" :indeterminate="isIndeterminate" @update:model-value="handleSelectAll" />
</th>
<th v-for="header in columns.filter(c => c.key !== 'actions')" :key="header.key">
<v-icon v-if="header.icon" :icon="header.icon" color="grey" class="mr-1" />
 {{ header.title }}
</th>
<th>Actions</th>
</tr>
</template>
<template #item="{ item }">
<tr :class="{ 'item-selected': isSelected(item) }">
<td><v-checkbox-btn :model-value="isSelected(item)" @update:model-value="() => toggleItemSelection(item)" /></td>
<td v-for="header in headers" :key="header.key">
<DynamicField :schema="schema" :field="{ ...schema.properties[header.key], name: header.key }" :modelValue="item[header.key]" :label="header.title" :modeType="'update'" :isInput="isEditing[getItemKey(item)] && !primaryKeys.includes(header.key)" @update:modelValue="updateField(item, header.key, $event)" />
</td>
<td><ItemActions :is-editing="isEditing[getItemKey(item)] || false" :item="item" :table-name="tableName" :primary-keys="primaryKeys" @toggle-edit="toggleEdit(item)" @save="saveRecord(item)" @delete="requestDeleteItem(item)" /></td>
</tr>
</template>
<template #no-data><v-alert type="info" variant="tonal">Нет данных для отображения.</v-alert></template>
</v-data-table>
<v-alert v-else type="info" variant="tonal" class="ma-4">Нет данных или схема пуста.</v-alert>
</template>
</GridData>
</template>

<script setup lang="ts">
import type { Dict, GridViewSchema } from "@/core/types";
import { getFieldIcon } from "@/core/utils/fieldMapping";
import DynamicField from "@/ui/molecules/DynamicField.vue";
import ItemActions from "@/ui/molecules/ItemActions.vue";
import GridCrud from "@/ui/organisms/GridCrud.vue";
import GridData from "@/ui/organisms/GridData.vue";
import { computed, ref } from "vue";
interface Props {
	schema: GridViewSchema;
	tableName: string;
	showHead: boolean;
	filters?: Dict;
}
const props = defineProps<Props>();
const gridDataRef = ref(null);
const searchQuery = ref("");
const itemsPerPage = 10;
const headers = computed(() =>
	Object.entries(props.schema.properties).map(([key, field]) => ({
		title: field.label || key,
		key,
		icon: getFieldIcon(field),
		sortable: true,
	})),
);
const dynamicHeaders = computed(() => [
	...headers.value,
	{ key: "actions", title: "Actions", sortable: false, align: "end" },
]);
const hasEditing = computed(() => gridDataRef.value?.hasActiveEdits ?? false);
const handleAction = (actionName: string) =>
	gridDataRef.value?.handleAction(actionName);
</script>

<style scoped>
.item-selected { background-color: rgba(var(--v-theme-primary), 0.1); }
</style>