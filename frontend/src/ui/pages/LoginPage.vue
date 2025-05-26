<!-- frontend/src/ui/pages/LoginPage.vue -->

<template>
<v-container>
<v-row justify="center">
<v-col cols="12" sm="8" md="4">
<v-card>
<v-card-title>Вход в систему</v-card-title>
<v-card-text>
<v-form @submit.prevent="submitLogin" ref="formRef" v-model="isValid">
<v-text-field v-model="username" label="Имя пользователя" placeholder="Введите имя пользователя" required autocomplete="username" outlined :rules="[rules.required]"></v-text-field>
<v-text-field v-model="password" label="Пароль" type="password" placeholder="Введите пароль" required autocomplete="current-password" outlined :rules="[rules.required]"></v-text-field>
<div class="d-flex flex-column gap-3">
<v-btn color="primary" :loading="isLoading" type="submit" :disabled="!formValid" block>
 Войти
</v-btn>
<v-divider class="my-4">
<span class="text-caption text-medium-emphasis">или</span>
</v-divider>
<v-btn color="secondary" variant="outlined" :loading="isGuestLoading" @click="loginAsGuest" block>
 Войти как гость
</v-btn>
</div>
</v-form>
<v-alert v-if="errorMessage" type="error" dismissible class="mt-4" @dismissed="errorMessage = ''">
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
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
const username = ref<string>("");
const password = ref<string>("");
const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const formRef = ref();
const isLoading = ref<boolean>(false);
const isGuestLoading = ref<boolean>(false);
const errorMessage = ref<string>("");
const isValid = ref<boolean>(false);
const rules = {
	required: (value: string) => !!value || "Поле обязательно",
};
const formValid = computed(() => {
	return username.value.trim() !== "" && password.value.trim() !== "";
});
const submitLogin = useErrorHandler(async () => {
	if (!isValid.value) return;
	isLoading.value = true;
	await authStore.login(username.value, password.value);
	await router.push(route.query.redirect?.toString() || "/");
	isLoading.value = false;
}, "Login");
const loginAsGuest = useErrorHandler(async () => {
	isGuestLoading.value = true;
	await authStore.loginAsGuest();
	await router.push(route.query.redirect?.toString() || "/");
	isGuestLoading.value = false;
}, "Guest Login");
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
