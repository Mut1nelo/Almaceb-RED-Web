window.addEventListener('DOMContentLoaded', () => {
    // Dark Mode Toggle + API color preference
    const btn = document.getElementById('dark-toggle');
    const elementos = document.querySelectorAll('.dark-mode');
    const STORAGE_KEY = "dark-mode-active";
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

    function setDarkOn() {
        elementos.forEach(el => el.classList.add('dark-mode--active'));
    }
    function setDarkOff() {
        elementos.forEach(el => el.classList.remove('dark-mode--active'));
    }

    function applyPreference(pref) {
        if (pref === 'dark') setDarkOn();
        else setDarkOff();
    }

    function toggleDarkMode() {
        if (!elementos.length) return;
        const active = elementos[0].classList.contains("dark-mode--active");
        if (active) {
            setDarkOff();
            localStorage.setItem(STORAGE_KEY, "no");
        } else {
            setDarkOn();
            localStorage.setItem(STORAGE_KEY, "yes");
        }
    }

    if (btn) btn.addEventListener('click', toggleDarkMode);

    // Inicialización:
    // 1) Si el usuario ya eligió (localStorage) -> respetar
    // 2) Si no, usar la preferencia del sistema
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "yes") {
        applyPreference('dark');
    } else if (stored === "no") {
        applyPreference('light');
    } else {
        applyPreference(prefersDark.matches ? 'dark' : 'light');
    }

    // Si el usuario no seleccionó manualmente, actualizar según cambios del sistema
    prefersDark.addEventListener('change', (e) => {
        const storedNow = localStorage.getItem(STORAGE_KEY);
        if (!storedNow) {
            applyPreference(e.matches ? 'dark' : 'light');
        }
    });
});