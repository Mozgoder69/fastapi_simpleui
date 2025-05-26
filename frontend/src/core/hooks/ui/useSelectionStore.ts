// frontend/src/core/hooks/ui/useSelectionStore.ts

import { defineStore } from "pinia";

const areKeysEqual = (item1, item2, keys) =>
	item1 && item2 && keys.every((key) => item1[key] === item2[key]);

export const useSelectionStore = defineStore("selection", {
	state: () => ({ selectedItems: {} }),
	getters: {
		getSelectedItems: (state) => (tableName) =>
			state.selectedItems[tableName] || [],
		selectedCount: (state) => (tableName) =>
			state.selectedItems[tableName]?.length || 0,
		isSelected: (state) => (tableName, item, primaryKeys) =>
			state.selectedItems[tableName]?.some((selected) =>
				areKeysEqual(selected, item, primaryKeys),
			) || false,
	},
	actions: {
		ensureTableExists(tableName) {
			if (!this.selectedItems[tableName]) this.selectedItems[tableName] = [];
		},
		toggleItemSelection(tableName, item, primaryKeys) {
			this.ensureTableExists(tableName);
			const index = this.selectedItems[tableName].findIndex((selected) =>
				areKeysEqual(selected, item, primaryKeys),
			);
			index !== -1
				? this.selectedItems[tableName].splice(index, 1)
				: this.selectedItems[tableName].push({ ...item });
		},
		selectItems(tableName, items) {
			this.ensureTableExists(tableName);
			this.selectedItems[tableName] = [...items];
		},
		deselectItems(tableName, items, primaryKeys) {
			this.ensureTableExists(tableName);
			this.selectedItems[tableName] = this.selectedItems[tableName].filter(
				(selected) =>
					!items.some((item) => areKeysEqual(selected, item, primaryKeys)),
			);
		},
		selectAllItems(tableName, items) {
			this.ensureTableExists(tableName);
			this.selectedItems[tableName] = [...items];
		},
		deselectAllItems(tableName) {
			this.ensureTableExists(tableName);
			this.selectedItems[tableName] = [];
		},
	},
});
