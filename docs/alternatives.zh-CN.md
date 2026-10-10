# 同类项目对比

核对日期：2026-10-10。以下依据各项目公开 README 和本仓库代码，**没有**对所有项目运行同一条旅行需求；“未强调”不等于没有该能力。Star 数和价格变化快，因此不作为功能判断依据。

| 项目 | 形态 | 公开说明中最突出的能力 | 选择时要考虑 |
|---|---|---|---|
| [Plan & Maintain Trips](../README.md) | Codex / Agent Skill | 证据与复查时间、精确预约状态、硬锚点与改版控制；SVG、离线 HTML、KML、ICS 和可选文档发布 | 需要 Agent 调研真实信息；不是多人协作 App；部分输出取决于输入是否有时间和坐标 |
| [trip-planner-skill](https://github.com/skywain/trip-planner-skill) | Agent Skill | 小时级行程、航班比较、KML、ICS、八种设计主题与多种改计划模式 | 更侧重完整网页路书与视觉呈现；依赖的查询和设计流程更复杂 |
| [见好旅行规划器](https://github.com/awangwang123/jianhao-travel-planner) | 中文 Agent Skill | 联网实查、单文件离线路书、实拍图、手绘导览与城市美食情报卡 | 适合中文内容很丰富的路书；其公开说明侧重内容产出和视觉交付 |
| [travel-plan-viz](https://github.com/zexuanw958-svg/travel-plan-viz) | Agent Skill | 手机优先的单文件 HTML、交互地图、时间轴、提醒和生成后字段/坐标校验 | 适合优先获得轻量网页攻略；其 README 说明离线时地图底图和图片可能需要网络 |
| [marco-polo.skill](https://github.com/megumi-ben/marco-polo.skill) | Agent Skill | 高德地点/入口/路线、小红书体验研究、地图/美食/城市手册 | 国内目的地能力突出；完整流程需要额外 Skill、密钥和登录配置 |
| [TREK](https://github.com/liketrek/TREK) | 自托管旅行 App | 多人协作、交互地图、预订和费用管理、离线 PWA、MCP | 适合长期管理和共同执行旅行；需要部署与维护，和 Agent 研究工作流处于不同层次 |

## 我们优先保持的边界

本项目重点是把一个不断变化的旅行计划保存在 `trip.json`，对营业、开票、预约与价格留下来源和复查时间，再同步行程、地图与执行材料。它可以通过已连接的工具发布到飞书等平台，但不内置这些平台的账号或服务。

路线 SVG、离线网页、KML 和 ICS 可以由同一份带时间与坐标的行程生成。示例见 [Lisbon → Cascais 输出包](../examples/lisbon-coast/README.md)。实地导航、当前库存、餐厅营业和交通运营仍需使用当日官方信息核对。

## 下一轮值得比较的实测题

用同一组多城市日期、固定预约、天气中断和已售罄票务输入，分别生成攻略，比较实际查证来源、日期与时区准确性、临时改动后的输出一致性、手机可读性和总运行成本。公开 README 的能力表不能替代这种实测。
