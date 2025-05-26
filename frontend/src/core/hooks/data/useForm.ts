// frontend/src/core/hooks/data/useForm.ts

import { useValidation } from "@/core/hooks/ui/useValidation";
import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { api } from "@/core/services/api";
import type { Dict, JsonSchema, ModeViewSchema } from "@/core/types";
import { initFormData } from "@/core/utils/dataUtils";
import {
	extractPrimaryKeys,
	extractProperties,
} from "@/core/utils/schemaUtils";
import {
	type Ref,
	computed,
	nextTick,
	ref,
	shallowRef,
	toRaw,
	watch,
} from "vue";
import { useToast } from "vue-toastification";

export function useForm(
	schemaInput: JsonSchema | ModeViewSchema,
	tableName: string,
	mode: Ref<"insert" | "select" | "update">,
	recordId: Ref<Dict | null>,
) {
	const toast = useToast();
	const formData = ref<Dict>({});
	const isReading = ref(false);
	const readError = ref<Error | null>(null);
	const schemaRef = shallowRef(schemaInput);

	// Обновляем schemaRef, если внешняя схема поменяется
	watch(
		() => schemaInput,
		(s) => {
			schemaRef.value = s;
		},
		{ deep: true },
	);

	const primaryKeys = computed(() => extractPrimaryKeys(schemaRef.value));
	const properties = computed(() =>
		extractProperties(schemaRef.value, mode.value),
	);
	const { validationSchema } = useValidation(schemaRef, mode);

	const isFieldReadOnly = (name: string) =>
		computed(() => {
			const f = properties.value[name];
			return (
				mode.value === "select" ||
				(primaryKeys.value.includes(name) && mode.value === "update") ||
				f?.is_enabled === false
			);
		}).value;

	// Инициализация формы (insert или после чтения)
	function initForm(
		modeName: "insert" | "select" | "update",
		existing: Dict = {},
	) {
		formData.value = initFormData(
			extractProperties(schemaRef.value, modeName),
			existing,
		);
	}

	// Загрузка из API
	const loadRecord = useErrorHandler(async (m: string, id: Dict | null) => {
		const keys = id ? toRaw(id) : null;
		if (m === "insert" || !keys || !Object.keys(keys).length) {
			initForm("insert");
			readError.value = null;
			return;
		}
		isReading.value = true;
		readError.value = null;
		try {
			const rec = await api.readOne(tableName, keys);
			if (rec?.keys || rec?.data) {
				initForm(m, { ...(rec.keys || {}), ...(rec.data || {}) });
			} else {
				toast.info("Record not found");
				initForm(m);
			}
		} catch (err) {
			readError.value =
				err instanceof Error ? err : new Error(err?.message || "");
			toast.error(`Error loading record: ${readError.value.message}`);
			initForm(m);
		} finally {
			isReading.value = false;
		}
	}, "Load Record");

	// Отправка формы (insert/update)
	const handleSubmit = useErrorHandler(
		async () => {
			const m = mode.value;
			const raw = toRaw(formData.value);
			await validationSchema.value.validate(raw, { abortEarly: false });

			// Собираем ключи и данные
			const pkObj: Dict = {};
			const dataObj: Dict = {};
			for (const k of Object.keys(raw)) {
				const v = raw[k];
				const f = properties.value[k];
				if (!f) continue;
				if (primaryKeys.value.includes(k) && v != null) pkObj[k] = v;
				if (
					v !== undefined &&
					f.is_enabled &&
					(m === "insert" || !primaryKeys.value.includes(k))
				)
					dataObj[k] = v;
			}

			let rid: Dict | null;

			if (m === "insert") {
				if (!Object.keys(dataObj).length) {
					toast.warning("No data to insert");
					return null;
				}
				const res = await api.newOne(tableName, { data: dataObj });
				rid = res?.keys || pkObj;
			} else {
				rid = recordId.value
					? toRaw(recordId.value)
					: Object.keys(pkObj).length
						? pkObj
						: null;
				if (!rid) {
					toast.warning("No primary key for update");
					return null;
				}
				await api.editOne(tableName, { keys: rid, data: dataObj });
			}
			return { recordId: rid, data: raw };
		},
		"Submit Form",
		true,
	);

	// Перезагружаем при смене mode или recordId
	watch(
		() => [mode.value, recordId.value],
		() => nextTick(() => loadRecord(mode.value, recordId.value)),
		{ immediate: true, deep: true },
	);

	return {
		formData,
		isReading,
		readError,
		validationSchema,
		handleSubmit,
		primaryKeys,
		isFieldReadOnly,
		schemaRef,
	};
}
