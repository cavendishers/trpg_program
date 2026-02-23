<template>
  <div class="game-layout" :class="{ 'glitch-active': lowSanity }">
    <header class="game-header">
      <span class="header-title">
        AI TRPG: {{ store.scenarioTitle || "Game" }}
      </span>
      <span class="header-actions">
        <span v-if="store.turnState.mode === 'combat'" class="turn-badge combat">
          COMBAT R{{ store.turnState.round_number }}
        </span>
        <span v-else class="turn-badge explore">EXPLORE</span>
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
        <div v-if="store.turnState.mode === 'combat'" class="combat-queue">
          <span
            v-for="(cid, idx) in store.turnState.turn_queue"
            :key="cid"
            class="queue-slot"
            :class="{ 'queue-active': idx === store.turnState.current_index }"
          >{{ getCharName(cid) }}</span>
        </div>
        <div class="action-label">
          [ {{ store.activeCharacter?.name || '...' }} ] &gt;
        </div>
        <ActionInput @send="handleSend" />
      </div>

      <div class="side-column">
        <div
          v-for="char in store.party"
          :key="char.id"
          class="party-member"
          :class="{
            active: char.id === store.activeCharacterId,
            'combat-current': store.turnState.mode === 'combat' && char.id === store.turnState.turn_queue[store.turnState.current_index],
            'combat-disabled': store.turnState.mode === 'combat' && char.id !== store.turnState.turn_queue[store.turnState.current_index],
          }"
          @click="switchCharacter(char.id)"
        >
          <CharacterSheet
            v-if="char.id === store.activeCharacterId"
            :character="char"
          />
          <div v-else class="mini-card">
            <span class="mini-name">{{ char.name }}</span>
            <span class="mini-hp">HP {{ char.derived.hp }}/{{ char.derived.hp_max }}</span>
            <span class="mini-san">SAN {{ char.derived.san }}/{{ char.derived.san_max }}</span>
          </div>
        </div>
        <CluePanel :clues="store.clues" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGameStore } from "~/stores/game";
import { useGameSocket } from "~/composables/useGameSocket";

const config = useRuntimeConfig();
const route = useRoute();
const store = useGameStore();
const sessionId = route.params.id as string;

const { connect, sendAction, saveGame, disconnect } = useGameSocket(sessionId);

const lowSanity = computed(() => {
  const char = store.activeCharacter;
  if (!char) return false;
  const { san, san_max } = char.derived;
  return san < san_max * 0.3;
});

function handleSend(text: string) {
  sendAction(text);
  store.addNarrative("system", `> ${text}`);
}

function handleSave() {
  saveGame("manual");
}

function switchCharacter(id: string) {
  if (store.turnState.mode === "combat") return;
  store.setActiveCharacter(id);
}

function getCharName(id: string): string {
  return store.party.find((c) => c.id === id)?.name || id;
}

onMounted(async () => {
  // Track active session for smart resume on homepage
  localStorage.setItem("trpg_active_session", sessionId);

  // Fetch session state to populate character (critical for resume flow)
  try {
    const state = await $fetch<any>(
      `${config.public.apiBase}/api/sessions/${sessionId}/state`
    );
    if (state.party?.length > 0) {
      store.setParty(state.party);
    }
    if (state.phase) {
      store.updatePhase(state.phase);
    }
  } catch {
    // Session state fetch failed, WebSocket will still work
  }
  connect();
});

onUnmounted(() => {
  localStorage.removeItem("trpg_active_session");
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
  font-size: 18px;
  letter-spacing: 1px;
}
.header-actions {
  display: flex;
  gap: 8px;
}
.save-btn {
  background: transparent;
  border: 1px solid var(--text-dim);
  color: var(--text-dim);
  padding: 4px 14px;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
}
.save-btn:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}
.header-status {
  color: var(--text-dim);
  font-size: 16px;
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
  width: 360px;
  border-left: 1px solid var(--border-color);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.party-member {
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
}
.party-member.active {
  border-left: 3px solid var(--accent);
}
.mini-card {
  padding: 10px 14px;
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 14px;
}
.mini-card:hover {
  background: var(--bg-secondary);
}
.mini-name {
  color: var(--text-primary);
  flex: 1;
}
.mini-hp {
  color: var(--text-red);
}
.mini-san {
  color: #6666ff;
}
.turn-badge {
  padding: 2px 10px;
  font-size: 13px;
  letter-spacing: 1px;
}
.turn-badge.combat {
  color: var(--text-red);
  border: 1px solid var(--text-red);
}
.turn-badge.explore {
  color: var(--text-primary);
  border: 1px solid var(--text-dim);
}
.combat-queue {
  display: flex;
  gap: 4px;
  padding: 6px 16px;
  background: rgba(255, 50, 50, 0.08);
  border-top: 1px solid var(--border-color);
  overflow-x: auto;
}
.queue-slot {
  padding: 3px 10px;
  font-size: 13px;
  color: var(--text-dim);
  border: 1px solid var(--border-color);
  white-space: nowrap;
}
.queue-slot.queue-active {
  color: var(--text-amber);
  border-color: var(--text-amber);
  background: rgba(255, 170, 0, 0.1);
}
.action-label {
  padding: 4px 16px 0;
  color: var(--text-amber);
  font-size: 14px;
}
.combat-current {
  border-left: 3px solid var(--text-red) !important;
}
.combat-disabled {
  opacity: 0.5;
  cursor: not-allowed !important;
}
</style>
