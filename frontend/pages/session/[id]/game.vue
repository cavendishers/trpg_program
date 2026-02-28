<template>
  <div class="game-layout" :class="{ 'glitch-active': lowSanity }">
    <header class="game-header">
      <span class="header-title">
        <span class="title-full">AI TRPG: {{ store.scenarioTitle || "Game" }}</span>
        <span class="title-short">{{ store.scenarioTitle || "TRPG" }}</span>
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
          {{ store.connected ? "ON" : "OFF" }}
        </span>
      </span>
    </header>

    <div class="game-body">
      <div class="main-column">
        <NarrativePanel :entries="store.narrativeLog" />
        <div v-if="store.turnState.mode === 'combat' && !isMobile" class="combat-queue">
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
        <ActionInput @send="handleSend" @focus="onInputFocus" @blur="onInputBlur" />
      </div>

      <div
        class="side-column"
        :class="{ 'is-collapsed': isMobile && isBottomCollapsed }"
      >
        <!-- Mobile tab bar -->
        <div v-if="isMobile" class="mobile-tab-bar" role="tablist">
          <button
            role="tab" :aria-selected="activeTab === 'character'"
            class="tab-btn" :class="{ active: activeTab === 'character' }"
            @click="setTab('character')"
          >[ 角色 ]</button>
          <button
            role="tab" :aria-selected="activeTab === 'clues'"
            class="tab-btn" :class="{ active: activeTab === 'clues' }"
            @click="setTab('clues')"
          >[ 线索 ]</button>
          <button
            v-if="store.turnState.mode === 'combat'"
            role="tab" :aria-selected="activeTab === 'combat'"
            class="tab-btn" :class="{ active: activeTab === 'combat' }"
            @click="setTab('combat')"
          >[ 战斗 ]</button>
          <button
            class="tab-collapse"
            aria-label="Toggle bottom panel"
            :aria-expanded="!isBottomCollapsed"
            @click="isBottomCollapsed = !isBottomCollapsed"
          >
            {{ isBottomCollapsed ? '[ + ]' : '[ _ ]' }}
          </button>
        </div>

        <!-- Tab content -->
        <div v-show="!isMobile || !isBottomCollapsed" class="tab-content">
          <!-- Character tab (or desktop default) -->
          <div v-show="!isMobile || activeTab === 'character'">
            <div
              v-for="char in store.party"
              :key="char.id"
              class="party-member"
              :class="{
                active: char.id === store.activeCharacterId,
                'combat-current': isCombatActor(char.id),
                'combat-disabled': isCombatDisabled(char.id),
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
          </div>

          <!-- Clues tab -->
          <div v-show="!isMobile || activeTab === 'clues'">
            <CluePanel :clues="store.clues" />
          </div>

          <!-- Combat tab (mobile only) -->
          <div v-if="isMobile && activeTab === 'combat'" class="mobile-combat-panel">
            <div class="combat-queue mobile">
              <span
                v-for="(cid, idx) in store.turnState.turn_queue"
                :key="cid"
                class="queue-slot"
                :class="{ 'queue-active': idx === store.turnState.current_index }"
              >{{ getCharName(cid) }}</span>
            </div>
            <div class="combat-info">
              Round {{ store.turnState.round_number }}
            </div>
          </div>
        </div>
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

const isMobile = ref(false);
const activeTab = ref<"character" | "clues" | "combat">("character");
const isBottomCollapsed = ref(false);

function checkMobile() {
  isMobile.value = window.innerWidth <= 768;
}

const lowSanity = computed(() => {
  const char = store.activeCharacter;
  if (!char) return false;
  const { san, san_max } = char.derived;
  return san < san_max * 0.3;
});

function isCombatActor(id: string): boolean {
  return store.turnState.mode === "combat"
    && id === store.turnState.turn_queue[store.turnState.current_index];
}

function isCombatDisabled(id: string): boolean {
  return store.turnState.mode === "combat" && !isCombatActor(id);
}

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

function setTab(tab: "character" | "clues" | "combat") {
  activeTab.value = tab;
  isBottomCollapsed.value = false;
}

watch(
  () => store.turnState.mode,
  (newMode) => {
    if (newMode !== "combat" && activeTab.value === "combat") {
      activeTab.value = "character";
    }
  }
);

function onInputFocus() {
  if (isMobile.value) isBottomCollapsed.value = true;
}

