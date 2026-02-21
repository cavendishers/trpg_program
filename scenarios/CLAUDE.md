[根目录](../CLAUDE.md) > **scenarios**

# scenarios - 剧本数据

## 模块职责

存放 YAML 格式的 CoC 剧本文件和 JSON Schema 校验定义。剧本采用"导演手册"风格，给 AI KP 自由发挥空间。

## 入口与启动

- 无运行时入口，由后端 `backend/scenario/loader.py` 加载
- 校验：`schema.json` 定义剧本格式约束

## 对外接口

剧本 YAML 结构：

| 顶级字段 | 说明 |
|----------|------|
| `meta` | 剧本元信息（id/title/era/player_count/difficulty/synopsis） |
| `keeper_guide` | KP 专用全局信息（玩家不可见） |
| `key_plot_points` | 关键剧情节点（必须发生的事件，AI 自由决定触发时机） |
| `endings` | 结局条件与 SAN 奖励 |
| `npcs` | NPC 模板（初始设定，运行时状态归角色模块） |
| `locations` | 地点定义（氛围、可搜索区域、危险） |
| `clues` | 线索清单（重要性、发现方式） |

## 关键依赖与配置

- 格式：YAML
- 校验：JSON Schema (`schema.json`)

## 数据模型

见计划文件中 "剧本格式（YAML）" 章节的完整示例（"鬼屋惊魂"）。

## 测试与质量

- `tests/test_scenario_loader.py` 校验剧本加载与格式验证

## 相关文件清单

```
scenarios/
  schema.json              # JSON Schema 校验定义
  the_haunting/
    scenario.yaml          # 示例剧本 "鬼屋惊魂"
```

## 变更记录 (Changelog)

| 日期 | 变更 |
|------|------|
| 2026-02-20 | 初始创建：基于计划文件生成模块文档框架 |
