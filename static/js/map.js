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
    // Coordenadas de San Rámon, Santiago de Chile
    let  initLat = -33.5532855;
    let initLng = -70.6528958;
    const map = L.map('map').setView([initLat, initLng], 17);

    // 2. Añadir una capa de tiles (mapa base) de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        minZoom: 4.5,
        attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);


    // 3. Crear iconos personalizados para los marcadores
    const markerIcon = (imageUrl) => L.divIcon({
        className: 'custom-marker',
        html: `<img src="${imageUrl}" style="width: 100%; height: 100%; object-fit: cover;">`,
        iconSize: [50, 50],
        iconAnchor: [25, 50],
        popupAnchor: [0, -45]
    });

    // 4. Datos dummy para los puntos de interés cerca de San Ramón
    // Cambia esto a un punto de interés real luego de hacerlo funcional
    const iconImage = "../static/imgs/icons/in-1.png";
    const locations = [
  {
    coords: [-33.553033, -70.650312],
    name: 'Burger House',
    image: iconImage,
    cardImage: '../static/imgs/img-proto.png',
    category: 'Comida rápida',
    promotions: 2,
    featured: true,
    url: '/Negocio'
  }
];

    // 5. Preparar la mini tarjeta de negocio
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

    // Calcula la distancia entre dos puntos usando sus coordenadas.
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

        if (distance < 1) {
            businessCardDistance.textContent = `A ${Math.round(distance * 1000)} m`;
        } else {
            businessCardDistance.textContent = `A ${distance.toFixed(1)} km`;
        }
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

    // 6. Añadir los marcadores al mapa
    locations.forEach(location => {
        const marker = L.marker(location.coords, { icon: markerIcon(location.image) })
            .addTo(map);

        marker.on('click', () => showBusinessCard(location));
    });

    map.on('click', hideBusinessCard);

    // Localización en tiempo real del usuario
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

});