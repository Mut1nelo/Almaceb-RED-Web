document.addEventListener('DOMContentLoaded', () => {
    // Sidebar menu toggle
    const brailleBtn = document.querySelector('.header-toggle i');
    const sidebarMenu = document.getElementById('sidebarPanel');
    if (brailleBtn) {
        brailleBtn.style.cursor = 'pointer';
        brailleBtn.addEventListener('click', () => {
            sidebarMenu.classList.toggle('active');
            document.querySelector('.header').classList.toggle('move-right', sidebarMenu.classList.contains('active'));
        });
    }

    // --- LEER COORDENADAS GUARDADAS EN MYSQL DESDE EL HTML ---
    const userMeta = document.getElementById('user-metadata');
    let initLat = -33.5532855; // Coordenadas por defecto de San Ramón
    let initLng = -70.6528958;
    let tieneUbicacionGuardada = false;

    if (userMeta) {
        const savedLat = userMeta.getAttribute('data-lat');
        const savedLng = userMeta.getAttribute('data-lng');

        if (savedLat && savedLng && savedLat !== '' && savedLng !== '') {
            initLat = parseFloat(savedLat);
            initLng = parseFloat(savedLng);
            tieneUbicacionGuardada = true;
        }
    }

    // 1. Inicializar el mapa
    const map = L.map('map').setView([initLat, initLng], 17);

    // 2. Capa base de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        minZoom: 4.5,
        attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Forzar a Leaflet a recalcular el tamaño para evitar el fondo gris
    setTimeout(() => { map.invalidateSize(); }, 200);

    // 3. Crear iconos personalizados para los marcadores
    const markerIcon = (imageUrl) => L.divIcon({
        className: 'custom-marker',
        html: `<img src="${imageUrl}" style="width: 100%; height: 100%; object-fit: cover;">`,
        iconSize: [30, 30],
        iconAnchor: [15, 15],
        popupAnchor: [0, -45]
    });

    // 4. Datos dummy para los puntos de interés cerca de San Ramón
    const iconImage = "https://github.com";
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
            .bindPopup(`<b>${location.name}</b><br>${location.description}`);
    });

    // --- FUNCIÓN PARA ENVIAR LAS COORDENADAS A FLASK VIA FETCH ---
    function enviarUbicacionAlServidor(lat, lon) {
        fetch('/guardar-ubicacion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitud: lat, longitud: lon })
        })
        .then(response => response.json())
        .then(data => console.log('Ubicación actualizada en MySQL:', data))
        .catch(error => console.error('Error al enviar a Flask:', error));
    }

    // Localización en tiempo real del usuario
    let userMarker = null;
    let ubicacionGuardadaEnEstaSesion = false;

    if (tieneUbicacionGuardada) {
        userMarker = L.marker([initLat, initLng], {
            icon: L.icon({
                iconUrl: 'https://flaticon.com',
                iconSize: [25, 25],
                iconAnchor: [12.5, 12.5],
                popupAnchor: [0, -32]
            })
        }).addTo(map).bindPopup('¡Tu ubicación guardada!').openPopup();
        ubicacionGuardadaEnEstaSesion = true;
    }

    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                
                if (!userMarker) {
                    userMarker = L.marker([lat, lng], {
                        icon: L.icon({
                            iconUrl: 'https://flaticon.com',
                            iconSize: [25, 25],
                            iconAnchor: [12.5, 12.5],
                            popupAnchor: [0, -32]
                        })
                    }).addTo(map).bindPopup('¡Tu ubicación actual!').openPopup();
                    map.setView([lat, lng], 16);
                } else {
                    userMarker.setLatLng([lat, lng]);
                }

                if (!ubicacionGuardadaEnEstaSesion) {
                    enviarUbicacionAlServidor(lat, lng);
                    ubicacionGuardadaEnEstaSesion = true;
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
