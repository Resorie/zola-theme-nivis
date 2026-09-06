const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");
const mobileSidebar = window.matchMedia("(max-width: 960px)");
const feedButton = document.querySelector(".feed-icon");
const feedDropdown = document.getElementById("feed-dropdown");
const feedContainer = document.querySelector(".feed_btn");
let feedPinned = false;

function setFeedOpen(open, restoreFocus = false) {
  if (!feedButton) return;
  if (open && document.getElementById("search-toggle")?.getAttribute("aria-expanded") === "true") return;
  feedDropdown.hidden = !open;
  feedButton.setAttribute("aria-expanded", String(open));
  if (!open) feedPinned = false;
  if (restoreFocus) feedButton.focus();
}

function setSidebarOpen(open, restoreFocus = false) {
  if (!sidebar) return;
  open = open && mobileSidebar.matches;
  sidebar.classList.toggle("open", open);
  document.getElementById("sidebar-mask").classList.toggle("open", open);
  sidebar.inert = mobileSidebar.matches && !open;
  sidebarToggle.setAttribute("aria-expanded", String(open));
  if (restoreFocus) sidebarToggle.focus();
}

function toggleSidebar() {
  if (!sidebar) return;
  const open = !sidebar.classList.contains("open");
  setFeedOpen(false);
  setSidebarOpen(open, !open);
  if (open) sidebar.querySelector(".sidebar-nav a").focus();
}

if (sidebar) {
  setSidebarOpen(false);
  mobileSidebar.addEventListener("change", () => setSidebarOpen(false));
  sidebar.addEventListener("focusout", (event) => {
    if (event.relatedTarget && !sidebar.contains(event.relatedTarget) && event.relatedTarget !== sidebarToggle) {
      setSidebarOpen(false);
    }
  });
}

if (feedButton) {
  feedButton.addEventListener("click", () => {
    feedPinned = !feedPinned;
    setFeedOpen(feedPinned);
  });
  feedButton.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      feedPinned = true;
      setFeedOpen(true);
      feedDropdown.querySelector("a").focus();
    }
  });
  feedContainer.addEventListener("pointerenter", (event) => {
    if (event.pointerType === "mouse") setFeedOpen(true);
  });
  feedContainer.addEventListener("pointerleave", () => {
    if (!feedPinned && !feedContainer.contains(document.activeElement)) setFeedOpen(false);
  });
  feedContainer.addEventListener("focusout", (event) => {
    if (!feedContainer.contains(event.relatedTarget)) setFeedOpen(false);
  });
  feedDropdown.addEventListener("click", (event) => {
    if (event.target.closest("a")) setFeedOpen(false, true);
  });
  document.addEventListener("pointerdown", (event) => {
    if (!feedContainer.contains(event.target)) setFeedOpen(false);
  });
}

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (feedDropdown && !feedDropdown.hidden) {
    setFeedOpen(false, feedContainer.contains(document.activeElement));
  } else if (sidebar && sidebar.classList.contains("open")) {
    setSidebarOpen(false, true);
  }
});

const getPreferredScheme = () => window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

function updateThemeIcon(scheme) {
  const themeIcon = document.getElementById("theme-icon");
  if (themeIcon) {
    themeIcon.closest("button").setAttribute("aria-pressed", String(scheme === "dark"));
    if (scheme === 'dark') {
      themeIcon.classList.remove("fa-moon");
      themeIcon.classList.add("fa-sun");
    } else {
      themeIcon.classList.remove("fa-sun");
      themeIcon.classList.add("fa-moon");
    }
  }
}

function toggleTheme() {
  const root = document.documentElement;
  const effectiveScheme = root.style.colorScheme || getPreferredScheme();
  const targetScheme = effectiveScheme === 'dark' ? 'light' : 'dark';

  root.style.colorScheme = targetScheme;
  localStorage.setItem("theme", targetScheme);
  updateThemeIcon(targetScheme);
}

// Initialize theme icon
(function() {
  const savedTheme = localStorage.getItem("theme");
  const systemTheme = getPreferredScheme();
  updateThemeIcon(savedTheme || systemTheme);

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem("theme")) {
      updateThemeIcon(e.matches ? 'dark' : 'light');
    }
  });
})();
