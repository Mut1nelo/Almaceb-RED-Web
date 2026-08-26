document.addEventListener("DOMContentLoaded", () => {
    const elementSelect = document.getElementById("report-element");
    const reasonSelect = document.getElementById("report-reason");

    const reasons = {
        negocio: [
            ["informacion_incorrecta", "Información incorrecta"],
            ["negocio_cerrado", "Negocio cerrado o inexistente"],
            ["categoria_incorrecta", "Categoría incorrecta"],
            ["imagenes_inapropiadas", "Imágenes inapropiadas"],
            ["negocio_duplicado", "Negocio duplicado"],
            ["ubicacion_incorrecta", "Ubicación incorrecta"]
        ],

        promocion: [
            ["promocion_vencida", "Promoción vencida"],
            ["precio_incorrecto", "Precio incorrecto"],
            ["promocion_no_disponible", "Promoción no disponible"],
            ["informacion_enganosa", "Información engañosa"],
            ["condiciones_incorrectas", "Condiciones incorrectas"]
        ],

        usuario: [
            ["nombre_imagen_inapropiada", "Nombre o imagen inapropiada"],
            ["spam", "Spam"],
            ["suplantacion", "Suplantación"],
            ["comportamiento_inapropiado", "Comportamiento inapropiado"]
        ],

        ubicacion: [
            ["marcador_incorrecto", "Marcador en ubicación incorrecta"],
            ["negocio_faltante", "Negocio faltante"],
            ["negocio_duplicado", "Negocio duplicado"]
        ],

        plataforma: [
            ["boton_no_funciona", "Un botón no funciona"],
            ["pagina_no_carga", "Una página no carga"],
            ["error_visual", "Error visual"],
            ["problema_inicio_sesion", "Problema con inicio de sesión"],
            ["otra_falla", "Otra falla"]
        ],

        otro: [
            ["otro", "Otro problema"]
        ]
    };

    function updateReasons() {
        if (!elementSelect || !reasonSelect) {
            return;
        }

        const selectedElement = elementSelect.value;

        reasonSelect.innerHTML = "";

        if (!selectedElement || !reasons[selectedElement]) {
            const option = document.createElement("option");

            option.value = "";
            option.textContent = "Selecciona primero qué estás reportando";
            option.disabled = true;
            option.selected = true;

            reasonSelect.appendChild(option);

            return;
        }

        const placeholder = document.createElement("option");

        placeholder.value = "";
        placeholder.textContent = "Selecciona un motivo";
        placeholder.disabled = true;
        placeholder.selected = true;

        reasonSelect.appendChild(placeholder);

        reasons[selectedElement].forEach(([value, text]) => {
            const option = document.createElement("option");

            option.value = value;
            option.textContent = text;

            reasonSelect.appendChild(option);
        });
    }

    if (elementSelect) {
        elementSelect.addEventListener("change", updateReasons);

        // Hace que también funcione si Flask ya dejó
        // un tipo de elemento seleccionado al cargar la página.
        updateReasons();
    }

});
