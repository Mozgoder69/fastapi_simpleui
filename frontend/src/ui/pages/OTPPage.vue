<!-- frontend/src/ui/pages/OTPPage.vue -->

<template>
<v-container>
<v-row justify="center">
<v-col cols="12" sm="8" md="4">
<v-card>
<v-card-title>Верификация</v-card-title>
<v-card-text>
<v-form ref="formRef" @submit.prevent="handleSubmit">
<v-text-field v-model="contact" label="Телефон или Email" placeholder="Введите ваш телефон или email" required outlined :disabled="isContactVerified" :rules="[rules.required]" @input="handleContactInput" />
<v-fade-transition>
<div v-if="customerName" class="my-3">
<v-alert type="success" text>
 Здравствуйте, {{ customerName }}! Вам отправлен одноразовый код.
</v-alert>
</div>
</v-fade-transition>
<v-fade-transition>
<v-text-field v-if="isContactVerified" v-model="otp" label="Код подтверждения" placeholder="Введите полученный код" required outlined :rules="[rules.required]" />
</v-fade-transition>
<v-btn color="primary" :loading="isLoading" type="submit">
 {{ isContactVerified ? "Подтвердить" : "Получить код" }}
</v-btn>
<v-btn v-if="isContactVerified" text class="ml-2" @click="resetForm" >
 Изменить контакт
</v-btn>
</v-form>
<v-alert v-if="errorMessage" type="error" dismissible class="mt-3" @dismissed="errorMessage = ''" >
 {{ errorMessage }}
</v-alert>
</v-card-text>
</v-card>
</v-col>
</v-row>
</v-container>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/core/auth/useAuthStore";
import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import { api } from "@/core/services/api";
import { ref } from "vue";
import { useRouter } from "vue-router";
const router = useRouter();
const authStore = useAuthStore();
const contact = ref<string>("");
const otp = ref<string>("");
const customerId = ref<number | null>(null);
const customerName = ref<string>("");
const isContactVerified = ref<boolean>(false);
const isLoading = ref<boolean>(false);
const errorMessage = ref<string>("");
const formRef = ref();
const rules = {
	required: (v: string) => !!v || "Поле обязательно",
};
const resetForm = () => {
	contact.value = "";
	otp.value = "";
	isContactVerified.value = false;
	customerName.value = "";
	customerId.value = null;
	localStorage.removeItem("customer_id");
};
const handleContactInput = () => {
	if (isContactVerified.value) {
		otp.value = "";
	}
};
const handleSubmit = useErrorHandler(async () => {
	isLoading.value = true;
	if (!isContactVerified.value) {
		// первый шаг: получить OTP
		const response = await api.generateOTP(contact.value);
		customerId.value = response.customer_id;
		customerName.value = response.customer_name || "Клиент";
		localStorage.setItem("customer_id", customerId.value.toString());
		isContactVerified.value = true;
	} else {
		// второй шаг: подтвердить
		const stored = localStorage.getItem("customer_id");
		if (!stored) {
			resetForm();
			throw new Error("ID клиента не найден. Пожалуйста, начните сначала.");
		}
		customerId.value = Number.parseInt(stored, 10);
		const response = await api.validateOTP(customerId.value, otp.value);
		if (!response.access_token) {
			throw new Error(response.detail || "Неверный код подтверждения");
		}
		// сохраняем токены и дальше по обычной схеме
		authStore.setTokens(response.access_token, response.refresh_token);
		await router.push("/");
	}
	isLoading.value = false;
}, "OTP Submission");
</script>

<style scoped>
.v-divider {
  position: relative;
}
.v-divider span {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: 0 1rem;
}
</style>