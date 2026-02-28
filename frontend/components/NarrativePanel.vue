<template>
  <div class="narrative-panel" ref="panelRef">
    <div
      v-for="(entry, i) in entries"
      :key="i"
      class="narrative-entry"
      :class="entry.type"
    >
      <span v-if="entry.type === 'dice_result'" class="dice-icon">D100</span>
      <span v-if="entry.type === 'system'" class="system-prefix">&gt;</span>
      <span class="entry-text">{{ entry.content }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  entries: Array<{ type: string; content: string; timestamp: number }>;
}>();

const panelRef = ref<HTMLElement | null>(null);

watch(
  () => props.entries.length,
  () => {
    nextTick(() => {
      if (panelRef.value) {
        panelRef.value.scrollTop = panelRef.value.scrollHeight;
      }
    });
  }
);
</script>

<style scoped>
.narrative-panel {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  touch-action: pan-y;
  padding: 16px 20px;
  min-height: 0;
}
.narrative-entry {
  margin: 12px 0;
  line-height: 1.6;
  font-size: 18px;
}
.narrative-entry.narrative {
  color: var(--text-primary);
}
.narrative-entry.dice_result {
  color: var(--text-amber);
  padding: 6px 10px;
  border-left: 2px solid var(--text-amber);
  background: rgba(255, 170, 0, 0.06);
}
.narrative-entry.system {
  color: var(--text-dim);
  font-size: 16px;
  border-left: 2px solid var(--border-color);
  padding-left: 10px;
}
.dice-icon {
  display: inline-block;
  background: var(--text-amber);
  color: var(--bg-primary);
  padding: 2px 6px;
  font-size: 13px;
  margin-right: 8px;
}
.system-prefix {
  color: var(--text-dim);
  margin-right: 6px;
}
@media (max-width: 768px) {
  .narrative-panel { padding: 10px 12px; overflow-y: scroll; }
  .narrative-entry { font-size: 16px; margin: 8px 0; line-height: 1.7; }
  .narrative-entry.system { font-size: 14px; }
}
</style>
