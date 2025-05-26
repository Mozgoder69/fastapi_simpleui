<!-- frontend/src/ui/molecules/TableSelector.vue -->

<template>
<v-select v-if="tables" v-model="selectedTable" :items="tables" label="Select a Table" outlined />
<v-progress-circular v-else indeterminate/>
</template>

<script setup lang="ts">
import { useSchemas } from "@/core/hooks/data/useSchemas";
import { computed, onMounted, ref, watch } from "vue";
const emit = defineEmits(["table-selected"]);
const { getTables } = useSchemas();
const tablesData = ref<string[]>([]);
onMounted(async () => {
	tablesData.value = await getTables();
});
const tables = computed(() => tablesData.value);
const selectedTable = ref("");
watch(
	() => selectedTable.value,
	(newValue) => {
		emit("table-selected", newValue);
	},
);
</script>