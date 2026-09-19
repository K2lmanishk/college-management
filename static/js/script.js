// Theme toggle + service worker registration
document.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-bs-theme', saved);

  const btn = document.getElementById('themeToggle');
  if (btn) {
    btn.addEventListener('click', () => {
      const cur = document.documentElement.getAttribute('data-bs-theme');
      const nxt = cur === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-bs-theme', nxt);
      localStorage.setItem('theme', nxt);
    });
  }

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/service-worker.js').catch(() => {});
  }
});
