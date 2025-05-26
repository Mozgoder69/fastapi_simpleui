<!-- frontend/src/ui/molecules/ViewSelector.vue -->

<template>
<v-select v-if="viewOptions" v-model="selectedView" :items="viewOptions" label="Select View Type" outlined />
<v-progress-circular v-else indeterminate/>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
const props = defineProps<{ tableName: string }>();
const emit = defineEmits<(e: "change-view", viewName: string) => void>();
const selectedView = ref("");
const viewOptions = ref<string[]>([
	"TableView",
	"CardView",
	"FormView",
	"WizardView",
]);
watch(
	() => selectedView.value,
	(newValue) => {
		emit("change-view", newValue);
	},
);
</script>