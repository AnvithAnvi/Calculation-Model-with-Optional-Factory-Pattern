// Theme Switcher with Local Storage
(function() {
  const themeKey = 'calc-theme';
  const currentTheme = localStorage.getItem(themeKey) || 'dark';
  
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(themeKey, theme);
    
    // Update toggle button if it exists
    const toggleBtn = document.getElementById('themeToggle');
    if (toggleBtn) {
      toggleBtn.innerHTML = theme === 'dark' 
        ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
        : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    }
  }
  
  // Apply theme immediately to prevent flash
  applyTheme(currentTheme);
  
  // Initialize theme toggle when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('themeToggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', function() {
        const theme = localStorage.getItem(themeKey) || 'dark';
        applyTheme(theme === 'dark' ? 'light' : 'dark');
      });
    }
  });
  
  window.setTheme = applyTheme;
})();
