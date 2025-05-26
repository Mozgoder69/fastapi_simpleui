<!-- frontend/src/ui/organisms/FormData.vue -->

<template>
<v-card-text class="form-data">
<v-form ref="formRef">
<template v-if="Object.keys(currentProperties).length > 0">
<DynamicField v-for="(field, key) in currentProperties" :key="`${props.mode}-${key}`" :schema="props.schema" :field="{ ...field, name: key }" :modelValue="formData[key]" @update:modelValue="formData[key] = $event" :label="field.label || key" :modeType="props.mode" :isInput="true" :disabled="props.disabledAll || false" />
</template>
<v-alert v-else type="warning" density="compact">No properties defined for mode '{{ props.mode }}'.</v-alert>
</v-form>
</v-card-text>
</template>

<script setup lang="ts">
import type { FormDataProps } from "@/core/types";
import DynamicField from "@/ui/molecules/DynamicField.vue";
import { computed, ref } from "vue";
const props = defineProps<FormDataProps>();
const formRef = ref(null);
const currentProperties = computed(
	() =>
		props.schema?.modes?.find((m) => m.mode === props.mode)?.properties ||
		props.schema?.properties ||
		{},
);
</script>

<style scoped>
.form-data { padding: 16px; }
</style>