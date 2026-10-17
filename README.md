# JARVIS · prototipo local de chat

Asistente en español con interfaz inspirada en JARVIS, proveedor/modelo configurables, consulta meteorológica y Home Assistant de solo lectura. Windows o Linux con Node.js 22 o posterior. El proyecto utiliza los módulos incluidos en Node.js; no necesita descargar paquetes npm para arrancar.

## Prerrequisitos

### Sistema operativo y equipo

- **Windows:** Windows 11 de 64 bits con escritorio.
- **Linux:** Ubuntu Desktop 24.04 LTS de 64 bits como entorno recomendado para el mini PC. Otras distribuciones pueden servir si admiten Node.js y un navegador moderno, pero esta guía utiliza Ubuntu.
- **Hardware:** mini PC Intel N150 o Intel i5 con 16 GB de RAM y SSD, como equipo de referencia para este proyecto. La IA se ejecuta en la nube; no se necesita GPU dedicada ni descargar modelos locales. Estas referencias no son mínimos de hardware medidos.
- **Interfaz:** pantalla y teclado, o teclado en pantalla si el sistema ya lo tiene configurado. Micrófono, altavoces y cámara no son necesarios para esta versión de chat.
- **Permisos:** usuario con escritura en la carpeta del proyecto. Permisos de administrador únicamente para instalar software cuando el instalador los solicite; ejecuta JARVIS con tu usuario habitual.

La instalación del sistema operativo queda fuera de esta guía. Las instrucciones parten de un sistema instalado con acceso al escritorio e Internet. No se ha validado una instalación completa en cada combinación de sistema operativo y hardware.

### Software y servicios

| Requisito | Para qué sirve |
| --- | --- |
| **Node.js 22 o posterior** | Ejecuta el servidor y las pruebas. Se recomienda **Node.js 24 LTS** para una instalación nueva. |
| **Navegador actualizado** | Chrome, Edge o Firefox para abrir la interfaz local. |
| **Proveedor de IA y clave de API** | Cuenta con acceso a una API compatible con Chat Completions y cuota o saldo disponible según el proveedor. El modelo debe admitir llamadas a herramientas para consultar el tiempo y Home Assistant. |
| **Home Assistant operativo** | Necesario solo para consultar dispositivos. Puede estar en otro PC; prepara su URL y un token de acceso de larga duración. |
| **Git, opcional** | Permite clonar y actualizar el repositorio. También puedes descargar el ZIP sin instalar Git. |

No son necesarios Python, Docker, Pipecat, Ollama, una base de datos externa ni herramientas de compilación en esta versión. npm viene con Node.js, pero **no hace falta ejecutar `npm install` ni generar una compilación de la interfaz**.

### Red y datos que debes preparar

- Conexión a Internet desde el equipo de JARVIS para la API de IA y Open-Meteo, normalmente por HTTPS en el puerto 443.
- Acceso desde ese equipo a la URL de Home Assistant y su puerto real, por ejemplo `http://192.168.1.50:8123`. Si Home Assistant está en otra red, necesitas que ya exista una ruta o VPN entre ambos equipos.
- URL base de la API de IA, clave y nombre exacto del modelo. Una suscripción a una aplicación de chat no sustituye una clave de API.
- Localidad y coordenadas para la consulta meteorológica. Open-Meteo no requiere clave en la integración actual.
- Puerto local **3210** libre. JARVIS escucha únicamente en `127.0.0.1`: el navegador debe abrirse en el mismo equipo que ejecuta el servidor. No necesitas abrir ese puerto al exterior ni configurar CORS en Home Assistant; las consultas se hacen desde el servidor local.

## Instalación en Windows

### 1. Instalar Node.js

