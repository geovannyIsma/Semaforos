import random
import time
import threading
import pygame
import sys

# Valores por defecto para los temporizadores de luces
verdePicoDefecto = 20  # 20 segundos de luz verde en horas pico
rojoPicoDefecto = 40   # 40 segundos de luz roja en horas pico
verdeFueraPicoDefecto = 30  # 30 segundos de luz verde fuera de horas pico
rojoFueraPicoDefecto = 30   # 30 segundos de luz roja fuera de horas pico

# Selección manual de horario
usarHorasPico = True  # Cambia a False para usar horas no pico
casoSeleccionado = 1

señales = []
numeroDeSeñales = 4
verdeActual = 0  # Indica cuál señal está en verde actualmente
siguienteVerde = (verdeActual + 1) % numeroDeSeñales  # Indica cuál señal se pondrá verde a continuación

# Velocidad para el único tipo de vehículo (por ejemplo, "coche")
velocidades = {'coche': 2.25}

# Coordenadas de inicio de los vehículos
x = {'derecha': [0, 0, 0], 'abajo': [755, 727, 697], 'izquierda': [1400, 1400, 1400], 'arriba': [602, 627, 657]}
y = {'derecha': [348, 370, 398], 'abajo': [0, 0, 0], 'izquierda': [498, 466, 436], 'arriba': [800, 800, 800]}

vehiculos = {'derecha': {0: [], 1: [], 2: [], 'cruzado': 0}, 'abajo': {0: [], 1: [], 2: [], 'cruzado': 0},
             'izquierda': {0: [], 1: [], 2: [], 'cruzado': 0}, 'arriba': {0: [], 1: [], 2: [], 'cruzado': 0}}
tiposDeVehiculos = {0: 'coche'}
numerosDeDireccion = {0: 'derecha', 1: 'abajo', 2: 'izquierda', 3: 'arriba'}

# Coordenadas de la imagen de la señal, temporizador y conteo de vehículos
coordenadasSeñal = [(530, 230), (810, 230), (810, 570), (530, 570)]
coordenadasTemporizadorSeñal = [(530, 210), (810, 210), (810, 550), (530, 550)]

# Coordenadas de las líneas de parada
lineasDeParada = {'derecha': 590, 'abajo': 330, 'izquierda': 800, 'arriba': 535}
paradaDefecto = {'derecha': 580, 'abajo': 320, 'izquierda': 810, 'arriba': 545}

# Espacio entre vehículos
espacioDeParada = 15  # espacio de parada
espacioDeMovimiento = 15  # espacio de movimiento

# Tiempo de espera promedio para cada dirección
tiemposDeEspera = {'derecha': [], 'abajo': [], 'izquierda': [], 'arriba': []}  # Almacena los tiempos de espera individuales
tiempoDeEsperaPromedio = {'derecha': 0, 'abajo': 0, 'izquierda': 0, 'arriba': 0}  # Almacena el tiempo de espera promedio

pygame.init()
simulacion = pygame.sprite.Group()

# Tiempo total de simulación en segundos (60 minutos)
tiempoTotalSimulacion = 60 * 60

# Factor de velocidad de simulación
velocidadSimulacion = 1  # Ajuste de la velocidad de simulación (1 = tiempo real)

class SeñalDeTrafico:
    def __init__(self, rojo, verde):
        self.rojo = rojo
        self.verde = verde
        self.textoSeñal = ""

