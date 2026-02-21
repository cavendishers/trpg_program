<template>
  <div class="action-input">
    <div class="quick-actions">
      <button @click="emit('send', '我想调查周围环境')">调查</button>
      <button @click="emit('send', '我想和NPC交谈')">交谈</button>
      <button @click="emit('send', '我想战斗')">战斗</button>
      <button @click="emit('send', '我想使用物品')">物品</button>
    </div>
    <div class="input-row">
      <input
        v-model="text"
        placeholder="What do you do?"
        @keydown.enter="send"
      />
      <button class="send-btn" @click="send">&gt;</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{ send: [text: string] }>();
const text = ref("");

function send() {
  const val = text.value.trim();
  if (!val) return;
  emit("send", val);
  text.value = "";
}
</script>

<style scoped>
.action-input {
  border-top: 1px solid var(--border-color);
  padding: 8px 16px;
  background: var(--bg-secondary);
}
.quick-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
.quick-actions button {
  font-size: 14px;
  padding: 4px 12px;
}
.input-row {
  display: flex;
  gap: 8px;
}
.input-row input {
  flex: 1;
}
.send-btn {
  width: 40px;
  font-size: 22px;
  color: var(--text-amber);
  border-color: var(--text-amber);
}
</style>
