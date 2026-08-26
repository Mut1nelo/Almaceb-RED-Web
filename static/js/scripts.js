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

    // Carrusel de promociones de la página del negocio.
    const promotionList = document.querySelector('.promotion-list');
    const promotionPrev = document.querySelector('.promotion-prev');
    const promotionNext = document.querySelector('.promotion-next');

    if (promotionList && promotionPrev && promotionNext) {
        const movePromotions = (direction) => {
            const promotionCard = promotionList.querySelector('.promotion-card');

            if (promotionCard) {
                const cardGap = 24;
                const distance = promotionCard.offsetWidth + cardGap;

                promotionList.scrollBy({
                    left: distance * direction,
                    behavior: 'smooth'
                });
            }
        };

        promotionPrev.addEventListener('click', () => movePromotions(-1));
        promotionNext.addEventListener('click', () => movePromotions(1));
    }

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
