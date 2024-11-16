import random
import time
import threading
import pygame
import sys

verdePicoDefecto = 20  # 20 segundos de luz verde en horas pico
rojoPicoDefecto = 40  # 40 segundos de luz roja en horas pico
verdeFueraPicoDefecto = 30  # 30 segundos de luz verde fuera de horas pico
rojoFueraPicoDefecto = 30  # 30 segundos de luz roja fuera de horas pico

usarHorasPico = True
casoSeleccionado = 1

signals = []
numeroDeSignals = 4
verdeActual = 0
siguienteVerde = (verdeActual + 1) % numeroDeSignals

velocidades = {'coche': 2.25}

x = {'este': [0, 0, 0], 'sur': [755, 727, 697], 'oeste': [1400, 1400, 1400], 'norte': [602, 627, 657]}
y = {'este': [348, 370, 398], 'sur': [0, 0, 0], 'oeste': [498, 466, 436], 'norte': [800, 800, 800]}

vehiculos = {'este': {0: [], 1: [], 2: [], 'cruzado': 0}, 'sur': {0: [], 1: [], 2: [], 'cruzado': 0},
             'oeste': {0: [], 1: [], 2: [], 'cruzado': 0}, 'norte': {0: [], 1: [], 2: [], 'cruzado': 0}}
tiposDeVehiculos = {0: 'coche'}
numerosDeDireccion = {0: 'este', 1: 'sur', 2: 'oeste', 3: 'norte'}

coordenadasSeñal = [(530, 230), (810, 230), (810, 570), (530, 570)]
coordenadasTemporizadorSeñal = [(530, 210), (810, 210), (810, 550), (530, 550)]

lineasDeParada = {'este': 590, 'sur': 330, 'oeste': 800, 'norte': 535}
paradaDefecto = {'este': 580, 'sur': 320, 'oeste': 810, 'norte': 545}

espacioDeParada = 15
espacioDeMovimiento = 15

tiemposDeEspera = {'este': [], 'sur': [], 'oeste': [], 'norte': []}
tiempoDeEsperaPromedio = {'este': 0, 'sur': 0, 'oeste': 0, 'norte': 0}

pygame.init()
simulacion = pygame.sprite.Group()

# Tiempo total de simulación en segundos (60 minutos)
tiempoTotalSimulacion = 6 * 60

velocidadSimulacion = 1


class SignalTrafico:
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

        self.color = (0, 0, 255)

        if direccion in ['este', 'oeste']:
            self.ancho = 30
            self.alto = 15
        else:
            self.ancho = 15
            self.alto = 30

        # Establecer posición de parada
        if len(vehiculos[direccion][carril]) > 1 and vehiculos[direccion][carril][self.indice - 1].cruzado == 0:
            if direccion == 'este':
                self.parada = vehiculos[direccion][carril][self.indice - 1].parada - self.ancho - espacioDeParada
            elif direccion == 'oeste':
                self.parada = vehiculos[direccion][carril][self.indice - 1].parada + self.ancho + espacioDeParada
            elif direccion == 'sur':
                self.parada = vehiculos[direccion][carril][self.indice - 1].parada - self.alto - espacioDeParada
            elif direccion == 'norte':
                self.parada = vehiculos[direccion][carril][self.indice - 1].parada + self.alto + espacioDeParada
        else:
            self.parada = paradaDefecto[direccion]

        self.tiempoInicio = time.time()  # Tiempo en que el vehículo empieza a esperar
        simulacion.add(self)

    def renderizar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, (self.x, self.y, self.ancho, self.alto))

    def mover(self):
        if self.direccion == 'este':
            if self.cruzado == 0 and self.x + self.ancho > lineasDeParada[self.direccion]:
                self.cruzado = 1
                tiempoDeEspera = time.time() - self.tiempoInicio
                tiemposDeEspera[self.direccion].append(tiempoDeEspera)
                tiempoDeEsperaPromedio[self.direccion] = sum(tiemposDeEspera[self.direccion]) / len(
                    tiemposDeEspera[self.direccion])
            if (self.x + self.ancho <= self.parada or self.cruzado == 1 or verdeActual == 0) and \
                    (self.indice == 0 or self.x + self.ancho < (
                            vehiculos[self.direccion][self.carril][self.indice - 1].x - espacioDeMovimiento)):
                self.x += self.velocidad
        elif self.direccion == 'sur':
            if self.cruzado == 0 and self.y + self.alto > lineasDeParada[self.direccion]:
                self.cruzado = 1
                tiempoDeEspera = time.time() - self.tiempoInicio
                tiemposDeEspera[self.direccion].append(tiempoDeEspera)
                tiempoDeEsperaPromedio[self.direccion] = sum(tiemposDeEspera[self.direccion]) / len(
                    tiemposDeEspera[self.direccion])
            if (self.y + self.alto <= self.parada or self.cruzado == 1 or verdeActual == 1) and \
                    (self.indice == 0 or self.y + self.alto < (
                            vehiculos[self.direccion][self.carril][self.indice - 1].y - espacioDeMovimiento)):
                self.y += self.velocidad
        elif self.direccion == 'oeste':
            if self.cruzado == 0 and self.x < lineasDeParada[self.direccion]:
                self.cruzado = 1
                tiempoDeEspera = time.time() - self.tiempoInicio
                tiemposDeEspera[self.direccion].append(tiempoDeEspera)
                tiempoDeEsperaPromedio[self.direccion] = sum(tiemposDeEspera[self.direccion]) / len(
                    tiemposDeEspera[self.direccion])
            if (self.x >= self.parada or self.cruzado == 1 or verdeActual == 2) and \
                    (self.indice == 0 or self.x > (
                            vehiculos[self.direccion][self.carril][
                                self.indice - 1].x + self.ancho + espacioDeMovimiento)):
                self.x -= self.velocidad
        elif self.direccion == 'norte':
            if self.cruzado == 0 and self.y < lineasDeParada[self.direccion]:
                self.cruzado = 1
                tiempoDeEspera = time.time() - self.tiempoInicio
                tiemposDeEspera[self.direccion].append(tiempoDeEspera)
                tiempoDeEsperaPromedio[self.direccion] = sum(tiemposDeEspera[self.direccion]) / len(
                    tiemposDeEspera[self.direccion])
            if (self.y >= self.parada or self.cruzado == 1 or verdeActual == 3) and \
                    (self.indice == 0 or self.y > (
                            vehiculos[self.direccion][self.carril][
                                self.indice - 1].y + self.alto + espacioDeMovimiento)):
                self.y -= self.velocidad


