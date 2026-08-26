(function () {
  const darkPreference = window.matchMedia("(prefers-color-scheme: dark)");

  function applyPreferredTheme() {
    const theme = darkPreference.matches ? "dark" : "light";
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme === "light" ? "light" : "dark";
  }

  applyPreferredTheme();
  darkPreference.addEventListener("change", applyPreferredTheme);
})();
