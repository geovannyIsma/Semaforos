verdePicoDefecto = 20  # 20 segundos de luz verde en horas pico
rojoPicoDefecto = 40  # 40 segundos de luz roja en horas pico
verdeFueraPicoDefecto = 30  # 30 segundos de luz verde fuera de horas pico
rojoFueraPicoDefecto = 30  # 30 segundos de luz roja fuera de horas pico

usarHorasPico = True
casoSeleccionado = 1

semaforos = []
numeroDeSemaforos = 4
verdeActual = 0
siguienteVerde = (verdeActual + 1) % numeroDeSemaforos

velocidades = {'coche': 2.25}

x = {'este': [0, 0, 0], 'sur': [755, 727, 697], 'oeste': [1400, 1400, 1400], 'norte': [602, 627, 657]}
y = {'este': [348, 370, 398], 'sur': [0, 0, 0], 'oeste': [498, 466, 436], 'norte': [800, 800, 800]}

vehiculos = {'este': {0: [], 1: [], 2: [], 'cruzado': 0}, 'sur': {0: [], 1: [], 2: [], 'cruzado': 0},
             'oeste': {0: [], 1: [], 2: [], 'cruzado': 0}, 'norte': {0: [], 1: [], 2: [], 'cruzado': 0}}
tiposDeVehiculos = {0: 'coche'}
numerosDeDireccion = {0: 'este', 1: 'sur', 2: 'oeste', 3: 'norte'}

coordenadasSemaforo = [(530, 230), (810, 230), (810, 570), (530, 570)]
coordenadasTemporizadorSemaforo = [(530, 210), (810, 210), (810, 550), (530, 550)]

lineasDeParada = {'este': 590, 'sur': 330, 'oeste': 800, 'norte': 535}
paradaDefecto = {'este': 580, 'sur': 320, 'oeste': 810, 'norte': 545}

espacioDeParada = 15
espacioDeMovimiento = 15

tiemposDeEspera = {'este': [], 'sur': [], 'oeste': [], 'norte': []}
tiempoDeEsperaPromedio = {'este': 0, 'sur': 0, 'oeste': 0, 'norte': 0}

# Tiempo total de simulación en segundos (60 minutos)
tiempoTotalSimulacion = 60 * 60

# x1, x2, ......
velocidadSimulacion = 1

