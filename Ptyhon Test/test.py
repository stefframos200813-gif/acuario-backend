import random
import time
import threading
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import schedule

# ============================================
# CONFIGURACIÓN
# ============================================
WIFI_SSID = "T_ELEC"
WIFI_PASSWORD = "Taller$2025"
FIREBASE_URL = "https://acuariointeligente-426c3-default-rtdb.firebaseio.com/"
FIREBASE_SECRET = "82AHYGwB9U69jkcX7F4xnKD3U0f7idzFFjtOjCpF"

# Credenciales de Firebase (necesitas descargar este archivo de la consola de Firebase)
# Ve a Configuración del proyecto > Cuentas de servicio > Generar nueva clave privada
FIREBASE_CREDENTIALS_FILE = "firebase-credentials.json"

# Umbrales
TEMP_MIN, TEMP_MAX = 24.0, 28.0
PH_MIN, PH_MAX = 6.5, 8.5
TDS_MAX, TURB_MAX = 800.0, 20.0

# Variables globales
tempC = 0.0
pH_value = 0.0
tds_ppm = 0
turbidez_ntu = 0
systemOK = True

# ============================================
# INICIALIZACIÓN FIREBASE
# ============================================
def init_firebase():
    """Inicializa la conexión con Firebase"""
    try:
        # Usar autenticación con archivo de credenciales
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_FILE)
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_URL
        })
        print("✅ Firebase inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error inicializando Firebase: {e}")
        print("\n⚠️  Necesitas descargar el archivo de credenciales de Firebase:")
        print("1. Ve a la consola de Firebase → Configuración del proyecto")
        print("2. Cuentas de servicio → Generar nueva clave privada")
        print("3. Guarda el archivo como 'firebase-credentials.json'")
        return False

# ============================================
# GENERACIÓN DE DATOS SIMULADOS
# ============================================
def generar_datos_aleatorios():
    """Genera datos simulados como el ESP32"""
    global tempC, pH_value, tds_ppm, turbidez_ntu, systemOK
    
    # Generar valores aleatorios
    tempC = random.randint(200, 320) / 10.0        # 20.0 - 32.0 °C
    pH_value = random.randint(55, 90) / 10.0       # 5.5 - 9.0 pH
    tds_ppm = random.randint(200, 1000)            # 200 - 1000 ppm
    turbidez_ntu = random.randint(0, 50)            # 0 - 50 NTU
    
    # Evaluar estado del sistema
    systemOK = (tempC >= TEMP_MIN and tempC <= TEMP_MAX and 
                pH_value >= PH_MIN and pH_value <= PH_MAX and 
                tds_ppm <= TDS_MAX and turbidez_ntu <= TURB_MAX)
    
    return tempC, pH_value, tds_ppm, turbidez_ntu, systemOK

