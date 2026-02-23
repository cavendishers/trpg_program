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
        @focus="emit('focus')"
        @blur="emit('blur')"
      />
      <button class="send-btn" @click="send">&gt;</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  send: [text: string];
  focus: [];
  blur: [];
}>();
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
  padding: 10px 20px;
  background: var(--bg-secondary);
}
.quick-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}
.quick-actions button {
  font-size: 16px;
  padding: 6px 16px;
}
.input-row {
  display: flex;
  gap: 8px;
}
.input-row input {
  flex: 1;
  padding: 10px 14px;
  font-size: 18px;
}
.send-btn {
  width: 44px;
  font-size: 24px;
  color: var(--text-amber);
  border-color: var(--text-amber);
}
@media (max-width: 768px) {
  .action-input { padding: 8px 10px; }
  .quick-actions { gap: 4px; margin-bottom: 6px; flex-wrap: wrap; }
  .quick-actions button { font-size: 14px; padding: 6px 10px; min-height: 36px; }
  .input-row input { font-size: 16px; min-height: 44px; }
  .send-btn { min-height: 44px; }
}
</style>
