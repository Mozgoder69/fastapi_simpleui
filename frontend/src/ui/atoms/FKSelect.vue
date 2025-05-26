<!-- frontend/src/ui/atoms/FKSelect.vue -->

<template>
<KeySelect v-bind="props" :options="options" @update:modelValue="v => emit('update:modelValue', v)"
 />
</template>

<script setup lang="ts">
import { useForeignKey } from "@/core/hooks/ui/useKeyFields";
import type { JsonSchema } from "@/core/types";
import KeySelect from "./KeySelect.vue";
const props = defineProps<{
	schema: JsonSchema;
	fieldName: string;
	modelValue: unknown;
	label?: string;
}>();
const emit = defineEmits<(e: "update:modelValue", v: unknown) => void>();
const { options } = useForeignKey(props.schema, props.fieldName);
</script>