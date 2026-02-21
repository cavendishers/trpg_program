<template>
  <div class="game-layout" :class="{ 'glitch-active': lowSanity }">
    <header class="game-header">
      <span class="header-title">
        AI TRPG: {{ store.scenarioTitle || "Game" }}
      </span>
      <span class="header-actions">
        <button class="save-btn" @click="handleSave">SAVE</button>
      </span>
      <span class="header-status">
        <span :class="store.connected ? 'online' : 'offline'">
          {{ store.connected ? "ONLINE" : "OFFLINE" }}
        </span>
        | {{ store.phase }}
      </span>
    </header>

    <div class="game-body">
      <div class="main-column">
        <NarrativePanel :entries="store.narrativeLog" />
        <ActionInput @send="handleSend" />
      </div>

      <div class="side-column">
        <CharacterSheet
          v-if="store.character"
          :character="store.character"
        />
        <CluePanel :clues="store.clues" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGameStore } from "~/stores/game";
import { useGameSocket } from "~/composables/useGameSocket";

const route = useRoute();
const store = useGameStore();
const sessionId = route.params.id as string;

const { connect, sendAction, saveGame, disconnect } = useGameSocket(sessionId);

const lowSanity = computed(() => {
  if (!store.character) return false;
  const { san, san_max } = store.character.derived;
  return san < san_max * 0.3;
});

function handleSend(text: string) {
  sendAction(text);
  store.addNarrative("system", `> ${text}`);
}

function handleSave() {
  saveGame("manual");
}

onMounted(() => {
  connect();
});

onUnmounted(() => {
  disconnect();
});
</script>

<style scoped>
.game-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}
.header-title {
  color: var(--text-amber);
  font-size: 16px;
}
.header-actions {
  display: flex;
  gap: 8px;
}
.save-btn {
  background: transparent;
  border: 1px solid var(--text-dim);
  color: var(--text-dim);
  padding: 2px 10px;
  font-family: inherit;
  font-size: 12px;
  cursor: pointer;
}
.save-btn:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}
.header-status {
  color: var(--text-dim);
  font-size: 14px;
}
.online { color: var(--text-primary); }
.offline { color: var(--text-red); }
.game-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}
.main-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.side-column {
  width: 300px;
  border-left: 1px solid var(--border-color);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
</style>
