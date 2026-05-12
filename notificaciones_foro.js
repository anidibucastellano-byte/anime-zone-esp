// ==UserScript==
// @name         AnimeZoneESP - Notificaciones Visuales
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Muestra notificaciones visuales cuando te citan o mencionan
// @author       You
// @match        https://animezoneesp.foroactivo.com/*
// @grant        GM_notification
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    const CONFIG = {
        checkInterval: 60000,
        badgeColor: '#ff4444'
    };

    const NOTIFICATIONS_URL = '/t19093-notificaciones-de-citas-o-menciones';
    let lastCount = 0;

    // Crear badge
    function createBadge() {
        const badge = document.createElement('div');
        badge.id = 'notification-badge';
        badge.innerHTML = '📢 <span id="notif-count">0</span>';
        badge.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: ${CONFIG.badgeColor};
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-weight: bold;
            cursor: pointer;
            z-index: 9999;
            display: none;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            font-family: Arial, sans-serif;
        `;
        badge.addEventListener('click', () => window.open(NOTIFICATIONS_URL, '_blank'));
        document.body.appendChild(badge);
    }

    // Mostrar notificación
    function showNotification(title, body) {
        if (Notification.permission === 'granted') {
            new Notification(title, { body });
        }
    }

    // Verificar notificaciones
    async function checkNotifications() {
        try {
            const response = await fetch(NOTIFICATIONS_URL, { credentials: 'include' });
            const text = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(text, 'text/html');
            const mentions = doc.querySelectorAll('.post');
            const count = mentions.length;

            if (count > lastCount && lastCount > 0) {
                const newCount = count - lastCount;
                updateBadge(newCount);
                showNotification('AnimeZoneESP', `Tienes ${newCount} nueva(s) mención(es)`);
            }
            lastCount = count;
        } catch (e) {
            console.log('Error:', e);
        }
    }

    // Actualizar badge
    function updateBadge(count) {
        const badge = document.getElementById('notification-badge');
        const countSpan = document.getElementById('notif-count');
        if (badge && countSpan) {
            countSpan.textContent = count;
            badge.style.display = 'block';
        }
    }

    // Inicializar
    function init() {
        // Solicitar permiso
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
        createBadge();
        checkNotifications();
        setInterval(checkNotifications, CONFIG.checkInterval);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

/*
INSTRUCCIONES DE INSTALACIÓN:
1. Instala la extensión Tampermonkey en tu navegador (Chrome/Firefox)
2. Crea un nuevo script y pega este código
3. Guarda el script
4. Actívalo para que funcione en animezoneesp.foroactivo.com

FUNCIONALIDAD:
- Muestra un badge rojo con el número de notificaciones
- Verifica cada 60 segundos si hay nuevas menciones/citas
- Muestra notificaciones del navegador cuando hay nuevas
- Al hacer clic en el badge, te lleva a la página de notificaciones
*/
