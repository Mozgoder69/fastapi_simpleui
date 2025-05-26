<!-- frontend/src/ui/atoms/TextBool.vue -->

<template>
<v-text-field :label="label" :value="modelValue ?? false" readonly @click="$emit('update:modelValue', !(modelValue ?? false))" :append-inner-icon="(modelValue ?? false) ? 'mdi-toggle-switch' : 'mdi-toggle-switch-off'" persistent-placeholder persistent-clear tabindex="0" @keydown.space.prevent="$emit('update:modelValue', !(modelValue ?? false))" @keydown.enter.prevent="$emit('update:modelValue', !(modelValue ?? false))" />
</template>

<script setup lang="ts">
interface Props {
	modelValue: boolean | null;
	label?: string;
}
const props = withDefaults(defineProps<Props>(), { label: "" });
defineEmits(["update:modelValue"]);
</script>