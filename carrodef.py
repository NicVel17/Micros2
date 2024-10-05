import wifi
import socketpool
import time
import microcontroller
import pwmio
from digitalio import DigitalInOut, Direction

ssid = 'HOLArpb'
password = '12345678'

# Pines para los motores
Motor_A_Adelante = DigitalInOut(microcontroller.pin.GPIO1)
Motor_A_Atras = DigitalInOut(microcontroller.pin.GPIO2)
Motor_B_Adelante = DigitalInOut(microcontroller.pin.GPIO3)
Motor_B_Atras = DigitalInOut(microcontroller.pin.GPIO4)

Motor_A_Adelante.direction = Direction.OUTPUT
Motor_A_Atras.direction = Direction.OUTPUT
Motor_B_Adelante.direction = Direction.OUTPUT
Motor_B_Atras.direction = Direction.OUTPUT

# Configurar salidas PWM para controlar la velocidad de los motores
motor1_enable = pwmio.PWMOut(microcontroller.pin.GPIO0, frequency=1000)
motor2_enable = pwmio.PWMOut(microcontroller.pin.GPIO5, frequency=1000)

# Funciones de control de motores
def adelante():
    print("Moviendo adelante")  # Impresión para seguimiento
    Motor_A_Adelante.value = False
    Motor_B_Adelante.value = True
    Motor_A_Atras.value = True
    Motor_B_Atras.value = False
    motor1_enable.duty_cycle = 40000
    motor2_enable.duty_cycle = 40000

def atras():
    print("Moviendo atrás")  # Impresión para seguimiento
    Motor_A_Adelante.value = True
    Motor_B_Adelante.value = False
    Motor_A_Atras.value = False
    Motor_B_Atras.value = True
    motor1_enable.duty_cycle = 40000
    motor2_enable.duty_cycle = 40000

def detener():
    print("Deteniendo motores")  # Impresión para seguimiento
    Motor_A_Adelante.value = False
    Motor_B_Adelante.value = False
    Motor_A_Atras.value = False
    Motor_B_Atras.value = False
    motor1_enable.duty_cycle = 0
    motor2_enable.duty_cycle = 0

def derecha():
    print("Girando derecha")  # Impresión para seguimiento
    Motor_A_Adelante.value = True
    Motor_B_Adelante.value = True
    Motor_A_Atras.value = True
    Motor_B_Atras.value = True
    motor1_enable.duty_cycle = 40000
    motor2_enable.duty_cycle = 40000

def izquierda():
    print("Girando izquierda")  # Impresión para seguimiento
    Motor_A_Adelante.value = True
    Motor_B_Adelante.value = False
    Motor_A_Atras.value = False
    Motor_B_Atras.value = True
    motor1_enable.duty_cycle = 40000
    motor2_enable.duty_cycle = 40000

detener()

# Función de conexión Wi-Fi
def conectar():
    try:
        wifi.radio.connect(ssid, password)
        ip = wifi.radio.ipv4_address
        print(f'Conectado con IP: {ip}')
        return str(ip)
    except Exception as e:
        print(f'Error conectando: {e}')
        wifi.radio.enabled = False
        time.sleep(2)
        wifi.radio.enabled = True
        return None

# Apertura de socket
def open_socket(ip):
    pool = socketpool.SocketPool(wifi.radio)
    
    try:
        server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        server_socket.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
        server_socket.bind((ip, 80))
        server_socket.listen(1)
        return server_socket
    except OSError as e:
        print(f'Error al abrir el socket: {e}')
        return None

# Generar página web con joystick 3D
def pagina_web():
    html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Control de Motores</title>
                <style>
                    body, html { height: 100%; margin: 0; }
                    canvas { display: block; }
                    #joystick-container {
                        width: 300px;
                        height: 300px;
                        margin: 0 auto;
                    }
                </style>
            </head>
            <body>
                <div id="joystick-container"></div>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                <script>
                    let container = document.getElementById('joystick-container');
                    let scene = new THREE.Scene();
                    let camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
                    let renderer = new THREE.WebGLRenderer();
                    renderer.setSize(container.offsetWidth, container.offsetHeight);
                    container.appendChild(renderer.domElement);

                    let geometry = new THREE.SphereGeometry(5, 32, 32);
                    let material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
                    let joystick = new THREE.Mesh(geometry, material);
                    scene.add(joystick);

                    camera.position.z = 20;

                    let moveX = 0;
                    let moveY = 0;

                    function animate() {
                        requestAnimationFrame(animate);
                        joystick.position.x = moveX * 10;
                        joystick.position.y = moveY * 10;
                        renderer.render(scene, camera);
                    }
                    animate();

                    window.addEventListener('mousemove', function(event) {
                        const rect = container.getBoundingClientRect();
                        const x = event.clientX - rect.left;
                        const y = event.clientY - rect.top;

                        moveX = (x / rect.width) * 2 - 1;
                        moveY = -(y / rect.height) * 2 + 1;
                        
                        // Enviar las coordenadas a través de fetch
                        fetch(/joystick?x=${moveX}&y=${moveY})
                        .then(response => response.text())
                        .then(data => console.log(data))
                        .catch(error => console.error('Error:', error));
                    });
                </script>
            </body>
            </html>
            """
    return str(html)

# Servir solicitudes web
def serve(server_socket):
    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f'Conexión de {addr}')
            
            buffer = bytearray(1024)
            size = client_socket.recv_into(buffer)
            peticion = buffer[:size].decode("utf-8")
            
            print(f"Petición recibida: {peticion}")
            
            try:
                # Limpiar y extraer la petición
                peticion = peticion.split()[1].strip(' ?')  # Limpiar caracteres innecesarios
            except IndexError:
                print("Error al analizar la petición")
                continue
            
            # Ignorar favicon.ico
            if peticion == '/favicon.ico':
                client_socket.close()  # Cerrar la conexión sin hacer nada
                continue
            
            # Procesar el movimiento del joystick
            if peticion.startswith('/joystick'):
                params = peticion.split('?')[1]
                x, y = params.split('&')
                x = float(x.split('=')[1])
                y = float(y.split('=')[1])
                
                # Lógica para determinar el movimiento en función de x e y
                if y > 0.5:
                    adelante()
                elif y < -0.5:
                    atras()
                elif x > 0.5:
                    derecha()
                elif x < -0.5:
                    izquierda()
                else:
                    detener()
            else:
                print(f"Petición no válida: {peticion}")  # Mostrar la petición no válida
            
            html = pagina_web()
            client_socket.send(html.encode("utf-8"))
        except OSError as e:
            print(f'Error del socket: {e}')
        except Exception as e:
            print(f'Ocurrió un error: {e}')
        finally:
            client_socket.close()

# Iniciar la aplicación
try:
    ip = conectar()
    if ip:
        server_socket = open_socket(ip)
        if server_socket:  # Asegurarse de que el socket se haya abierto correctamente
            serve(server_socket)
except KeyboardInterrupt:
    microcontroller.reset()