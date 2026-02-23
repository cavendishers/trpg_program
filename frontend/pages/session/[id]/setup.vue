<template>
  <div class="setup">
    <div class="panel scenario-info" v-if="scenarioTitle">
      <div class="panel-title">// {{ scenarioTitle }}</div>
      <div class="scenario-hint">
        Recommended: {{ playerMin }}-{{ playerMax }} investigators
      </div>
    </div>

    <div class="panel">
      <div class="panel-title">// CREATE INVESTIGATOR</div>
      <div class="form-row">
        <div class="form-group">
          <label>Name</label>
          <input v-model="charName" placeholder="调查员名" />
        </div>
        <div class="form-group">
          <label>Occupation</label>
          <input v-model="occupation" placeholder="侦探, 记者, 教授..." />
        </div>
        <button class="add-btn" @click="addCharacter" :disabled="creating">
          {{ creating ? "..." : "+ ADD" }}
        </button>
      </div>
      <div class="divider"></div>
      <div class="gen-row">
        <span class="gen-label">AI Quick Generate</span>
        <input
          v-model.number="genCount"
          type="number"
          min="1"
          max="6"
          class="gen-input"
        />
        <button class="gen-btn" @click="generateParty" :disabled="generating">
          {{ generating ? "GENERATING..." : "> GENERATE TEAM" }}
        </button>
      </div>
    </div>

    <div v-if="party.length > 0" class="panel">
      <div class="panel-title">// PARTY ({{ party.length }})</div>
      <div v-for="c in party" :key="c.id" class="char-card">
        <div class="char-header">
          <span class="char-name">{{ c.name }}</span>
          <span class="char-occ">{{ c.occupation }}</span>
          <button class="del-btn" @click="removeCharacter(c.id)">X</button>
        </div>
        <div class="char-stats">
          <span>STR {{ c.characteristics?.STR }}</span>
          <span>CON {{ c.characteristics?.CON }}</span>
          <span>DEX {{ c.characteristics?.DEX }}</span>
          <span>INT {{ c.characteristics?.INT }}</span>
          <span>HP {{ c.derived.hp }}</span>
          <span>SAN {{ c.derived.san }}</span>
        </div>
      </div>
    </div>

    <button
      class="start-btn"
      :disabled="party.length === 0"
      @click="startGame"
    >
      > BEGIN INVESTIGATION
    </button>
  </div>
</template>

<script setup lang="ts">
import { useGameStore } from "~/stores/game";

const config = useRuntimeConfig();
const route = useRoute();
const router = useRouter();
const store = useGameStore();

const sessionId = route.params.id as string;
const charName = ref("调查员");
const occupation = ref("侦探");
const creating = ref(false);
const generating = ref(false);
const genCount = ref(3);
const party = ref<any[]>([]);
const scenarioTitle = ref("");
const playerMin = ref(1);
const playerMax = ref(4);

onMounted(async () => {
  try {
    const session = await $fetch<any>(
      `${config.public.apiBase}/api/sessions/${sessionId}`
    );
    const scenarios = await $fetch<any[]>(
      `${config.public.apiBase}/api/scenarios`
    );
    const sc = scenarios.find((s: any) => s.id === session.scenario_id);
    if (sc) {
      scenarioTitle.value = sc.title;
      playerMin.value = sc.player_count?.min || 1;
      playerMax.value = sc.player_count?.max || 4;
    }
  } catch {}
  try {
    const chars = await $fetch<any[]>(
      `${config.public.apiBase}/api/sessions/${sessionId}/characters`
    );
    party.value = chars;
  } catch {}
});

async function addCharacter() {
  creating.value = true;
  try {
    const data = await $fetch<any>(
      `${config.public.apiBase}/api/sessions/${sessionId}/characters`,
      {
        method: "POST",
        body: { name: charName.value, occupation: occupation.value },
      }
    );
    party.value.push(data);
    charName.value = "调查员";
    occupation.value = "";
  } catch (e) {
    console.error("Failed to create character:", e);
  } finally {
    creating.value = false;
  }
}

async function generateParty() {
  generating.value = true;
  try {
    const chars = await $fetch<any[]>(
      `${config.public.apiBase}/api/sessions/${sessionId}/characters/generate`,
      { method: "POST", body: { count: genCount.value } }
    );
    party.value.push(...chars);
  } catch (e) {
    console.error("Failed to generate party:", e);
  } finally {
    generating.value = false;
  }
}

async function removeCharacter(charId: string) {
  try {
    await $fetch(
      `${config.public.apiBase}/api/sessions/${sessionId}/characters/${charId}`,
      { method: "DELETE" }
    );
    party.value = party.value.filter((c: any) => c.id !== charId);
  } catch (e) {
    console.error("Failed to remove character:", e);
  }
}

async function startGame() {
  try {
    await $fetch(`${config.public.apiBase}/api/sessions/${sessionId}/start`, {
      method: "POST",
    });
    store.setParty(party.value);
    store.setSession(sessionId, scenarioTitle.value);
    router.push(`/session/${sessionId}/game`);
  } catch (e) {
    console.error("Failed to start game:", e);
  }
}
</script>

<style scoped>
.setup {
  max-width: 700px;
  margin: 40px auto;
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.scenario-info {
  text-align: center;
}
.scenario-hint {
  color: var(--text-dim);
  font-size: 14px;
  margin-top: 4px;
}
.form-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}
.form-group {
  flex: 1;
}
.form-group label {
  display: block;
  color: var(--text-amber);
  font-size: 14px;
  margin-bottom: 4px;
}
.form-group input {
  width: 100%;
}
.add-btn {
  padding: 8px 16px;
  font-size: 18px;
  white-space: nowrap;
}
.divider {
  border-top: 1px solid var(--border-color);
  margin: 12px 0;
}
.gen-row {
  display: flex;
  gap: 10px;
  align-items: center;
}
.gen-label {
  color: var(--text-dim);
  font-size: 14px;
}
.gen-input {
  width: 50px;
  text-align: center;
}
.gen-btn {
  flex: 1;
  padding: 8px 16px;
  color: var(--text-amber);
  border-color: var(--text-amber);
}
.char-card {
  padding: 10px;
  margin: 6px 0;
  border: 1px solid var(--border-color);
}
.char-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.char-name {
  color: var(--text-primary);
  font-size: 18px;
}
.char-occ {
  color: var(--text-dim);
  font-size: 14px;
  flex: 1;
}
.del-btn {
  background: transparent;
  border: 1px solid var(--text-dim);
  color: var(--text-dim);
  font-size: 14px;
  padding: 2px 8px;
  cursor: pointer;
}
.del-btn:hover {
  border-color: var(--text-red);
  color: var(--text-red);
}
.char-stats {
  display: flex;
  gap: 12px;
  margin-top: 6px;
  color: var(--text-secondary);
  font-size: 14px;
}
.start-btn {
  width: 100%;
  padding: 14px;
  font-size: 22px;
  color: var(--text-amber);
  border-color: var(--text-amber);
}
.start-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
@media (max-width: 768px) {
  .setup-page { padding: 16px 12px; }
  .scenario-info { font-size: 14px; }
  .form-row { flex-direction: column; }
  .form-row input { width: 100%; }
  .gen-row { flex-direction: column; }
  .gen-row input { width: 100%; }
  .start-btn { font-size: 18px; padding: 12px; position: sticky; bottom: 0; background: var(--bg-primary); }
}
</style>
