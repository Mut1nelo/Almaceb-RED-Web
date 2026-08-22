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

    // 7. Lógica de búsqueda (AHORA DENTRO del mismo scope)
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await runSearch(searchInput.value);
    });

    async function runSearch(query) {
        if (!query || query.trim().length < 2) {
            searchResults.innerHTML = '<li>Escribe al menos 2 caracteres</li>';
            return;
        }

        try {
            const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            renderResults(data);
        } catch (err) {
            console.error('Error en búsqueda:', err);
            searchResults.innerHTML = '<li>Error al buscar</li>';
        }
    }

    function renderResults(results) {
        searchResults.innerHTML = '';

        if (results.length === 0) {
            searchResults.innerHTML = '<li>Sin resultados</li>';
            return;
        }

        results.forEach(r => {
            const li = document.createElement('li');
            li.textContent = `${r.nombre_negocio} — ${r.business_type}`;
            li.addEventListener('click', () => selectResult(r));
            searchResults.appendChild(li);
        });
    }

    function selectResult(result) {
        const entry = markersById[result.id];
        if (!entry) return;

        map.setView(entry.location.coords, 18);
        entry.marker.openPopup?.();
        showBusinessCard(entry.location);

        searchResults.innerHTML = '';
        searchInput.value = result.nombre_negocio;
    }

}); // Movemos todo dentro del DOM content