class Vehiculo(pygame.sprite.Sprite):
    def __init__(self, carril, numeroDeDireccion, direccion):
        pygame.sprite.Sprite.__init__(self)
        self.carril = carril
        self.claseVehiculo = 'coche'  # Solo un tipo de vehículo
        self.velocidad = velocidades[self.claseVehiculo] * velocidadSimulacion
        self.numeroDeDireccion = numeroDeDireccion
        self.direccion = direccion
        self.x = x[direccion][carril]
        self.y = y[direccion][carril]
        self.cruzado = 0
        vehiculos[direccion][carril].append(self)
        self.indice = len(vehiculos[direccion][carril]) - 1

        # Establecer color para todos los vehículos a azul (color del coche)
        self.color = (0, 0, 255)

        # Ajusta el tamaño del vehículo según la dirección
        if direccion in ['derecha', 'izquierda']:
            self.ancho = 30
            self.alto = 15
        else:
            self.ancho = 15
            self.alto = 30

        # Establecer posición de parada
        if len(vehiculos[direccion][carril]) > 1 and vehiculos[direccion][carril][self.indice - 1].cruzado == 0:
            if direccion == 'derecha':
                self.parada = vehiculos[direccion][carril][self.indice - 1].parada - self.ancho - espacioDeParada
            elif direccion == 'izquierda':
                self.parada = vehiculos[direccion][carril][self.indice - 1].parada + self.ancho + espacioDeParada
            elif direccion == 'abajo':
                self.parada = vehiculos[direccion][carril][self.indice - 1].parada - self.alto - espacioDeParada
            elif direccion == 'arriba':
                self.parada = vehiculos[direccion][carril][self.indice - 1].parada + self.alto + espacioDeParada
        else:
            self.parada = paradaDefecto[direccion]

        self.tiempoInicio = time.time()  # Tiempo en que el vehículo empieza a esperar
        simulacion.add(self)

    def renderizar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, (self.x, self.y, self.ancho, self.alto))

    def mover(self):
        if self.direccion == 'derecha':
            if self.cruzado == 0 and self.x + self.ancho > lineasDeParada[self.direccion]:
                self.cruzado = 1
                tiempoDeEspera = time.time() - self.tiempoInicio
                tiemposDeEspera[self.direccion].append(tiempoDeEspera)
                tiempoDeEsperaPromedio[self.direccion] = sum(tiemposDeEspera[self.direccion]) / len(tiemposDeEspera[self.direccion])
            if (self.x + self.ancho <= self.parada or self.cruzado == 1 or verdeActual == 0) and \
                    (self.indice == 0 or self.x + self.ancho < (
                            vehiculos[self.direccion][self.carril][self.indice - 1].x - espacioDeMovimiento)):
                self.x += self.velocidad
        elif self.direccion == 'abajo':
            if self.cruzado == 0 and self.y + self.alto > lineasDeParada[self.direccion]:
                self.cruzado = 1
                tiempoDeEspera = time.time() - self.tiempoInicio
                tiemposDeEspera[self.direccion].append(tiempoDeEspera)
                tiempoDeEsperaPromedio[self.direccion] = sum(tiemposDeEspera[self.direccion]) / len(tiemposDeEspera[self.direccion])
            if (self.y + self.alto <= self.parada or self.cruzado == 1 or verdeActual == 1) and \
                    (self.indice == 0 or self.y + self.alto < (
                            vehiculos[self.direccion][self.carril][self.indice - 1].y - espacioDeMovimiento)):
                self.y += self.velocidad
        elif self.direccion == 'izquierda':
            if self.cruzado == 0 and self.x < lineasDeParada[self.direccion]:
                self.cruzado = 1
                tiempoDeEspera = time.time() - self.tiempoInicio
                tiemposDeEspera[self.direccion].append(tiempoDeEspera)
                tiempoDeEsperaPromedio[self.direccion] = sum(tiemposDeEspera[self.direccion]) / len(tiemposDeEspera[self.direccion])
            if (self.x >= self.parada or self.cruzado == 1 or verdeActual == 2) and \
                    (self.indice == 0 or self.x > (
                            vehiculos[self.direccion][self.carril][self.indice - 1].x + self.ancho + espacioDeMovimiento)):
                self.x -= self.velocidad
        elif self.direccion == 'arriba':
            if self.cruzado == 0 and self.y < lineasDeParada[self.direccion]:
                self.cruzado = 1
                tiempoDeEspera = time.time() - self.tiempoInicio
                tiemposDeEspera[self.direccion].append(tiempoDeEspera)
                tiempoDeEsperaPromedio[self.direccion] = sum(tiemposDeEspera[self.direccion]) / len(tiemposDeEspera[self.direccion])
            if (self.y >= self.parada or self.cruzado == 1 or verdeActual == 3) and \
                    (self.indice == 0 or self.y > (
                            vehiculos[self.direccion][self.carril][self.indice - 1].y + self.alto + espacioDeMovimiento)):
                self.y -= self.velocidad

