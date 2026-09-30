(() => {
  const controls = document.querySelector('[data-filters]');
  if (!controls) return;
  const cards = [...document.querySelectorAll('[data-publication]')];
  const status = document.querySelector('[data-filter-status]');
  controls.hidden = false;
  controls.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-topic]');
    if (!button) return;
    controls.querySelectorAll('button').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    let count = 0;
    cards.forEach((card) => {
      card.hidden = button.dataset.topic !== 'all' && card.dataset.topic !== button.dataset.topic;
      if (!card.hidden) count++;
    });
    status.textContent = document.documentElement.lang === 'zh-CN' ? `显示 ${count} 篇论文` : `${count} publications shown`;
  });
})();
