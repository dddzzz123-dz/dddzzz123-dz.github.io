# 戴颖 / 项目入口

这是一个 GitHub Pages 入口页，用来集中展示我的公开仓库、已部署网页和简历。

入口页目前分成三部分：

- 3 个可以直接打开的网页工具：CityU 选课板、罗湖通勤租房地图、北沙滩租房路线地图。
- 2 个 Agent / Skill 项目：地铁通勤租房研究 Skill、Codex DSH Bridge。
- 2 组插件：DeepSeek Harness 输入插件，以及面向不同网站的采集插件。

入口页的仓库筛选记录见 [REPO_REVIEW.md](REPO_REVIEW.md)。项目描述根据公开 README 重新整理；入口页不复制仓库代码。

## 本地查看

直接打开 site/index.html 可以查看静态页面。需要在浏览器里检查所有相对路径时，运行：

    python -m http.server 4173 --bind 127.0.0.1 --directory site

打开 http://127.0.0.1:4173/。

## 检查

    python scripts/check_portfolio.py

检查脚本会在桌面、手机和小屏宽度下检查横向溢出、卡片数量、图片加载和简历链接，并保存报告与 QA 截图到 qa/。qa/ 不上传到 GitHub Pages。

## GitHub Pages

仓库根目录的 GitHub Actions 工作流会先检查 `site/`，再只打包入口页需要的文件到 Pages artifact。如果将本目录作为独立仓库推送到 main，在仓库 Settings → Pages 中选择 GitHub Actions 即可发布。

当前页面使用相对路径，项目仓库地址变化时不需要改页面资源路径。三个已部署网页和所有代码仓库均使用绝对链接跳转。

## 简历

site/assets/daiying-resume.pdf 是工作区中 2026 年 9 月整理的公开简历版本。网页内保留一份简短经历摘要，同时提供 PDF 下载。
