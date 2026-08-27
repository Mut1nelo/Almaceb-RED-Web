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

    // Menú de acciones secundarias en las tarjetas de "Mis negocios".
    const businessMenus = document.querySelectorAll('.ab-more-menu');
    businessMenus.forEach(menu => {
        menu.querySelector('summary')?.addEventListener('click', () => {
            businessMenus.forEach(otherMenu => {
                if (otherMenu !== menu) otherMenu.removeAttribute('open');
            });
        });
    });

    document.addEventListener('click', event => {
        businessMenus.forEach(menu => {
            if (!menu.contains(event.target)) menu.removeAttribute('open');
        });
    });

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
            const productDetailIsOpen = document.querySelector('.product-detail-modal')?.hidden === false;
            if (event.key === 'Escape' && !galleryModal.hidden && !productDetailIsOpen) {
                closeGallery();
            }
        });
    }

    // Muestra la ficha del producto sin abandonar la página del negocio.
    const productTriggers = document.querySelectorAll('.product-card-trigger');
    const productDetailModal = document.querySelector('.product-detail-modal');
    const productDetailClose = document.querySelector('.product-detail-close');

    if (productTriggers.length && productDetailModal && productDetailClose) {
        const detailImage = productDetailModal.querySelector('.product-detail-image');
        const detailTitle = productDetailModal.querySelector('#product-detail-title');
        const detailPrice = productDetailModal.querySelector('.product-detail-price');
        const detailDescription = productDetailModal.querySelector('.product-detail-description');
        const detailEdit = productDetailModal.querySelector('.product-detail-edit');
        let lastProductTrigger = null;

        const openProductDetail = (trigger) => {
            lastProductTrigger = trigger;
            detailImage.src = trigger.dataset.productImage || '';
            detailImage.alt = trigger.dataset.productName || 'Producto';
            detailTitle.textContent = trigger.dataset.productName || 'Producto';
            detailPrice.textContent = trigger.dataset.productPrice || 'Precio no informado';
            detailDescription.textContent = trigger.dataset.productDescription || 'Sin descripción disponible.';

            if (trigger.dataset.productEditUrl) {
                detailEdit.href = trigger.dataset.productEditUrl;
                detailEdit.hidden = false;
            } else {
                detailEdit.hidden = true;
                detailEdit.removeAttribute('href');
            }

            productDetailModal.hidden = false;
            document.body.classList.add('gallery-modal-open');
            productDetailClose.focus();
        };

        const closeProductDetail = () => {
            productDetailModal.hidden = true;
            if (!galleryModal || galleryModal.hidden) {
                document.body.classList.remove('gallery-modal-open');
            }
            lastProductTrigger?.focus();
        };

        productTriggers.forEach(trigger => {
            trigger.addEventListener('click', () => openProductDetail(trigger));
        });

        productDetailClose.addEventListener('click', closeProductDetail);
        productDetailModal.addEventListener('click', (event) => {
            if (event.target === productDetailModal) closeProductDetail();
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && !productDetailModal.hidden) {
                closeProductDetail();
            }
        });
    }
});
