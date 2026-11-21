# 静态站点构建

从 Obsidian vault 生成可部署到 GitHub Pages 的纯静态网站，输出到仓库的 `docs/`。

## 重建

在项目根目录执行：

```bash
python3 scripts/build_site.py
python3 scripts/verify_site.py
```

依赖：Python 3 与已安装的 PyYAML。不要改 vault 里的案例 Markdown，改完案例后重新运行上述命令即可。

## 基路径

默认使用**相对路径**，因此：

- 本地直接打开 `docs/index.html` 可以浏览
- 在 `docs/` 下开本地服务器可以浏览
- GitHub Pages 项目站（站点地址为 `/structure-case-library/`）也可以浏览，因为相对路径会解析到该基路径下

若必须写成绝对基路径，再构建一次：

```bash
python3 scripts/build_site.py --base /structure-case-library/
# 或挂到自定义域名根路径
python3 scripts/build_site.py --base /
```

使用绝对基路径后，本地请用本地服务器，并把站点放在对应前缀下；不要再用 `file://` 直接打开。

当前写入的 BASE 见 `docs/assets/config.js` 里的 `window.SITE_CONFIG.base`。

## 本地预览

相对路径模式（默认）：

```bash
cd docs
python3 -m http.server 8080
# 浏览器打开 http://127.0.0.1:8080/
```

或直接用浏览器打开 `docs/index.html`。