1. Abre la [página oficial de Node.js](https://nodejs.org/en/download).
2. Selecciona **Node.js 24 LTS**, Windows y arquitectura **x64**, y descarga el instalador `.msi`.
3. Ejecuta el instalador manteniendo la opción de añadir Node.js a `PATH`. Las herramientas adicionales de compilación no son necesarias para este proyecto.
4. Abre una **nueva** ventana de PowerShell y comprueba la instalación:

```powershell
node --version
```

Debe mostrar `v24.x.x`, o una versión admitida igual o superior a 22. Si no reconoce `node`, cierra y vuelve a abrir la terminal después de instalarlo.

### 2. Descargar el proyecto

1. Abre [nunezruj88/jarvis](https://github.com/nunezruj88/jarvis).
2. Pulsa **Code → Download ZIP** y extrae todo el contenido en una carpeta de tu usuario, por ejemplo `Documentos\jarvis`. No lo ejecutes desde dentro del ZIP.
3. Comprueba que la carpeta extraída contiene `server.mjs`, `package.json`, `public` y `test`.

Si prefieres Git, instala [Git for Windows](https://git-scm.com/downloads/win), abre una nueva terminal en la carpeta donde quieras guardar el proyecto y ejecuta:

```powershell
git clone https://github.com/nunezruj88/jarvis.git
cd jarvis
```

### 3. Comprobar y arrancar

Abre PowerShell dentro de la carpeta que contiene `server.mjs` y ejecuta:

```powershell
node --test
node server.mjs
```

Las pruebas no usan tus credenciales ni consumen API de IA. Si pasan, el segundo comando mostrará `JARVIS disponible en http://127.0.0.1:3210`. Deja la terminal abierta y visita esa dirección en el navegador. Para los siguientes arranques también puedes hacer doble clic en `iniciar.cmd`.

## Instalación en Ubuntu Desktop

### 1. Instalar herramientas y Node.js

Abre Terminal e instala las herramientas para descargar el proyecto y el gestor de versiones de Node.js:

```sh
sudo apt update
sudo apt install -y curl ca-certificates git
```

Instala **nvm** siguiendo su [guía oficial](https://github.com/nvm-sh/nvm#installing-and-updating). El siguiente comando descarga y ejecuta el instalador publicado por sus mantenedores; puedes revisar el script en ese repositorio antes de ejecutarlo:

```sh
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
```

Cierra y vuelve a abrir Terminal para cargar nvm y ejecuta:

```sh
command -v nvm
nvm install 24
nvm alias default 24
nvm use 24
node --version
```

El primer comando debe mostrar `nvm` y el último una versión `v24.x.x`. Si nvm no aparece, revisa la sección de solución de problemas de su guía antes de continuar. No ejecutes `nvm` ni el servidor JARVIS con `sudo`.

### 2. Descargar, comprobar y arrancar

Desde una carpeta de tu usuario donde quieras guardar el proyecto:

```sh
git clone https://github.com/nunezruj88/jarvis.git
cd jarvis
node --test
node server.mjs
```

También puedes descargar y extraer **Code → Download ZIP** desde GitHub; en ese caso, abre Terminal dentro de la carpeta extraída y ejecuta los dos comandos de Node.js. Git solo es necesario para la opción de clonado.

Abre Firefox u otro navegador actualizado y visita `http://127.0.0.1:3210`. En los siguientes arranques puedes usar `sh iniciar.sh` desde la carpeta del proyecto, en una terminal con Node.js disponible. No se requiere dar permisos de ejecución al script para invocarlo de esta manera.

## Primer uso y comprobaciones

1. Abre **Ajustes** e introduce proveedor, URL base, clave y modelo de IA.
2. Pulsa **Probar conexión y respuesta**. Verás la respuesta real y el tiempo empleado, o un error. Esta petición puede consumir una pequeña cantidad de tu cuota. Puedes probar los datos antes de guardarlos.
3. Si vas a consultar dispositivos, introduce URL y token de Home Assistant, pulsa **Conectar y seleccionar entidades** y marca las entidades permitidas.
4. Para el tiempo, introduce localidad, latitud y longitud, y pulsa **Guardar configuración**.
5. Escribe una pregunta general; después pregunta por una entidad seleccionada y por el tiempo. La prueba de conexión de IA no comprueba que ese modelo admita herramientas.

La terminal debe permanecer abierta mientras utilizas JARVIS. Para detenerlo, pulsa **Ctrl+C** en ella. Esta guía no configura el arranque automático; al reiniciar el equipo hay que iniciar el servidor de nuevo.

### Problemas frecuentes

| Síntoma | Qué revisar |
| --- | --- |
| `node` no se reconoce o no se encuentra | Instala una versión admitida, abre otra terminal y repite `node --version`. En Ubuntu comprueba que nvm esté cargado. |
| No encuentra `server.mjs` | La terminal debe estar en la carpeta del proyecto, no en su carpeta superior. |
| `EADDRINUSE` al arrancar | El puerto 3210 ya está ocupado, posiblemente por otra instancia de JARVIS. Detén esa instancia antes de iniciar otra. |
| El navegador no conecta | Comprueba que el servidor siga ejecutándose y abre `http://127.0.0.1:3210` en ese mismo PC. No abras `index.html` directamente. |
| La prueba de IA devuelve HTTP 401/403 | Revisa la clave, su proveedor y sus permisos. |
| HTTP 404 o respuesta incompatible | Revisa la URL base y el modelo. El servidor añade `/chat/completions`; no incluyas esa terminación en la URL base. |
| HTTP 429 | Revisa cuota, saldo o límites del proveedor. |
| La IA conversa pero falla al consultar dispositivos o tiempo | Selecciona un modelo con soporte de herramientas y revisa los ajustes de cada integración. |
| Home Assistant no conecta | Abre su URL desde el PC de JARVIS, comprueba puerto, conectividad y token. Usa HTTPS con certificado válido si tu instalación lo requiere. |

Las claves se guardan en `config.local.json` dentro del proyecto: no lo subas al repositorio ni lo incluyas en un ZIP para compartir. Los detalles de almacenamiento y privacidad figuran más abajo.

## Arranque

Abre una terminal en esta carpeta y ejecuta:

```sh
node server.mjs
```

Abre http://127.0.0.1:3210 en tu navegador. En Windows puedes utilizar `iniciar.cmd`. En Linux puedes ejecutar `sh iniciar.sh`. Para una mini pantalla, activa pantalla completa en el navegador. El servidor solo escucha en este equipo; Home Assistant puede estar en otro PC de la misma red. Para detenerlo, pulsa Ctrl+C en la terminal.

## Configuración desde Ajustes

1. Elige proveedor. Los perfiles OpenAI, OpenRouter y Groq rellenan sus URL; cualquier otro servicio debe ofrecer la API compatible con Chat Completions. Anthropic nativo no está implementado; sus modelos pueden usarse mediante un proveedor compatible que los ofrezca.
2. Introduce tu propia clave de API. La suscripción de una aplicación de chat no sustituye esta clave. Escribe el identificador del modelo o pulsa **Cargar modelos**. El modelo debe admitir llamadas a herramientas para consultar el tiempo y Home Assistant.
3. Pulsa **Probar conexión y respuesta** para verificar autenticación y respuesta. Esta prueba puede tener un pequeño coste del proveedor y no verifica todavía el uso de herramientas.
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
