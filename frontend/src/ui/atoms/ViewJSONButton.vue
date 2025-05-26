<!-- frontend/src/ui/atoms/ViewJSONButton.vue -->

<template>
<v-btn icon @click="isOpen = true" title="View JSON Schema" class="mr-2">
<v-icon>mdi-code-json</v-icon>
</v-btn>
<v-dialog v-model="isOpen" max-width="600px">
<v-card>
<v-card-title>JSON Schema</v-card-title>
<v-card-text>
<v-textarea v-model="json" readonly rows="20" outlined auto-grow/>
</v-card-text>
<v-card-actions>
<v-spacer/>
<v-btn text @click="isOpen = false">Close</v-btn>
</v-card-actions>
</v-card>
</v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
const props = defineProps<{ schema: object }>();
const isOpen = ref(false);
const json = ref("");
watch(isOpen, (open) => {
	if (open) json.value = JSON.stringify(props.schema, null, 2);
});
</script>