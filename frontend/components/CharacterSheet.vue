<template>
  <div class="character-sheet panel">
    <div class="panel-title">// {{ character.name }}</div>
    <div v-if="character.occupation" class="occupation">{{ character.occupation }}</div>

    <!-- Vital bars -->
    <div class="stat-bar">
      <span class="stat-bar-label">HP</span>
      <div class="stat-bar-track">
        <div class="stat-bar-fill hp" :style="{ width: hpPct + '%' }" />
      </div>
      <span class="stat-bar-value">{{ character.derived.hp }}/{{ character.derived.hp_max }}</span>
    </div>
    <div class="stat-bar">
      <span class="stat-bar-label">SAN</span>
      <div class="stat-bar-track">
        <div class="stat-bar-fill san" :style="{ width: sanPct + '%' }" />
      </div>
      <span class="stat-bar-value">{{ character.derived.san }}/{{ character.derived.san_max }}</span>
    </div>
    <div class="stat-bar">
      <span class="stat-bar-label">MP</span>
      <div class="stat-bar-track">
        <div class="stat-bar-fill mp" :style="{ width: mpPct + '%' }" />
      </div>
      <span class="stat-bar-value">{{ character.derived.mp }}/{{ character.derived.mp_max }}</span>
    </div>

    <!-- Core characteristics -->
    <div class="section-label">ATTRIBUTES</div>
    <div class="attr-grid">
      <div v-for="(val, key) in attrs" :key="key" class="attr-cell">
        <span class="attr-key">{{ key }}</span>
        <span class="attr-val">{{ val }}</span>
      </div>
    </div>

    <!-- Derived extras -->
    <div class="derived-row">
      <span>LUCK {{ character.derived.luck }}</span>
      <span>DB {{ character.derived.damage_bonus }}</span>
      <span>MOV {{ character.derived.move_rate }}</span>
    </div>

    <!-- Key skills (non-default values) -->
    <div v-if="topSkills.length" class="section-label">SKILLS</div>
    <div v-if="topSkills.length" class="skills-list">
      <div v-for="s in topSkills" :key="s.name" class="skill-row">
        <span class="skill-name">{{ s.name }}</span>
        <span class="skill-val">{{ s.current_value }}</span>
      </div>
    </div>

    <!-- Inventory -->
    <div class="section-label">INVENTORY</div>
    <div v-if="character.inventory?.length" class="inventory-list">
      <div v-for="(item, i) in character.inventory" :key="i" class="inv-item">
        {{ item }}
      </div>
    </div>
    <div v-else class="empty-hint">Empty</div>

    <!-- Conditions -->
    <div v-if="character.conditions?.length" class="section-label">CONDITIONS</div>
    <div v-if="character.conditions?.length" class="conditions">
      <span v-for="c in character.conditions" :key="c" class="condition-tag">{{ c }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ character: any }>();

const hpPct = computed(() => (props.character.derived.hp / props.character.derived.hp_max) * 100);
const sanPct = computed(() => (props.character.derived.san / props.character.derived.san_max) * 100);
const mpPct = computed(() => (props.character.derived.mp / props.character.derived.mp_max) * 100);

const attrs = computed(() => {
  const c = props.character.characteristics;
  if (!c) return {};
  return { STR: c.STR, CON: c.CON, SIZ: c.SIZ, DEX: c.DEX, APP: c.APP, INT: c.INT, POW: c.POW, EDU: c.EDU };
});

const topSkills = computed(() => {
  const skills = props.character.skills;
  if (!skills) return [];
  return Object.values(skills)
    .filter((s: any) => s.current_value > s.base_value)
    .sort((a: any, b: any) => b.current_value - a.current_value)
    .slice(0, 12);
});
</script>

<style scoped>
.occupation {
  color: var(--text-dim);
  font-size: 14px;
  margin-bottom: 10px;
}
.section-label {
  color: var(--text-amber);
  font-size: 14px;
  margin-top: 12px;
  margin-bottom: 6px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 3px;
  letter-spacing: 2px;
}
.attr-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px 4px;
}
.attr-cell {
  text-align: center;
  padding: 4px 0;
  background: rgba(0, 255, 0, 0.03);
  border: 1px solid var(--border-color);
}
.attr-key {
  display: block;
  color: var(--text-dim);
  font-size: 12px;
}
.attr-val {
  font-size: 22px;
  color: var(--text-primary);
}
.derived-row {
  display: flex;
  justify-content: space-around;
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: 8px;
  padding: 6px 0;
  border-top: 1px solid var(--border-color);
}
.skills-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px 10px;
}
.skill-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  padding: 2px 0;
}
.skill-name { color: var(--text-secondary); }
.skill-val { color: var(--text-primary); }
.inventory-list {
  font-size: 14px;
  color: var(--text-secondary);
}
.inv-item {
  padding: 3px 0;
  border-bottom: 1px dotted var(--border-color);
}
.inv-item::before {
  content: "> ";
  color: var(--text-dim);
}
.empty-hint {
  color: var(--text-dim);
  font-size: 13px;
  font-style: italic;
}
.conditions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.condition-tag {
  font-size: 13px;
  padding: 2px 8px;
  border: 1px solid var(--text-red);
  color: var(--text-red);
}
</style>