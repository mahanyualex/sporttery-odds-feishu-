# 飞书群查询接入说明

本文件说明如何把 `sporttery-odds-feishu` 项目接到 Hermes / 飞书网关中，支持群内固定命令查询。

## 目标交互

群内固定格式：
- `@机器人 查询 法国`
- `@机器人 查询 周四201`

Hermes 网关侧应保持最薄短路逻辑：
1. 仅处理 Feishu 群消息
2. 必须 `@机器人`
3. 去掉 self mention 后，如果正文以 `查询 ` 开头，则短路调用：

```bash
python -m odds_tool.main feishu-query --text "查询 法国"
```

4. 将 stdout 直接回发群里
5. 如果 stdout 为空，则静默返回

## 下游命令约定

推荐调用方式：

```bash
python -m odds_tool.main feishu-query --text "查询 法国"
python -m odds_tool.main feishu-query --text "查询 周四201"
```

不要假设项目有 `main.py` 顶层可执行入口，应保持模块调用方式一致。

## 用户体验约束

- 只做固定命令 `查询 <关键词>`
- 不做自然语言理解
- 不做群内多轮澄清
- 返回多场时一次性展示全部比赛
- 如果当天没有比赛或无可售场次，应返回明确业务提示，而不是系统错误

## README 里建议保留的示例

- `@机器人 查询 法国`
- `@机器人 查询 周四201`
- `python -m odds_tool.main feishu-query --text "查询 法国"`
