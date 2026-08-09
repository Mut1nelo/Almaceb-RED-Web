document.addEventListener('DOMContentLoaded', () => {
    // Sidebar menu toggle
    const profileBtn = document.querySelector('.nav-profile');
    const sidebarMenu = document.getElementsByClassName('sidebarPanel')[0];
    profileBtn.style.cursor = 'pointer';
    profileBtn.addEventListener('click', () => {
        sidebarMenu.classList.toggle('active');
        document.querySelector('.nav-container').classList.toggle('move-left', sidebarMenu.classList.contains('active'));
    });

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
    name: 'Punto de Interés Central',
    image: iconImage,
    description: 'Punto de referencia inicial para el área.'
  }
];

    // 5. Añadir los marcadores al mapa
    locations.forEach(location => {
        L.marker(location.coords, { icon: markerIcon(location.image) })
            .addTo(map)
            .bindPopup(`
        <b>${location.name}</b><br>${location.description}
    `);
    });

    // Localización en tiempo real del usuario
    let userMarker = null;
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
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
            },
            { enableHighAccuracy: true, maximumAge: 10000, timeout: 20000 }
        );
    } else {
        console.warn('Geolocalización no soportada por este navegador.');
    }

});