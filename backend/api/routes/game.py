"""WebSocket game endpoint for real-time gameplay."""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.api.routes.session import get_session_engine

router = APIRouter(tags=["game"])


@router.websocket("/api/game/{session_id}/ws")
async def game_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()

    try:
        engine = get_session_engine(session_id)
    except KeyError:
        await websocket.send_json({"type": "error", "content": "Session not found"})
        await websocket.close()
        return

    try:
        # Auto-send opening narrative if no history yet
        if not engine.keeper.history:
            opening = await engine.generate_opening()
            await websocket.send_json({
                "type": "narrative",
                "content": opening["narrative"],
            })
            for npc in opening.get("npc_actions", []):
                await websocket.send_json({"type": "npc_action", **npc})
            await websocket.send_json({
                "type": "state_update",
                "phase": opening["phase"],
                "atmosphere": opening.get("atmosphere", "calm"),
                "turn_state": opening.get("turn_state"),
            })
        else:
            # Reconnection / resume: replay last AI narrative
            for entry in engine.keeper.history[-2:]:
                if entry["role"] == "assistant":
                    from backend.ai.response_parser import parse_response
                    try:
                        kp = parse_response(entry["content"])
                        await websocket.send_json({
                            "type": "narrative",
                            "content": kp.narrative,
                        })
                    except Exception:
                        await websocket.send_json({
                            "type": "narrative",
                            "content": entry["content"],
                        })

            # Sync discovered clues
            for clue_id in engine.guardian.discovered_clues:
                clue = engine.scenario.clues.get(clue_id)
                if clue:
                    await websocket.send_json({
                        "type": "clue_discovered",
                        "clue_id": clue_id,
                        "description": clue.description,
                    })

            await websocket.send_json({
                "type": "system",
                "content": "已从存档恢复，继续你的冒险...",
            })

            # Send current turn state on reconnection
            await websocket.send_json({
                "type": "turn_update",
                "turn_state": engine.turn_manager.to_dict(),
            })

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "player_action":
                character_id = data.get("character_id", "")
                content = data.get("content", "")

                result = await engine.process_player_input(
                    player_input=content,
                    character_id=character_id,
                )

                # Handle not_your_turn error
                if result.get("error") == "not_your_turn":
                    await websocket.send_json({
                        "type": "system",
                        "content": "现在不是该角色的行动回合。",
                    })
                    await websocket.send_json({
                        "type": "turn_update",
                        "turn_state": result["turn_state"],
                    })
                    continue

                # Send narrative
                await websocket.send_json({
                    "type": "narrative",
                    "content": result["narrative"],
                })

                # Send directive results (dice rolls, etc.)
                for d in result.get("directives", []):
                    await websocket.send_json({
                        "type": "dice_result",
                        "description": d["description"],
                        **d["details"],
                    })

                # Send continuation narrative if any
                if result.get("continuation"):
                    await websocket.send_json({
                        "type": "narrative",
                        "content": result["continuation"],
                    })

                # Send NPC actions
                for npc in result.get("npc_actions", []):
                    await websocket.send_json({
                        "type": "npc_action",
                        **npc,
                    })

                # Send clue discoveries
                for clue in result.get("clues_discovered", []):
                    await websocket.send_json({
                        "type": "clue_discovered",
                        **clue,
                    })

                # Send state update
                await websocket.send_json({
                    "type": "state_update",
                    "phase": result["phase"],
                    "atmosphere": result.get("atmosphere", "calm"),
                })

                # Send turn state update
                if result.get("turn_state"):
                    await websocket.send_json({
                        "type": "turn_update",
                        "turn_state": result["turn_state"],
                    })

                # Auto-save after each action
                try:
                    engine.save_to_file("auto")
                except Exception:
                    pass

            elif msg_type == "save_game":
                slot = data.get("slot", "manual")
                try:
                    engine.save_to_file(slot)
                    await websocket.send_json({
                        "type": "system",
                        "content": f"游戏已保存到存档位: {slot}",
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"保存失败: {e}",
                    })

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        try:
            engine.save_to_file("auto")
        except Exception:
            pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "content": str(e),
            })
        except Exception:
            pass
