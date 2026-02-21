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
  padding: 16px;
}
.narrative-entry {
  margin: 8px 0;
  line-height: 1.5;
}
.narrative-entry.narrative {
  color: var(--text-primary);
}
.narrative-entry.dice_result {
  color: var(--text-amber);
  padding: 4px 8px;
  border-left: 2px solid var(--text-amber);
}
.narrative-entry.system {
  color: var(--text-dim);
  font-size: 16px;
}
.dice-icon {
  display: inline-block;
  background: var(--text-amber);
  color: var(--bg-primary);
  padding: 1px 4px;
  font-size: 12px;
  margin-right: 6px;
}
.system-prefix {
  color: var(--text-dim);
  margin-right: 4px;
}
</style>
