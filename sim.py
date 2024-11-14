import random
import time
import threading
import pygame
import sys

# Valores por defecto para los temporizadores de luces
defaultGreenPeak = 20  # 20 segundos de luz verde en horas pico
defaultRedPeak = 40    # 40 segundos de luz roja en horas pico
defaultGreenOffPeak = 30  # 30 segundos de luz verde fuera de horas pico
defaultRedOffPeak = 30    # 30 segundos de luz roja fuera de horas pico

# Selección manual de horario
use_peak_hours = True  # Cambia a False para usar horas no pico

signals = []
noOfSignals = 4
currentGreen = 0  # Indicates which signal is green currently
nextGreen = (currentGreen + 1) % noOfSignals  # Indicates which signal will turn green next

# Speed for the single vehicle type (e.g., "car")
speeds = {'car': 2.25}

# Coordinates of vehicles' start
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]

# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Gap between vehicles
stoppingGap = 15  # stopping gap
movingGap = 15  # moving gap

# Tiempo de espera promedio para cada dirección
waitingTimes = {'right': [], 'down': [], 'left': [], 'up': []}  # Almacena los tiempos de espera individuales
averageWaitingTime = {'right': 0, 'down': 0, 'left': 0, 'up': 0}  # Almacena el tiempo de espera promedio

pygame.init()
simulation = pygame.sprite.Group()


