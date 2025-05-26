<!-- frontend/src/ui/atoms/PKSelect.vue -->

<template>
<KeySelect v-bind="props" :options="pkOptions" @update:modelValue="v => emit('update:modelValue', v)"
 />
</template>

<script setup lang="ts">
import { usePrimaryKey } from "@/core/hooks/ui/useKeyFields";
import type { JsonSchema } from "@/core/types";
import { computed } from "vue";
import KeySelect from "./KeySelect.vue";
const props = defineProps<{
	schema: JsonSchema;
	fieldName: string;
	modelValue: unknown;
	label?: string;
}>();
const emit = defineEmits<(e: "update:modelValue", v: unknown) => void>();
const { options } = usePrimaryKey(props.schema, props.fieldName);
const pkOptions = computed(() => options.value[props.fieldName] || []);
</script>