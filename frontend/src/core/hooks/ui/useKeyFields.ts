// frontend/src/core/hooks/ui/useKeyFields.ts

import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { api } from "@/core/services/api";
import { truncateValue } from "@/core/utils/dataUtils";
import {
	extractPrimaryKeys,
	extractProperties,
} from "@/core/utils/schemaUtils";
import { computed, ref, watchEffect } from "vue";

const MAX_LABEL_PART_LENGTH = 15; // <-- Макс. длина части лейбла
const OPTIONS_FETCH_LIMIT = 100; // <-- Лимит записей для загрузки опций (увеличить при необходимости)

// const fetchOptions = useErrorHandler(
// 	async (tableName, column, labelFields = []) =>
// 		(await api.listMany(tableName)).records.map((item) => ({
// 			value: item.keys?.[column] ?? item.data?.[column],
// 			label: labelFields.length
// 				? labelFields.map((f) => item.data?.[f] ?? "").join(" - ")
// 				: String(item.keys?.[column] ?? item.data?.[column] ?? ""),
// 		})),
// 	"Fetch Options",
// );

const fetchOptions = useErrorHandler(
	async (tableName, column, labelFields = []) => {
		// labelFields больше не используется напрямую для label
		// Запрашиваем записи. Указываем пустой columns для получения всех
		// и увеличенный limit.
		const response = await api.listMany(
			tableName,
			{},
			[],
			OPTIONS_FETCH_LIMIT,
			0,
		);

		if (!response || !Array.isArray(response.records)) {
			console.warn(`No records received for options in ${tableName}`);
			return [];
		}

		return response.records.map((item) => {
			// Значение для v-select (сам ключ)
			const actualValue = item.keys?.[column] ?? item.data?.[column];

			// Объединяем keys и data для получения всех полей записи
			const fullRecordData = { ...(item.keys ?? {}), ...(item.data ?? {}) };

			// Получаем ключи всех полей, фильтруем сам ключ ID ('column') и сортируем
			const displayKeys = Object.keys(fullRecordData)
				.filter((key) => key !== column) // Исключаем сам ключ ID из лейбла
				.sort(); // Сортируем для консистентности

			// Формируем части лейбла, обрезая каждое значение
			const labelParts = displayKeys.map((key) =>
				truncateValue(fullRecordData[key], MAX_LABEL_PART_LENGTH),
			);

			// Собираем опцию для v-select
			return {
				value: actualValue,
				label: labelParts.join(" | "), // Соединяем части через разделитель
			};
		});
	},
	"Fetch Options",
);

export function useForeignKey(schema, fieldName, mode = "insert") {
	const options = ref([]);
	const fks = extractProperties(schema, mode)[fieldName]?.foreign_keys;
	const fk = fks[0];
	if (!fk)
		return {
			options,
			isLoading: ref(false),
			error: ref(null),
			refetch: () => {},
		};
	const { ref_table, ref_column, label_fields } = fk;
	const fetchFK = useErrorHandler(async () => {
		options.value = await fetchOptions(ref_table, ref_column, label_fields);
	}, "Fetch Foreign Key Options");
	fetchFK();
	return { options, isLoading: ref(false), error: ref(null), refetch: fetchFK };
}

export function usePrimaryKey(schema, fieldName) {
	const primaryKeys = ref([]);
	watchEffect(() => {
		primaryKeys.value = extractPrimaryKeys(schema);
	});
	if (!primaryKeys.value.length)
		return {
			selectedPkValues: ref({}),
			pkEntries: [],
			options: ref({}),
			validatePkValues: () => false,
		};

	const selectedPkValues = ref({});
	const validatePkValues = () =>
		primaryKeys.value.every(
			(pk) =>
				selectedPkValues.value[pk] !== undefined &&
				selectedPkValues.value[pk] !== null &&
				selectedPkValues.value[pk] !== "",
		);
	const pkEntries = primaryKeys.value.map((pk) => {
		const field = schema.properties?.[pk] || {};
		const fks = field.foreign_keys || [];
		const fk = fks[0];
		const refTable = fk ? fk.ref_table : schema.entity;
		const refColumn = fk ? fk.ref_column : pk;
		const labelFields = fk ? fk.label_fields || [] : [];
		const optionsRef = ref([]);
		const fetchPK = useErrorHandler(async () => {
			optionsRef.value = await fetchOptions(refTable, refColumn, labelFields);
		}, "Fetch Primary Key Options");
		fetchPK();
		return { pk, optionsRef, refetch: fetchPK };
	});

	return {
		selectedPkValues,
		pkEntries,
		options: computed(() =>
			Object.fromEntries(pkEntries.map((e) => [e.pk, e.optionsRef.value])),
		),
		validatePkValues,
	};
}
