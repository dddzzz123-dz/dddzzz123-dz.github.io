(() => {
  const data = window.REPO_DATA;
  if (!data) return;
  const esc = (value) => String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link = (url, label, className = '') => '<a class="item-link ' + className + '" href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(label) + ' <span>↗</span></a>';

  document.querySelector('#web-projects').innerHTML = data.web.map((item) => {
    if (item.children) {
      return '<article class="web-item web-group"><div class="web-group-head"><div><h3>' + esc(item.title) + '</h3><p>' + esc(item.description) + '</p><a class="related-link" href="#metro-rental-skill" data-highlight-target="skill">查看对应 Skill ↓</a></div></div><div class="web-children">' + item.children.map((child) => '<article class="web-child"><a class="web-preview" href="' + esc(child.live) + '" target="_blank" rel="noopener"><img src="' + esc(child.preview) + '" alt="' + esc(child.title) + '预览图"><span>打开网页 ↗</span></a><div class="web-info"><h4>' + esc(child.title) + '</h4><p>' + esc(child.description) + '</p><small>' + esc(child.name) + '</small></div></article>').join('') + '</div></article>';
    }
    return '<article class="web-item"><a class="web-preview" href="' + esc(item.live) + '" target="_blank" rel="noopener"><img src="' + esc(item.preview) + '" alt="' + esc(item.title) + '预览图"><span>打开网页 ↗</span></a><div class="web-info"><h3>' + esc(item.title) + '</h3><p>' + esc(item.description) + '</p><small>' + esc(item.name) + '</small></div></article>';
  }).join('');

  document.querySelector('#skill-list').innerHTML = data.skills.map((item) =>
    '<article class="skill-item" data-skill="' + esc(item.name) + '"><div class="item-heading"><div><h3>' + esc(item.title) + '</h3><small>' + esc(item.name) + '</small></div>' + link(item.repo, '仓库') + '</div><p>' + esc(item.description) + '</p>' + (item.name === 'metro-rental-research-skill' ? '<a class="related-link" href="#rental-results" data-highlight-target="web">查看网页结果 ↓</a>' : '') + '<div class="prompt-box"><div class="prompt-head"><span>复制给你的 Agent</span><button type="button" class="copy-button" data-copy="' + esc(item.prompt) + '">复制</button></div><code>' + esc(item.prompt) + '</code></div></article>'
  ).join('');

  const collectionPlugins = data.plugins.filter((item) => !item.children);
  const dshPlugin = data.plugins.find((item) => item.children);
  const pluginCard = (item) => '<article class="plugin-item"><div><h3>' + esc(item.title) + '</h3><small>' + esc(item.kind) + '</small><p>' + esc(item.description) + '</p></div><a class="download-button" href="' + esc(item.download) + '" download>下载 ZIP <span>↓</span></a></article>';
  const dshCard = dshPlugin ? '<article class="plugin-item plugin-group"><div><h3>' + esc(dshPlugin.title) + '</h3><small>' + esc(dshPlugin.kind) + '</small><p>' + esc(dshPlugin.description) + '</p></div><div class="plugin-subitems">' + dshPlugin.children.map((child) => '<a class="download-button" href="' + esc(child.download) + '" download>' + esc(child.title) + ' ZIP <span>↓</span></a>').join('') + '</div></article>' : '';
  document.querySelector('#plugin-list').innerHTML = '<div class="plugin-project"><div class="plugin-project-head"><div><h3>采集提效工具开发</h3><p>把搜索、筛选、采集、记录和导出整理成可重复使用的 Chrome 插件。</p></div><span>四个插件</span></div><div class="plugin-project-grid">' + collectionPlugins.map(pluginCard).join('') + '</div></div>' + dshCard;

  document.querySelectorAll('[data-copy]').forEach((button) => button.addEventListener('click', async () => {
    const text = button.dataset.copy;
    try { await navigator.clipboard.writeText(text); button.textContent = '已复制'; }
    catch { button.textContent = '请手动复制'; }
    window.setTimeout(() => { button.textContent = '复制'; }, 1800);
  }));

  const highlightTarget = (kind) => {
    const target = document.querySelector(kind === 'skill' ? '[data-skill="metro-rental-research-skill"]' : kind === 'web' ? '.web-group' : '.plugin-project');
    if (!target) return;
    target.classList.remove('is-highlighted');
    window.requestAnimationFrame(() => target.classList.add('is-highlighted'));
    window.setTimeout(() => target.classList.remove('is-highlighted'), 1800);
  };
  document.querySelectorAll('[data-highlight-target]').forEach((anchor) => anchor.addEventListener('click', () => window.setTimeout(() => highlightTarget(anchor.dataset.highlightTarget), 120)));
})();