class TrafficSignal:
    def __init__(self, red, green):
        self.red = red
        self.green = green
        self.signalText = ""

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = 'car'  # Only one vehicle type
        self.speed = speeds[self.vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1

        # Set color for all vehicles to blue (car color)
        self.color = (0, 0, 255)

        # Ajusta el tamaño del vehículo según la dirección
        if direction in ['right', 'left']:
            self.width = 30
            self.height = 15
        else:
            self.width = 15
            self.height = 30

        # Set stop position
        if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
            if direction == 'right':
                self.stop = vehicles[direction][lane][self.index - 1].stop - self.width - stoppingGap
            elif direction == 'left':
                self.stop = vehicles[direction][lane][self.index - 1].stop + self.width + stoppingGap
            elif direction == 'down':
                self.stop = vehicles[direction][lane][self.index - 1].stop - self.height - stoppingGap
            elif direction == 'up':
                self.stop = vehicles[direction][lane][self.index - 1].stop + self.height + stoppingGap
        else:
            self.stop = defaultStop[direction]

        self.startTime = time.time()  # Tiempo en que el vehículo empieza a esperar
        simulation.add(self)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def move(self):
        if self.direction == 'right':
            if self.crossed == 0 and self.x + self.width > stopLines[self.direction]:
                self.crossed = 1
                waitingTime = time.time() - self.startTime
                waitingTimes[self.direction].append(waitingTime)
                averageWaitingTime[self.direction] = sum(waitingTimes[self.direction]) / len(waitingTimes[self.direction])
            if (self.x + self.width <= self.stop or self.crossed == 1 or currentGreen == 0) and \
                    (self.index == 0 or self.x + self.width < (
                            vehicles[self.direction][self.lane][self.index - 1].x - movingGap)):
                self.x += self.speed
        elif self.direction == 'down':
            if self.crossed == 0 and self.y + self.height > stopLines[self.direction]:
                self.crossed = 1
                waitingTime = time.time() - self.startTime
                waitingTimes[self.direction].append(waitingTime)
                averageWaitingTime[self.direction] = sum(waitingTimes[self.direction]) / len(waitingTimes[self.direction])
            if (self.y + self.height <= self.stop or self.crossed == 1 or currentGreen == 1) and \
                    (self.index == 0 or self.y + self.height < (
                            vehicles[self.direction][self.lane][self.index - 1].y - movingGap)):
                self.y += self.speed
        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
                waitingTime = time.time() - self.startTime
                waitingTimes[self.direction].append(waitingTime)
                averageWaitingTime[self.direction] = sum(waitingTimes[self.direction]) / len(waitingTimes[self.direction])
            if (self.x >= self.stop or self.crossed == 1 or currentGreen == 2) and \
                    (self.index == 0 or self.x > (
                            vehicles[self.direction][self.lane][self.index - 1].x + self.width + movingGap)):
                self.x -= self.speed
        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
                waitingTime = time.time() - self.startTime
                waitingTimes[self.direction].append(waitingTime)
                averageWaitingTime[self.direction] = sum(waitingTimes[self.direction]) / len(waitingTimes[self.direction])
            if (self.y >= self.stop or self.crossed == 1 or currentGreen == 3) and \
                    (self.index == 0 or self.y > (
                            vehicles[self.direction][self.lane][self.index - 1].y + self.height + movingGap)):
                self.y -= self.speed

# Inicializamos los tiempos de luces en función de si es hora pico o no
def get_current_traffic_time():
    if use_peak_hours:  # Si usamos hora pico
        return defaultGreenPeak, defaultRedPeak
    else:  # Si usamos fuera de hora pico
        return defaultGreenOffPeak, defaultRedOffPeak


# Lógica de actualización de luces
def initialize():
    global defaultGreen, defaultRed
    green_time, red_time = get_current_traffic_time()
    defaultGreen = {i: green_time for i in
                    range(noOfSignals)}  # Asignar el mismo tiempo de verde para todas las señales
    defaultRed = red_time
    for i in range(noOfSignals):
        signals.append(TrafficSignal(red_time, green_time))
    repeat()


# Actualizar los tiempos de las luces
def repeat():
    global currentGreen, nextGreen
    while signals[currentGreen].green > 0:
        updateValues()
        time.sleep(1)

    signals[currentGreen].green = defaultGreen[currentGreen]
    signals[currentGreen].red = defaultRed

    currentGreen = nextGreen
    nextGreen = (currentGreen + 1) % noOfSignals
    signals[nextGreen].red = signals[currentGreen].green
    repeat()


def updateValues():
    for i in range(noOfSignals):
        if i == currentGreen:
            signals[i].green -= 1
        else:
            signals[i].red -= 1


# Función para generar vehículos con tasas ajustadas según hora pico o no pico
def generateVehicles():
    while True:
        lane_number = random.randint(1, 2)
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [25, 50, 75, 100]
        if temp < dist[0]:
            direction_number = 0
        elif temp < dist[1]:
            direction_number = 1
        elif temp < dist[2]:
            direction_number = 2
        elif temp < dist[3]:
            direction_number = 3
        Vehicle(lane_number, direction_number, directionNumbers[direction_number])

        # Ajuste dinámico de la tasa de generación de vehículos según hora pico o no pico
        if use_peak_hours:
            # Generación de 20-40 vehículos por minuto (1.5 - 3 segundos por vehículo)
            time.sleep(random.uniform(60/40, 60/20))  # Espera entre 1.5 y 3 segundos por vehículo
        else:
            # Generación de 10-25 vehículos por minuto (2.4 - 6 segundos por vehículo)
            time.sleep(random.uniform(60/25, 60/10))  # Espera entre 2.4 y 6 segundos por vehículo


class Main:
    def __init__(self):
        # Elegir el tipo de hora (pico o no pico)
        global use_peak_hours
        user_choice = input("Selecciona el tipo de horario (pico/no pico): ").strip().lower()
        if user_choice == 'pico':
            use_peak_hours = True
        elif user_choice == 'no pico':
            use_peak_hours = False
        else:
            print("Opción no válida, usando hora pico por defecto.")
            use_peak_hours = True

        # Iniciar la simulación
        self.start_simulation()

    def start_simulation(self):
        thread1 = threading.Thread(name="initialization", target=initialize, args=())
        thread1.daemon = True
        thread1.start()

        black = (0, 0, 0)
        white = (255, 255, 255)
        red = (255, 0, 0)
        green = (0, 255, 0)
        screenWidth = 1400
        screenHeight = 800
        screen = pygame.display.set_mode((screenWidth, screenHeight))
        pygame.display.set_caption("Simulación de Tráfico")

        background = pygame.image.load('images/intersection.png')

        thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())
        thread2.daemon = True
        thread2.start()

        font = pygame.font.Font(None, 30)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            screen.blit(background, (0, 0))

            for i in range(noOfSignals):
                if i == currentGreen:
                    signals[i].signalText = signals[i].green
                    color = green
                else:
                    signals[i].signalText = signals[i].red
                    color = red
                pygame.draw.circle(screen, color, signalCoods[i], 20)
                text = font.render(str(signals[i].signalText), True, white, black)
                screen.blit(text, signalTimerCoods[i])

            for direction in averageWaitingTime:
                avg_wait_text = font.render(
                    f"Avg Wait {direction.capitalize()}: {averageWaitingTime[direction]:.2f}s", True, white, black
                )
                screen.blit(avg_wait_text, (50, 50 + list(averageWaitingTime.keys()).index(direction) * 30))

            for vehicle in simulation:
                vehicle.move()
                vehicle.render(screen)

            pygame.display.update()

Main()
