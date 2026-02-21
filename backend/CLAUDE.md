[根目录](../CLAUDE.md) > **backend**

# backend - FastAPI 后端

## 模块职责

Python FastAPI 异步后端，包含游戏核心逻辑、AI 集成、规则引擎、角色管理和 API 层。

## 入口与启动

- 入口文件：`main.py`（FastAPI 应用实例）
- 配置：`config.py`（Pydantic Settings，读取 `.env`）
- 依赖注入：`dependencies.py`
- 启动命令：`uv run uvicorn backend.main:app --reload`

## 子模块结构

| 子模块 | 路径 | 职责 |
|--------|------|------|
| API 层 | `api/routes/` | REST 端点（session/character/scenario）+ WebSocket 游戏端点 |
| 游戏引擎 | `core/` | `game_engine.py` 主循环编排 + `state_machine.py` 游戏阶段状态机 |
| 剧本模块 | `scenario/` | YAML 剧本加载/校验、剧情守护层（plot_guardian） |
| 主持人模块 | `ai/` | AI Provider 抽象层、KP 引擎、Prompt 分层构建、响应解析 |
| 规则与判定 | `rules/` | CoC 7e 骰子(D100)、技能检定、战斗、理智检定、属性计算 |
| 角色模块 | `character/` | PC/NPC 数据模型与运行时状态管理 |
| 持久化 | `persistence/` | SQLite + SQLAlchemy async、ORM 模型、数据访问层 |

## 对外接口

### REST API

```
POST   /api/sessions              创建游戏会话
GET    /api/sessions/{id}         获取会话信息
DELETE /api/sessions/{id}         结束会话
GET    /api/scenarios             列出可用剧本
GET    /api/scenarios/{id}        获取剧本详情
POST   /api/characters            创建角色
GET    /api/characters/{id}       获取角色卡
PUT    /api/characters/{id}       更新角色
GET    /api/sessions/{id}/state   游戏状态快照
POST   /api/sessions/{id}/save    手动存档
POST   /api/sessions/{id}/load    读取存档
```

### WebSocket

```
WS /api/game/{session_id}/ws
```

消息类型：`player_action` / `dice_roll_confirm` / `push_roll`（客户端）；`narrative` / `dice_request` / `dice_result` / `clue_discovered` / `state_update`（服务端）。

## 关键依赖与配置

```
fastapi, uvicorn[standard], pydantic>=2.0, pydantic-settings
pyyaml, sqlalchemy[asyncio], aiosqlite
anthropic, openai, httpx (Ollama)
python-dotenv, pytest, pytest-asyncio
```

## 数据模型

- `CoCCharacter`：八大属性 + 派生属性 + 技能 + 状态 + 物品栏
- `Scenario`：meta + keeper_guide + key_plot_points + endings + npcs + locations + clues
- `KPResponse`：narrative + game_directives + npc_actions + atmosphere
- `GameState`：会话状态、角色列表、剧情进度、对话历史

## 测试与质量

- 规则模块：纯逻辑单元测试（`tests/test_dice.py`, `test_skill_check.py`, `test_combat.py`, `test_sanity.py`）
- 剧本模块：`tests/test_scenario_loader.py`
- 游戏引擎：`tests/test_game_engine.py`（mock AI Provider）
- 测试命令：`uv run pytest tests/`

## 常见问题 (FAQ)

- Q: AI 不按结构化格式返回怎么办？A: `response_parser.py` 实现 fallback 解析，必要时重试。
- Q: 长会话超出 token 限制？A: Prompt Layer 4 使用滑动窗口，定期让 AI 自我总结。
- Q: 规则模块与 AI 的边界？A: 规则模块是唯一骰子来源，AI 只能请求检定，不可自行掷骰。

## 相关文件清单

```
backend/
  main.py, config.py, dependencies.py
  api/routes/{session,game,character,scenario}.py, api/middleware.py
  core/{game_engine,state_machine}.py
  scenario/{loader,models,plot_guardian}.py
  ai/providers/{base,claude,openai_provider,ollama}.py
  ai/{keeper_engine,prompt_builder,response_parser}.py
  rules/{dice,skill_check,combat,sanity,character_calc}.py
  character/{models,service}.py
  persistence/{database,repositories,orm_models}.py
```

## 变更记录 (Changelog)

| 日期 | 变更 |
|------|------|
| 2026-02-20 | 初始创建：基于计划文件生成模块文档框架 |
