# 🌊 Firebase Sync Backend

Backend para sincronizar datos en tiempo real desde Firebase Realtime Database (RTDB) a Firestore, con sistema de **throttling** para evitar sobrecarga de escrituras. Ideal para dashboards de monitoreo de sensores IoT.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación Rápida](#-instalación-rápida)
- [Configuración Detallada](#-configuración-detallada)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Despliegue en Render](#-despliegue-en-render)
- [Monitoreo y Logs](#-monitoreo-y-logs)
- [Solución de Problemas](#-solución-de-problemas)
- [Seguridad](#-seguridad)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

## ✨ Características

- **🔄 Sincronización en tiempo real** - Escucha cambios en RTDB y los replica en Firestore
- **⏱️ Throttling inteligente** - Máximo 1 escritura cada 4 segundos (configurable)
- **📊 Cola de escrituras** - No pierde datos, encola lecturas durante el throttling
- **✅ Validación de datos** - Verifica tipos, rangos y estructura de los sensores
- **🧹 Limpieza automática** - Elimina documentos antiguos (>30 días configurable)
- **📈 Endpoints de monitoreo** - Health check y estadísticas en tiempo real
- **🔒 Seguridad** - Helmet, CORS configurable, validación de entrada
- **🚀 Listo para producción** - Manejo de errores, cierre graceful, logs detallados

## 🏗️ Arquitectura

```
┌─────────┐     ┌──────────────────┐     ┌────────────┐
│ ESP32   │────▶│ Firebase RTDB    │────▶│ Este       │
│ Sensor  │     │ /acuario/monitoreo│     │ Backend    │
└─────────┘     └──────────────────┘     └─────┬──────┘
                                                │
                                                ▼
                                      ┌─────────────────┐
                                      │ Firestore       │
                                      │ historial_acuario│
                                      └─────────────────┘
                                                │
                                                ▼
                                      ┌─────────────────┐
                                      │ Dashboard React │
                                      └─────────────────┘
```

**Flujo de datos:**
1. ESP32 escribe datos en RTDB (`/acuario/monitoreo`)
2. Este backend detecta el cambio
3. Aplica throttling (espera 4s entre escrituras)
4. Guarda en Firestore (`historial_acuario`)
5. Dashboard lee historial desde Firestore

## 📦 Requisitos Previos

- Node.js 18+ 
- Cuenta en [Firebase](https://console.firebase.google.com/)
- Proyecto de Firebase con RTDB y Firestore habilitados
- (Opcional) Cuenta en [Render](https://render.com/) para desplegar

## 🚀 Instalación Rápida

### 1. Clonar o crear el proyecto

```bash
mkdir firebase-sync-backend
cd firebase-sync-backend
npm init -y
```

### 2. Instalar dependencias

```bash
npm install firebase-admin express dotenv cors helmet
npm install --save-dev nodemon
```

### 3. Estructura de archivos

Crea esta estructura en tu proyecto:

```
firebase-sync-backend/
├── .env
├── .gitignore
├── index.js
├── package.json
└── serviceAccountKey.json (⬅️ descargar de Firebase)
```

### 4. Configurar Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a **Configuración del proyecto** → **Cuentas de servicio**
4. Haz clic en **Generar nueva clave privada**
5. Guarda el archivo como `serviceAccountKey.json` en la raíz del proyecto

### 5. Configurar variables de entorno

Crea un archivo `.env`:

```env
# Configuración del servidor
PORT=3000
NODE_ENV=development

# Firebase - REEMPLAZA CON TU URL
FIREBASE_DATABASE_URL=https://tu-proyecto.firebaseio.com

# Throttling: tiempo mínimo entre escrituras (ms)
MIN_WRITE_INTERVAL=4000

# Limpieza de datos antiguos
CLEANUP_DAYS=30
ENABLE_CLEANUP=true
```

### 6. Iniciar el servidor

```bash
# Modo desarrollo (con nodemon)
npm run dev

# Modo producción
npm start
```

## 🔧 Configuración Detallada

### Variables de Entorno

| Variable | Descripción | Valor por defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `PORT` | Puerto del servidor | `3000` | No |
| `NODE_ENV` | Entorno (development/production) | `development` | No |
| `FIREBASE_DATABASE_URL` | URL de tu RTDB | - | **Sí** |
| `MIN_WRITE_INTERVAL` | Ms entre escrituras | `4000` | No |
| `CLEANUP_DAYS` | Días a mantener historial | `30` | No |
| `ENABLE_CLEANUP` | Activar limpieza automática | `true` | No |
| `MAX_BATCH_SIZE` | Máx documentos por batch | `500` | No |

### Estructura de Datos Esperada

El backend espera datos del ESP32 con este formato en RTDB:

```json
{
  "temperatura": 25.5,
  "ph": 7.2,
  "tds": 120,
  "turbidez": 2.5,
  "systemOK": true
}
```

**Validaciones:**
- `temperatura`: número entre -10 y 60 °C
- `ph`: número entre 0 y 14
- `tds`: número entre 0 y 5000 ppm
- `turbidez`: número entre 0 y 1000 NTU
- `systemOK`: booleano

### Datos en Firestore

Cada documento guardado tendrá esta estructura:

```json
{
  "temperatura": 25.5,
  "ph": 7.2,
  "tds": 120,
  "turbidez": 2.5,
  "systemOK": true,
  "timestamp": "2024-01-15T14:35:22.123Z",  // Momento del sensor
  "receivedAt": "2024-01-15T14:35:22.456Z", // Momento de recepción
  "raw_data": { ... } // Datos originales por si acaso
}
```

## 📡 Uso

### Con ESP32 (Arduino)

Si puedes modificar el ESP32, añade esta escritura adicional:

```cpp
// Con Firebase ESP32 Client
Firebase.pushJSON(fbdo, "/acuario/monitoreo", {
  temperatura: temperatura,
  ph: ph,
  tds: tds,
  turbidez: turbidez,
  systemOK: true
});
```

El backend detectará automáticamente los cambios.

### Con Dashboard React

En tu dashboard, lee los datos históricos de Firestore:

```javascript
import { collection, query, orderBy, limit, getDocs } from 'firebase/firestore';

const loadHistory = async () => {
  const q = query(
    collection(db, 'historial_acuario'), 
    orderBy('timestamp', 'desc'), 
    limit(100)
  );
  
  const snapshot = await getDocs(q);
  const data = snapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data(),
    timestamp: doc.data().timestamp?.toDate()
  }));
  
  setHistoryData(data.reverse());
};
```

## 🌐 API Endpoints

### `GET /`
Información básica del servicio.

**Respuesta:**
```json
{
  "name": "Firebase Sync Backend",
  "version": "2.0.0",
  "status": "operational",
  "throttling": "4s",
  "timestamp": "2024-01-15T14:35:22.123Z"
}
```

### `GET /health`
Health check detallado con estadísticas.

**Respuesta:**
```json
{
  "status": "healthy",
  "environment": "production",
  "uptime": "2h 15m",
  "throttling": {
    "minInterval": "4s",
    "enabled": true
  },
  "stats": {
    "totalWrites": 1250,
    "totalReads": 1250,
    "throttledWrites": 45,
    "errors": 2,
    "queueSize": 0,
    "hasPendingData": false,
    "isWriting": false,
    "lastWrite": "2024-01-15T14:35:22.123Z"
  },
  "timestamp": "2024-01-15T14:35:22.123Z"
}
```

### `GET /stats`
Estadísticas más detalladas del sistema.

### `POST /force-write` (solo pruebas)
Fuerza una escritura manual (útil para pruebas).

**Body:**
```json
{
  "temperatura": 26.5,
  "ph": 7.4,
  "tds": 130,
  "turbidez": 2.8,
  "systemOK": true
}
```

## ☁️ Despliegue en Render

### Opción 1: Desde GitHub (recomendada)

1. **Sube el código a GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tu-usuario/firebase-sync-backend.git
git push -u origin main
```

2. **En [Render.com](https://render.com):**
   - Haz clic en **New +** → **Web Service**
   - Conecta tu repositorio de GitHub
   - Configura:
     - **Name:** `firebase-sync-backend`
     - **Environment:** `Node`
     - **Build Command:** `npm install`
     - **Start Command:** `npm start`
     - **Plan:** Free

3. **Variables de entorno:**
   - Agrega `FIREBASE_DATABASE_URL`: `https://tu-proyecto.firebaseio.com`
   - (Opcional) Otras variables como `MIN_WRITE_INTERVAL`

4. **Archivos secretos:**
   - En la sección **Secret Files**, agrega un nuevo archivo
   - **Filename:** `serviceAccountKey.json`
   - **Content:** Pega TODO el contenido de tu archivo JSON

5. **Haz clic en "Create Web Service"**

### Opción 2: Con Docker

Crea un `Dockerfile`:

```dockerfile
FROM node:18-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

ENV PORT=3000
EXPOSE 3000

CMD ["npm", "start"]
```

## 📊 Monitoreo y Logs

### Logs esperados

```
==================================================
🚀 SERVIDOR BACKEND INICIADO
==================================================
📡 Puerto: 3000
🌍 Entorno: production
⏱️  Throttling: 4 segundos
📊 Health check: http://localhost:3000/health
==================================================

🔄 Iniciando sincronización RTDB → Firestore...
   ⏱️  Intervalo mínimo entre escrituras: 4 segundos
   🧹 Limpieza automática: Sí (30 días)
   📊 Colección Firestore: historial_acuario

👂 Escuchando cambios en /acuario/monitoreo
📡 Datos recibidos - Temp: 25.5°C, pH: 7.2
💾 Escribiendo en Firestore después del throttle...
✅ Datos guardados en Firestore: abc123
   📊 Temperatura: 25.5°C, pH: 7.2
   ⏱️  Próxima escritura disponible en 4s
```

### Verificar funcionamiento

```bash
# Health check
curl https://tu-backend.onrender.com/health

# Ver logs en Render
# Dashboard → tu servicio → Logs
```

## 🔍 Solución de Problemas

### Error: "Cannot find module 'firebase-admin'"

```bash
npm install firebase-admin --save
```

### Error: "FIREBASE_DATABASE_URL no configurada"

Verifica tu archivo `.env` o las variables de entorno en Render.

### Error: "serviceAccountKey.json not found"

Asegúrate de:
1. Haber descargado el archivo desde Firebase Console
2. Colocarlo en la raíz del proyecto
3. En Render, subirlo como **Secret File**

### No se guardan datos en Firestore

1. Revisa que el ESP32 esté escribiendo en RTDB
2. Verifica los logs del backend
3. Comprueba las reglas de seguridad de Firebase

### Muchas escrituras, quiero aumentar el throttling

Cambia `MIN_WRITE_INTERVAL` en `.env`:
```env
MIN_WRITE_INTERVAL=10000  # 10 segundos
```

## 🔐 Seguridad

### Reglas de Firebase RTDB

```json
{
  "rules": {
    "acuario": {
      "monitoreo": {
        ".read": "auth != null",
        ".write": "auth != null"
      }
    }
  }
}
```

### Reglas de Firestore

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /historial_acuario/{document} {
      allow read: if request.auth != null;
      allow write: if false; // Solo el backend escribe
    }
  }
}
```

### Recomendaciones adicionales

- Usa HTTPS siempre
- Mantén actualizadas las dependencias
- No subas `serviceAccountKey.json` a GitHub
- Usa variables de entorno para datos sensibles

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

---

## 🆘 Soporte

Si tienes problemas:

1. Revisa los [logs](#-monitoreo-y-logs)
2. Consulta la [solución de problemas](#-solución-de-problemas)
3. Abre un issue en GitHub

---

Hecho con ❤️ para la comunidad de acuarios inteligentes