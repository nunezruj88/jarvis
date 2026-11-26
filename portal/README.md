# JARVIS local con Docker

Este despliegue ejecuta el portal HUD Full HD (1920 × 1080), FastAPI, LiteLLM, Ollama y el puente Home Assistant. Convive con el prototipo Node.js del directorio raíz.

## Prueba en paralelo en el Firebat

1. Usa una copia de la rama en un directorio aparte y comprueba que el puerto 8010 está libre.
2. Copia `.env.example` a `.env`. Usa `openssl rand -hex 32` para generar un valor para `LITELLM_KEY`. Mantén `.env` privado, por ejemplo con `chmod 600 .env`.
3. Ejecuta estos comandos desde la raíz:

   ```sh
   docker compose -p jarvis-hud config --quiet
   docker compose -p jarvis-hud up -d --build
   docker compose -p jarvis-hud exec ollama ollama pull qwen2.5:3b
   curl -fsS http://127.0.0.1:8010/health
   ```

   Si cambias `OLLAMA_MODEL`, descarga el modelo correspondiente en el último comando de Ollama. La ruta `/health` comprueba que FastAPI y su almacenamiento han arrancado. Envía un mensaje para comprobar la conexión completa con Ollama.

4. Abre [el portal en el Firebat](http://127.0.0.1:8010/) y activa la pantalla completa. Para verlo desde otro equipo, reenvía el puerto mediante SSH al Firebat y abre la misma dirección local.

El despliegue de prueba usa un proyecto Compose independiente. Solo se publica el puerto del portal en la interfaz local. Para parar la prueba, ejecuta `docker compose -p jarvis-hud down`. Los volúmenes de modelos e historial se conservan.

## Home Assistant

En `.env`, configura `HA_URL` con la URL que el contenedor puede alcanzar y `HA_TOKEN` con el token de acceso. Completa las entidades con sus identificadores reales.

| Variable | Lectura |
| --- | --- |
| `HA_WEATHER` | Estado meteorológico actual |
| `HA_LIGHT` | Estado de la luz Shelly |
| `HA_SOLAR` | Sensor de energía solar acumulada |
| `HA_HEATING` | Sensor de temperatura del circuito, por ejemplo `sensor.sondas_cale_circuito_1_ida` |

Aplica los cambios con `docker compose -p jarvis-hud up -d`. Prueba los cuatro botones de Home Assistant y comprueba sus valores en tu instalación. También puedes escribir consultas en español. Una consulta domótica reconocida lee el estado en ese momento y muestra los errores de conexión o de configuración. El puente acepta únicamente lecturas GET de entidades explícitamente configuradas. Solo el puente recibe el token.

## Historial y Kimi

El portal conserva en SQLite los últimos 20 mensajes de cada conversación, identificada en el navegador. Recargar la página restaura el historial. **Nueva conversación** borra el historial de ese navegador. Los intercambios que Jarvis identifica como consultas domóticas se guardan localmente y se omiten del contexto enviado al modelo.

Ollama es el proveedor predeterminado. Para usar Kimi de Moonshot, añade tu clave como `MOONSHOT_API_KEY`, configura `LITELLM_CONFIG=litellm-kimi.yaml` y `JARVIS_MODEL=kimi`, y vuelve a ejecutar `docker compose -p jarvis-hud up -d`. Kimi recibe las preguntas generales y su contexto. El alias usa `moonshot/kimi-k2.5`, editable en `portal/litellm-kimi.yaml` si tu cuenta utiliza otro modelo.

El proyecto de prueba empieza con su propia base de datos. El historial del despliegue anterior se queda en su almacenamiento original.
