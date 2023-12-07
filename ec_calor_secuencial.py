import matplotlib.pyplot as plt
import numpy as np

#Datos del aluminio

Densidad= 2702 #Kg/m3
Calor_específico= 903 #J/Kg.K
Conductividad_térmica= 237 #W/m.K 
Temperatura_inicial= 330 #K
Lx= 2 #m
Ly= 2 #m
Nx= 20
Ny= 20

#Placa del material
plate_temperature = np.zeros((Nx+1, Ny+1))
plate_temperature[:] = Temperatura_inicial
print(plate_temperature)

#Condiciones de contorno
# Condiciones de contorno: establece temperaturas en los bordes
plate_temperature[:, 0] = 860  # Borde inferior
plate_temperature[:, -1] = 420   # Borde superior
plate_temperature[0, :] = 560    # Borde izquierdo
plate_temperature[-1, :] = 480   # Borde derecho
print(plate_temperature)

plt.imshow(plate_temperature, extent=[0, Lx, 0, Ly], origin='lower', cmap='viridis')
plt.colorbar(label='Temperatura')
plt.xlabel('Posición en el eje x')
plt.ylabel('Posición en el eje y')
plt.title('Simulación de Temperatura inicial en la Placa')
plt.show()


#Simulacion de transferencia de calor
num_steps = 200  # Número de pasos de tiempo
a= Conductividad_térmica/(Densidad*Calor_específico) #Difusividad térmica

for step in range(num_steps):
    # Calcula la temperatura en el siguiente paso de tiempo
    for i in range(1, Nx):
        for j in range(1, Ny):
            F = a * step / (i / Nx) ** 2
            if 1 - 4*F >= 0:
                plate_temperature[i, j] = F*((plate_temperature)[i+1, j] + (plate_temperature)[i-1, j] 
                + (plate_temperature)[i, j+1] + (plate_temperature)[i, j-1]) + (1-4*F)*(plate_temperature)[i, j]


plt.imshow(plate_temperature, extent=[0, Lx, 0, Ly], origin='lower', cmap='viridis')
plt.colorbar(label='Temperatura')
plt.xlabel('Posición en el eje x')
plt.ylabel('Posición en el eje y')
plt.title('Simulación de Temperatura Final en la Placa')

# Agregar cuadrícula
plt.grid(True, linestyle='--', alpha=0.7)

plt.show()

          



