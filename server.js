const express = require("express");
const admin = require("firebase-admin");

// 🔐 Firebase
const serviceAccount = require("./serviceAccountKey.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://acuario-tesis-default-rtdb.firebaseio.com"
});

const db = admin.database();

const app = express();
app.use(express.json());

// 🔴 POST
app.post("/datos", async (req, res) => {
  try {
    const data = req.body;

    await db.ref("sensores").set({
      temperatura: data.temperatura,
      ph: data.ph,
      tds: data.tds,
      turbidez: data.turbidez,
      timestamp: Date.now()
    });

    console.log("📥 Datos recibidos:", data);

    res.status(200).json({ estado: "ok" });

  } catch (error) {
    console.error("❌ Error en POST:", error);
    res.status(500).json({ error: "Error al guardar datos" });
  }
});

// 🟢 GET
app.get("/datos", async (req, res) => {
  try {
    const snapshot = await db.ref("sensores").once("value");
    res.json(snapshot.val());
  } catch (error) {
    console.error("❌ Error en GET:", error);
    res.status(500).json({ error: "Error al obtener datos" });
  }
});

// 🔵 ROOT
app.get("/", (req, res) => {
  res.send("Servidor activo 🚀");
});

// 🔥 CLAVE
app.listen(3000, "0.0.0.0", () => {
  console.log("🔥 SERVIDOR ENCENDIDO EN http://0.0.0.0:3000");
});