"""5-layer prompt builder for the AI KP."""

from backend.ai.providers.base import AIMessage
from backend.character.models import CoCCharacter
from backend.scenario.models import Scenario


KP_SYSTEM_PROMPT = """你是一位经验丰富的 CoC 7e 守密人（KP）。你的职责是：
1. 根据剧本设定主持游戏，营造恐怖氛围
2. 扮演 NPC，推动剧情发展
3. 描述场景和事件，回应玩家行动
4. 在需要时请求技能检定（你不能自己掷骰）
5. 当玩家获得关键信息时，用 clue_discovered 标记线索发现
6. 管理多角色回合：在战斗时切换战斗模式，在探索时可叫停角色切换

你必须以 JSON 格式回复，包含以下字段：
{
  "narrative": "你的叙事描述文本",
  "game_directives": [
    {"type": "skill_check", "skill": "技能名", "difficulty": "regular/hard/extreme", "reason": "原因"},
    {"type": "san_check", "san_loss_success": "0", "san_loss_failure": "1d6", "reason": "原因"},
    {"type": "clue_discovered", "clue_id": "线索ID", "reason": "发现方式"},
    {"type": "mode_switch", "mode": "combat/exploration", "reason": "切换原因"},
    {"type": "switch_character", "next_character_id": "角色ID", "reason": "切换原因"},
    {"type": "grant_extra_action", "target_character": "角色ID", "action_count": 1, "reason": "原因"}
  ],
  "npc_actions": [
    {"npc_id": "npc标识", "action": "dialogue/move/attack", "content": "内容"}
  ],
  "atmosphere": "calm/tense/tension_rising/horror/panic"
}

规则：
- 你是叙事者，不是规则裁判。需要掷骰时用 game_directives 请求
- narrative 中不要包含骰子结果，等系统返回结果后再继续叙事
- 保持克苏鲁风格：未知、渐进恐怖、理智的脆弱
- game_directives 可以为空数组（纯叙事时）
- npc_actions 可以为空数组（无 NPC 行动时）
- 当玩家通过对话、调查等方式获得了关键信息，必须在 game_directives 中加入 clue_discovered
- clue_id 必须使用剧本中定义的线索 ID（见下方线索清单）
- 遇到战斗场景时，发出 mode_switch 切换到 combat 模式；战斗结束后切回 exploration
- 探索模式下，如果某角色行动过于离谱或需要换人，可用 switch_character 切换
- switch_character 的 next_character_id 必须是队伍中存在的角色 ID"""


def build_messages(
    scenario: Scenario,
    characters: list[CoCCharacter],
    plot_progress: str,
    history: list[dict],
    player_input: str,
    max_history: int = 20,
    turn_state: dict | None = None,
) -> list[AIMessage]:
    """Build the 5-layer prompt for the AI KP."""
    messages: list[AIMessage] = []

    # Layer 1: KP persona + rules (system)
    messages.append(AIMessage(role="system", content=KP_SYSTEM_PROMPT))

    # Layer 2: Scenario context
    scenario_ctx = _build_scenario_context(scenario, characters)
    messages.append(AIMessage(role="system", content=scenario_ctx))

    # Layer 3: Plot progress + turn state
    if plot_progress:
        messages.append(AIMessage(role="system", content=plot_progress))

    if turn_state:
        turn_ctx = _build_turn_context(turn_state, characters)
        if turn_ctx:
            messages.append(AIMessage(role="system", content=turn_ctx))

    # Layer 4: Conversation history (sliding window)
    trimmed = history[-max_history:] if len(history) > max_history else history
    for entry in trimmed:
        messages.append(AIMessage(role=entry["role"], content=entry["content"]))

    # Layer 5: Current player input
    messages.append(AIMessage(role="user", content=player_input))

    return messages


def _build_scenario_context(
    scenario: Scenario, characters: list[CoCCharacter]
) -> str:
    parts = [
        f"[剧本] {scenario.meta.title}",
        f"时代：{scenario.meta.era}",
        f"[KP 指南] {scenario.keeper_guide}",
    ]

    # Active NPCs
    if scenario.npcs:
        npc_lines = []
        for npc_id, npc in scenario.npcs.items():
            npc_lines.append(
                f"- {npc.name}({npc_id}): {npc.personality}. "
                f"知道: {', '.join(npc.knows[:3])}"
            )
        parts.append("[NPC]\n" + "\n".join(npc_lines))

    # Current location info
    if scenario.locations:
        loc_lines = []
        for loc_id, loc in scenario.locations.items():
            loc_lines.append(f"- {loc.name}: {loc.atmosphere}")
        parts.append("[地点]\n" + "\n".join(loc_lines))

    # Character summary
    if characters:
        char_lines = []
        for c in characters:
            char_lines.append(
                f"- {c.name}: HP {c.derived.hp}/{c.derived.hp_max}, "
                f"SAN {c.derived.san}/{c.derived.san_max}, "
                f"MP {c.derived.mp}/{c.derived.mp_max}"
            )
        parts.append("[调查员状态]\n" + "\n".join(char_lines))

    # Available clues (so AI knows valid clue_ids)
    if scenario.clues:
        clue_lines = []
        for clue_id, clue in scenario.clues.items():
            clue_lines.append(
                f"- {clue_id}: {clue.description} (重要性: {clue.importance}, 发现方式: {clue.discovery})"
            )
        parts.append("[线索清单 - 使用这些 clue_id]\n" + "\n".join(clue_lines))

    return "\n\n".join(parts)


def _build_turn_context(
    turn_state: dict, characters: list[CoCCharacter]
) -> str:
    """Build turn state context for the AI KP."""
    mode = turn_state.get("mode", "exploration")
    char_map = {c.id: c.name for c in characters}

    if mode == "combat":
        queue = turn_state.get("turn_queue", [])
        current_idx = turn_state.get("current_index", 0)
        round_num = turn_state.get("round_number", 1)
        actions = turn_state.get("actions_remaining", {})

        order_lines = []
        for i, cid in enumerate(queue):
            name = char_map.get(cid, cid)
            marker = " ← 当前行动" if i == current_idx else ""
            remaining = actions.get(cid, 0)
            order_lines.append(f"  {i+1}. {name} (剩余行动: {remaining}){marker}")

        return (
            f"[回合状态] 战斗模式 - 第 {round_num} 轮\n"
            f"行动顺序（按 DEX 降序）：\n"
            + "\n".join(order_lines)
            + "\n只有当前行动角色可以执行操作。"
        )
    else:
        active_id = turn_state.get("active_character_id")
        active_name = char_map.get(active_id, "未指定") if active_id else "未指定"
        party_names = [char_map.get(cid, cid) for cid in char_map]
        return (
            f"[回合状态] 探索模式\n"
            f"当前操作角色：{active_name}\n"
            f"队伍成员：{', '.join(party_names)}\n"
            f"队伍成员 ID：{', '.join(f'{name}={cid}' for cid, name in char_map.items())}\n"
            f"探索模式下角色可自由行动，你可以用 switch_character 切换角色。"
        )
