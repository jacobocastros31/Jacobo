import os
import time
import json
import glob
import paho.mqtt.client as paho
import streamlit as st
from PIL import Image
from gtts import gTTS
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# ==========================
# CONFIGURACIÓN DE MQTT
# ==========================
def on_publish(client, userdata, result):
    print("✅ Mensaje publicado correctamente.")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(f"📩 Mensaje recibido: {message_received}")

broker = "broker.mqttdashboard.com"
port = 1883
client = paho.Client("cliente_jacobo")
client.on_message = on_message

# ==========================
# CONFIGURACIÓN DE STREAMLIT
# ==========================
st.set_page_config(
    page_title="Control por Voz | Interfaces Multimodales",
    page_icon="🎙️",
    layout="centered"
)

# --- ENCABEZADO ---
st.title("🎙️ Control por Voz Inteligente")
st.caption("Desarrollado por Jacobo Castro | Interfaces Multimodales")

# --- IMAGEN ---
try:
    image = Image.open("voice_ctrl.jpg")
    st.image(image, width=250, caption="Reconocimiento de voz con MQTT")
except Exception:
    st.warning("⚠️ No se pudo cargar la imagen 'voice_ctrl.jpg'.")

# --- INTRODUCCIÓN ---
st.markdown("""
Esta aplicación te permite **controlar dispositivos o enviar comandos por voz**  
utilizando **MQTT (Message Queuing Telemetry Transport)**.  
Presiona el botón, habla, y el texto reconocido será publicado en el canal.
""")

st.divider()

# ==========================
# CAPTURA DE VOZ
# ==========================
st.subheader("🎧 Control por Voz en Tiempo Real")
st.write("Haz clic en el botón y empieza a hablar. La app detectará tu voz y la convertirá en texto.")

# Botón de reconocimiento de voz
stt_button = Button(label="🎤 Iniciar reconocimiento de voz", width=300)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value !== "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="voice_capture",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0,
)

# ==========================
# PROCESAMIENTO DEL TEXTO
# ==========================
if result and "GET_TEXT" in result:
    user_text = result.get("GET_TEXT").strip()
    st.success(f"🗣️ Texto reconocido: **{user_text}**")

    # Envío del mensaje por MQTT
    client.on_publish = on_publish
    client.connect(broker, port)
    message = json.dumps({"Act1": user_text})
    ret = client.publish("voicejaco", message)
    st.info("📡 Mensaje enviado al broker MQTT en el canal `voicejaco`")

    # Crear carpeta temporal si no existe
    os.makedirs("temp", exist_ok=True)

    # Generar audio del texto
    tts = gTTS(user_text, lang="es")
    audio_path = f"temp/audio_{int(time.time())}.mp3"
    tts.save(audio_path)
    st.audio(audio_path, format="audio/mp3")
    st.success("🔊 Audio generado a partir del texto reconocido.")

else:
    st.info("Presiona el botón para comenzar el reconocimiento de voz.")

# ==========================
# PIE DE PÁGINA
# ==========================
st.divider()
st.caption("© 2025 Jacobo Castro — Proyecto académico de Interfaces Multimodales 🎓")

    
    try:
        os.mkdir("temp")
    except:
        pass
