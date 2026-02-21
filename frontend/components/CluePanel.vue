<template>
  <div class="clue-panel panel">
    <div class="panel-title">// CLUES</div>
    <div v-if="clues.length === 0" class="empty">No clues yet.</div>
    <div v-for="(clue, i) in clues" :key="i" class="clue-item">
      <span class="clue-check">+</span> {{ clue }}
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ clues: string[] }>();
</script>

<style scoped>
.clue-item {
  color: var(--text-secondary);
  margin: 4px 0;
  font-size: 16px;
}
.clue-check {
  color: var(--text-primary);
  margin-right: 4px;
}
.empty {
  color: var(--text-dim);
  font-size: 14px;
}
</style>
