<!-- frontend/src/ui/molecules/ItemActions.vue -->

<template>
<div class="item-actions">
<v-btn icon small color="link" v-if="!isEditing" @click="view">
<v-icon>mdi-eye</v-icon>
</v-btn>
<v-btn icon small color="warn" v-if="!isEditing" @click="$emit('toggle-edit')">
<v-icon>mdi-pencil</v-icon>
</v-btn>
<v-btn icon small color="pass" v-if="isEditing" @click="$emit('save')">
<v-icon>mdi-content-save</v-icon>
</v-btn>
<v-btn icon small color="grey" v-if="isEditing" @click="$emit('toggle-edit')">
<v-icon>mdi-close</v-icon>
</v-btn>
<v-btn icon small color="fail" v-if="!isEditing" @click="$emit('delete')">
<v-icon>mdi-delete</v-icon>
</v-btn>
</div>
</template>

<script setup lang="ts">
import { useEntityNavigation } from "@/core/hooks/ui/useEntityNavigation";
import type { Dict } from "@/core/types";
const props = defineProps<{
	isEditing: boolean;
	item: Dict;
	tableName: string;
	primaryKeys: string[];
}>();
const { navigateTo, getKeysFromRecord } = useEntityNavigation();
function view() {
	const keys = getKeysFromRecord(props.item, props.primaryKeys);
	if (!keys) return console.error("Invalid primary keys");
	navigateTo(props.tableName, keys);
}
</script>

<style scoped>
.item-actions {
  display: flex;
  align-items: center;
}
</style>