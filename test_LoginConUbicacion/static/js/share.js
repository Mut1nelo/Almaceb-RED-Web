const button = document.querySelector('#share-btn');
button.addEventListener('click', (e) => {
    e.preventDefault();
    navigator.share({
        url: 'https://mut1nelo.github.io/Almaceb-RED-Web/',
        text: 'Te invitamos a visitar nuestro sitio web Almaceb RED, donde encontrarás información sobre nuestros servicios y cómo podemos ayudarte a mejorar tu experiencia de compra. ¡No te lo pierdas!',
        title: 'Google Site'
    })
})