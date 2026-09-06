# 轻量博客性能审计

AIGC：本记录由 Codex 于 2026-09-06 根据代码、构建产物、本机 Chromium 检查和用户确认的取舍整理。这里只记录可验证的行为与资源规模，不把单次本地加载时间视为线上性能结论。字体探索仍留在独立分支，不在此处恢复。

## 本轮已处理

- MathJax 由全站直接加载改为内容检测后加载，沿用 `extra.math_display = "mathjax"` 开关，不要求每篇文章手动标记。普通代码和无公式页面不会下载渲染器，列表摘要中的公式也纳入检测。
- 旧实现有两个数学代码转换入口，以及自动启动之外的 `typesetPromise()` 调用。确定性快缓存模拟复现了两次排版，且两次都早于数学代码块转换。现在模块在 DOM 就绪后先转换旧式行内包装和数学代码块，再插入 MathJax 脚本，只使用一次自动启动，范围限制在 `.content`。
- MathJax URL 固定为本轮实际运行过的 `4.1.3`，不再随 `@4` 漂移；未关闭数学辅助功能以换取体积下降。启动契约见 [MathJax Startup Options](https://docs.mathjax.org/en/latest/options/startup/startup.html)，普通代码跳过行为使用其 [Document Options](https://docs.mathjax.org/en/latest/options/document.html) 默认设置。
- 数学处理、代码块按钮和格言动画从每页重复的内联脚本迁入 `static/content.mjs`，使用带内容哈希的 URL。浏览器可以复用相同脚本；这不意味着首次访问完全没有脚本成本，也不改变部署服务器的缓存头。
- 格言打字动画在后台标签页暂停、回到前台后恢复，保留 reduced-motion 的静态显示。代码复制失败被捕获，不再产生未处理的 Promise 拒绝。
- 顶栏交互迁入带内容哈希的 `static/topbar.js`，在 head 中以 `defer` 加载，保留全局接口和最小首屏配色脚本。独立脚本为 4,268 字节，可跨页复用；这是缓存与维护收益，不宣称增加一次请求后首访一定更快。
- Giallo 高亮样式改为 HTML 中直接声明的条件 stylesheet 链接，去掉主 CSS 中的 `@import`，保持原有媒体条件和级联顺序。仅在 Zola 的 class 高亮模式下引用这些生成文件，配置契约见 [Zola Syntax Highlighting](https://www.getzola.org/documentation/content/syntax-highlighting/)。
- 友链头像添加原生 `loading="lazy"`、`decoding="async"` 和固定尺寸，保留现有方形 CSS 容器；首屏身份头像和正文图片没有统一设为 lazy。这些属性由浏览器处理，不引入图片 JavaScript，语义见 [MDN img](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img)。
- 独立 404 页复用格言模块，其动画遵循 reduced-motion；About 描述移除不安全的 `safe` 属性输出，并补上引号和 HTML 实体的回归测试。
- 上一轮的正文宽度限制保留：`.content-article` 最大 `64rem`，在现有内容区内居中，不改变首页或列表布局。

## 检查结果

修复前后使用相同博客内容和实际 MathJax 4.1.3 对照，四篇数学文章的公式数均未变化：`mogic` 为 44，`mpqs` 为 263，`p-h` 为 74，`perec` 为 136，合计 517。没有新增公式错误、残留数学 code 包装或页面脚本错误。

首页、About、文章列表、`2025-end`、`psychedelic-renaissance-essay` 和 `yesterday` 的 MathJax 相关请求均由本次旧实现观察到的 4 个降为 0 个。数学文章仍需相同的渲染器和扩展，本轮不宣称降低了大量公式本身的 SVG 排版成本。

第一阶段仅完成内容模块抽取时，旧 About 页 HTML 为 19,629 字节，新实现同一生产 base URL 的 HTML 为 13,460 字节，减少 6,169 字节；抽出的内容模块为 5,611 字节。这是未压缩文件大小对照，不是首访传输量净减少。独立 gzip 估计分别为 5,265、3,723、2,042 字节，实际服务器可能采用不同压缩和缓存策略。随后又抽取了顶栏脚本，因此上述 HTML 数据不是最终构建大小。无公式页面的主要收益来自省去 MathJax，而不是把 JavaScript 换了一个存放位置。

搜索按钮点击前没有索引、搜索核心或 Fuse 请求；点击后才加载三者，真实查询 `Montgomery` 能正常返回结果。约 68 KiB 的本地全文索引和约 18 KiB 的 Fuse 源文件不应计入未打开搜索时的首屏负担。

回归覆盖 34 项 Python 模板及数学处理测试、13 项 Node 单元测试、20 组浏览器启动与动画场景。浏览器场景包含快慢 CDN、CDN 失败、禁用开关、普通代码、被忽略区域、行内和块级公式、四类数学代码块、列表摘要、后台暂停及 reduced-motion。顺序测试使用模拟 MathJax；真实文章另用实际 CDN 验证，二者不混为一谈。

另外检查 About 和 404 的主题切换及持久化、侧栏焦点状态、RSS 菜单、全文搜索与 Escape 关闭，以及数学文章在 390、1440、3440 像素视口下的排版和截图。顶栏脚本刻意延迟响应，验证外置后的交互仍然可用；页面无新增 JavaScript 错误。所有本轮浏览器复查均使用隔离的 headless Chromium，不启动可见窗口或接入用户已有会话。

## 已确认的取舍与后续边界

| 项目 | 已观察到的情况 | 建议与边界 |
| --- | --- | --- |
| 图标资源 | `_base.html` 和独立 404 模板引入 Font Awesome 完整样式；站点仅用其中少量图标，但社交图标名称允许配置 | 本轮保留 Font Awesome，不增加维护品牌图标的负担。以后只有在能方便地保留现有品牌图标能力时，才重新考虑精简 |
| 正文图片 | 友链头像的原生懒加载和尺寸已补齐；图片 component 与普通 Markdown 图片仍各有生成路径 | 已确认正文图片暂不设置懒加载，也不新增要求使用者逐张指定的加载参数；友链头像的独立优化保留 |
| 预取 | `_base.html` 无条件引入 `instant.page` 第三方模块 | 已确认保留当前预取行为，本轮不关闭，也不新增开关；预取请求仍与实际点击后的必要请求区分统计 |
| CSS | 本轮改动前 `style.css` 为 74,591 字节，独立 gzip 约 12,285 字节，含首页、文章、友链和组件规则；高亮 CSS 的延迟发现已处理 | 若继续清理，先做多页覆盖率检查，确认哪些是旧布局遗留。当前压缩后规模不大，不建议为删几条选择器引入复杂构建流水线 |
| 字体 | 多套 Google Fonts 和中文字体 CSS 仍在首屏请求路径上 | 已明确暂缓，本轮只记录，不改变字体职责、引入方式或授权决策 |
| 数学长文 | 真实数学文章依然生成大量 SVG 节点 | 本轮只解决无公式页面下载和重复启动。按屏幕可见性分段排版可能影响公式编号、跳转和辅助功能，需单独测量与决策 |
| 搜索 | 已按交互延迟加载、输入防抖、限制展示条数 | 当前文章量无需 Worker、服务端搜索或分页加载引擎；文章数量显著增加后再测索引解析与查询耗时 |

## 复查方法

从主题根目录执行已有测试，无需新增生产依赖：

```bash
python3 -B -m unittest scripts.test_theme_templates scripts.test_process_math
node --test scripts/test_search.mjs scripts/test_content.mjs
git diff --check
```

浏览器测试通过专用入口运行，固定使用隔离的 headless Chromium，不会打开可见窗口。内容测试读取真实模板脚本并构造测试页面，不向博客写入测试文章；界面测试使用本博客的 About、404 和 `posts/mogic/` 页面。启动本地站点后，在主题目录执行：

```bash
node scripts/run_browser_checks.mjs http://127.0.0.1:1116/blog/ scripts/check_content_browser.js scripts/check_interface_browser.js
```

需有可导入的 Playwright 和匹配的 Chromium；也可用环境变量 `PLAYWRIGHT_MODULE` 指定现有 Playwright 安装的入口文件绝对路径。它们仅用于测试，不是主题生产依赖。布局截图输出到系统临时目录 `/tmp/nivis-performance-*.png`。

首次渲染依赖外部 CDN，故图片和字体的真实加载仍需联网。检测器只决定是否下载，不是 TeX 解析器；语法解析交给 MathJax。内容在首次加载后由自定义插件动态插入的场景不在静态博客契约内，需要插件自行触发加载和排版。线上冷缓存、弱网、低端手机的时间与内存尚未测量，不能据此给出 Lighthouse 分数或速度倍数。
