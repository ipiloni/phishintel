// Configuración global de la aplicación
// Obtiene la URL del backend desde el endpoint de configuración
let API_BASE_URL = 'http://localhost:8080'; // Valor por defecto

// Función para inicializar la URL del backend
// Se ejecuta inmediatamente para que la URL esté disponible antes de que otros scripts la usen
(function initApiUrl() {
    try {
        // Usar la URL actual de la página como base para evitar problemas de CORS
        const currentProtocol = window.location.protocol;
        const currentHost = window.location.host;
        const baseUrl = `${currentProtocol}//${currentHost}`;
        
        // Usar XMLHttpRequest síncrono para asegurar que la URL esté disponible inmediatamente
        // Nota: Aunque está deprecado, es necesario aquí para evitar problemas de timing
        const xhr = new XMLHttpRequest();
        xhr.open('GET', `${baseUrl}/api/config/url`, false); // false = síncrono
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(null);
        
        if (xhr.status === 200) {
            try {
                const data = JSON.parse(xhr.responseText);
                if (data.url) {
                    API_BASE_URL = data.url;
                    console.log('URL del backend configurada desde properties.env:', API_BASE_URL);
                }
            } catch (parseError) {
                console.warn('Error parseando respuesta del servidor:', parseError);
            }
        } else {
            console.warn('No se pudo obtener la URL del backend (status:', xhr.status + '), usando valor por defecto:', API_BASE_URL);
        }
    } catch (error) {
        console.warn('Error obteniendo URL del backend:', error);
        console.warn('Usando valor por defecto:', API_BASE_URL);
    }
})();

