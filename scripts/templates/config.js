/* 站点基路径
 *
 * 默认使用相对路径：本地直接打开 docs/index.html，
 * 或用本地服务器预览，以及 GitHub Pages 项目站
 * （https://<user>.github.io/structure-case-library/）均可浏览。
 *
 * 若需要改成绝对基路径（例如自定义域名根路径，或必须写死
 * /structure-case-library/），重新运行：
 *
 *   python3 scripts/build_site.py --base /structure-case-library/
 *   python3 scripts/build_site.py --base /
 *
 * 当前构建写入的 BASE 见 window.SITE_CONFIG.base。
 */
window.SITE_CONFIG = {
  base: "__SITE_BASE__",
  title: "结构设计案例库"
};
