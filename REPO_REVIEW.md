# GitHub 仓库筛选记录

检查日期：2026-09-21

入口页不把 11 个公开仓库全部平铺。展示顺序按“别人能不能马上看懂、有没有可以直接打开的成品、能不能代表一类工作”来定。

## 首屏精选

| 仓库 | 入口页位置 | 选择理由 |
| --- | --- | --- |
| `cityu-msaib-course-board` | 网页工具 | 有明确使用场景，课程筛选和排课结果可以直接打开。 |
| `luohu-rental-map` | 网页工具 | 数据整理、筛选、图片和路线都在一个可用页面里，内容完整。 |
| `beishatan-rental-map` | 网页工具 | 与罗湖项目形成对照，突出移动端和实际步行路线。 |
| `metro-rental-research-skill` | Agent Skill | 展示如何把找房这种模糊任务拆成可执行的研究流程。 |
| `codex-dsh-bridge` | Agent 工具 | 展示对 Agent 协作、任务传递和本地工具连接的实践。 |

## 合并展示

- `dsh-read-image-plugin`、`dsh-voice-input-plugin`：归为 DeepSeek Harness 插件，分别说明图片输入和语音输入。
- `pinterest-collection-console`、`huaban-downloader`、`zcool-downloader`、`wikihow-clipper`：归为网页采集插件。它们共享批量采集、队列、去重、断点续采或导出思路，入口页展示共同方法，并保留每个仓库链接。

## 暂不单独做项目页的原因

这些仓库都可以公开访问，但插件之间的差异主要在网站适配层。如果把每个插件都做成独立项目，入口页会变成仓库清单，反而看不出工作主线。后续如果要补案例页，再选 Pinterest 或花瓣其中一个作为完整代表。

## 页面链接核对

截至检查日期，以下三个 GitHub Pages 地址返回 200：

- `https://dddzzz123-dz.github.io/cityu-msaib-course-board/`
- `https://dddzzz123-dz.github.io/luohu-rental-map/`
- `https://dddzzz123-dz.github.io/beishatan-rental-map/`

仓库介绍和项目名称根据公开 README 整理，没有复制仓库代码到本入口页。
