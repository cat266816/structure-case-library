# 结构设计案例库

产品与机械结构设计案例库（外壳、连接件、转轴铰链、机构、密封、拆解结构等），以 [Obsidian](https://obsidian.md/) 仓库形式整理，目前共 111 篇案例。

本仓库为**私有**。配图版权归原作者，仅供个人学习，请勿公开再分发。

## 用 Obsidian 打开

1. 克隆本仓库。
2. 用 Obsidian「打开本地仓库」选择里面的 `vault` 文件夹。
3. 从 `首页.md` 开始浏览；可视化地图在 `案例地图.canvas`。

建议安装社区插件 Dataview，并在其设置中打开 Enable JavaScript Queries。

## 可视化网页

静态站点位于 `docs/`（生成后可用于 GitHub Pages）。本地可直接打开 `docs/index.html`，或在仓库根目录运行：

```bash
python3 scripts/build_site.py
```

按当前约定，仓库里会放好网页文件，但先不开启 GitHub Pages，避免站点被公开访问。

## 目录

```
vault/          Obsidian 案例库
docs/           可视化静态站点（构建产物）
scripts/        站点构建脚本
```
