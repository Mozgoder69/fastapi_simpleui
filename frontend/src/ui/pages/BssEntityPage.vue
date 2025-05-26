<!-- frontend/src/ui/pages/BssEntityPage.vue -->
<template>
  <v-container v-if="!isLoading && schema && entity">
    <BssEntityMain
      :schema="schema"
      :recordId="recordId"
      :viewType="viewType"
      @update:viewType="viewType = $event"
    >
      <template #actions>
        <v-btn icon @click="emit('record-updated', recordId)">
          <v-icon>mdi-pencil</v-icon>
        </v-btn>
        <v-btn icon @click="emit('record-deleted', recordId)">
          <v-icon>mdi-delete</v-icon>
        </v-btn>
      </template>
    </BssEntityMain>

    <BssEntityTabs
      :groups="grouped"
      :calculateFilters="calculateFilters"
      :viewType="viewType"
      :getTabIcon="getTabIcon"
      :getTabTitle="getTabTitle"
      @record-updated="payload => emit('record-updated', payload)"
      @record-deleted="payload => emit('record-deleted', payload)"
    />
  </v-container>

  <v-container v-else-if="isLoading" class="d-flex justify-center align-center" style="height:300px">
    <v-progress-circular indeterminate size="64" color="primary"/>
  </v-container>

  <v-container v-else>
    <v-alert type="error">
      Не удалось загрузить данные объекта. Проверьте корректность ID или имени таблицы.
    </v-alert>
  </v-container>
</template>

<script setup lang="ts">
import { useSchemas } from "@/core/hooks/data/useSchemas";
import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { api } from "@/core/services/api";
import type { Dict, JsonSchema } from "@/core/types";
import BssEntityMain from "@/ui/templates/BssEntityMain.vue";
import BssEntityTabs from "@/ui/templates/BssEntityTabs.vue";
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";

const emit = defineEmits<{
	(e: "record-updated", payload: Dict): void;
	(e: "record-deleted", payload: Dict): void;
}>();

const props = defineProps<{ tableName: string }>();
const route = useRoute();

const isLoading = ref(false);
const schema = ref<JsonSchema | null>(null);
const entity = ref<Dict | null>(null);
const backRefs = ref([]);

const recordId = computed<Dict>(() => ({ ...route.query }));

const grouped = computed<Record>(() =>
	backRefs.value.reduce((acc, r) => {
		const t = r.back_ref_table;
		if (!t) return acc;
		if (!acc[t]) acc[t] = [];
		acc[t].push(r);
		return acc;
	}, {} as Record),
);

const calculateFilters = (infos): Dict => {
	if (!entity.value) return {};
	return infos.reduce<Dict>((f, i) => {
		f[i.back_ref_column] = entity.value[i.ref_column];
		return f;
	}, {});
};

const load = useErrorHandler(async () => {
	if (!props.tableName || Object.keys(recordId.value).length === 0) {
		schema.value = null;
		entity.value = null;
		backRefs.value = [];
		return;
	}
	isLoading.value = true;
	try {
		const { getSchema } = useSchemas();
		const [sRes, dRes, rRes] = await Promise.allSettled([
			getSchema(props.tableName),
			api.readOne(props.tableName, recordId.value),
			api.getBackRefs(props.tableName),
		]);
		if (sRes.status === "fulfilled") schema.value = sRes.value;
		if (dRes.status === "fulfilled" && dRes.value) {
			entity.value = { ...(dRes.value.keys || {}), ...(dRes.value.data || {}) };
		}
		if (rRes.status === "fulfilled") backRefs.value = rRes.value;
	} finally {
		isLoading.value = false;
	}
}, "Load BssEntityPage");

watch([() => props.tableName, () => recordId.value], load, { immediate: true });

const viewType = ref<"TableView" | "CardView">("TableView");

function getTabIcon(_: string): string {
	return "mdi-link-variant";
}

function getTabTitle(t: string): string {
	return t.replace(/_/g, " ");
}
</script>
