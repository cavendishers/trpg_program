<template>
  <div class="home">
    <div class="title-block">
      <pre class="ascii-title">
 █████╗ ██╗    ████████╗██████╗ ██████╗  ██████╗
██╔══██╗██║    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝
███████║██║       ██║   ██████╔╝██████╔╝██║  ███╗
██╔══██║██║       ██║   ██╔══██╗██╔═══╝ ██║   ██║
██║  ██║██║       ██║   ██║  ██║██║     ╚██████╔╝
╚═╝  ╚═╝╚═╝       ╚═╝   ╚═╝  ╚═╝╚═╝      ╚═════╝
      </pre>
      <p class="subtitle">Call of Cthulhu 7e - AI Keeper</p>
    </div>

    <div v-if="saves.length > 0" class="saves-section panel">
      <div class="panel-title">// CONTINUE GAME</div>
      <div
        v-for="s in saves"
        :key="s.filename"
        class="save-card"
        @click="resumeGame(s)"
      >
        <div class="save-header">
          <div class="save-title">{{ s.scenario_title || s.scenario_id }}</div>
          <button class="delete-btn" @click.stop="deleteSave(s)" title="Delete save">X</button>
        </div>
        <div class="save-meta">
          {{ s.characters.join(', ') || 'No character' }} | {{ s.phase }} | {{ s.slot }}
        </div>
        <div class="save-time">{{ formatTime(s.modified) }}</div>
      </div>
    </div>

    <div class="scenarios-section panel">
      <div class="panel-title">// SELECT SCENARIO</div>
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="scenarios.length === 0" class="empty">
        No scenarios found.
      </div>
      <div
        v-for="s in scenarios"
        :key="s.id"
        class="scenario-card"
        @click="selectScenario(s)"
      >
        <div class="scenario-title">{{ s.title }}</div>
        <div class="scenario-meta">
          {{ s.era }} | {{ s.difficulty }} |
          {{ s.player_count?.min }}-{{ s.player_count?.max }} players
        </div>
        <div class="scenario-synopsis">{{ s.synopsis }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const router = useRouter();

const scenarios = ref<any[]>([]);
const saves = ref<any[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const [scenarioData, saveData] = await Promise.all([
      $fetch<any[]>(`${config.public.apiBase}/api/scenarios`).catch(() => []),
      $fetch<any>(`${config.public.apiBase}/api/saves`).catch(() => ({ saves: [] })),
    ]);
    scenarios.value = scenarioData;
    saves.value = saveData.saves || [];
  } finally {
    loading.value = false;
  }
});

function formatTime(ts: number) {
  return new Date(ts * 1000).toLocaleString();
}

async function resumeGame(save: any) {
  try {
    const result = await $fetch<any>(
      `${config.public.apiBase}/api/sessions/resume`,
      { method: "POST", body: { filename: save.filename } }
    );
    router.push(`/session/${result.session_id}/game`);
  } catch (e) {
    console.error("Failed to resume:", e);
  }
}

async function deleteSave(save: any) {
  if (!confirm(`Delete save "${save.scenario_title || save.filename}"?`)) return;
  try {
    await $fetch(`${config.public.apiBase}/api/saves/${save.filename}`, {
      method: "DELETE",
    });
    saves.value = saves.value.filter((s: any) => s.filename !== save.filename);
  } catch (e) {
    console.error("Failed to delete save:", e);
  }
}

async function selectScenario(s: any) {
  try {
    const session = await $fetch<any>(
      `${config.public.apiBase}/api/sessions`,
      { method: "POST", body: { scenario_id: s.id } }
    );
    if (session.resumed) {
      router.push(`/session/${session.session_id}/game`);
    } else {
      router.push(`/session/${session.session_id}/setup`);
    }
  } catch (e) {
    console.error("Failed to create session:", e);
  }
}
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}
.title-block {
  text-align: center;
  margin-bottom: 40px;
}
.ascii-title {
  color: var(--text-primary);
  font-size: 10px;
  line-height: 1.1;
  overflow: hidden;
}
.subtitle {
  color: var(--text-amber);
  font-size: 22px;
  margin-top: 12px;
}
.scenario-card {
  padding: 12px;
  margin: 8px 0;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.15s;
}
.scenario-card:hover {
  border-color: var(--accent);
  background: var(--bg-secondary);
}
.scenario-title {
  color: var(--text-amber);
  font-size: 22px;
}
.scenario-meta {
  color: var(--text-dim);
  font-size: 14px;
  margin: 4px 0;
}
.scenario-synopsis {
  color: var(--text-secondary);
  font-size: 16px;
}
.loading, .empty {
  color: var(--text-dim);
  padding: 20px;
  text-align: center;
}
.saves-section {
  margin-bottom: 24px;
}
.save-card {
  padding: 12px;
  margin: 8px 0;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.15s;
}
.save-card:hover {
  border-color: var(--text-primary);
  background: var(--bg-secondary);
}
.save-title {
  color: var(--text-primary);
  font-size: 18px;
}
.save-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.delete-btn {
  background: transparent;
  border: 1px solid var(--text-dim);
  color: var(--text-dim);
  font-family: inherit;
  font-size: 14px;
  padding: 2px 8px;
  cursor: pointer;
}
.delete-btn:hover {
  border-color: var(--text-red);
  color: var(--text-red);
}
.save-meta {
  color: var(--text-dim);
  font-size: 14px;
  margin: 4px 0;
}
.save-time {
  color: var(--text-dim);
  font-size: 12px;
}
</style>
