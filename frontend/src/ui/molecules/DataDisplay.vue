<!-- frontend/src/ui/molecules/DataDisplay.vue -->

<template>
<component v-if="viewComponent && effectiveSchema && !isLoading" :is="viewComponent" :schema="effectiveSchema" :tableName="tableName" :filters="props.filters" :showHead="showHead" />
<v-progress-circular v-else indeterminate/>
</template>

<script setup lang="ts">
import { useSchemas } from "@/core/hooks/data/useSchemas";
import { useViewLoader } from "@/core/hooks/ui/useViewLoader";
import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import type { Dict, JsonSchema } from "@/core/types";
import { computed, markRaw, ref, shallowRef, watch } from "vue";
import { useToast } from "vue-toastification";
interface Props {
	tableName: string;
	schemaView: string;
	refreshKey?: number;
	showHead?: boolean;
	filters?: Dict;
	schemaOverride?: JsonSchema | null;
}
const props = withDefaults(defineProps<Props>(), {
	showHead: true,
	filters: () => ({}),
	refreshKey: 0,
	schemaOverride: null,
});
const emit = defineEmits(["record-updated", "record-deleted"]);
const toast = useToast();
const { getSchemaView } = useSchemas();
const { loadView } = useViewLoader();
const loadedSchema = ref<JsonSchema | null>(null);
const schemaError = ref<string | null>(null);
const viewComponent = shallowRef<unknown>(null);
const viewError = ref<string | null>(null);
const isSchemaLoading = ref(false);
const isViewLoading = ref(false);
const effectiveSchema = computed<JsonSchema | null>(() => {
	return props.schemaOverride ?? loadedSchema.value;
});
const isLoading = computed(() => isSchemaLoading.value || isViewLoading.value);
const errorMessage = computed(
	() => schemaError.value || viewError.value || null,
);
async function augmentSchemaWithHints(
	baseSchema: JsonSchema | null,
): Promise<JsonSchema | null> {
	if (!baseSchema || !baseSchema.properties) {
		return baseSchema;
	}
	const schema = JSON.parse(JSON.stringify(baseSchema));
	for (const key in schema.properties) {
		if (Object.prototype.hasOwnProperty.call(schema.properties, key)) {
			const field = schema.properties[key];
			if (!field.uiHints) {
				field.uiHints = {};
			}
			if (key === "address_coordinates") {
				field.uiHints.component = "MyMap";
				field.uiHints.icon = "mdi-map-marker";
			}
			if (field.type === "text" && key.includes("description")) {
				field.uiHints.component = "v-textarea";
			}
		}
	}
	return schema;
}
const loadSchemaInternal = useErrorHandler(
	async (table: string, view: string) => {
		if (!table || !view) {
			loadedSchema.value = null;
			return;
		}
		isSchemaLoading.value = true;
		schemaError.value = null;
		try {
			const baseSchema = await getSchemaView(table, view);
			loadedSchema.value = await augmentSchemaWithHints(baseSchema);
		} catch (e) {
			schemaError.value = e.message || "Failed to load schema";
			loadedSchema.value = null;
		} finally {
			isSchemaLoading.value = false;
		}
	},
	"Fetch Schema",
);
const loadViewComponentInternal = useErrorHandler(async (view: string) => {
	if (!view) {
		viewComponent.value = null;
		return;
	}
	isViewLoading.value = true;
	viewError.value = null;
	try {
		viewComponent.value = markRaw(await loadView(view));
	} catch (e) {
		viewError.value = e.message || "Failed to load view component";
		viewComponent.value = null;
	} finally {
		isViewLoading.value = false;
	}
}, "Load View Component");
watch(
	() => [
		props.tableName,
		props.schemaView,
		props.schemaOverride,
		props.refreshKey,
	],
	([table, view, override], [oldTable, oldView, oldOverride] = []) => {
		if (!override && (table !== oldTable || view !== oldView)) {
			loadSchemaInternal(table, view);
		} else if (!override && !loadedSchema.value) {
			loadSchemaInternal(table, view);
		} else if (override) {
			loadedSchema.value = null;
			schemaError.value = null;
		}
	},
	{ immediate: true },
);
watch(
	() => [props.schemaView, props.refreshKey],
	([view], [oldView] = []) => {
		if (view && view !== oldView) {
			loadViewComponentInternal(view);
		} else if (view && !viewComponent.value) {
			loadViewComponentInternal(view);
		}
	},
	{ immediate: true },
);
</script>