# Inicializamos los tiempos de luces en función de si es hora pico o no
def obtenerTiempoDeTraficoActual():
    if usarHorasPico:  # Si usamos hora pico
        return verdePicoDefecto, rojoPicoDefecto
    else:  # Si usamos fuera de hora pico
        return verdeFueraPicoDefecto, rojoFueraPicoDefecto

# Lógica de actualización de luces
def inicializar():
    global verdeDefecto, rojoDefecto
    tiempoVerde, tiempoRojo = obtenerTiempoDeTraficoActual()
    verdeDefecto = {i: tiempoVerde for i in range(numeroDeSeñales)}  # Asignar el mismo tiempo de verde para todas las señales
    rojoDefecto = tiempoRojo
    for i in range(numeroDeSeñales):
        señales.append(SeñalDeTrafico(tiempoRojo, tiempoVerde))
    repetir()

def actualizarValores():
    for i in range(numeroDeSeñales):
        if i == verdeActual:
            señales[i].verde -= 1
        else:
            señales[i].rojo -= 1

def repetir():
    global verdeActual, siguienteVerde
    while señales[verdeActual].verde > 0:
        actualizarValores()
        time.sleep(1 / velocidadSimulacion)  # Ajuste del tiempo de espera según la velocidad de simulación

    señales[verdeActual].verde = verdeDefecto[verdeActual]
    señales[verdeActual].rojo = rojoDefecto

    verdeActual = siguienteVerde
    siguienteVerde = (verdeActual + 1) % numeroDeSeñales
    señales[siguienteVerde].rojo = señales[verdeActual].verde
    repetir()

def generarVehiculos():
    while True:
        numeroDeCarril = random.randint(1, 2)
        temp = random.randint(0, 99)
        numeroDeDireccion = 0
        dist = [25, 50, 75, 100]
        if temp < dist[0]:
            numeroDeDireccion = 0
        elif temp < dist[1]:
            numeroDeDireccion = 1
        elif temp < dist[2]:
            numeroDeDireccion = 2
        elif temp < dist[3]:
            numeroDeDireccion = 3
        Vehiculo(numeroDeCarril, numeroDeDireccion, numerosDeDireccion[numeroDeDireccion])

        # Ajuste dinámico de la tasa de generación de vehículos según hora pico o no pico
        if usarHorasPico:
            # Generación de 20-40 vehículos por minuto (1.5 - 3 segundos por vehículo)
            time.sleep(random.uniform(60/40, 60/20) / velocidadSimulacion)  # Espera entre 1.5 y 3 segundos por vehículo
        else:
            # Generación de 10-25 vehículos por minuto (2.4 - 6 segundos por vehículo)
            time.sleep(random.uniform(60/25, 60/10) / velocidadSimulacion)  # Espera entre 2.4 y 6 segundos por vehículo

