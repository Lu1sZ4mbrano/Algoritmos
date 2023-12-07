import numpy as np
import pyopencl as cl
import matplotlib.pyplot as plt
import time

#Datos del aluminio

Densidad= 2702 #Kg/m3
Calor_específico= 903 #J/Kg.K
Conductividad_térmica= 237 #W/m.K m
Temperatura_inicial= 330 #K

a = Conductividad_térmica/(Densidad*Calor_específico) #Difusividad térmica

# Definimos las dimenciones de la placa

Nx= 50
Ny= 50


plate_temperature = np.zeros((Nx, Ny), dtype=np.float32)
plate_temperature[:] = Temperatura_inicial

# Condiciones de contorno: establece temperaturas en los bordes
plate_temperature[:, 0] = 860  # Borde inferior
plate_temperature[:, -1] = 420   # Borde superior
plate_temperature[0, :] = 560    # Borde izquierdo
plate_temperature[-1, :] = 480   # Borde derecho

# Parámetros de la simulación
t= 60 #segundos
num_steps = 1000  # Número de pasos de tiempo

# Configuración de OpenCL

platform = cl.get_platforms()[0]
gpu_devices = platform.get_devices(device_type=cl.device_type.GPU)
device = gpu_devices[0] if gpu_devices else None

if device is None:
    print("No se encontraron dispositivos GPU.")
    exit()

context = cl.Context([device])
queue = cl.CommandQueue(context)

# Modificación del kernel

kernel_code = """
__kernel void heat_transfer(__global float* plate, const int Nx, const int Ny, const float a, const float num_steps, const float t) {
    int i = get_global_id(0);
    int j = get_global_id(1);

    if (i > 0 && i < Nx - 1 && j > 0 && j < Ny - 1) {
        int index = i * Ny + j;
        int steps = num_steps;

        for (int step = 0; step < steps; ++step) {
            float F = a * (t/step) / (i / (float)Nx) * (i / (float)Nx);

            if (1.0 - 4.0 * F >= 0.0) {
                plate[index] = F * (plate[(i + 1) * Ny + j] + plate[(i - 1) * Ny + j] + plate[i * Ny + j + 1] + plate[i * Ny + j - 1])
                                + (1.0 - 4.0 * F) * plate[index];
            }
        }
    }
}

"""

program = cl.Program(context, kernel_code).build()
plate_buffer = cl.Buffer(context, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=plate_temperature)

# Especifica el número de hilos que deseas utilizar
num_threads = 16

# Ejecuta la simulación en paralelo

global_size = (num_threads, num_threads)

start_time = time.time() #inicio del tiempo
Placas = []
for step in range(num_steps-1):
    program.heat_transfer(queue, plate_temperature.shape, global_size, plate_buffer, np.int32(Nx), np.int32(Ny), np.float32(a), np.float32(num_steps), np.float32(t))
    cl.enqueue_copy(queue, plate_temperature, plate_buffer).wait()
    if step%200==0:
        Placas.append(plate_temperature.copy())

end_time = time.time() #fin del tiempo

print("Tiempo de ejecución: {:.3f} segundos".format(end_time - start_time))

#Visualización de resultados

for i, matriz in enumerate(Placas):
    fig, ax = plt.subplots()
    im = ax.imshow(matriz, cmap='hot', aspect='auto')
    ax.set_title(f"Paso {i * 200} Placa de Aluminio")
    plt.xlabel('Posición en el eje x')
    plt.ylabel('Posición en el eje y')
    plt.grid()
    plt.colorbar(im, label="Temperatura K")
    plt.draw()
    plt.pause(0.01)
    plt.waitforbuttonpress(timeout=-1)
    plt.close(fig)

plt.show()