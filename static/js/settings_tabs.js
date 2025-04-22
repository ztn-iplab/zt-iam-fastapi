document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.tab-btn');
  const contents = document.querySelectorAll('.tab-content');
  const hash = window.location.hash;
if (hash) {
  const activeTab = document.querySelector(`.tab-btn[data-tab="${hash.substring(1)}"]`);
  if (activeTab) activeTab.click();
}

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      document.getElementById(tab.dataset.tab).classList.add('active');
    });
  });
});