class Principal:
    def __init__(self):
        self.anchoPantalla = 1400
        self.altoPantalla = 800
        self.pantalla = pygame.display.set_mode((self.anchoPantalla, self.altoPantalla))
        pygame.display.set_caption("Simulación de Tráfico")
        self.fuente = pygame.font.Font('fonts/Roboto-Regular.ttf', 25)
        self.fondo = pygame.image.load('images/intersection.png')
        self.menu()

    def menu(self):
        while True:
            self.pantalla.fill((0, 0, 0))
            texto_menu = [
                "Selecciona el caso de prueba:",
                "1. Escenario 1: Horas pico con tiempos estándar de luz verde y roja.",
                "2. Escenario 2: Horas no pico con tiempos estándar de luz verde y roja.",
                "3. Escenario 3: Ajuste del tiempo de luz verde y roja para priorizar las direcciones con mayor flujo de tráfico.",
                "4. Establecer velocidad de simulación",
                "5. Salir"
            ]
            for i, texto in enumerate(texto_menu):
                texto_renderizado = self.fuente.render(texto, True, (255, 255, 255))
                self.pantalla.blit(texto_renderizado, (50, 50 + i * 30))

            pygame.display.update()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_1:
                        self.iniciar_simulacion(1)
                    elif evento.key == pygame.K_2:
                        self.iniciar_simulacion(2)
                    elif evento.key == pygame.K_3:
                        self.iniciar_simulacion(3)
                    elif evento.key == pygame.K_4:
                        pygame.quit()
                        sys.exit()

    def iniciar_simulacion(self, caso):
        global usarHorasPico, casoSeleccionado
        casoSeleccionado = caso
        if caso == 1:
            usarHorasPico = True
        elif caso == 2:
            usarHorasPico = False
        elif caso == 3:
            self.ajustar_tiempos_de_trafico()

        hilo1 = threading.Thread(name="inicializacion", target=inicializar, args=())
        hilo1.daemon = True
        hilo1.start()

        negro = (0, 0, 0)
        blanco = (255, 255, 255)
        rojo = (255, 0, 0)
        verde = (0, 255, 0)
        pantalla = self.pantalla

        hilo2 = threading.Thread(name="generarVehiculos", target=generarVehiculos, args=())
        hilo2.daemon = True
        hilo2.start()

        fuente = pygame.font.Font('fonts/Roboto-Regular.ttf', 30)
        tiempo_inicio = time.time()

        while True:
            tiempo_actual = time.time()
            tiempo_transcurrido = (tiempo_actual - tiempo_inicio) * velocidadSimulacion  # Ajuste del tiempo transcurrido según la velocidad de simulación

            if tiempo_transcurrido >= tiempoTotalSimulacion:
                self.finalizar_simulacion()
                break

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pantalla.blit(self.fondo, (0, 0))

            for i in range(numeroDeSeñales):
                if i == verdeActual:
                    señales[i].textoSeñal = señales[i].verde
                    color = verde
                else:
                    señales[i].textoSeñal = señales[i].rojo
                    color = rojo
                pygame.draw.circle(pantalla, color, coordenadasSeñal[i], 20)
                texto = fuente.render(str(señales[i].textoSeñal), True, blanco, negro)
                pantalla.blit(texto, coordenadasTemporizadorSeñal[i])

            for direccion in tiempoDeEsperaPromedio:
                texto_espera_promedio = fuente.render(
                    f"Espera Promedio {direccion.capitalize()}: {tiempoDeEsperaPromedio[direccion]:.2f}s", True, blanco, negro
                )
                pantalla.blit(texto_espera_promedio, (50, 50 + list(tiempoDeEsperaPromedio.keys()).index(direccion) * 30))

            for vehiculo in simulacion:
                vehiculo.mover()
                vehiculo.renderizar(pantalla)

            pygame.display.update()

    def finalizar_simulacion(self):
        print("Simulación finalizada. Resultados:")
        for direccion in tiempoDeEsperaPromedio:
            print(f"Tiempo de espera promedio {direccion.capitalize()}: {tiempoDeEsperaPromedio[direccion]:.2f}s")
        pygame.quit()
        sys.exit()

    def ajustar_tiempos_de_trafico(self):
        global señales
        # Ajustar los tiempos de luz verde para priorizar direcciones con mayor flujo de tráfico
        flujo_de_trafico = {
            direccion: len(vehiculos[direccion][0]) + len(vehiculos[direccion][1]) + len(vehiculos[direccion][2])
            for direccion in vehiculos}
        flujo_ordenado = sorted(flujo_de_trafico.items(), key=lambda item: item[1], reverse=True)
        tiempos_verde = [40, 30, 20, 10]  # Ejemplo de tiempos de verde ajustados

        # Asegurarse de que el número de tiempos de verde no exceda el número de señales
        tiempos_verde = tiempos_verde[:len(señales)]

        for i, direccion in enumerate(flujo_ordenado):
            if i < len(señales):
                señales[i].verde = tiempos_verde[i]
        rojoDefecto = 40

Principal()