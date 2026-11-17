# 远行策划工作台 · 在线使用与本机连接

这是 GitHub Pages 上的可交互前端，与本地 `trip.json` 和可选的 Codex 桥接配合。它不是托管式 AI 服务。

## 直接体验

打开[线上工作台](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/)即默认进入[巴黎五日历史攻略](../examples/france-2026/guide.md)的脱敏回放：9月25日凯旋门与蒙马特、26日奥赛、27日卢浮宫、28日左岸与西岱岛、29日凡尔赛。上半部是地图和时间轴；下半部「执行看板」随全程/单日切换，全程展示五天节奏与历史订票 Checklist，单日展示可点击的路线节点、必须保护/先删/雨天分支、交通、餐食、出发检查与官方入口。点击 Day 2 →「调整这一天」→「节奏轻松一点」→「生成修改提案」，可体验**明确标注为模拟**的修改、差异预览与确认。真实出票凭证未公开，页面不表示现在可预约。模拟结果只保存在当前浏览器标签页；下载 JSON 才能留存。

原来的虚构 Lisbon → Cascais 示例仍可通过[此链接](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/?demo=lisbon)查看，两份示例互不覆盖。巴黎只摘取五个观光日；9月24日抵达与30日巴黎飞尼斯仍留在[完整攻略](../examples/france-2026/guide.md)，不被误当作观光日。

本地预览：在仓库根目录执行 `python3 -m http.server 8765`，再打开 `http://127.0.0.1:8765/web/`。底图与字体需要联网；地图连线只表示站点顺序，不是导航路径。

工作台正式地图采用 F「图标寻宝」：地图默认显示图形和序号，点选后展开地名并同步高亮当天时间轴。`items[].icon` 可选用 `arc`、`sacrecoeur`、`invalides`、`eiffel`、`versailles`、`louvre`、`orsay`、`notredame`、`chapelle`、`tuileries` 或通用的 `museum`、`garden`、`food`、`rail`、`walk`、`landmark`；未指定时按名称或项目类型回退。没有坐标的项目仍在时间轴中，但不伪造地图点；整天都没有坐标时显示明确的未定位状态。巴黎历史回放的地图点是地标参考位置，不承诺是当前入口或登船口。

想比较其他标注方式，可打开[地图样式试验场](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/map-lab.html)：同一组巴黎地标可切换六种样式（A 旅行手帐、B 城市寻路、C 夜色导览、D 地标徽章、E 城市邮票、F 图标寻宝），点击地图标注或侧栏站点可联动聚焦。这是独立的视觉试验场，不会修改真实行程。

实现参考了 [MapLibre 自定义 Marker 示例](https://maplibre.org/maplibre-gl-js/docs/examples/add-custom-icons-with-markers/)、[Maki](https://github.com/mapbox/maki) 与 [Temaki](https://github.com/rapideditor/temaki)。后两者适合通用 POI 分类图标，不提供这些景点的官方标志；试验场中的卢浮宫金字塔、奥赛钟面等是本项目新画的建筑示意 SVG，**不是官方 logo**，不从第三方仓库复制图形。

## 连接自己的 Codex

先在 Codex 安装本项目 Skill，通过对话生成自己的 `trip.json`，文件放在 Skill 目录之外。网页本身尚不能从零生成完整行程；直接「导入行程」只在当前浏览器中查看，不会连接 Codex 或保存到 GitHub Pages。确认本机已安装并登录 Codex CLI，然后在仓库根目录执行：

```bash
python3 bridge/server.py --trip /absolute/path/to/your/trip.json
```

桥接只监听 `127.0.0.1:8766`，会打开带临时配对凭据的工作台链接。浏览器可能要求允许访问本机服务；点击页面中的「未连接 Codex」完成连接。请勿分享带 `#token=` 的配对链接，关闭桥接进程即可停止服务。

网页点「生成修改提案」时，桥接以只读方式调用**本机已登录的 Codex CLI**，使用已安装的 Skill，返回所选日期的完整替换提案。这会消耗你自己的 Codex 配额；整份行程 JSON 和修改要求会作为提示发送到你使用的模型服务。确认前不写文件；确认后才校验硬预约与全程状态、检查文件未被其他入口改动，创建 `.bak` 备份并原子写入。Codex 直接改动同一份 `trip.json` 后，可刷新工作台重新读取。

本版仍有边界：一次只能处理一个日期；提案生成期间无逐字流式进度；网站不自动同步 Codex 桌面聊天记录；手机若不能连接运行桥接的同一台电脑，就只能浏览或导入行程。网页不会代替用户购买门票或验证实时开放情况；任何 AI 提案仍需人工检查来源与预约。

## 安全边界

桥接仅接受指定网页来源和随机配对凭据，不提供任意命令接口。GitHub Pages 不接收模型密钥或存储行程；旅行数据经本机接口进入浏览器，并在生成提案时进入 Codex 模型请求。若修改工作台域名，可在启动时显式添加 `--allow-origin` 并指定 `--web-url`；不要对未知网站开放来源。
