<template>
  <div class="character-sheet panel">
    <div class="panel-title">// {{ character.name }}</div>

    <div class="stat-bar">
      <span class="stat-bar-label">HP</span>
      <div class="stat-bar-track">
        <div
          class="stat-bar-fill hp"
          :style="{ width: hpPercent + '%' }"
        />
      </div>
      <span class="stat-bar-value">
        {{ character.derived.hp }}/{{ character.derived.hp_max }}
      </span>
    </div>

    <div class="stat-bar">
      <span class="stat-bar-label">SAN</span>
      <div class="stat-bar-track">
        <div
          class="stat-bar-fill san"
          :style="{ width: sanPercent + '%' }"
        />
      </div>
      <span class="stat-bar-value">
        {{ character.derived.san }}/{{ character.derived.san_max }}
      </span>
    </div>

    <div class="stat-bar">
      <span class="stat-bar-label">MP</span>
      <div class="stat-bar-track">
        <div
          class="stat-bar-fill mp"
          :style="{ width: mpPercent + '%' }"
        />
      </div>
      <span class="stat-bar-value">
        {{ character.derived.mp }}/{{ character.derived.mp_max }}
      </span>
    </div>

    <div class="luck-line">LUCK: {{ character.derived.luck }}</div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ character: any }>();

const hpPercent = computed(
  () => (props.character.derived.hp / props.character.derived.hp_max) * 100
);
const sanPercent = computed(
  () => (props.character.derived.san / props.character.derived.san_max) * 100
);
const mpPercent = computed(
  () => (props.character.derived.mp / props.character.derived.mp_max) * 100
);
</script>

<style scoped>
.luck-line {
  color: var(--text-amber);
  font-size: 14px;
  margin-top: 8px;
  text-align: center;
}
</style>
