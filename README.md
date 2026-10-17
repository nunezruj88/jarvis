# JARVIS · prototipo local de chat

Asistente en español con interfaz inspirada en JARVIS, proveedor/modelo configurables, consulta meteorológica y Home Assistant de solo lectura. Sin dependencias externas de instalación. Windows o Linux con Node.js 22 o posterior.

## Arranque

Abre una terminal en esta carpeta y ejecuta:

```sh
node server.mjs
```

Abre http://127.0.0.1:3210 en tu navegador. En Windows puedes utilizar `iniciar.cmd`. En Linux puedes ejecutar `sh iniciar.sh`. Para una mini pantalla, activa pantalla completa en el navegador. El servidor solo escucha en este equipo; Home Assistant puede estar en otro PC de la misma red. Para detenerlo, pulsa Ctrl+C en la terminal.

## Configuración desde Ajustes

1. Elige proveedor. Los perfiles OpenAI, OpenRouter y Groq rellenan sus URL; cualquier otro servicio debe ofrecer la API compatible con Chat Completions. Anthropic nativo no está implementado; sus modelos pueden usarse mediante un proveedor compatible que los ofrezca.
2. Introduce tu propia clave de API. La suscripción de una aplicación de chat no sustituye esta clave. Escribe el identificador del modelo o pulsa **Cargar modelos**. El modelo debe admitir llamadas a herramientas para consultar el tiempo y Home Assistant.
3. Pulsa **Probar IA** para verificar autenticación y respuesta. Esta prueba puede tener un pequeño coste del proveedor y no verifica todavía el uso de herramientas.
4. Introduce la dirección de Home Assistant, con su puerto real (por ejemplo `http://192.168.1.50:8123`). En tu perfil de Home Assistant crea un token de acceso de larga duración y pégalo en Ajustes, nunca en el chat.
5. Pulsa **Conectar y seleccionar entidades**. Marca únicamente las entidades que quieres consultar y guarda. JARVIS no llama a servicios de control; el token de Home Assistant puede tener permisos más amplios que los utilizados por esta aplicación. No compartas el archivo de configuración.
6. Para el tiempo, introduce localidad y coordenadas. El prototipo consulta el tiempo actual de esa ubicación, no previsiones ni otras ciudades.

El botón Guardar escribe `config.local.json` en esta carpeta, incluyendo claves en texto legible. Se excluye de Git, no se sirve al navegador y los campos de clave no se devuelven en las consultas de configuración. Protégelo con los permisos de tu usuario y exclúyelo de copias compartidas. Un campo de clave vacío conserva la anterior; la casilla de eliminación permite borrarla. Cambiar de proveedor marca la eliminación de la clave anterior: introduce la nueva antes de guardar.

Las conversaciones permanecen en memoria de la pestaña y se envían al proveedor de IA. Los estados autorizados se comparten cuando el modelo solicita la herramienta; los nombres y valores no seleccionados no se envían. La consulta de estados descarga la lista completa desde Home Assistant al servidor local para filtrarla. El historial se limita a veinte mensajes y se reinicia al guardar ajustes o pulsar Nueva conversación. No hay almacenamiento de conversaciones ni acceso a micrófono/cámara.

## Prueba manual con tus conexiones

- Pregunta algo general y comprueba que responde el modelo elegido.
- Pregunta por el estado de una entidad seleccionada; comprueba respuesta y tarjeta contra Home Assistant.
- Desconecta Home Assistant y repite: debe informar del fallo, sin presentar estados anteriores como actuales.
- Pregunta por el tiempo de tu localidad y revisa la tarjeta de observación.
- Cambia de modelo y repite las consultas para verificar que ese modelo admite herramientas.

Si el proveedor rechaza `tools`, elige otro modelo compatible. Los perfiles de proveedor son configuraciones de URL; no constituyen una certificación de todos sus modelos. No hay conexión real probada hasta que introduzcas tus credenciales. Esta primera versión entrega la respuesta completa; streaming, voz, cámara, memoria permanente y control de dispositivos quedan para fases posteriores.

## Verificación del código

```sh
node --test
```

Pruebas de filtrado de entidades, errores de herramientas, configuración y protección del servidor. Utilizan simulaciones, sin servicios reales ni gasto de API.

## Evolución a voz

La interfaz llama a `/api/chat` con texto y contexto. Una futura transcripción puede enviar el mismo formato y una síntesis de voz leer `reply`. Las herramientas son independientes del canal; se pueden reutilizar al incorporar Pipecat. Este prototipo no necesita Pipecat todavía.

Fuentes de integración: https://developers.home-assistant.io/docs/api/rest/ y https://open-meteo.com/en/docs
