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
const loading = ref(true);

onMounted(async () => {
  try {
    const data = await $fetch<any[]>(
      `${config.public.apiBase}/api/scenarios`
    );
    scenarios.value = data;
  } catch {
    scenarios.value = [];
  } finally {
    loading.value = false;
  }
});

async function selectScenario(s: any) {
  try {
    const session = await $fetch<any>(
      `${config.public.apiBase}/api/sessions`,
      { method: "POST", body: { scenario_id: s.id } }
    );
    router.push(`/session/${session.session_id}/setup`);
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
</style>
