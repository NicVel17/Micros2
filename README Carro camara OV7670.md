
Nicolas Velasquez Amarillo 20202005010
Ana Londoño Marin          20212005072
---

# **Sistema de Seguimiento de Línea con Cámara y Motores**  

## **1. Introducción**  
Este código implementa un sistema de visión artificial para un robot móvil, utilizando la cámara **OV7670** y motores controlados por **PWM**. El objetivo es detectar una línea y corregir la trayectoria del robot en función de la desviación de la línea detectada.

---

## **2. Configuración del Hardware**  

### **Motores**  
- Se configuran dos motores conectados a los pines **GP10 y GP11**, controlados mediante **PWM**.  
- También se definen cuatro pines digitales (**GP16, GP17, GP26, GP27**) para controlar la dirección de los motores.  

### **Cámara (OV7670)**  
- Se comunica mediante **I2C** a través de los pines **GP21 (SCL) y GP20 (SDA)**.  
- La captura de imágenes usa un bus de datos con 8 pines y señales de sincronización (**VSYNC, HREF, CLOCK**).  
- Se configura el modo de imagen en **YUV** con un tamaño reducido para facilitar el procesamiento.  

---

## **3. Procesamiento de Imagen**  
1. **Captura de Imagen**  
   - Se almacena la imagen en un buffer de bytes, donde cada píxel representa un valor de intensidad.  

2. **Extracción de Línea**  
   - Se analiza la fila central de la imagen y se compara con una lista predefinida.  
   - Se identifican los píxeles que representan la línea basándose en caracteres (`N` para fondo y `A` para la línea).  

3. **Cálculo de Desviación**  
   - Se compara el número de píxeles `A` en la mitad izquierda y derecha.  
   - Se calcula una desviación porcentual que indica hacia qué lado está desplazada la línea.  

4. **Detección de Cambio Significativo**  
   - Se evalúa si hay más del **50% de diferencia** en la distribución de píxeles respecto a la imagen previa.  
   - Si hay un cambio brusco, se ajusta el movimiento del robot.  

---

## **4. Control de Motores**  
Basado en la desviación calculada, el robot ajusta su trayectoria:  

- **Desviación mínima** → Avanza recto con potencia equilibrada.  
- **Desviación negativa** (línea hacia la izquierda) → Se reduce la velocidad del motor izquierdo para corregir.  
- **Desviación positiva** (línea hacia la derecha) → Se reduce la velocidad del motor derecho.  
- **Cambio del 50% detectado** → Se activa una corrección más agresiva.  

Después de cada ajuste, los motores se detienen momentáneamente para mayor estabilidad.  

---

## **5. Bucle Principal**  
1. Captura la imagen.  
2. Procesa la fila central para detectar la línea.  
3. Calcula la desviación y decide la corrección.  
4. Controla los motores según la desviación.  
5. Espera antes de la siguiente lectura.  

---

## **6. Conclusión**  
Este código permite a un robot seguir una línea de forma autónoma usando visión por computadora. La combinación de **procesamiento de imagen en tiempo real** y **control de motores** permite ajustes dinámicos en la trayectoria.  

Este enfoque es útil en aplicaciones como **logística automatizada**, **vehículos autónomos**, y **robots de exploración**.  

---
