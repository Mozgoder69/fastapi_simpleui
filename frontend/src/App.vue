<!-- frontend/src/App.vue -->

<template>
  <v-app>
    <NavBar />
    <v-main>
      <router-view />
    </v-main>
    <v-footer app elevate-on-scroll elevation="4">
      <v-container>
        <v-row justify="center">
          <v-col cols="auto"><p>Privacy Policy</p></v-col>
          <v-col cols="auto"><p>© 2024 Cleaner's. All Rights Reserved</p></v-col>
          <v-col cols="auto"><p>Terms of Service</p></v-col>
        </v-row>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script setup lang="ts">
import NavBar from "@/ui/organisms/NavBar.vue";
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>