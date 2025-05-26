<!-- frontend/src/ui/pages/HomePage.vue -->

<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card>
          <v-card-title class="text-center">
            <h1>Добро пожаловать</h1>
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" class="text-center">
                <v-btn color="primary" class="mb-4" @click="newOrder" block>
                  Новый Заказ
                </v-btn>
              </v-col>
              <v-col cols="12" class="text-center">
                <v-btn color="secondary" @click="viewCatalog" block>
                  Посмотреть Каталог
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

// Navigate to the 'New Order' page
function newOrder() {
  router.push({ name: "NewOrder" }); // Assuming you have a route named 'NewOrder'
}

// Navigate to the 'Catalog' page
function viewCatalog() {
  router.push({ name: "Catalog" }); // Assuming you have a route named 'Catalog'
}
</script>

<style scoped>
/* Add any specific styles if needed */
</style>
