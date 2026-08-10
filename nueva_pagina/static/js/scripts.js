document.addEventListener('DOMContentLoaded', () => {
    // Botón reutilizable para regresar a la página anterior.
    const backButton = document.querySelector('.back-button');

    if (backButton) {
        backButton.addEventListener('click', () => {
            if (window.history.length > 1) {
                window.history.back();
            } else {
                window.location.href = '/';
            }
        });
    }

    // Selector temporal, cambia este valor por "invitado", "cliente" o "vendedor".
    const tipoUsuario = 'invitado';

    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebarMenu = document.getElementById('sidebarPanel');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const closeSidebarButton = document.getElementById('closeSidebar');
    const sidebarStates = document.querySelectorAll('.sidebar-state');

    // Muestra solamente el bloque que corresponde al tipo de usuario.
    const showSidebarState = (state) => {
        const validStates = ['invitado', 'cliente', 'vendedor'];
        const selectedState = validStates.includes(state) ? state : 'invitado';

        sidebarStates.forEach(sidebarState => {
            sidebarState.classList.toggle(
                'active',
                sidebarState.dataset.userState === selectedState
            );
        });
    };

    const openSidebar = () => {
        sidebarMenu.classList.add('active');
        sidebarOverlay.classList.add('active');
        sidebarMenu.setAttribute('aria-hidden', 'false');
        sidebarToggle.setAttribute('aria-expanded', 'true');
    };

    const closeSidebar = () => {
        sidebarMenu.classList.remove('active');
        sidebarOverlay.classList.remove('active');
        sidebarMenu.setAttribute('aria-hidden', 'true');
        sidebarToggle.setAttribute('aria-expanded', 'false');
    };

    showSidebarState(tipoUsuario);

    if (sidebarToggle && sidebarMenu && sidebarOverlay && closeSidebarButton) {
        sidebarToggle.addEventListener('click', openSidebar);
        closeSidebarButton.addEventListener('click', closeSidebar);
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && sidebarMenu && sidebarOverlay && sidebarToggle) {
            closeSidebar();
        }
    });
});