# ============================================
# ENVÍO A FIREBASE
# ============================================
def enviar_datos_firebase():
    """Envía los datos generados a Firebase"""
    global tempC, pH_value, tds_ppm, turbidez_ntu, systemOK
    
    # Generar nuevos datos
    generar_datos_aleatorios()
    
    # Crear objeto de datos
    data = {
        'temperatura': tempC,
        'ph': pH_value,
        'tds': tds_ppm,
        'turbidez': turbidez_ntu,
        'estado': "OK" if systemOK else "ALERTA",
        'timestamp': int(time.time()),
        'fecha_hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        # Enviar a Firebase
        ref = db.reference('/acuario/monitoreo')
        ref.set(data)
        
        # Mostrar resultados
        print(f"\n[{data['fecha_hora']}] Datos enviados a Firebase:")
        print(f"  🌡️  Temperatura: {tempC:.1f} °C")
        print(f"  🧪 pH: {pH_value:.1f}")
        print(f"  💧 TDS: {tds_ppm} ppm")
        print(f"  🌫️  Turbidez: {turbidez_ntu} NTU")
        print(f"  {'✅ SISTEMA OK' if systemOK else '⚠️ ALERTA'}")
        
        # Indicador visual de estado (como el LED en ESP32)
        if systemOK:
            print("  💚 Sistema funcionando correctamente")
        else:
            print("  ❤️ ALERTA: Parámetros fuera de rango")
            
    except Exception as e:
        print(f"❌ Error enviando a Firebase: {e}")

# ============================================
# SIMULACIÓN DE PANTALLA OLED
# ============================================
def mostrar_pantalla_simulada():
    """Simula la pantalla OLED en la terminal"""
    global tempC, pH_value, tds_ppm, turbidez_ntu, systemOK
    
    # Limpiar pantalla (opcional, depende del sistema)
    # print("\033c", end="")  # Para Linux/Mac
    # os.system('cls')  # Para Windows
    
    print("\n" + "="*40)
    print("     NEXUS - IoT Cloud (Python)")
    print("="*40)
    print(f"🌡️  Temperatura: {tempC:.1f} °C")
    print(f"🧪 pH: {pH_value:.1f}")
    print(f"💧 TDS: {tds_ppm} ppm")
    print(f"🌫️  Turbidez: {turbidez_ntu} NTU")
    print("-"*40)
    print(f"SISTEMA: {'✅ OK' if systemOK else '⚠️ ALERTA'}")
    if not systemOK:
        print("VALORES FUERA DE RANGO:")
        if tempC < TEMP_MIN or tempC > TEMP_MAX:
            print(f"  - Temperatura: {tempC:.1f}°C (rango {TEMP_MIN}-{TEMP_MAX}°C)")
        if pH_value < PH_MIN or pH_value > PH_MAX:
            print(f"  - pH: {pH_value:.1f} (rango {PH_MIN}-{PH_MAX})")
        if tds_ppm > TDS_MAX:
            print(f"  - TDS: {tds_ppm} ppm (máx {TDS_MAX} ppm)")
        if turbidez_ntu > TURB_MAX:
            print(f"  - Turbidez: {turbidez_ntu} NTU (máx {TURB_MAX} NTU)")
    print("="*40 + "\n")

# ============================================
# VERIFICACIÓN DE CONEXIÓN (simulando WiFi)
# ============================================
def verificar_conexion():
    """Simula la conexión WiFi del ESP32"""
    print(f"📡 Conectando a WiFi '{WIFI_SSID}'...", end="")
    time.sleep(2)  # Simular tiempo de conexión
    print(" CONECTADO ✅")
    print(f"📊 Conectando a Firebase: {FIREBASE_URL}")
    return True

# ============================================
# FUNCIÓN PRINCIPAL
# ============================================
def main():
    print("🚀 Iniciando Simulador ESP32 - Acuario Inteligente")
    print("="*50)
    
    # Verificar conexión (simulada)
    if not verificar_conexion():
        print("❌ Error de conexión. Saliendo...")
        return
    
    # Inicializar Firebase
    if not init_firebase():
        print("⚠️  Continuando en modo LOCAL (solo pantalla)")
        modo_firebase = False
    else:
        modo_firebase = True
        print("✅ Modo Firebase activado")
    
    print("\n📊 Generando datos cada 5 segundos...")
    print("Presiona Ctrl+C para detener\n")
    
    try:
        # Generar primeros datos
        generar_datos_aleatorios()
        mostrar_pantalla_simulada()
        
        if modo_firebase:
            enviar_datos_firebase()
        
        # Bucle principal
        last_reading = time.time()
        
        while True:
            current_time = time.time()
            
            if current_time - last_reading >= 5:  # Cada 5 segundos
                # Generar nuevos datos
                generar_datos_aleatorios()
                
                # Mostrar en pantalla simulada
                mostrar_pantalla_simulada()
                
                # Enviar a Firebase si está activado
                if modo_firebase:
                    enviar_datos_firebase()
                
                last_reading = current_time
            
            time.sleep(0.1)  # Pequeña pausa para no saturar la CPU
            
    except KeyboardInterrupt:
        print("\n\n👋 Programa detenido por el usuario")

# ============================================
# PUNTO DE ENTRADA
# ============================================
if __name__ == "__main__":
    main()