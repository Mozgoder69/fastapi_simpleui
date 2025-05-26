<!-- frontend/src/ui/templates/FormView.vue -->

<template>
<v-card>
<FormMode v-if="schema && showHead" :schema="schema" :isWizard="false" :mode="mode" :isSearching="isSearching" :title="currentModeInfo?.title || schema.title" :defaultIcon="schema.icon || 'mdi-form-select'" :showHead="showHead" @update:mode="handleModeChange" @search="handleSearch" />
<FormData ref="formDataComponentRef" v-if="schema" :key="mode" :schema="schema" :mode="mode" :recordId="recordIdRef" :tableName="tableName" :isInput="true" :disabledAll="mode !== 'update'" :formData="formData" />
<v-card-actions>
<v-spacer />
<v-btn v-if="mode === 'insert'" color="primary" @click="triggerSubmit"><v-icon left>mdi-send</v-icon> Submit</v-btn>
<v-btn v-else-if="mode === 'update'" color="success" @click="triggerSubmit"><v-icon left>mdi-content-save</v-icon> Save</v-btn>
<v-btn v-else-if="mode === 'select'" color="info" @click="handleSearch" :loading="isSearching"><v-icon left>mdi-magnify</v-icon> Search</v-btn>
</v-card-actions>
</v-card>
</template>

<script setup lang="ts">
import { useForm } from "@/core/hooks/data/useForm";
import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { api } from "@/core/services/api";
import type { Dict, ModeViewSchema } from "@/core/types";
import { extractPrimaryKeys } from "@/core/utils/schemaUtils";
import FormData from "@/ui/organisms/FormData.vue";
import FormMode from "@/ui/organisms/FormMode.vue";
import { computed, ref, toRaw, watch } from "vue";
import type { Ref } from "vue";
import { useToast } from "vue-toastification";
interface Props {
	schema: ModeViewSchema;
	defaultMode?: "insert" | "select" | "update";
	recordId?: Dict | null;
	showHead: boolean;
	tableName: string;
	isWizard?: boolean;
}
const props = defineProps<Props>();
const emit =
	defineEmits<
		(e: "completed", payload: { recordId: Dict; data: Dict }) => void
	>();
const toast = useToast();
const mode = ref(props.defaultMode || "insert");
const recordIdRef = ref<Dict | null>(
	props.recordId ? { ...props.recordId } : null,
);
const isSearching = ref(false);
// Используем useForm здесь
const { formData, isReading, readError, handleSubmit, primaryKeys } = useForm(
	props.schema,
	props.tableName,
	mode,
	recordIdRef,
);
// Следим за изменением входного recordId prop
watch(
	() => props.recordId,
	(newRecordId) => {
		console.log("FormView: props.recordId changed", newRecordId);
		recordIdRef.value = newRecordId ? { ...toRaw(newRecordId) } : null;
	},
	{ deep: true },
);
// Вычисляем текущий режим для заголовка
const currentModeInfo = computed(
	() =>
		props.schema.modes.find((m) => m.mode === mode.value) ||
		props.schema.modes[0], // Фоллбэк
);
// Обработчик смены режима
const handleModeChange = (newMode: "insert" | "select" | "update") => {
	console.log("FormView: handleModeChange", newMode);
	mode.value = newMode;
	if (newMode === "insert") {
		recordIdRef.value = null;
	}
};
// Обработчик успешной отправки (вызывается после handleSubmit из useForm)
const onFormSubmitted = (submittedPayload: { recordId: Dict; data: Dict }) => {
	if (!submittedPayload) {
		console.warn("onFormSubmitted received null payload.");
		return;
	}
	console.log("FormView: onFormSubmitted", submittedPayload);
	recordIdRef.value = submittedPayload.recordId
		? { ...submittedPayload.recordId }
		: null;
	toast.success(
		`Record successfully ${mode.value === "insert" ? "created" : "updated"}!`,
	);
	emit("completed", submittedPayload); // Сообщаем родителю
	if (mode.value === "insert" && !props.isWizard) {
		mode.value = "update";
	}
};
// Функция для вызова handleSubmit из useForm
const triggerSubmit = async () => {
	console.log("FormView: triggerSubmit called");
	try {
		const resultData = await handleSubmit();
		if (resultData) {
			onFormSubmitted(resultData);
		} else {
			console.log("FormView: handleSubmit returned null or undefined.");
		}
	} catch (error) {
		console.error(
			"FormView: Error during triggerSubmit -> handleSubmit:",
			error,
		);
	}
};
// Обработчик поиска
const handleSearch = useErrorHandler(async () => {
	if (mode.value !== "select" && mode.value !== "update") return;
	if (!formData.value || typeof formData.value !== "object") {
		return toast.error("Form data is not available.");
	}
	console.log("FormView: handleSearch using formData:", toRaw(formData.value));
	const currentPrimaryKeys = primaryKeys.value;
	const searchKeys: Dict = {};
	const allKeysProvided = currentPrimaryKeys.every((pk) => {
		const value = formData.value[pk];
		if (value !== undefined && value !== null && value !== "") {
			searchKeys[pk] = value;
			return true;
		}
		return false;
	});
	if (!allKeysProvided) {
		return toast.warning("Please fill in all primary key fields for search.");
	}
	console.log("FormView: Performing search with keys:", searchKeys);
	isSearching.value = true;
	try {
		const record = await api.readOne(props.tableName, searchKeys);
		if (record?.keys) {
			console.log("FormView: Search successful, record found:", record);
			recordIdRef.value = { ...record.keys };
			toast.success("Record found and loaded.");
			if (mode.value === "select") {
				mode.value = "update";
			}
		} else {
			console.log("FormView: Search completed, record not found.");
			toast.info("Record with these keys not found.");
			recordIdRef.value = null;
		}
	} catch (error) {
		console.error("FormView: Error during handleSearch API call:", error);
		recordIdRef.value = null;
	} finally {
		isSearching.value = false;
	}
}, "Record Search");
</script>