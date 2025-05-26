
<!-- frontend/src/ui/templates/CardView.vue -->
<template>
<GridCrud :tableName="tableName" :schema="schema" :title="schema.title || tableName" :defaultIcon="schema.icon" :showSearch="true" v-model="searchQuery" :showHead="showHead" :hasEditing="hasEditing" @action-clicked="handleAction" />
<GridData ref="gridDataRef" :tableName="tableName" :schema="schema" :searchQuery="searchQuery" :filters="filters">
<template #content="{ filteredRecords, primaryKeys, isSelected, toggleItemSelection, isEditing, getItemKey, toggleEdit, updateField, saveRecord, requestDeleteItem }">
<div v-if="schema && schema.properties">
<v-row v-if="filteredRecords.length">
<v-col v-for="item in filteredRecords" :key="getItemKey(item)" cols="12" sm="6" md="4" lg="3" >
<v-card elevation="2" class="mb-4 card-with-icon" :class="{ 'item-selected': isSelected(item) }" >
<!-- 1: чекбокс и кнопки -->
<v-card-title class="d-flex justify-space-between align-center py-2">
<v-checkbox-btn :model-value="isSelected(item)" @update:model-value="() => toggleItemSelection(item)"
 />
<ItemActions :is-editing="isEditing[getItemKey(item)] || false" :item="item" :table-name="tableName" :primary-keys="primaryKeys" @toggle-edit="toggleEdit(item)" @save="saveRecord(item)" @delete="requestDeleteItem(item)" />
</v-card-title>
<!-- 2: центрированная большая иконка через span -->
<v-card-text class="icon-container">
<span class="material-symbols-outlined icon-span">
 {{ schema.icon || 'mdi-card-text' }}
</span>
</v-card-text>
<v-card-text>
<v-list>
<v-list-item v-for="(field, key) in schema.properties" :key="key" :class="{ 'item-selected': isSelected(item) }">
<v-list-item-subtitle class="d-flex align-center w-100">
<v-icon color="grey" class="mr-2" v-if="!isEditing[getItemKey(item)]">{{ getFieldIcon(field) }}</v-icon>
<span class="field-container">
<strong v-if="!isEditing[getItemKey(item)]">{{ field.label || key }}:</strong>
<DynamicField :schema="schema" :field="{ ...field, name: key }" :modelValue="item[key]" :label="field.label || key" :modeType="'update'" :isInput="isEditing[getItemKey(item)] && !primaryKeys.includes(key)" @update:modelValue="updateField(item, key, $event)" class="field-value" />
</span>
</v-list-item-subtitle>
</v-list-item>
</v-list>
</v-card-text>
</v-card>
</v-col>
</v-row>
<v-row v-else><v-col cols="12"><v-alert type="info" variant="tonal">Нет данных для отображения.</v-alert></v-col></v-row>
</div>
<div v-else class="text-center pa-4"><v-progress-circular indeterminate color="primary" /></div>
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
const hasEditing = computed(() => gridDataRef.value?.hasActiveEdits ?? false);
const handleAction = (actionName: string) =>
	gridDataRef.value?.handleAction(actionName);
</script>

<style scoped>
.item-selected {
  background-color: rgba(var(--v-theme-primary), 0.1);
}
.v-list {
  padding: 0;
}
.icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
}
.icon-span {
  font-size: 6rem;
  display: block;
  width: 100%;
  text-align: center;
  line-height: 1;
}
.field-container {
  display: flex;
  justify-content: space-between;
  width: 100%;
  align-items: center;
}
</style>