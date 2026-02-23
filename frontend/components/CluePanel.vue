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
  margin: 6px 0;
  font-size: 16px;
  padding-bottom: 6px;
  border-bottom: 1px dotted var(--border-color);
}
.clue-item:last-child {
  border-bottom: none;
}
.clue-check {
  color: var(--text-amber);
  margin-right: 6px;
}
.empty {
  color: var(--text-dim);
  font-size: 14px;
}
@media (max-width: 768px) {
  .clue-item { font-size: 14px; margin: 4px 0; padding-bottom: 4px; }
}
</style>
