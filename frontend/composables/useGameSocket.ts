import { useGameStore } from "~/stores/game";

export function useGameSocket(sessionId: string) {
  const config = useRuntimeConfig();
  const store = useGameStore();
  let ws: WebSocket | null = null;

  function handleBeforeUnload() {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "save_game", slot: "auto" }));
    }
  }

  function connect() {
    const url = `${config.public.wsBase}/api/game/${sessionId}/ws`;
    ws = new WebSocket(url);

    ws.onopen = () => {
      store.setConnected(true);
    };

    ws.onclose = () => {
      store.setConnected(false);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleMessage(data);
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
  }

  function handleMessage(data: any) {
    switch (data.type) {
      case "narrative":
        store.addNarrative("narrative", data.content);
        break;
      case "dice_result":
        store.addNarrative(
          "dice_result",
          data.description || `Roll: ${data.roll}/${data.target}`
        );
        break;
      case "npc_action":
        store.addNarrative("narrative", `[${data.npc_id}] ${data.content}`);
        break;
      case "clue_discovered":
        store.addClue(data.description || data.clue_id);
        break;
      case "state_update":
        if (data.phase) store.updatePhase(data.phase);
        if (data.atmosphere) store.updateAtmosphere(data.atmosphere);
        break;
      case "system":
        store.addNarrative("system", data.content);
        break;
      case "error":
        store.addNarrative("system", `Error: ${data.content}`);
        break;
    }
  }

  function sendAction(content: string) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(
      JSON.stringify({
        type: "player_action",
        character_id: store.activeCharacter?.id || "",
        content,
      })
    );
  }

  function saveGame(slot: string = "manual") {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: "save_game", slot }));
  }

  function disconnect() {
    window.removeEventListener("beforeunload", handleBeforeUnload);
    ws?.close();
    ws = null;
  }

  return { connect, sendAction, saveGame, disconnect };
}
