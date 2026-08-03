document.addEventListener('DOMContentLoaded', () => {
    // Sidebar menu toggle
    const brailleBtn = document.querySelector('.header-toggle i');
    const sidebarMenu = document.getElementById('sidebarPanel');
    brailleBtn.style.cursor = 'pointer';
    brailleBtn.addEventListener('click', () => {
        sidebarMenu.classList.toggle('active');
        document.querySelector('.header').classList.toggle('move-right', sidebarMenu.classList.contains('active'));
    });

    // 1. Inicializar el mapa
    // Coordenadas de San Rámon, Santiago de Chile
    let  initLat = -33.5532855;
    let initLng = -70.6528958;
    const map = L.map('map').setView([initLat, initLng], 17);

    // 2. Añadir una capa de tiles (mapa base) de OpenStreetMap
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        minZoom: 4.5,
        attribution: '© OpenStreetMap'
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
    const iconImage = "https://github.com/Mut1nelo/Almaceb-RED-Web/blob/Flask/static/images/icons/in-1.png?raw=true";
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