function onInputBlur() {
  if (isMobile.value) isBottomCollapsed.value = false;
}

onMounted(async () => {
  checkMobile();
  window.addEventListener("resize", checkMobile);

  localStorage.setItem("trpg_active_session", sessionId);

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
  window.removeEventListener("resize", checkMobile);
  localStorage.removeItem("trpg_active_session");
  disconnect();
});
</script>

<style scoped>
.game-layout {
  height: 100dvh;
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
.header-title { color: var(--text-amber); font-size: 18px; letter-spacing: 1px; }
.title-short { display: none; }
.header-actions { display: flex; gap: 8px; }
.save-btn {
  background: transparent;
  border: 1px solid var(--text-dim);
  color: var(--text-dim);
  padding: 4px 14px;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
}
.save-btn:hover { border-color: var(--text-primary); color: var(--text-primary); }
.header-status { color: var(--text-dim); font-size: 16px; }
.online { color: var(--text-primary); }
.offline { color: var(--text-red); }
.game-body { flex: 1; display: flex; overflow: hidden; min-height: 0; }
.main-column { flex: 1; display: flex; flex-direction: column; min-width: 0; min-height: 0; }
.side-column {
  width: 360px;
  border-left: 1px solid var(--border-color);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.party-member { cursor: pointer; border-bottom: 1px solid var(--border-color); }
.party-member.active { border-left: 3px solid var(--accent); }
.mini-card { padding: 10px 14px; display: flex; gap: 12px; align-items: center; font-size: 14px; }
.mini-card:hover { background: var(--bg-secondary); }
.mini-name { color: var(--text-primary); flex: 1; }
.mini-hp { color: var(--text-red); }
.mini-san { color: #6666ff; }
.turn-badge { padding: 2px 10px; font-size: 13px; letter-spacing: 1px; }
.turn-badge.combat { color: var(--text-red); border: 1px solid var(--text-red); }
.turn-badge.explore { color: var(--text-primary); border: 1px solid var(--text-dim); }
.combat-queue {
  display: flex; gap: 4px; padding: 6px 16px;
  background: rgba(255, 50, 50, 0.08);
  border-top: 1px solid var(--border-color);
  overflow-x: auto;
}
.queue-slot {
  padding: 3px 10px; font-size: 13px; color: var(--text-dim);
  border: 1px solid var(--border-color); white-space: nowrap;
}
.queue-slot.queue-active {
  color: var(--text-amber); border-color: var(--text-amber);
  background: rgba(255, 170, 0, 0.1);
}
.action-label { padding: 4px 16px 0; color: var(--text-amber); font-size: 14px; }
.combat-current { border-left: 3px solid var(--text-red) !important; }
.combat-disabled { opacity: 0.5; cursor: not-allowed !important; }

/* Mobile tab bar (hidden on desktop) */
.mobile-tab-bar { display: none; }
.tab-content { flex: 1; overflow-y: auto; }

/* Mobile combat panel */
.mobile-combat-panel { padding: 10px; }
.combat-queue.mobile { flex-wrap: wrap; }
.combat-info { color: var(--text-amber); font-size: 14px; margin-top: 8px; }

/* ===== Mobile breakpoint ===== */
@media (max-width: 768px) {
  .title-full { display: none; }
  .title-short { display: inline; }
  .header-title { font-size: 16px; }
  .game-header { padding: 6px 10px; }

  .game-body { flex-direction: column; }

  .main-column { flex: 1 1 65%; }

  .side-column {
    width: 100%;
    flex: 0 0 35%;
    border-left: none;
    border-top: 1px solid var(--border-color);
    transition: flex 0.2s ease;
  }
  .side-column.is-collapsed {
    flex: 0 0 40px;
    overflow: hidden;
  }

  .mobile-tab-bar {
    display: flex;
    gap: 0;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-secondary);
    min-height: 40px;
    align-items: center;
  }
  .tab-btn {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-dim);
    font-family: inherit;
    font-size: 14px;
    padding: 8px 4px;
    cursor: pointer;
    min-height: 40px;
  }
  .tab-btn.active {
    color: var(--bg-primary);
    background: var(--text-primary);
  }
  .tab-collapse {
    background: transparent;
    border: none;
    color: var(--text-dim);
    font-family: inherit;
    font-size: 14px;
    padding: 8px;
    cursor: pointer;
    min-height: 40px;
  }
}
</style>
