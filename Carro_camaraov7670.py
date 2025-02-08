import time
import digitalio
import pwmio
import busio
import board
from adafruit_ov7670 import OV7670, OV7670_SIZE_DIV16, OV7670_COLOR_YUV

# Configuración de motores
motor_izq = pwmio.PWMOut(board.GP10, frequency=1000, duty_cycle=0)
motor_der = pwmio.PWMOut(board.GP11, frequency=1000, duty_cycle=0)
IN1 = digitalio.DigitalInOut(board.GP16)
IN2 = digitalio.DigitalInOut(board.GP17)
IN3 = digitalio.DigitalInOut(board.GP26)
IN4 = digitalio.DigitalInOut(board.GP27)

IN1.direction = digitalio.Direction.OUTPUT
IN2.direction = digitalio.Direction.OUTPUT
IN3.direction = digitalio.Direction.OUTPUT
IN4.direction = digitalio.Direction.OUTPUT

# Configuración de la cámara
cam_bus = busio.I2C(board.GP21, board.GP20)
cam = OV7670(
    cam_bus,
    data_pins=[board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7],
    clock=board.GP8,
    vsync=board.GP13,
    href=board.GP12,
    mclk=board.GP9,
    shutdown=board.GP15,
    reset=board.GP14
)
cam.size = OV7670_SIZE_DIV16
cam.colorspace = OV7670_COLOR_YUV
cam.flip_y = True

buf = bytearray(2 * cam.width * cam.height)
chars = b" NNNAAAAAA"
width = cam.width
row = bytearray(2 * width)

# Lista predefinida para la línea
predefined_list = bytearray(b'NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN')

# Umbral de cambio para correcciones (50%)
UMBRAL_CAMBIO = 0.50

# Tiempo de avance entre lecturas (en segundos)
TIEMPO_AVANCE = 0.14

# Sensibilidad aumentada
SENSIBILIDAD_CORRECCION = 2  # Antes era 3

# Intensidad de corrección ajustada
INTENSIDAD_CORRECCION = 35000
INTENSIDAD_CORRECCION_IZQ = 30000  # Menos potencia para corrección izquierda

def calcular_desviacion(row):
    """Calcula la desviación de la línea con respecto al patrón ideal."""
    row_str = row.decode('utf-8')
    total_pixeles = len(row_str)
    mitad = total_pixeles // 2
    izquierda = row_str[:mitad].count('A')
    derecha = row_str[mitad:].count('A')
    desviacion = (derecha - izquierda) / total_pixeles * 100
    return desviacion  # Positivo si se inclina a la derecha, negativo si a la izquierda

def detectar_cambio(row, predefined_list):
    """Detecta un cambio del 50% entre N y A en el arreglo"""
    cambios = sum(1 for i in range(len(predefined_list)) if row[i] != predefined_list[i])
    porcentaje_cambio = cambios / len(predefined_list)
    return porcentaje_cambio >= UMBRAL_CAMBIO

def motor_detener():
    """Detiene los motores inmediatamente"""
    motor_izq.duty_cycle = 0
    IN1.value = False
    IN2.value = False
    motor_der.duty_cycle = 0
    IN3.value = False
    IN4.value = False

def controlar_motores(desv):
    """Controla los motores según la desviación"""
    if -SENSIBILIDAD_CORRECCION <= desv <= SENSIBILIDAD_CORRECCION:
        print("Avanzando recto")
        motor_izq.duty_cycle = int(25000)
        IN1.value = True
        IN2.value = False
        motor_der.duty_cycle = int(25000)
        IN3.value = True
        IN4.value = False
        time.sleep(0.14)
    elif desv < -SENSIBILIDAD_CORRECCION:
        print("Corrigiendo a la izquierda")
        motor_izq.duty_cycle = int(10000)  # Motor izquierdo a menor potencia
        IN1.value = True
        IN2.value = False
        motor_der.duty_cycle = int(INTENSIDAD_CORRECCION_IZQ)
        IN3.value = True
        IN4.value = False
        time.sleep(0.12)
    elif desv > SENSIBILIDAD_CORRECCION:
        print("Corrigiendo a la derecha")
        motor_izq.duty_cycle = int(INTENSIDAD_CORRECCION)
        IN1.value = True
        IN2.value = False
        motor_der.duty_cycle = int(10000)  # Motor derecho a menor potencia
        IN3.value = True
        IN4.value = False
        time.sleep(0.12)
    motor_detener()

while True:
    # Capturar imagen
    cam.capture(buf)

    # Procesar la fila central
    for j in range(cam.height - 3, cam.height):
        for i in range(cam.width):
            row[i * 2] = row[i * 2 + 1] = chars[buf[2 * (width * j + i)] * (len(chars) - 1) // 255]
        print("Fila procesada:", row.decode())
    
    # Calcular la desviación
    desv = calcular_desviacion(row)
    print("Desviación:", desv)

    # Detectar cambio del 50% y controlar motores
    if detectar_cambio(row, predefined_list):
        print("Cambio del 50% detectado, corrigiendo...")
        controlar_motores(desv)
    else:
        print("No se detectó cambio significativo, avanzando recto")
        motor_izq.duty_cycle = int(25000)
        IN1.value = True
        IN2.value = False
        motor_der.duty_cycle = int(25000)
        IN3.value = True
        IN4.value = False
        time.sleep(0.14)
        motor_detener()

    time.sleep(0.14)  # Dar más tiempo para la lectura de la cámara