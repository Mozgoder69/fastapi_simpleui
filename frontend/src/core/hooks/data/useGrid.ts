// frontend/src/core/hooks/data/useGrid.ts

import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { api } from "@/core/services/api";
import { extractPrimaryKeys } from "@/core/utils/schemaUtils";
import { computed, ref, watch } from "vue";

export function useGrid(
	tableName: string,
	schema,
	externalSearchQuery: Ref<string> | undefined,
	filters: Record = {},
) {
	const records = ref([]);
	const searchQuery = externalSearchQuery || ref("");
	const filteredRecords = computed(() =>
		records.value.filter((r) =>
			Object.values(r)
				.map((v) => String(v).toLowerCase())
				.some((v) => v.includes(searchQuery.value.toLowerCase())),
		),
	);
	const primaryKeys = computed(() => extractPrimaryKeys(schema));
	const getRecordKey = (record) =>
		primaryKeys.value.map((k) => record[k]).join("-") || "";

	const fetchRecords = useErrorHandler(async () => {
		const res = await api.listMany(tableName, filters);
		records.value = res.records.map((r) => ({ ...r.keys, ...r.data }));
	}, `fetchRecords(${tableName})`);

	watch(() => tableName, fetchRecords, { immediate: true });
	watch(
		() => filters,
		() => {
			fetchRecords();
		},
		{ deep: true },
	);

	return {
		records,
		fetchRecords,
		searchQuery,
		filteredRecords,
		primaryKeys,
		getRecordKey,
	};
}
