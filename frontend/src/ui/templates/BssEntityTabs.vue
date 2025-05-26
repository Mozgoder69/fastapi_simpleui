<!-- frontend/src/ui/templates/BssEntityTabs.vue -->

<template>
<v-card v-if="tabNames.length">
<!-- 1) Заголовок табов -->
<v-tabs v-model="activeTab" background-color="secondary" dark grow>
<v-tab v-for="name in tabNames" :key="name" :value="name" >
<v-icon start>{{ getTabIcon(name) }}</v-icon>
 {{ getTabTitle(name) }}
</v-tab>
</v-tabs>
<!-- 2) Содержимое каждой вкладки -->
<v-window v-model="activeTab">
<v-window-item v-for="name in tabNames" :key="name" :value="name" >
<v-card flat>
<v-card-text>
<DataDisplay :key="`${name}-${JSON.stringify(groups[name])}`" :tableName="name" :schemaView="props.viewType" :filters="calculateFilters(groups[name])" :showHead="false" @record-updated="$emit('record-updated', $event)" @record-deleted="$emit('record-deleted', $event)" />
<slot name="actions" :tableName="name" :group="groups[name]" />
</v-card-text>
</v-card>
</v-window-item>
</v-window>
</v-card>
<v-alert v-else type="info" class="mt-4" variant="tonal">
 Нет связанных данных для отображения.
</v-alert>
</template>

<script setup lang="ts">
import type { Dict } from "@/core/types";
import DataDisplay from "@/ui/molecules/DataDisplay.vue";
import { computed, ref, watch } from "vue";
const props = withDefaults(
	defineProps<{
		groups: Record;
		calculateFilters: (infos) => Dict;
		viewType?: "TableView" | "CardView";
		getTabIcon?: (table: string) => string;
		getTabTitle?: (table: string) => string;
	}>(),
	{
		viewType: "TableView",
		getTabIcon: () => "mdi-link-variant",
		getTabTitle: (t: string) => t.replace(/_/g, " "),
	},
);
const tabNames = computed(() => Object.keys(props.groups));
const activeTab = ref(tabNames.value[0] || "");
watch(tabNames, (names) => {
	if (!names.includes(activeTab.value)) {
		activeTab.value = names[0] || "";
	}
});
</script>