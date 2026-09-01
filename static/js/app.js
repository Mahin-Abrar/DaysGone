document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initUserMenu();
    initAvatarPicker();
    initPWA();
    initPageTransitions();
});

function initPageTransitions() {
    const main = document.getElementById('page-content');
    if (!main) return;

    document.querySelectorAll('a.internal-nav').forEach((link) => {
        link.addEventListener('click', (e) => {
            if (e.metaKey || e.ctrlKey || e.shiftKey || link.target === '_blank') return;
            const href = link.getAttribute('href');
            if (!href || href.startsWith('#') || href.startsWith('http')) return;

            e.preventDefault();
            main.classList.remove('page-enter');
            main.classList.add('page-exit');

            const go = () => { window.location.href = href; };

            if (document.startViewTransition) {
                document.startViewTransition(go);
            } else {
                setTimeout(go, 220);
            }
        });
    });
}

function initPWA() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(() => {});
    }

    const isStandalone = window.matchMedia('(display-mode: standalone)').matches
        || window.navigator.standalone === true;
    const dismissed = localStorage.getItem('install-dismissed');
    const banner = document.getElementById('install-banner');
    const installBtn = document.getElementById('install-btn');
    const dismissBtn = document.getElementById('install-dismiss');

    let deferredPrompt = null;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        if (!isStandalone && !dismissed && banner) banner.classList.remove('hidden');
    });

    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    if (isMobile && !isStandalone && !dismissed && banner && !deferredPrompt) {
        setTimeout(() => banner.classList.remove('hidden'), 1500);
    }

    if (installBtn) {
        installBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                await deferredPrompt.userChoice;
                deferredPrompt = null;
                banner.classList.add('hidden');
            } else {
                window.location.href = '/install/';
            }
        });
    }

    if (dismissBtn) {
        dismissBtn.addEventListener('click', () => {
            banner.classList.add('hidden');
            localStorage.setItem('install-dismissed', '1');
        });
    }
}

function setTheme(dark) {
    document.documentElement.classList.toggle('dark', dark);
    localStorage.setItem('theme', dark ? 'dark' : 'light');
    updateThemeMeta(dark);
    updateThemeUI(dark);
}

function updateThemeMeta(dark) {
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = dark ? '#111827' : '#6366f1';
}

function updateThemeUI(dark) {
    const dropdownIcon = document.getElementById('theme-dropdown-icon');
    const dropdownLabel = document.getElementById('theme-dropdown-label');
    if (dropdownIcon) dropdownIcon.textContent = dark ? '☀️' : '🌙';
    if (dropdownLabel) dropdownLabel.textContent = dark ? 'Light Mode' : 'Dark Mode';
}

function toggleTheme() {
    setTheme(!document.documentElement.classList.contains('dark'));
}

function initTheme() {
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const dark = saved === 'dark' || (!saved && prefersDark);
    setTheme(dark);

    document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);
    document.getElementById('theme-toggle-mobile')?.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleTheme();
    });
}

function initUserMenu() {
    const btn = document.getElementById('user-menu-btn');
    const menu = document.getElementById('user-dropdown');
    if (!btn || !menu) return;

    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const open = menu.classList.toggle('open');
        btn.classList.toggle('open', open);
        btn.setAttribute('aria-expanded', open);
    });

    document.addEventListener('click', () => {
        menu.classList.remove('open');
        btn.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
    });

    menu.addEventListener('click', (e) => e.stopPropagation());
}

function initAvatarPicker() {
    const picker = document.getElementById('avatar-picker');
    if (!picker) return;

    const colorInput = document.querySelector('input[name="avatar_color"]');
    const preview = document.getElementById('avatar-preview');

    picker.querySelectorAll('.avatar-option').forEach(opt => {
        opt.addEventListener('click', () => {
            picker.querySelectorAll('.avatar-option').forEach(o => o.classList.remove('selected'));
            opt.classList.add('selected');
            const radio = opt.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
            if (preview) preview.textContent = opt.dataset.avatar;
        });
    });

    document.querySelectorAll('.color-swatch').forEach(swatch => {
        swatch.addEventListener('click', () => {
            document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
            swatch.classList.add('selected');
            const color = swatch.dataset.color;
            if (colorInput) colorInput.value = color;
            if (preview) preview.style.background = color;
        });
    });
}