# Inicializamos los tiempos de luces en función de si es hora pico o no
def obtenerTiempoDeTraficoActual():
    if usarHorasPico:  # Si usamos hora pico
        return verdePicoDefecto, rojoPicoDefecto
    else:
        return verdeFueraPicoDefecto, rojoFueraPicoDefecto


# Lógica de actualización de luces
def inicializar():
    global verdeDefecto, rojoDefecto
    tiempoVerde, tiempoRojo = obtenerTiempoDeTraficoActual()
    verdeDefecto = {i: tiempoVerde for i in range(numeroDeSignals)}
    rojoDefecto = tiempoRojo
    for i in range(numeroDeSignals):
        signals.append(SignalTrafico(tiempoRojo, tiempoVerde))
    repetir()


def actualizarValores():
    for i in range(numeroDeSignals):
        if i == verdeActual:
            signals[i].verde -= 1
        else:
            signals[i].rojo -= 1


def repetir():
    global verdeActual, siguienteVerde
    while signals[verdeActual].verde > 0:
        actualizarValores()
        time.sleep(1 / velocidadSimulacion)

    signals[verdeActual].verde = verdeDefecto[verdeActual]
    signals[verdeActual].rojo = rojoDefecto

    verdeActual = siguienteVerde
    siguienteVerde = (verdeActual + 1) % numeroDeSignals
    signals[siguienteVerde].rojo = signals[verdeActual].verde
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

        if usarHorasPico:
            # Generación de 20-40 vehículos por minuto (1.5 - 3 segundos por vehículo)
            time.sleep(
                random.uniform(60 / 40, 60 / 20) / velocidadSimulacion)  # Espera entre 1.5 y 3 segundos por vehículo
        else:
            # Generación de 10-25 vehículos por minuto (2.4 - 6 segundos por vehículo)
            time.sleep(
                random.uniform(60 / 25, 60 / 10) / velocidadSimulacion)  # Espera entre 2.4 y 6 segundos por vehículo


