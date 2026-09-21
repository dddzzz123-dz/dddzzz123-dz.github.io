# 公开文件说明

这个目录现在是戴颖的 GitHub 作品集入口页。页面把公开仓库按用途整理成三类：网页工具、Agent / Skill，以及浏览器插件。

## 页面实际使用的文件

- `site/index.html`：作品集入口页。
- `site/assets/github.css`、`site/assets/github.js`：页面样式与项目卡片渲染。
- `site/data/repos.js`：公开仓库的展示数据和链接。
- `site/assets/previews/`：三个已部署网页的封面截图。
- `site/assets/daiying-resume.pdf`：可下载的简历。
- `.github/workflows/pages.yml`：GitHub Pages 部署流程。

页面源文件位于 `site/`，GitHub Actions 会把入口页需要的文件复制到干净的 Pages artifact 后再发布。页面使用仓库名、README 中的公开描述、公开的 GitHub Pages 地址和简历信息；没有把任何私有数据、凭证或业务原始数据放进展示内容。

## 展示边界

- 页面先放简历和快捷链接，再按“网页 / Skill / 插件”分区。
- Skill 区提供可复制给 Agent 的拉取与使用提示。
- 插件区提供 GitHub 分支 ZIP 的直接下载，不把访客带到仓库列表页。
- 项目卡片只写能从公开仓库验证的功能，不延伸到未公开的业务背景、客户信息或内部指标。
- 简历作为 PDF 下载提供；网页中的经历说明保持简短，并链接到对应项目。

仓库里还保留了一些早期本地验证文件，它们不在入口页导航中，也不会进入 GitHub Pages artifact。后续若要整理代码仓库，可以再单独清理历史文件。
