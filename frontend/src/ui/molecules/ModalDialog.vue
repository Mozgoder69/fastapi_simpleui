<!-- frontend/src/ui/molecules/ModalDialog.vue -->

<template>
<v-dialog v-model="openForm" max-width="800" persistent>
<v-card>
<v-card-title>
<span class="text-h5">{{ title }}</span>
<v-spacer/>
<v-btn icon @click="openForm = false"><v-icon>mdi-close</v-icon></v-btn>
</v-card-title>
<v-card-text>
<FormView v-if="formSchema" :schema="formSchema" :tableName="props.tableName" :defaultMode="mode" :recordId="recordId" :showHead="false" @completed="onCompleted" />
<v-progress-circular indeterminate v-else/>
</v-card-text>
</v-card>
</v-dialog>
<v-dialog v-model="openDelete" max-width="400">
<v-card>
<v-card-title>Confirm Delete</v-card-title>
<v-card-text>
 Delete {{ itemsToDelete.length }} item(s)?
</v-card-text>
<v-card-actions>
<v-spacer/>
<v-btn text @click="openDelete = false">No</v-btn>
<v-btn color="fail" @click="executeDelete">Yes</v-btn>
</v-card-actions>
</v-card>
</v-dialog>
</template>

<script setup lang="ts">
import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { api } from "@/core/services/api";
import type { Dict, FormViewSchema, GridViewSchema } from "@/core/types";
import { extractPrimaryKeys } from "@/core/utils/schemaUtils";
import FormView from "@/ui/templates/FormView.vue";
import { onMounted, ref } from "vue";
import { useToast } from "vue-toastification";
const props = defineProps<{
	tableName: string;
	schema: GridViewSchema | FormViewSchema;
	fetchRecords: () => Promise<void>;
}>();
const toast = useToast();
const openForm = ref(false);
const title = ref("");
const mode = ref<"insert" | "update">("insert");
const recordId = ref<Dict | null>(null);
const formSchema = ref<FormViewSchema | null>(null);
const openDelete = ref(false);
const itemsToDelete = ref<Dict[]>([]);
const primaryKeys = extractPrimaryKeys(props.schema);
const loadSchema = useErrorHandler(async () => {
	const resp = await api.getSimpleSchemaView(props.tableName, "FormView");
	formSchema.value = resp.view === "FormView" ? resp : null;
}, "Load Form Schema");
onMounted(loadSchema);
function openCreateDialog() {
	title.value = `Create ${formSchema.value?.title || props.tableName}`;
	mode.value = "insert";
	recordId.value = null;
	openForm.value = true;
}
function openEdit(item: Dict) {
	const keys: Dict = {};
	for (const pk of primaryKeys) {
		if (item[pk] !== undefined) keys[pk] = item[pk];
	}
	title.value = `Edit ${formSchema.value?.title || props.tableName}`;
	mode.value = "update";
	recordId.value = keys;
	openForm.value = true;
}
async function onCompleted({ recordId: rid }: { recordId: Dict }) {
	openForm.value = false;
	await props.fetchRecords();
}
function confirmDelete(items: Dict[]) {
	itemsToDelete.value = items;
	openDelete.value = true;
}
const executeDelete = useErrorHandler(async () => {
	const list = itemsToDelete.value.map((item) => {
		const keys: Dict = {};
		for (const pk of primaryKeys) {
			keys[pk] = item[pk];
		}
		return { keys };
	});
	if (list.length === 1) {
		await api.delOne(props.tableName, list[0]);
	} else {
		await api.trimMany(props.tableName, list);
	}
	toast.success(`Deleted ${list.length} item(s)`);
	openDelete.value = false;
	itemsToDelete.value = [];
	await props.fetchRecords();
}, "Delete Items");
defineExpose({ openCreateDialog, openEdit, confirmDelete });
</script>