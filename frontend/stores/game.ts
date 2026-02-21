import { defineStore } from "pinia";

interface Character {
  id: string;
  name: string;
  is_npc: boolean;
  occupation?: string;
  characteristics?: {
    STR: number; CON: number; SIZ: number; DEX: number;
    APP: number; INT: number; POW: number; EDU: number;
  };
  derived: {
    hp: number;
    hp_max: number;
    san: number;
    san_max: number;
    mp: number;
    mp_max: number;
    luck: number;
    damage_bonus?: string;
    build?: number;
    move_rate?: number;
  };
  skills: Record<string, { name: string; base_value: number; current_value: number }>;
  inventory: string[];
  conditions: string[];
}

interface NarrativeEntry {
  type: "narrative" | "dice_result" | "system";
  content: string;
  timestamp: number;
}

interface GameState {
  sessionId: string;
  scenarioTitle: string;
  phase: string;
  character: Character | null;
  narrativeLog: NarrativeEntry[];
  clues: string[];
  atmosphere: string;
  connected: boolean;
}

export const useGameStore = defineStore("game", {
  state: (): GameState => ({
    sessionId: "",
    scenarioTitle: "",
    phase: "lobby",
    character: null,
    narrativeLog: [],
    clues: [],
    atmosphere: "calm",
    connected: false,
  }),
  actions: {
    setSession(id: string, title: string) {
      this.sessionId = id;
      this.scenarioTitle = title;
    },
    setCharacter(char: Character) {
      this.character = char;
    },
    addNarrative(type: NarrativeEntry["type"], content: string) {
      this.narrativeLog.push({ type, content, timestamp: Date.now() });
    },
    addClue(clue: string) {
      if (!this.clues.includes(clue)) this.clues.push(clue);
    },
    updateAtmosphere(atm: string) {
      this.atmosphere = atm;
    },
    updatePhase(phase: string) {
      this.phase = phase;
    },
    setConnected(val: boolean) {
      this.connected = val;
    },
  },
});
