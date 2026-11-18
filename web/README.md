# 远行策划工作台 · 在线使用与本机连接

这是 GitHub Pages 上的可交互前端，与本地 `trip.json` 配合。任意能安装本 Skill、读写本地文件的代理都可通过 JSON 导入/导出使用；Codex CLI 与 Claude Code CLI 另有可选本机桥接。它不是托管式 AI 服务。

## 用你自己的 AI 代理

1. 在支持 Agent Skills 的代理中安装本项目 Skill，要求它在 Skill 目录外生成 `trip.json`。
2. 点击工作台的「导入行程」查看地图、日程和执行看板。文件仅在当前浏览器标签页读取，不会传到 GitHub Pages。
3. 需要调整某天时，选中日期并写下要求，依次点「① 下载交接 JSON」「② 复制要求给 AI 代理」。把 JSON 与要求交给代理；完成后重新导入更新后的 JSON。请核对固定预约和实时事实。

不同设备间的 JSON 交接不由网页调用模型，也不会自动同步；重新导入前请保留旧文件，它不会自动比较或备份。同一台电脑上可用下方的共享文件模式，让所有能够编辑同一份文件的代理与工作台自动同步。Codex CLI 与 Claude Code CLI 另有本机自动提案适配器；其他代理尚未验证网页一键调用模型。不同代理的 Skill 安装目录和调用语法见[项目首页](../README.md)及各产品文档；WorkBuddy/CodeBuddy 的本地导入因产品版本不同需自行核对。

## 同机共享文件模式（跨代理推荐）

代理先用本 Skill 在 Skill 目录外建立并校验 `trip.json`。在安装目录或仓库根目录运行：

```bash
python3 bridge/server.py --provider manual --trip /absolute/path/to/your/trip.json
```

打开命令打印的专属链接，点「连接本机」。选一天、写下要求、点「复制要求给 AI 代理」；复制内容包含这份文件的本机路径。把文字发给已安装 Skill 且能够编辑该文件的代理。代理保存并校验后，工作台在页面可见时每 5 秒检查一次版本变化并刷新地图与日程；无效或尚未写完的 JSON 不会替换当前画面。这个模式不从网页调用模型，也没有远程自动控制代理的能力。请保留文件旧版，代理的写入不经过网页的确认与 `.bak` 备份机制。

## 直接体验

打开[线上工作台](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/)即默认进入[巴黎五日历史攻略](../examples/france-2026/guide.md)的脱敏回放：9月25日凯旋门与蒙马特、26日奥赛、27日卢浮宫、28日左岸与西岱岛、29日凡尔赛。上半部是地图和时间轴；下半部「执行看板」随全程/单日切换，全程展示五天节奏与历史订票 Checklist，单日展示可点击的路线节点、必须保护/先删/雨天分支、交通、餐食、出发检查与官方入口。点击 Day 2 →「调整这一天」→「节奏轻松一点」→「生成修改提案」，可体验**明确标注为模拟**的修改、差异预览与确认。真实出票凭证未公开，页面不表示现在可预约。模拟结果只保存在当前浏览器标签页；下载 JSON 才能留存。

原来的虚构 Lisbon → Cascais 示例仍可通过[此链接](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/?demo=lisbon)查看，两份示例互不覆盖。巴黎只摘取五个观光日；9月24日抵达与30日巴黎飞尼斯仍留在[完整攻略](../examples/france-2026/guide.md)，不被误当作观光日。

本地预览：在仓库根目录执行 `python3 -m http.server 8765`，再打开 `http://127.0.0.1:8765/web/`。底图与字体需要联网；地图连线只表示站点顺序，不是导航路径。

工作台正式地图采用 F「图标寻宝」：地图默认显示图形和序号，点选后展开地名并同步高亮当天时间轴。`items[].icon` 可选用 `arc`、`sacrecoeur`、`invalides`、`eiffel`、`versailles`、`louvre`、`orsay`、`notredame`、`chapelle`、`tuileries` 或通用的 `museum`、`garden`、`food`、`rail`、`walk`、`landmark`；未指定时按名称或项目类型回退。没有坐标的项目仍在时间轴中，但不伪造地图点；整天都没有坐标时显示明确的未定位状态。巴黎历史回放的地图点是地标参考位置，不承诺是当前入口或登船口。

想比较其他标注方式，可打开[地图样式试验场](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/map-lab.html)：同一组巴黎地标可切换六种样式（A 旅行手帐、B 城市寻路、C 夜色导览、D 地标徽章、E 城市邮票、F 图标寻宝），点击地图标注或侧栏站点可联动聚焦。这是独立的视觉试验场，不会修改真实行程。

实现参考了 [MapLibre 自定义 Marker 示例](https://maplibre.org/maplibre-gl-js/docs/examples/add-custom-icons-with-markers/)、[Maki](https://github.com/mapbox/maki) 与 [Temaki](https://github.com/rapideditor/temaki)。后两者适合通用 POI 分类图标，不提供这些景点的官方标志；试验场中的卢浮宫金字塔、奥赛钟面等是本项目新画的建筑示意 SVG，**不是官方 logo**，不从第三方仓库复制图形。

## 连接本机代理

先在所用代理安装本项目 Skill，通过对话生成自己的 `trip.json`，文件放在 Skill 目录之外。网页本身尚不能从零生成完整行程；直接「导入行程」只在当前浏览器中查看，不会连接代理或保存到 GitHub Pages。若要由网页自动调用模型，确认 Codex CLI 或 Claude Code CLI 已安装，且拥有可用的模型配额。在仓库根目录执行（默认 Codex）：

```bash
python3 bridge/server.py --trip /absolute/path/to/your/trip.json
```

Claude Code CLI：`python3 bridge/server.py --provider claude --trip /absolute/path/to/your/trip.json`。可用 `--cli-bin` 指定所选 CLI 的路径。Claude 适配器的协议与安全校验已有测试；本机真实生成测试遇到账号端 `402 insufficient balance`，尚未验证完整模型响应。

桥接只监听 `127.0.0.1:8766`，会打开带临时配对凭据的工作台链接。浏览器可能要求允许访问本机服务；点击页面中的「连接本机」完成连接。请勿分享带 `#token=` 的配对链接，关闭桥接进程即可停止服务。

网页点「生成修改提案」时，桥接调用所选本机 CLI，返回所选日期的完整替换提案。Codex 使用已安装的 Skill 和只读沙盒；Claude 请求携带本仓库 Skill 指导并禁用内置与 MCP 工具，不要求额外安装脚本执行权限。这会消耗所选代理自己的配额；整份行程 JSON 和修改要求会作为提示发送到相应模型服务。确认前不写文件；确认后才校验硬预约与全程状态、检查文件未被其他入口改动，创建 `.bak` 备份并原子写入。代理在对话中直接改动同一份 `trip.json` 后，可刷新工作台重新读取。

本版仍有边界：一次只能处理一个日期；提案生成期间无逐字流式进度；网站不自动同步 Codex 桌面聊天记录；手机若不能连接运行桥接的同一台电脑，就只能浏览或导入行程。网页不会代替用户购买门票或验证实时开放情况；任何 AI 提案仍需人工检查来源与预约。

## 安全边界

桥接仅接受指定网页来源和随机配对凭据，不提供任意命令接口。GitHub Pages 不接收模型密钥或存储行程；旅行数据经本机接口进入浏览器，并在生成提案时进入所选代理的模型请求。若修改工作台域名，可在启动时显式添加 `--allow-origin` 并指定 `--web-url`；不要对未知网站开放来源。
