[根目录](../CLAUDE.md) > **frontend**

# frontend - Nuxt 3 前端

## 模块职责

像素/终端风格的 CoC 跑团游戏界面。通过 WebSocket 与后端实时通信，展示 AI KP 叙事、骰子动画、角色卡、线索收集等。

## 入口与启动

- 框架：Nuxt 3 (Vue 3 Composition API)
- 配置：`nuxt.config.ts`
- 启动命令：`pnpm dev`
- 包管理：pnpm

## 对外接口

### 核心页面

| 路由 | 页面 | 职责 |
|------|------|------|
| `/` | `pages/index.vue` | 首页：选择剧本、创建/加入会话 |
| `/session/:id/setup` | `pages/session/[id]/setup.vue` | 会话设置：参与人数、角色创建 |
| `/session/:id/game` | `pages/session/[id]/game.vue` | 游戏主界面 |

### 核心组件

| 组件 | 职责 |
|------|------|
| `NarrativePanel.vue` | AI KP 叙事面板（打字机效果，流式显示） |
| `CharacterSheet.vue` | 角色卡（HP/SAN/MP 条、技能列表） |
| `DiceRoller.vue` | 像素风 D100 骰子动画 |
| `CluePanel.vue` | 线索收集面板 |
| `ActionInput.vue` | 玩家行动输入（文本 + 快捷按钮） |
| `InventoryPanel.vue` | 物品栏 |

### Composables

| Composable | 职责 |
|------------|------|
| `useGameSocket.ts` | WebSocket 连接管理 |
| `useGameState.ts` | 游戏状态响应式管理 |

### Store

- `stores/game.ts`：Pinia 游戏状态（会话、角色、叙事历史、线索）

## 关键依赖与配置

```
nuxt@3, @pinia/nuxt, @vueuse/nuxt
```

## 数据模型

前端状态镜像后端 GameState：当前会话、角色列表、叙事历史、线索列表、骰子结果队列。

## 视觉风格

- 暗色主题：黑/深绿/琥珀色调
- 像素字体：Press Start 2P / VT323
- CRT 扫描线效果（CSS filter）
- 打字机效果显示 AI 叙事
- 骰子动画：像素风 D100 滚动
- 理智值降低时屏幕边缘 glitch 效果

## 测试与质量

- 组件测试 + WebSocket 交互测试（计划）

## 相关文件清单

```
frontend/
  nuxt.config.ts
  pages/{index.vue, session/[id]/{setup,game}.vue}
  components/{NarrativePanel,CharacterSheet,DiceRoller,CluePanel,ActionInput,InventoryPanel}.vue
  composables/{useGameSocket,useGameState}.ts
  stores/game.ts
  assets/fonts/, assets/styles/crt.css
```

## 变更记录 (Changelog)

| 日期 | 变更 |
|------|------|
| 2026-02-20 | 初始创建：基于计划文件生成模块文档框架 |
