document.addEventListener('DOMContentLoaded', () => {
    // Panel inferior de promociones cercanas
    const bottomPanel = document.getElementById('bottomPanel');
    const panelHandle = document.getElementById('panelHandle');

    if (bottomPanel && panelHandle) {
        panelHandle.addEventListener('click', () => {
            const isOpen = bottomPanel.classList.toggle('active');
            panelHandle.setAttribute('aria-expanded', String(isOpen));
            panelHandle.setAttribute(
                'aria-label',
                isOpen ? 'Ocultar promociones cerca de ti' : 'Mostrar promociones cerca de ti'
            );
        });
    }

    // 1. Inicializar el mapa
    let initLat = -33.5532855;
    let initLng = -70.6528958;
    const map = L.map('map').setView([initLat, initLng], 17);

    // 2. Capa de tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        minZoom: 4.5,
        attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);

    // 3. Icono personalizado
    const markerIcon = (imageUrl) => L.divIcon({
        className: 'custom-marker',
        html: `<img src="${imageUrl}" style="width: 100%; height: 100%; object-fit: cover;">`,
        iconSize: [50, 50],
        iconAnchor: [25, 50],
        popupAnchor: [0, -45]
    });

    // 4. Datos reales desde Flask
    const defaultIcon = '/static/imgs/default-business.png';
    const locations = (typeof negociosData !== 'undefined' ? negociosData : []).map(n => ({
        id: n.id,
        coords: [Number(n.lat), Number(n.lon)],
        name: n.nombre_negocio,
        image: n.image_url || defaultIcon,
        cardImage: n.card_image_url || n.image_url || defaultIcon,
        category: n.business_type,
        address: n.direccion,
        promotions: Number(n.active_promotions) || 0,
        featured: Boolean(n.featured),
        url: n.url || `/Negocio/${n.id || ''}`
    }));

    const nearbyPromotions = (typeof promocionesData !== 'undefined' ? promocionesData : []).map(p => ({
        id: p.id,
        businessId: p.business_id,
        businessName: p.business_name,
        businessType: p.business_type,
        name: p.promotion_name,
        description: p.description,
        price: p.price,
        banner: p.banner_url || defaultIcon,
        logo: p.logo_url || defaultIcon,
        coords: [Number(p.lat), Number(p.lon)],
        endDate: p.end_date,
        url: p.url || `/Negocio/${p.business_id || ''}#promociones`
    }));

    // 5. Mini tarjeta de negocio
    const businessCard = document.getElementById('businessCard');
    const closeBusinessCard = document.getElementById('closeBusinessCard');
    const businessFeatured = document.getElementById('businessFeatured');
    const businessCardImage = document.getElementById('businessCardImage');
    const businessCardName = document.getElementById('businessCardName');
    const businessCardCategory = document.getElementById('businessCardCategory');
    const businessCardDistance = document.getElementById('businessCardDistance');
    const businessCardPromotions = document.getElementById('businessCardPromotions');
    const businessCardLink = document.getElementById('businessCardLink');
    const nearbyPromotionsList = document.getElementById('nearbyPromotionsList');
    const nearbyPromotionsSummary = document.getElementById('nearbyPromotionsSummary');
    let userCoords = null;
    let selectedBusiness = null;

    const calculateDistance = (user, business) => {
        const earthRadius = 6371;
        const toRadians = degrees => degrees * Math.PI / 180;
        const latDifference = toRadians(business[0] - user[0]);
        const lngDifference = toRadians(business[1] - user[1]);
        const userLat = toRadians(user[0]);
        const businessLat = toRadians(business[0]);

        const a = Math.sin(latDifference / 2) ** 2
            + Math.cos(userLat) * Math.cos(businessLat)
            * Math.sin(lngDifference / 2) ** 2;

        return earthRadius * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    };

    const formatDistance = distance => distance < 1
        ? `${Math.round(distance * 1000)} m`
        : `${distance.toFixed(1)} km`;

    const renderNearbyPromotions = (origin, fromUserLocation = false) => {
        if (!nearbyPromotionsList || !nearbyPromotionsSummary) return;

        nearbyPromotionsList.replaceChildren();

        if (nearbyPromotions.length === 0) {
            nearbyPromotionsSummary.textContent = 'No hay promociones activas cerca por ahora.';
            const emptyState = document.createElement('div');
            emptyState.className = 'nearby-promotions-state';
            const icon = document.createElement('i');
            icon.className = 'fa-solid fa-tags';
            icon.setAttribute('aria-hidden', 'true');
            const message = document.createElement('p');
            message.textContent = 'Cuando los negocios publiquen promociones, aparecerán aquí.';
            emptyState.append(icon, message);
            nearbyPromotionsList.appendChild(emptyState);
            return;
        }

        const seenBusinesses = new Set();
        const promotions = nearbyPromotions
            .map(promotion => ({
                ...promotion,
                distance: calculateDistance(origin, promotion.coords)
            }))
            .sort((a, b) => a.distance - b.distance)
            .filter(promotion => {
                if (seenBusinesses.has(promotion.businessId)) return false;
                seenBusinesses.add(promotion.businessId);
                return true;
            })
            .slice(0, 3);

        nearbyPromotionsSummary.textContent = fromUserLocation
            ? 'Ofertas activas ordenadas desde tu ubicación.'
            : 'Ofertas activas en la zona visible del mapa.';

        const colorClasses = [
            { label: 'red-label', button: 'red-btn' },
            { label: 'yellow-label', button: 'yellow-btn' },
            { label: 'green-label', button: 'green-btn' }
        ];

        promotions.forEach((promotion, index) => {
            const colors = colorClasses[index % colorClasses.length];
            const card = document.createElement('article');
            card.className = 'bottomPanel-business';

            const banner = document.createElement('img');
            banner.className = 'promo-img';
            banner.src = promotion.banner;
            banner.alt = `Banner de ${promotion.businessName}`;

            const logo = document.createElement('img');
            logo.className = 'business-logo';
            logo.src = promotion.logo;
            logo.alt = `Logo de ${promotion.businessName}`;

            const content = document.createElement('div');
            content.className = 'business-text';
            const businessName = document.createElement('p');
            businessName.textContent = promotion.businessName;
            const title = document.createElement('h3');
            title.textContent = promotion.name;
            const description = document.createElement('p');
            description.textContent = promotion.description || promotion.price || 'Promoción activa';
            const distance = document.createElement('p');
            distance.className = 'promotion-distance';
            distance.textContent = `A ${formatDistance(promotion.distance)}`;
            content.append(businessName, title, description, distance);

            const endLabel = document.createElement('span');
            endLabel.className = `map-label ${colors.label}`;
            if (!promotion.endDate) {
                endLabel.textContent = 'Promoción activa';
            } else {
                const endDate = new Date(`${promotion.endDate}T00:00:00`);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                const daysLeft = Math.round((endDate - today) / 86400000);
                endLabel.textContent = daysLeft === 0
                    ? 'Vence hoy'
                    : daysLeft === 1
                        ? 'Hasta mañana'
                        : `Hasta ${endDate.toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit' })}`;
            }

            const businessLink = document.createElement('a');
            businessLink.className = colors.button;
            businessLink.href = promotion.url;
            businessLink.textContent = 'Ver negocio';

            card.append(banner, logo, content, endLabel, businessLink);
            nearbyPromotionsList.appendChild(card);
        });
    };

    const showDistance = (location) => {
        if (!userCoords) {
            businessCardDistance.textContent = 'Calculando distancia...';
            return;
        }
        const distance = calculateDistance(userCoords, location.coords);
        businessCardDistance.textContent = distance < 1
            ? `A ${Math.round(distance * 1000)} m`
            : `A ${distance.toFixed(1)} km`;
    };

    const showBusinessCard = (location) => {
        selectedBusiness = location;
        businessCardImage.src = location.cardImage;
        businessCardImage.alt = `Logo de ${location.name}`;
        businessCardName.textContent = location.name;
        businessCardCategory.textContent = location.category;
        showDistance(location);
        businessCardPromotions.textContent = location.promotions === 1
            ? '1 promoción activa'
            : `${location.promotions} promociones activas`;
        businessCardLink.href = location.url;
        businessFeatured.hidden = !location.featured;
        businessCard.classList.add('active');
        businessCard.setAttribute('aria-hidden', 'false');
    };

    const hideBusinessCard = () => {
        selectedBusiness = null;
        businessCard.classList.remove('active');
        businessCard.setAttribute('aria-hidden', 'true');
    };

    closeBusinessCard.addEventListener('click', hideBusinessCard);

    // 6. Añadir marcadores (UNA SOLA VEZ) + guardar referencia por id
    const markerGroup = L.featureGroup();
    const markersById = {};

    locations.forEach(location => {
        const marker = L.marker(location.coords, { icon: markerIcon(location.image) });
        marker.on('click', () => showBusinessCard(location));
        markerGroup.addLayer(marker);
        markersById[location.id] = { marker, location };
    });

    markerGroup.addTo(map);

    if (locations.length > 0) {
        map.fitBounds(markerGroup.getBounds(), { padding: [50, 50] });
    }

    const mapCenter = map.getCenter();
    renderNearbyPromotions([mapCenter.lat, mapCenter.lng]);

    map.on('click', hideBusinessCard);
    map.on('moveend', () => {
        if (userCoords) return;
        const center = map.getCenter();
        renderNearbyPromotions([center.lat, center.lng]);
    });

    // Ubicación en tiempo real del usuario
    let userMarker = null;
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                userCoords = [lat, lng];
                renderNearbyPromotions(userCoords, true);

                if (selectedBusiness) {
                    showDistance(selectedBusiness);
                }
                if (!userMarker) {
                    userMarker = L.marker([lat, lng], {
                        icon: L.icon({
                            iconUrl: 'https://cdn-icons-png.flaticon.com/512/64/64113.png',
                            iconSize: [50, 50],
                            iconAnchor: [16, 32],
                            popupAnchor: [0, -32]
                        })
                    }).addTo(map).bindPopup('¡Tu ubicación actual!').openPopup();
                    map.setView([lat, lng], 16);
                } else {
                    userMarker.setLatLng([lat, lng]);
                }
            },
            (err) => {
                console.warn('Error obteniendo ubicación:', err);
                if (selectedBusiness) {
                    businessCardDistance.textContent = 'Ubicación no disponible';
                }
            },
            { enableHighAccuracy: true, maximumAge: 10000, timeout: 20000 }
        );
    } else {
        console.warn('Geolocalización no soportada por este navegador.');
    }

    // 7. Búsqueda unificada y panel flotante de resultados
    const searchArea = document.getElementById('searchArea');
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const searchResultsPanel = document.getElementById('searchResultsPanel');
    const searchResultsSummary = document.getElementById('searchResultsSummary');
    const searchResults = document.getElementById('searchResults');
    let searchController = null;

    const openSearchResults = () => {
        searchResultsPanel.hidden = false;
        searchInput.setAttribute('aria-expanded', 'true');
    };

    const closeSearchResults = () => {
        searchResultsPanel.hidden = true;
        searchInput.setAttribute('aria-expanded', 'false');
    };

    const renderSearchState = ({ summary, icon, title, description }) => {
        searchResults.replaceChildren();
        searchResultsSummary.textContent = summary;

        const item = document.createElement('li');
        item.className = 'search-results-state';

        const iconContainer = document.createElement('span');
        iconContainer.className = 'search-results-state-icon';

        const iconElement = document.createElement('i');
        iconElement.className = icon;
        iconElement.setAttribute('aria-hidden', 'true');
        iconContainer.appendChild(iconElement);

        const message = document.createElement('div');
        const heading = document.createElement('h3');
        const text = document.createElement('p');
        heading.textContent = title;
        text.textContent = description;
        message.append(heading, text);

        item.append(iconContainer, message);
        searchResults.appendChild(item);
        openSearchResults();
    };

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await runSearch(searchInput.value);
    });

    async function runSearch(query) {
        const normalizedQuery = query.trim();

        if (!normalizedQuery) {
            renderSearchState({
                summary: 'Búsqueda vacía',
                icon: 'fa-solid fa-magnifying-glass',
                title: 'Escribe qué quieres encontrar.',
                description: 'Busca negocios, usuarios o promociones.'
            });
            return;
        }

        if (normalizedQuery.length < 2) {
            renderSearchState({
                summary: 'Falta un carácter',
                icon: 'fa-solid fa-keyboard',
                title: 'Escribe al menos 2 caracteres.',
                description: 'Así podremos mostrarte resultados más útiles.'
            });
            return;
        }

        if (searchController) {
            searchController.abort();
        }

        const currentController = new AbortController();
        searchController = currentController;

        renderSearchState({
            summary: 'Buscando en Almaceb RED',
            icon: 'fa-solid fa-spinner fa-spin',
            title: 'Buscando...',
            description: 'Estamos revisando negocios, usuarios y promociones.'
        });

        try {
            const res = await fetch(`/search?q=${encodeURIComponent(normalizedQuery)}`, {
                signal: currentController.signal
            });

            if (!res.ok) {
                throw new Error(`La búsqueda respondió con estado ${res.status}`);
            }

            const data = await res.json();
            renderResults(data, normalizedQuery);
        } catch (err) {
            if (err.name === 'AbortError') return;

            console.error('Error en búsqueda:', err);
            renderSearchState({
                summary: 'No pudimos completar la búsqueda',
                icon: 'fa-solid fa-circle-exclamation',
                title: 'Ocurrió un problema al buscar.',
                description: 'Inténtalo nuevamente en unos momentos.'
            });
        } finally {
            if (searchController === currentController) {
                searchController = null;
            }
        }
    }

    function renderResults(results, query) {
        searchResults.replaceChildren();

        if (results.length === 0) {
            renderSearchState({
                summary: 'Sin resultados',
                icon: 'fa-solid fa-magnifying-glass',
                title: `No encontramos resultados para “${query}”.`,
                description: 'Prueba con otro nombre, categoría o promoción.'
            });
            return;
        }

        searchResultsSummary.textContent = results.length === 1
            ? '1 resultado encontrado'
            : `${results.length} resultados encontrados`;

        results.forEach(r => {
            const resultType = r.result_type || 'business';
            const titleText = r.title || r.nombre_negocio || 'Resultado';
            const li = document.createElement('li');
            li.className = 'search-result-item';

            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'search-result-button';
            button.dataset.resultType = resultType;
            button.setAttribute('aria-label', `Seleccionar ${titleText}`);

            const imageSource = r.image_url || r.image || r.logo;
            let visual;

            if (imageSource) {
                visual = document.createElement('img');
                visual.className = 'search-result-image';
                visual.src = imageSource;
                visual.alt = `Imagen de ${titleText}`;
            } else {
                visual = document.createElement('span');
                visual.className = `search-result-image-placeholder search-result-image-placeholder--${resultType}`;
                visual.setAttribute('aria-hidden', 'true');
                const placeholderIcon = document.createElement('i');
                placeholderIcon.className = resultType === 'user'
                    ? 'fa-solid fa-user'
                    : resultType === 'promotion'
                        ? 'fa-solid fa-tag'
                        : 'fa-solid fa-store';
                visual.appendChild(placeholderIcon);
            }

            const content = document.createElement('span');
            content.className = 'search-result-content';

            const name = document.createElement('h3');
            name.textContent = titleText;
            content.appendChild(name);

            const typeLabels = {
                business: 'Negocio',
                user: 'Usuario',
                promotion: 'Promoción'
            };
            const typeBadge = document.createElement('span');
            typeBadge.className = `search-result-type search-result-type--${resultType}`;
            typeBadge.textContent = typeLabels[resultType] || 'Resultado';
            content.appendChild(typeBadge);

            const locationText = r.location || r.comuna || r.ubicacion || r.direccion;
            let metadata = [];

            if (resultType === 'user') {
                metadata = [r.account_label];
            } else if (resultType === 'promotion') {
                metadata = [r.business_name && `De ${r.business_name}`, r.business_type, locationText];
            } else {
                metadata = [r.business_type, locationText];
            }
            metadata = metadata.filter(Boolean);

            if (metadata.length) {
                const meta = document.createElement('p');
                meta.className = 'search-result-meta';
                meta.textContent = metadata.join(' · ');
                content.appendChild(meta);
            }

            if (resultType === 'promotion') {
                const promotionLabel = document.createElement('span');
                promotionLabel.className = 'search-result-promotions crimson-label';
                const promotionPrice = r.price === null || r.price === undefined
                    ? ''
                    : String(r.price).trim();
                promotionLabel.textContent = /^\d+$/.test(promotionPrice)
                    ? new Intl.NumberFormat('es-CL', {
                        style: 'currency',
                        currency: 'CLP',
                        maximumFractionDigits: 0
                    }).format(Number(promotionPrice))
                    : promotionPrice || 'Promoción activa';
                content.appendChild(promotionLabel);
            } else if (resultType === 'business') {
                const promotionCount = r.active_promotions ?? r.promociones_activas ?? r.promotions;
                if (Number(promotionCount) > 0) {
                    const promotions = document.createElement('span');
                    promotions.className = 'search-result-promotions green-label';
                    promotions.textContent = Number(promotionCount) === 1
                        ? '1 promoción activa'
                        : `${promotionCount} promociones activas`;
                    content.appendChild(promotions);
                }
            }

            const arrow = document.createElement('i');
            arrow.className = 'search-result-arrow fa-solid fa-chevron-right';
            arrow.setAttribute('aria-hidden', 'true');

            button.append(visual, content, arrow);
            button.addEventListener('click', () => selectResult(r));
            li.appendChild(button);
            searchResults.appendChild(li);
        });

        openSearchResults();
    }

    function selectResult(result) {
        if (result.result_type === 'user') {
            if (result.url) window.location.assign(result.url);
            return;
        }

        const businessId = result.marker_business_id || result.id;
        const entry = markersById[businessId];
        if (!entry) {
            if (result.url) window.location.assign(result.url);
            return;
        }

        map.setView(entry.location.coords, 18);
        showBusinessCard(entry.location);

        searchInput.value = result.title || result.nombre_negocio || '';
        closeSearchResults();
    }

    searchInput.addEventListener('input', () => {
        if (searchInput.value.trim()) return;

        if (searchController) {
            searchController.abort();
            searchController = null;
        }

        searchResults.replaceChildren();
        closeSearchResults();
    });

    document.addEventListener('pointerdown', (event) => {
        if (!searchResultsPanel.hidden && !searchArea.contains(event.target)) {
            closeSearchResults();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !searchResultsPanel.hidden) {
            closeSearchResults();
            searchInput.focus();
        }
    });
}); // Movemos todo dentro del DOM content
// Bailamos un poquito
