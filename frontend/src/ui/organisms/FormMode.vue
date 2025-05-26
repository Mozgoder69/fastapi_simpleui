<!-- frontend/src/ui/organisms/FormMode.vue -->

<template>
<div v-if="showHead" class="form-mode">
<div class="form-header d-flex align-center mb-2">
<ViewJSONButton v-if="schema" :schema="schema" />
<span v-if="schema" class="material-symbols-outlined mr-2">{{ defaultIcon }}</span>
<span class="form-title">{{ title }}</span>
</div>
<div class="form-mode-buttons d-flex align-center">
<div class="mode-buttons d-flex" style="gap: 8px">
<v-btn v-for="modeOption in modeOptions" :key="modeOption.mode" :color="mode === modeOption.mode ? 'primary' : 'grey'" @click="$emit('update:mode', modeOption.mode)">
 {{ modeOption.title || modeOption.mode }}
</v-btn>
</div>
<v-spacer />
<v-btn v-if="searchVisible" color="secondary" :loading="isSearching" @click="$emit('search')">Search</v-btn>
</div>
</div>
</template>

<script setup lang="ts">
import type { ModeViewSchema } from "@/core/types";
import ViewJSONButton from "@/ui/atoms/ViewJSONButton.vue";
import { computed } from "vue";
interface Props {
	isWizard: boolean;
	mode: string;
	schema: ModeViewSchema;
	isSearching: boolean;
	title: string;
	defaultIcon: string;
	showHead: boolean;
}
const props = defineProps<Props>();
const emit = defineEmits(["update:mode", "search"]);
const modeOptions = computed(() => props.schema?.modes || []);
const searchVisible = computed(
	() => props.mode === "select" || props.mode === "update",
);
</script>

<style scoped>
.form-mode { padding: 8px; }
.form-header { display: flex; align-items: center; }
.form-title { font-size: 1.5rem; font-weight: bold; }
</style>