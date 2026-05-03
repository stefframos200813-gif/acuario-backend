const express = require("express");
const admin = require("firebase-admin");

const app = express();
app.use(express.json());

// 🔥 Cargar credenciales Firebase (archivo local)
const serviceAccount = require("./serviceAccountKey.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

// Ruta de prueba
app.get("/", (req, res) => {
  res.send("🚀 Backend funcionando correctamente en Render");
});

// Ejemplo usando Firebase (puedes borrar si quieres)
app.get("/test-firebase", async (req, res) => {
  try {
    const db = admin.firestore();
    const snapshot = await db.collection("test").get();

    const data = snapshot.docs.map(doc => doc.data());
    res.json(data);

  } catch (error) {
    res.status(500).send(error.toString());
  }
});

// Puerto dinámico para Render
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
});