// frontend/src/core/hooks/ui/useInlineEdit.ts

import { api } from "@/core/services/api";
import { ref } from "vue";
import { useToast } from "vue-toastification";

export function useInlineEdit(tableName, primaryKeys) {
	const isEditing = ref({});
	const toast = useToast();

	const getItemKey = (item) =>
		primaryKeys.value.length
			? primaryKeys.value.map((key) => item[key]).join("-")
			: Math.random().toString();
	const toggleEdit = (item) => {
		const key = getItemKey(item);
		isEditing.value[key] = !isEditing.value[key];
	};
	const updateField = (item, fieldName, newValue) => {
		item[fieldName] = newValue;
	};
	const saveRecord = async (item) => {
		const keys = Object.fromEntries(
			primaryKeys.value.map((pk) => [pk, item[pk]]),
		);
		const data = { ...item };
		for (const pk of primaryKeys.value) {
			delete data[pk];
		}
		const success = await api.editOne(tableName, { keys, data });
		if (success) {
			isEditing.value[getItemKey(item)] = false;
			toast.success("Record updated");
			return true;
		}
		return false;
	};

	return { isEditing, getItemKey, toggleEdit, updateField, saveRecord };
}
