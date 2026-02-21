<template>
  <div class="setup">
    <div class="panel">
      <div class="panel-title">// CHARACTER CREATION</div>
      <div class="form-group">
        <label>Name</label>
        <input v-model="charName" placeholder="Enter investigator name" />
      </div>
      <div class="form-group">
        <label>Player</label>
        <input v-model="playerName" placeholder="Your name" />
      </div>
      <div class="form-group">
        <label>Occupation</label>
        <input v-model="occupation" placeholder="e.g. 侦探, 记者, 教授" />
      </div>
      <button class="create-btn" @click="createCharacter" :disabled="creating">
        {{ creating ? "CREATING..." : "> CREATE INVESTIGATOR" }}
      </button>
    </div>

    <div v-if="character" class="panel character-preview">
      <div class="panel-title">// {{ character.name }}</div>
      <div class="stats">
        <div class="stat" v-for="(v, k) in mainStats" :key="k">
          <span class="stat-label">{{ k }}</span>
          <span class="stat-value">{{ v }}</span>
        </div>
      </div>
      <div class="derived">
        HP: {{ character.derived.hp }} |
        SAN: {{ character.derived.san }} |
        MP: {{ character.derived.mp }} |
        LUCK: {{ character.derived.luck }}
      </div>
      <button class="start-btn" @click="startGame">
        > BEGIN INVESTIGATION
      </button>
    </div>
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
const playerName = ref("Player 1");
const occupation = ref("侦探");
const creating = ref(false);
const character = ref<any>(null);

const mainStats = computed(() => {
  if (!character.value) return {};
  const c = character.value.characteristics;
  return { STR: c.STR, CON: c.CON, SIZ: c.SIZ, DEX: c.DEX, APP: c.APP, INT: c.INT, POW: c.POW, EDU: c.EDU };
});

async function createCharacter() {
  creating.value = true;
  try {
    const data = await $fetch<any>(
      `${config.public.apiBase}/api/characters`,
      {
        method: "POST",
        body: {
          name: charName.value,
          player_name: playerName.value,
          occupation: occupation.value,
        },
      }
    );
    character.value = data;
    store.setCharacter(data);
  } catch (e) {
    console.error("Failed to create character:", e);
  } finally {
    creating.value = false;
  }
}

async function startGame() {
  try {
    await $fetch(`${config.public.apiBase}/api/sessions/${sessionId}/start`, {
      method: "POST",
    });
    store.setSession(sessionId, "");
    router.push(`/session/${sessionId}/game`);
  } catch (e) {
    console.error("Failed to start game:", e);
  }
}
</script>

<style scoped>
.setup {
  max-width: 600px;
  margin: 40px auto;
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.form-group {
  margin: 12px 0;
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
.create-btn, .start-btn {
  width: 100%;
  margin-top: 12px;
  padding: 12px;
  font-size: 20px;
}
.start-btn {
  color: var(--text-amber);
  border-color: var(--text-amber);
}
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin: 12px 0;
}
.stat {
  text-align: center;
}
.stat-label {
  display: block;
  color: var(--text-dim);
  font-size: 12px;
}
.stat-value {
  font-size: 24px;
  color: var(--text-primary);
}
.derived {
  color: var(--text-secondary);
  text-align: center;
  margin: 8px 0;
}
</style>
