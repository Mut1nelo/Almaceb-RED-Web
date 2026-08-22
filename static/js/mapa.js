document.addEventListener('DOMContentLoaded', () => {
    // Panel inferior de promociones
    const bottomPanel = document.getElementById('bottomPanel');
    const panelHandle = document.getElementById('panelHandle');

    if (bottomPanel && panelHandle) {
        panelHandle.addEventListener('click', () => {
            bottomPanel.classList.toggle('active');
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
    const defaultIcon = "../static/imgs/icons/in-1.png";
    const locations = (typeof negociosData !== 'undefined' ? negociosData : []).map(n => ({
        id: n.id,
        coords: [n.lat, n.lon],
        name: n.nombre_negocio,
        image: defaultIcon,
        cardImage: '../static/imgs/img-proto.png',
        category: n.business_type,
        promotions: 0,
        featured: false,
        url: `/Negocio/${n.id || ''}`
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
        businessCardPromotions.textContent = `${location.promotions} promociones activas`;
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

    map.on('click', hideBusinessCard);

    // Ubicación en tiempo real del usuario
    let userMarker = null;
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                userCoords = [lat, lng];

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

    // 7. Búsqueda de negocios y panel flotante de resultados
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
                description: 'Busca un negocio por su nombre o categoría.'
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
            summary: 'Buscando negocios',
            icon: 'fa-solid fa-spinner fa-spin',
            title: 'Buscando...',
            description: 'Estamos revisando los negocios de Almaceb RED.'
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
                icon: 'fa-solid fa-store-slash',
                title: `No encontramos resultados para “${query}”.`,
                description: 'Prueba con otro nombre o categoría.'
            });
            return;
        }

        searchResultsSummary.textContent = results.length === 1
            ? '1 negocio encontrado'
            : `${results.length} negocios encontrados`;

        results.forEach(r => {
            const li = document.createElement('li');
            li.className = 'search-result-item';

            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'search-result-button';
            button.dataset.resultType = r.result_type || 'business';
            button.setAttribute('aria-label', `Seleccionar ${r.nombre_negocio}`);

            const imageSource = r.image_url || r.image || r.logo;
            let visual;

            if (imageSource) {
                visual = document.createElement('img');
                visual.className = 'search-result-image';
                visual.src = imageSource;
                visual.alt = `Logo de ${r.nombre_negocio}`;
            } else {
                visual = document.createElement('span');
                visual.className = 'search-result-image-placeholder';
                visual.setAttribute('aria-hidden', 'true');
                const storeIcon = document.createElement('i');
                storeIcon.className = 'fa-solid fa-store';
                visual.appendChild(storeIcon);
            }

            const content = document.createElement('span');
            content.className = 'search-result-content';

            const name = document.createElement('h3');
            name.textContent = r.nombre_negocio;
            content.appendChild(name);

            const locationText = r.comuna || r.ubicacion || r.direccion;
            const metadata = [r.business_type, locationText].filter(Boolean);

            if (metadata.length) {
                const meta = document.createElement('p');
                meta.className = 'search-result-meta';
                meta.textContent = metadata.join(' · ');
                content.appendChild(meta);
            }

            const promotionCount = r.active_promotions ?? r.promociones_activas ?? r.promotions;
            if (Number(promotionCount) > 0) {
                const promotions = document.createElement('span');
                promotions.className = 'search-result-promotions green-label';
                promotions.textContent = Number(promotionCount) === 1
                    ? '1 promoción activa'
                    : `${promotionCount} promociones activas`;
                content.appendChild(promotions);
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
        const entry = markersById[result.id];
        if (!entry) return;

        map.setView(entry.location.coords, 18);
        showBusinessCard(entry.location);

        searchInput.value = result.nombre_negocio;
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