class Principal:
    def __init__(self):
        self.anchoPantalla = 1400
        self.altoPantalla = 800
        self.pantalla = pygame.display.set_mode((self.anchoPantalla, self.altoPantalla))
        pygame.display.set_caption("Simulación de Tráfico")
        self.fuente = pygame.font.Font('fonts/Roboto-Regular.ttf', 20)
        self.fondo = pygame.image.load('images/6p.png')
        self.menu()

    def menu(self):
        while True:
            self.pantalla.fill((0, 0, 0))
            texto_menu = [
                "Selecciona el caso de prueba:",
                "1. Escenario 1: Horas pico con tiempos estándar de luz verde y roja.",
                "2. Escenario 2: Horas no pico con tiempos estándar de luz verde y roja.",
                "3. Escenario 3: Ajuste del tiempo de luz verde y roja para priorizar las direcciones con mayor flujo de tráfico.",
                "4. Salir"
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
        azul = (0, 0, 255)
        pantalla = self.pantalla

        hilo2 = threading.Thread(name="generarVehiculos", target=generarVehiculos, args=())
        hilo2.daemon = True
        hilo2.start()

        fuente = pygame.font.Font('fonts/Roboto-Regular.ttf', 27)
        tiempo_inicio = time.time()

        while True:
            tiempo_actual = time.time()
            tiempo_transcurrido = (tiempo_actual - tiempo_inicio) * velocidadSimulacion

            if tiempo_transcurrido >= tiempoTotalSimulacion:
                self.finalizar_simulacion()
                break

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pantalla.blit(self.fondo, (0, 0))

            for i in range(numeroDeSignals):
                if i == verdeActual:
                    signals[i].textoSeñal = signals[i].verde
                    color = verde
                else:
                    signals[i].textoSeñal = signals[i].rojo
                    color = rojo
                pygame.draw.circle(pantalla, color, coordenadasSeñal[i], 20)
                texto = fuente.render(str(signals[i].textoSeñal), True, negro)
                pantalla.blit(texto, coordenadasTemporizadorSeñal[i])

            # Mostrar el tiempo de espera promedio en la posición de cada dirección
            posiciones_espera_promedio = {
                'este': (850, 250),
                'sur': (800, 640),
                'oeste': (100, 600),
                'norte': (200, 120)
            }
            for direccion, posicion in posiciones_espera_promedio.items():
                texto_espera_promedio = fuente.render(
                    f"Espera Promedio {direccion.capitalize()}: {tiempoDeEsperaPromedio[direccion]:.2f}s", True, blanco
                )
                pantalla.blit(texto_espera_promedio, posicion)

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
        global verdeDefecto, rojoDefecto, verdeActual
        # Primero, calculamos el número de vehículos esperando en cada dirección
        vehiculos_en_espera = {
            'este': sum(len(vehiculos['este'][i]) for i in range(3)),
            'sur': sum(len(vehiculos['sur'][i]) for i in range(3)),
            'oeste': sum(len(vehiculos['oeste'][i]) for i in range(3)),
            'norte': sum(len(vehiculos['norte'][i]) for i in range(3)),
        }

        # Calculamos el total de vehículos esperando
        total_vehiculos = sum(vehiculos_en_espera.values())

        # Si no hay vehículos, no hacemos ningún ajuste
        if total_vehiculos == 0:
            return

        # Ajuste de tiempos en función del número de vehículos esperando
        tiempo_total_ajustado = sum(
            [verdePicoDefecto, verdeFueraPicoDefecto])  # Tiempo total verde para todas las direcciones
        tiempos_verde_ajustados = {}

        for direccion, vehiculos_en_espera_direccion in vehiculos_en_espera.items():
            porcentaje_espera = vehiculos_en_espera_direccion / total_vehiculos
            tiempo_verde_ajustado = tiempo_total_ajustado * porcentaje_espera
            tiempos_verde_ajustados[direccion] = max(5,
                                                     int(tiempo_verde_ajustado))  # Evitar que el tiempo verde sea demasiado bajo

        # Actualizamos los tiempos de luz verde para cada dirección
        for i in range(numeroDeSignals):
            direccion = numerosDeDireccion[i]
            if usarHorasPico:
                verdeDefecto[i] = tiempos_verde_ajustados[direccion]
            else:
                verdeDefecto[i] = max(verdeFueraPicoDefecto, tiempos_verde_ajustados[direccion])

        # Ajustamos los tiempos de luz roja en función del tiempo verde de la señal
        for i in range(numeroDeSignals):
            if usarHorasPico:
                rojoDefecto = max(rojoPicoDefecto, sum(verdeDefecto.values()) - verdeDefecto[
                    i])  # El tiempo rojo depende de los verdes restantes
            else:
                rojoDefecto = max(rojoFueraPicoDefecto, sum(verdeDefecto.values()) - verdeDefecto[i])

        # Iniciamos el ciclo de luces de tráfico con los nuevos tiempos
        print("Tiempos ajustados de luces de tráfico:", verdeDefecto, rojoDefecto)

        # Reemplazar las señales de tráfico con los nuevos tiempos ajustados
        for i in range(numeroDeSignals):
            signals[i].verde = verdeDefecto[i]
            signals[i].rojo = rojoDefecto

Principal()