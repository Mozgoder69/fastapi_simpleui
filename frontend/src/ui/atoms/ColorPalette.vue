<!-- frontend/src/ui/atoms/ColorPalette.vue -->

<template>
  <div class="color-palette">
    <div class="grid" :style="[gridBaseStyle, gridComputedLayout]">
      <div
        v-for="color in cells"
        :key="color"
        class="cell"
        :style="{ background: color }"
        @click="selectColor(color)"
      />
    </div>

    <div class="tabs">
      <v-btn text :class="{ active: mode === '3x3' }" @click="mode = '3x3'">
        3×3
      </v-btn>
      <v-btn text :class="{ active: mode === '5x5' }" @click="mode = '5x5'">
        5×5
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const emit = defineEmits<(e: "color-selected", color: string) => void>();

const palettes = {
	"3x3": [
		["#fa0", "#c44", "#333"],
		["#690", "#999", "#44c"],
		["#fff", "#096", "#0af"],
	],
	"5x5": [
		["#cb9", "#986", "#653", "#320", "#000"],
		["#c44", "#906", "#622", "#333", "#023"],
		["#fa0", "#690", "#999", "#226", "#356"],
		["#fec", "#4c4", "#096", "#609", "#689"],
		["#fff", "#cef", "#0af", "#44c", "#9bc"],
	],
};

const mode = ref<"3x3" | "5x5">("3x3");
const cols = computed(() => +mode.value.charAt(0));
const cells = computed(() => palettes[mode.value].flat());

const CELL_SIZE = 32;
const GAP = 4;
const MAX_COLS_OR_ROWS = 5; // Renamed for clarity

// Стиль, определяющий фиксированные размеры сетки
const gridBaseStyle = computed(() => ({
	width: `${MAX_COLS_OR_ROWS * CELL_SIZE + (MAX_COLS_OR_ROWS - 1) * GAP}px`,
	height: `${MAX_COLS_OR_ROWS * CELL_SIZE + (MAX_COLS_OR_ROWS - 1) * GAP}px`,
}));

// Стиль, определяющий внутреннюю раскладку сетки (grid)
const gridComputedLayout = computed(() => ({
	display: "grid",
	gap: `${GAP}px`,
	gridTemplateColumns: `repeat(${cols.value}, ${CELL_SIZE}px)`,
	justifyContent: "center", // Центрирует колонки, если их меньше MAX
	alignContent: "center", // Центрирует строки, если их меньше MAX
}));

function selectColor(color: string) {
	emit("color-selected", color);
}
</script>

<style scoped>
.color-palette {
  display: flex;
  flex-direction: column;
  align-items: center; /* Центрирует grid и tabs по горизонтали */
  gap: 16px; /* Отступ между сеткой и вкладками, настройте по вкусу */
}

.grid {
  /* Ширина и высота теперь задаются через :style="[gridBaseStyle, gridComputedLayout]" */
  /* gridComputedLayout содержит display: grid и другие свойства сетки */
}

.cell {
  width: 32px;
  height: 32px;
  border: 1px solid #eee;
  cursor: pointer;
  transition: transform .1s, border-color .1s;
}
.cell:hover {
  transform: scale(1.1);
  border-color: #999;
}

.tabs {
  /* Больше не нужно абсолютное позиционирование */
  display: flex;
  gap: 8px;
}
.tabs .v-btn.active {
  font-weight: bold;
}
</style>