<!-- frontend/src/ui/pages/APIRoutesPage.vue -->

<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h2>API Routes</h2>
        <v-btn @click="fetchEndpoints" color="primary" class="mb-4">Refresh</v-btn>
      </v-col>
    </v-row>

    <!-- Search and Filter -->
    <v-row>
      <v-col cols="12" sm="6" md="4">
        <v-text-field v-model="search" label="Search endpoints" prepend-icon="mdi-magnify" clearable></v-text-field>
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <v-select v-model="selectedMethods" :items="availableMethods" label="Filter by method" multiple chips></v-select>
      </v-col>
    </v-row>

    <!-- Loading Indicator -->
    <v-row v-if="loading">
      <v-col cols="12">
        <v-progress-linear indeterminate color="primary"></v-progress-linear>
      </v-col>
    </v-row>

    <!-- Error Message -->
    <v-row v-if="error">
      <v-col cols="12">
        <v-alert type="error">{{ error }}</v-alert>
      </v-col>
    </v-row>

    <!-- Endpoints List Grouped by Tags -->
    <v-row v-else>
      <v-col cols="12">
        <v-expansion-panels>
          <template v-for="(group, tag) in groupedEndpoints">
            <v-expansion-panel>
              <v-expansion-panel-header>
                <strong>{{ tag }}</strong>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-list>
                  <v-list-item v-for="endpoint in group" :key="`${endpoint.path}-${endpoint.method}`" class="method-item">
                    <v-row align="center" no-gutters>
                      <v-col cols="2" class="method-col">
                        <v-chip :color="methodColor(endpoint.method)" class="method-chip">
                          {{ endpoint.method.toUpperCase() }}
                        </v-chip>
                      </v-col>
                      <v-col cols="8" class="path-col">
                        <v-list-item-title class="summary">
                          <strong>{{
                            endpoint.summary || "No summary available"
                          }}</strong>
                        </v-list-item-title>
                        <v-list-item-subtitle class="path-title" :style="{
                              color: 'link',
                              backgroundColor: 'rgba(170, 85, 255, 0.1)',
                              borderRadius: '10px',
                              padding: '2px 8px',
                            }">
                          {{ endpoint.path }}
                        </v-list-item-subtitle>
                        <v-list-item-subtitle class="description" :style="{ color: getTextColor('212121', false) }"
                          v-if="endpoint.description">
                          {{ endpoint.description }}
                        </v-list-item-subtitle>
                        <v-list-item-subtitle class="operation-id" :style="{ color: getTextColor('212121', false) }"
                          v-if="endpoint.operationId">
                          Operation ID: {{ endpoint.operationId }}
                        </v-list-item-subtitle>
                      </v-col>
                      <v-col cols="2" class="action-col" align="end">
                        <v-btn icon @click.stop="copyToClipboard(endpoint.path)">
                          <v-icon>mdi-content-copy</v-icon>
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-list-item>
                </v-list>
              </v-expansion-panel-content>
            </v-expansion-panel>
            <v-divider></v-divider>
          </template>
        </v-expansion-panels>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import type { Value } from "@/core/types";
import { getTextColor } from "@/global/plugins/colorUtils";
import axios from "axios";
import { computed, onMounted, ref, watch } from "vue";
import { useToast } from "vue-toastification";

const toast = useToast();

enum HttpMethod {
  GET = "get",
  POST = "post",
  PUT = "put",
  DELETE = "delete",
}

// Функция для определения цвета метода
function methodColor(method: string): string {
  const colors: Record<string, string> = {
    [HttpMethod.GET]: "pass",
    [HttpMethod.POST]: "info",
    [HttpMethod.PUT]: "warn",
    [HttpMethod.DELETE]: "fail",
  };
  return colors[method] || "grey";
}

// Интерфейсы
interface Endpoint {
  path: string;
  method: string;
  summary?: string;
  description?: string;
  tags: string[];
  operationId?: string;
}

type RawEndpoints = Record<string, Record<string, Value>>;

// Состояния
const rawEndpoints = ref<RawEndpoints | null>(null);
const loading = ref<boolean>(false);
const error = ref<string | null>(null);
const search = ref<string>("");
const selectedMethods = ref<string[]>([]);

// Функция для получения данных
const fetchEndpoints = useErrorHandler(async () => {
  loading.value = true;
  const response = await axios.get("/api/openapi.json");
  rawEndpoints.value = response.data.paths;
  loading.value = false;
}, "Load API routes");

// Обработка и структура данных
const endpoints = computed<Endpoint[]>(() => {
  if (!rawEndpoints.value) return [];
  return Object.entries(rawEndpoints.value).flatMap(([path, methods]) =>
    Object.entries(methods).map(([method, details]) => ({
      path,
      method,
      summary: details.summary,
      description: details.description,
      tags: details.tags || ["Default"],
      operationId: details.operationId,
    })),
  );
});

// Фильтрация маршрутов
const filteredEndpoints = computed<Endpoint[]>(() => {
  return endpoints.value.filter((endpoint) => {
    const matchesSearch =
      search.value === "" ||
      endpoint.path.toLowerCase().includes(search.value.toLowerCase()) ||
      endpoint.summary?.toLowerCase().includes(search.value.toLowerCase()) ||
      endpoint.description?.toLowerCase().includes(search.value.toLowerCase());
    const matchesMethod =
      selectedMethods.value.length === 0 ||
      selectedMethods.value.includes(endpoint.method.toUpperCase());
    return matchesSearch && matchesMethod;
  });
});

const groupedEndpoints = ref<Record<string, Endpoint[]>>({});

watch(
  [filteredEndpoints, search, selectedMethods],
  ([newEndpoints]) => {
    const groups: Record<string, Endpoint[]> = {};
    for (const endpoint of newEndpoints) {
      for (const tag of endpoint.tags) {
        if (!groups[tag]) {
          groups[tag] = [];
        }
        groups[tag].push(endpoint);
      }
    }
    groupedEndpoints.value = groups;
  },
  { immediate: true },
);

// Доступные методы для фильтрации
const availableMethods = computed<string[]>(() => {
  const methodsSet = new Set<string>();
  for (const endpoint of endpoints.value) {
    methodsSet.add(endpoint.method.toUpperCase());
  }
  return Array.from(methodsSet).sort();
});

const copyToClipboard = (text: string) => {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      toast.success("Path copied to clipboard!");
    })
    .catch((err) => {
      console.error("Could not copy text: ", err);
      toast.error("Failed to copy path");
    });
};

// Инициализация
onMounted(async () => {
  await fetchEndpoints();
});
</script>

<style scoped>
.method-item {
  padding: 8px 0;
}

.method-col {
  display: flex;
  align-items: center;
}

.method-chip {
  font-weight: bold;
  text-transform: uppercase;
}

.path-col {
  padding-left: 8px;
}

.path-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  font-weight: normal;
  /* Больше не делаем жирным */
}

.summary {
  font-size: 1em;
  color: white;
  /* Для темного фона */
  font-weight: bold;
  /* Делаем название жирным */
}

.description,
.operation-id {
  font-size: 0.7em;
  margin-top: 2px;
}

.action-col {
  display: flex;
  justify-content: flex-end;
}
</style>
