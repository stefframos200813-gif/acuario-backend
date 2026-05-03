const admin = require("firebase-admin");
require("dotenv").config();

// Cargar credenciales
const serviceAccount = require("./serviceAccountKey.json");

// Inicializar Firebase Admin SDK
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://acuario-tesis-default-rtdb.firebaseio.com"
});

console.log("✅ Firebase Admin SDK inicializado correctamente");

// Referencia a Realtime Database
const db = admin.database();
const ref = db.ref("acuario/monitoreo");

// Leer datos
ref.once("value", (snapshot) => {
  const data = snapshot.val();
  console.log("📡 Datos obtenidos desde Firebase:");
  console.log(data);
}).catch((error) => {
  console.error("❌ Error al leer datos:", error);
});