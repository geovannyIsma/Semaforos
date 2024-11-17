import random
import time
import threading
import pygame
import sys

from configuracion import *

pygame.init()
simulacion = pygame.sprite.Group()

contadorVehiculos = {'este': 0, 'sur': 0, 'oeste': 0, 'norte': 0}

class Semaforo:
    def __init__(self, rojo, verde):
        self.rojo = rojo
        self.verde = verde
        self.textoSemaforo = ""

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
        contadorVehiculos[direccion] += 1
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
                contadorVehiculos[self.direccion] -= 1
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
                contadorVehiculos[self.direccion] -= 1
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
                contadorVehiculos[self.direccion] -= 1
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
                contadorVehiculos[self.direccion] -= 1
            if (self.y >= self.parada or self.cruzado == 1 or verdeActual == 3) and \
                    (self.indice == 0 or self.y > (
                            vehiculos[self.direccion][self.carril][
                                self.indice - 1].y + self.alto + espacioDeMovimiento)):
                self.y -= self.velocidad


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

        # Generación de vehículos en horas pico
        time.sleep(random.uniform(60 / 40, 60 / 20) / velocidadSimulacion)

class Escenario:
    def __init__(self, usar_horas_pico, ajuste_dinamico):
        self.usar_horas_pico = usar_horas_pico
        self.ajuste_dinamico = ajuste_dinamico
        self.verde_defecto = {}
        self.rojo_defecto = 0
        self.semaforos = []

    def obtener_tiempo_de_trafico_actual(self):
        if self.usar_horas_pico:
            return verdePicoDefecto, rojoPicoDefecto
        else:
            return verdeFueraPicoDefecto, rojoFueraPicoDefecto

    def inicializar(self):
        tiempo_verde, tiempo_rojo = self.obtener_tiempo_de_trafico_actual()
        self.verde_defecto = {i: tiempo_verde for i in range(numeroDeSemaforos)}
        self.rojo_defecto = tiempo_rojo
        for i in range(numeroDeSemaforos):
            self.semaforos.append(Semaforo(tiempo_rojo, tiempo_verde))
        if self.ajuste_dinamico:
            self.ajustar_tiempos_semaforos()
        self.repetir()

    def actualizar_valores(self):
        for i in range(numeroDeSemaforos):
            if i == verdeActual:
                self.semaforos[i].verde -= 1
            else:
                self.semaforos[i].rojo -= 1

    def ajustar_tiempos_semaforos(self):
        base_verde = 10
        max_verde = 40
        umbral_espera = 10
        for i in range(numeroDeSemaforos):
            direccion = numerosDeDireccion[i]
            num_vehiculos = sum(len(vehiculos[direccion][j]) for j in range(3))
            tiempo_espera_promedio = tiempoDeEsperaPromedio[direccion]

            if num_vehiculos > 0 or tiempo_espera_promedio > umbral_espera:
                tiempo_verde = base_verde + int(min(num_vehiculos / 2, max_verde - base_verde))
            else:
                tiempo_verde = base_verde

            self.semaforos[i].verde = tiempo_verde
            self.semaforos[i].rojo = 60 - tiempo_verde

    def repetir(self):
        global verdeActual, siguienteVerde
        while True:
            while self.semaforos[verdeActual].verde > 0:
                self.actualizar_valores()
                time.sleep(1 / velocidadSimulacion)
            self.semaforos[verdeActual].verde = self.verde_defecto[verdeActual]
            self.semaforos[verdeActual].rojo = self.rojo_defecto
            verdeActual = siguienteVerde
            siguienteVerde = (verdeActual + 1) % numeroDeSemaforos
            self.semaforos[siguienteVerde].rojo = self.semaforos[verdeActual].verde
            if self.ajuste_dinamico:
                self.ajustar_tiempos_semaforos()

class Principal:
    def __init__(self):
        self.anchoPantalla = 1400
        self.altoPantalla = 800
        self.pantalla = pygame.display.set_mode((self.anchoPantalla, self.altoPantalla))
        pygame.display.set_caption("Simulación de Tráfico")
        self.fuente = pygame.font.Font('fonts/Roboto-Regular.ttf', 20)
        self.fondo = pygame.image.load('images/interseccion.png')
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
        global verdeActual, siguienteVerde
        verdeActual = 0
        siguienteVerde = (verdeActual + 1) % numeroDeSemaforos

        if caso == 1:
            escenario = Escenario(usar_horas_pico=True, ajuste_dinamico=False)
        elif caso == 2:
            escenario = Escenario(usar_horas_pico=False, ajuste_dinamico=False)
        elif caso == 3:
            escenario = Escenario(usar_horas_pico=True, ajuste_dinamico=True)

        hilo1 = threading.Thread(name="inicializacion", target=escenario.inicializar, args=())
        hilo1.daemon = True
        hilo1.start()

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
            self.pantalla.blit(self.fondo, (0, 0))

            for i in range(numeroDeSemaforos):
                if i == verdeActual:
                    color = (0, 255, 0)
                else:
                    color = (255, 0, 0)
                pygame.draw.circle(self.pantalla, color, coordenadasSemaforo[i], 20)

            if verdeActual is not None:
                texto = fuente.render(str(escenario.semaforos[verdeActual].verde), True, (255, 255, 255))
                self.pantalla.blit(texto, coordenadasTemporizadorSemaforo[verdeActual])

            posiciones_espera_promedio = {
                'este': (850, 250),
                'sur': (800, 640),
                'oeste': (100, 600),
                'norte': (200, 120)
            }
            for direccion, posicion in posiciones_espera_promedio.items():
                texto_espera_promedio = fuente.render(
                    f"Espera Promedio {direccion.capitalize()}: {tiempoDeEsperaPromedio[direccion]:.2f}s", True, (255, 255, 255)
                )
                self.pantalla.blit(texto_espera_promedio, posicion)

                texto_numero_vehiculos = fuente.render(
                    f"Número de vehículos {direccion.capitalize()}: {contadorVehiculos[direccion]}", True, (255, 255, 255))
                self.pantalla.blit(texto_numero_vehiculos, (posicion[0], posicion[1] + 30))

            for vehiculo in simulacion:
                vehiculo.mover()
                vehiculo.renderizar(self.pantalla)

            pygame.display.update()

    def finalizar_simulacion(self):
        print("Simulación finalizada. Resultados:")
        for direccion in tiempoDeEsperaPromedio:
            print(f"Tiempo de espera promedio {direccion.capitalize()}: {tiempoDeEsperaPromedio[direccion]:.2f}s")

        tiemposDeEsperaTotal = sum([sum(tiemposDeEspera[direccion]) for direccion in tiemposDeEspera])
        numeroDeVehiculosTotal = sum([len(vehiculos[direccion][i]) for direccion in vehiculos for i in range(3)])
        tiempoPromedioTotal = tiemposDeEsperaTotal / numeroDeVehiculosTotal

        print(f"\nNúmero total de vehículos: {numeroDeVehiculosTotal}")
        print(f"\nTiempo de espera promedio total: {tiempoPromedioTotal:.2f}s")

        pygame.quit()
        sys.exit()

Principal()