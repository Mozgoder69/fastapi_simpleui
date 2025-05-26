<!-- frontend/src/ui/organisms/NavBar.vue -->

<template>
<v-navigation-drawer app left temporary v-model="drawer">
<v-list>
<v-list-item v-for="(entry, index) in tableSchemas" :key="index" @click="selectTable(entry.tableName)">
<v-list-item-title class="list-item-content">
<span class="material-symbols-outlined mr-2">{{ entry.icon }}</span>
 {{ entry.title || entry.tableName }}
</v-list-item-title>
</v-list-item>
</v-list>
</v-navigation-drawer>
<v-app-bar color="accent">
<v-app-bar-nav-icon @click="drawer = !drawer" />
<v-toolbar-title>MyApp</v-toolbar-title>
<v-btn text to="/">Home</v-btn>
<v-btn text to="/apitest">API Test</v-btn>
<v-btn text to="/apiroutes">API Routes</v-btn>
<v-spacer />
<v-toolbar-items>
<v-btn icon @click="showNotifications = !showNotifications"><v-icon>mdi-bell</v-icon></v-btn>
<v-menu>
<template v-slot:activator="{ props }">
<v-btn v-bind="props">
<v-avatar><v-icon>mdi-account-circle</v-icon></v-avatar>
<span v-if="isAuthenticated" class="ml-2">{{ userUname }}</span>
</v-btn>
</template>
<v-list>
<v-list-item v-if="!isAuthenticated" @click="navigateToLogin"><v-list-item-title>Login</v-list-item-title></v-list-item>
<v-list-item @click="navigateToOTP"><v-list-item-title>OTP</v-list-item-title></v-list-item>
<v-list-item @click="toggleTheme"><v-list-item-title>Toggle Theme</v-list-item-title></v-list-item>
<v-list-item @click="showAccent = true"><v-list-item-title>Pick Accent</v-list-item-title></v-list-item>
<v-list-item @click="resetPassword"><v-list-item-title>Reset Password</v-list-item-title></v-list-item>
<v-list-item v-if="isAuthenticated" @click="logout"><v-list-item-title>Logout</v-list-item-title></v-list-item>
</v-list>
</v-menu>
</v-toolbar-items>
</v-app-bar>

<v-dialog v-model="showNotifications">
<v-card>
<v-card-title>Notifications</v-card-title>
<v-card-text><DataDisplay tableName="message" schemaView="TableView" :refreshKey="refreshKey" /></v-card-text>
</v-card>
</v-dialog>

  <v-dialog v-model="showAccent" max-width="320" min-height="320">
    <v-card>
      <v-card-title>Accent Color</v-card-title>
      <v-card-text class="d-flex justify-center align-center" style="min-height: 200px;">
        <ColorPalette @color-selected="onAccentSelect" />
      </v-card-text>
      <!-- <v-card-actions>
        <v-spacer/>
        <v-btn text @click="showAccent = false">Закрыть</v-btn>
      </v-card-actions> -->
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/core/auth/useAuthStore";
import { useSchemas } from "@/core/hooks/data/useSchemas";
import ColorPalette from "@/ui/atoms/ColorPalette.vue";
import DataDisplay from "@/ui/molecules/DataDisplay.vue";
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { useTheme } from "vuetify";

const theme = useTheme(); // ← единственный вызов useTheme()

const showAccent = ref(false);
const DEFAULT_ACCENT_COLOR = "#aa00ff";
let currentAccentColor = DEFAULT_ACCENT_COLOR;

// function applyAccent(color: string) {
// 	// только меняем цвет через theme, без повторного useTheme():
// 	theme.global.current.value.colors.accent = color;
// }

function applyAccent(color: string) {
	// 1. get the active theme name, e.g. 'dark' or 'light'
	const cur = theme.global.name.value;

	// 2. update the raw theme definition
	theme.themes.value[cur].colors.accent = color;
}

onMounted(() => {
	const saved = localStorage.getItem("accentColor");
	currentAccentColor = saved || DEFAULT_ACCENT_COLOR;
	applyAccent(currentAccentColor); // ← теперь без второго аргумента
	loadSchemas().catch(() => toast.error("Не удалось загрузить схемы."));
});

watch(
	() => theme.global.name.value,
	() => {
		// при смене темы повторно проставляем текущий accent
		applyAccent(currentAccentColor);
	},
	{ immediate: true },
);

function onAccentSelect(color: string) {
	localStorage.setItem("accentColor", color);
	currentAccentColor = color;
	applyAccent(color); // ← без второго аргумента
	showAccent.value = false;
}

const drawer = ref(false);
const showNotifications = ref(false);
const refreshKey = ref(0);
const router = useRouter();
const toast = useToast();
const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const userUname = ref(authStore.uname);
watch(
	() => authStore.state.uname,
	(newUname) => {
		userUname.value = newUname;
	},
);

const { getSchemas } = useSchemas();
const tableSchemas = ref<
	Array<{ tableName: string; icon: string; title: string }>
>([]);
const loadSchemas = async () => {
	const schemasRecord = await getSchemas();
	tableSchemas.value = Object.entries(schemasRecord).map(
		([tableName, schema]) => ({
			tableName,
			icon: schema.icon || "mdi-database",
			title: schema.title || tableName,
		}),
	);
};

watch(isAuthenticated, () => {
	if (isAuthenticated.value)
		loadSchemas().catch(() => toast.error("Не удалось загрузить схемы."));
});

function selectTable(tableName: string) {
	router.push({ name: "API Test", query: { table: tableName } });
	drawer.value = false;
}
const navigateToLogin = () => router.push("/login");
const navigateToOTP = () => router.push("/otp");
const toggleTheme = () => {
	theme.global.name.value =
		theme.global.name.value === "dark" ? "light" : "dark";
	toast.info(`Тема изменена на ${theme.global.name.value}`);
};
const resetPassword = () => {};
const logout = () => {
	authStore.logout();
	router.push("/login");
	toast.success("Вы успешно вышли из системы.");
};
</script>

<style scoped>
.list-item-content { display: flex; align-items: center; }
.ml-2 { margin-left: 8px; }
.mr-2 { margin-right: 8px; }
</style>