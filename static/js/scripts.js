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

    // Pesca el tipo de cuenta desde html en vez de complicarlo
    const tipoUsuario = document.body.getAttribute('data-account-type') || 'invitado';

    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebarMenu = document.getElementById('sidebarPanel');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const closeSidebarButton = document.getElementById('closeSidebar');
    const sidebarStates = document.querySelectorAll('.sidebar-state');

    // Traducciones pq no quiero cambiar muxo tu codigo 
    const accountTypeMap = {
        'invitado': 'invitado',
        'client': 'cliente',
        'business': 'vendedor'
    };

    // Muestra solamente el bloque que corresponde al tipo de usuario.
    const showSidebarState = (state) => {
        const mappedState = accountTypeMap[state] || 'invitado';
        const validStates = ['invitado', 'cliente', 'vendedor'];
        const selectedState = validStates.includes(mappedState) ? mappedState : 'invitado';

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

    // Control reutilizable para los carruseles de promociones y del ranking.
    const setupHorizontalCarousel = (list, previousButton, nextButton, itemSelector) => {
        if (!list || !previousButton || !nextButton) {
            return;
        }

        const updateButtons = () => {
            const maxScroll = Math.max(0, list.scrollWidth - list.clientWidth);
            previousButton.disabled = list.scrollLeft <= 2;
            nextButton.disabled = list.scrollLeft >= maxScroll - 2;
        };

        const moveCarousel = (direction) => {
            const item = list.querySelector(itemSelector);
            if (!item) {
                return;
            }

            const styles = window.getComputedStyle(list);
            const gap = Number.parseFloat(styles.columnGap || styles.gap) || 24;
            const distance = list.dataset.carouselStep === 'page'
                ? list.clientWidth + gap
                : item.offsetWidth + gap;

            list.scrollBy({
                left: distance * direction,
                behavior: 'smooth'
            });
        };

        previousButton.addEventListener('click', () => moveCarousel(-1));
        nextButton.addEventListener('click', () => moveCarousel(1));
        list.addEventListener('scroll', updateButtons, { passive: true });
        window.addEventListener('resize', updateButtons);
        updateButtons();
    };

    setupHorizontalCarousel(
        document.querySelector('.promotion-list'),
        document.querySelector('.promotion-prev'),
        document.querySelector('.promotion-next'),
        '.promotion-card'
    );

    setupHorizontalCarousel(
        document.getElementById('featured-card-container'),
        document.querySelector('.featured-prev'),
        document.querySelector('.featured-next'),
        '.featured-card'
    );

    // Abre y cierra la galería completa de productos.
    const galleryOpen = document.querySelector('.gallery-open');
    const galleryModal = document.querySelector('.gallery-modal');
    const galleryClose = document.querySelector('.gallery-close');

    if (galleryOpen && galleryModal && galleryClose) {
        const openGallery = () => {
            galleryModal.hidden = false;
            document.body.classList.add('gallery-modal-open');
            galleryClose.focus();
        };

        const closeGallery = () => {
            galleryModal.hidden = true;
            document.body.classList.remove('gallery-modal-open');
            galleryOpen.focus();
        };

        galleryOpen.addEventListener('click', openGallery);
        galleryClose.addEventListener('click', closeGallery);

        galleryModal.addEventListener('click', (event) => {
            if (event.target === galleryModal) {
                closeGallery();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && !galleryModal.hidden) {
                closeGallery();
            }
        });
    }
});
