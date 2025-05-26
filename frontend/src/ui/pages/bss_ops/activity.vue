<template>
  <v-container>
    <!-- Title and User Role Information -->
    <v-row>
      <v-col cols="12">
        <h2>Activity</h2>
        <!-- Display the user role if necessary -->
        <v-chip>{{ userRole }}</v-chip>
      </v-col>
    </v-row>

    <!-- Filters and View Selector -->
    <v-row>
      <v-col cols="12">
        <v-select
          v-model="filter"
          :items="filterOptions"
          label="Filter by"
          outlined
          clearable
        ></v-select>
        <ViewSelector :tableName="selectedTable" @change-view="setSchemaView" />
      </v-col>
    </v-row>

    <!-- Data Display -->
    <v-row v-if="selectedTable && schemaView">
      <v-col cols="12">
        <DataDisplay
          :key="dataDisplayKey"
          :tableName="selectedTable"
          :schemaView="schemaView"
          @record-updated="handleRecordUpdated"
          @record-deleted="handleRecordDeleted"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from "vue"
import ViewSelector from "@/components/ui/ViewSelector.vue"
import DataDisplay from "@/components/ui/DataDisplay.vue"
import { useToastStore } from "@/stores/toastStore"

// User role could be dynamically set based on user context (e.g., Customer, Service Master)
const userRole = ref("Service Master")

// Filter and view settings
const filter = ref("")
const filterOptions = ref(["Status", "Category", "Date"]) // Adjust options based on the page requirements
const selectedTable = ref("activity")
const schemaView = ref("")
const dataDisplayKey = ref(0)
const toastStore = useToastStore()

// Methods
const setSchemaView = (view) => {
  schemaView.value = view
}

const handleRecordUpdated = () => {
  toastStore.showToast("Record updated successfully", "is-success")
}

const handleRecordDeleted = () => {
  toastStore.showToast("Record deleted successfully", "is-success")
}
</script>
