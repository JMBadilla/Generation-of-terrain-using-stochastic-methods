import numpy as np
import matplotlib.pyplot as plt
import noise
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
import scipy as sp
import scipy.ndimage
from PIL import Image
#from arrows3dplot import * # python_file in project with class
import matplotlib.cm as cm
import math 
import random

# Función para generar un terreno inicial aleatorio usando ruido Perlin
def generate_perlin_terrain(size, scale, octaves, persistence, lacunarity, seed):
    #genera un Array 2D de elementos de rango [-1,1] usando perlin noise:
    #Size : las dimensiones del terreno generado, en este caso solo puede ser un cuadrado
    #Scale : el grado de zoom que tendrá el terreno
    #Octave : agrega detalles a las superficie, por ejemplo octave 1 pueden ser las montañas,
    #octave 2 pueden ser las rocas, son como multiples pasadas al terreno para agregarle detalle
    #Lacuranity : ajusta la frequencia en la que se agrega detalle en octave,
    #un valor deseable suele ser 2
    #Persistence : determina la influencia que tiene cada octave
    terrain = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            terrain[i][j] = noise.pnoise2(i/scale, j/scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, repeatx=size, repeaty=size, base=seed)
    return terrain

def calculate_energy(matrix):
    # Puedes definir tu propia función de energía aquí.
    #como input considera un terreno, ie una matriz de numeros entre -1 y 1
    rows, cols = matrix.shape
    all_cells = [(i, j) for i in range(rows) for j in range(cols)]
    inner_cells = [(i, j) for i in range(1, rows - 1) for j in range(1, cols - 1)]

    #se implementa una penalización de elevación para evitar tener picos muy altos
    elevation_penalty =sum(abs(matrix[i, j] - matrix[i + 1, j]) 
                        + abs(matrix[i, j] - matrix[i, j + 1])/
                        + abs(matrix[i, j] - matrix[i, j - 1])/
                        + abs(matrix[i, j] - matrix[i+1, j + 1])/
                        + abs(matrix[i, j] - matrix[i+1, j - 1])/
                        + abs(matrix[i, j] - matrix[i-1, j - 1])/
                        + abs(matrix[i, j] - matrix[i-1, j])/
                        + abs(matrix[i, j] - matrix[i-1, j + 1]) for i, j in inner_cells)
    
    gradient_x, gradient_y = np.gradient(matrix)
    total_gradient = np.sqrt(gradient_x**2 + gradient_y**2)

    #se implementa una recompensa a la suavidad del terreno:
    #smoothness_penalty = sum(abs(matrix[i, j] - 2 * matrix[i + 1, j] + matrix[i + 1, j]) + abs(matrix[i, j] - 2 * matrix[i, j + 1] + matrix[i, j + 1]) for i, j in inner_cells)

    #se implementa una cohesión con respecto a los vecinos de la matrix:
    #cohesion_penalty = sum(abs(matrix[i, j] - matrix[i + 1, j + 1]) + abs(matrix[i, j + 1] - matrix[i + 1, j]) for i, j in inner_cells)

    #incentiva máximizar los rangos de elevación posible
    elevation_range_penalty = max(matrix.flatten()) - min(matrix.flatten())




    energy = elevation_penalty  - elevation_range_penalty + np.mean(total_gradient)
    return energy

def generate_neighbor(state, temperature):
    # Genera un vecino cambiando aleatoriamente algunos puntos del terreno.
    neighbor = state.copy()
    num_changes = int(np.shape(state)[0]/10)
    
    for _ in range(num_changes):
        x, y = np.random.randint(0, state.shape[0]), np.random.randint(0, state.shape[1])
        neighbor[x, y] += np.random.normal(0, temperature)
    return neighbor

def simulated_annealing(initial_state, max_iterations, cooling_rate):
    current_state = initial_state
    current_energy = calculate_energy(current_state)
    iteration_arr = []
    energy_arr = []
    for iteration in range(max_iterations):
        temperature = initial_temperature / (1 + cooling_rate * iteration)
        
        # Perturb the current state
        new_state = generate_neighbor(current_state, temperature)
        new_energy = calculate_energy(new_state)

        # Calculate the change in energy
        delta_energy = new_energy - current_energy

        # Accept the new state with a probability based on the temperature and energy change
        if delta_energy < 0 or random.uniform(0, 1) < math.exp(-delta_energy / temperature):
            current_state = new_state
            current_energy = new_energy

        # Print or log the energy at regular intervals
        if iteration % 100 == 0:
            print(f"Iteration {iteration}, Energy: {current_energy}")

        iteration_arr.append(iteration)
        energy_arr.append(current_energy)


        # Add other termination conditions if needed
    return current_state, iteration_arr , energy_arr


def ploteo3d(terrain, size, title="3D Plot"):
    # get aspect ratio of tif file for late plot box-plot-ratio
    y_ratio, x_ratio = size, size

    # create arrays and declare x, y, z variables
    lin_x = np.linspace(0, 500, terrain.shape[0], endpoint=False)
    lin_y = np.linspace(0, 500, terrain.shape[1], endpoint=False)
    y, x = np.meshgrid(lin_y, lin_x)

    z = terrain

    # Apply gaussian filter, with sigmas as variables. Higher sigma = more smoothing and more calculations.
    sigma_y = 1
    sigma_x = 1
    sigma = [sigma_y, sigma_x]
    z_smoothed = sp.ndimage.gaussian_filter(z, sigma)

    # Some min and max and range values coming from gaussian_filter calculations
    z_smoothed_min = np.amin(z_smoothed)
    z_smoothed_max = np.amax(z_smoothed)

    # Creating figure with the specified title
    fig = plt.figure(figsize=(12, 10))
    fig.suptitle(title, fontsize=16)
    ax = plt.axes(projection='3d')
    ax.azim = -30
    ax.elev = 0
    ax.set_box_aspect((x_ratio, y_ratio, ((x_ratio + y_ratio) / 8)))

    surf = ax.plot_surface(x, y, z_smoothed, cmap='terrain', edgecolor='none')

    m = cm.ScalarMappable(cmap=surf.cmap, norm=surf.norm)
    m.set_array(z_smoothed)

    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 500)
    fig.tight_layout()

    plt.show()

# Parámetros
terrain_size = 30
scale = 20.0
octaves = 6
persistence = 0.5
lacunarity = 2.0
seed = 42
iterations = 7000
initial_temperature = 1.0
cooling_rate = 0.01

# Generar terreno inicial usando ruido Perlin
initial_terrain = generate_perlin_terrain(terrain_size, scale, octaves, persistence, lacunarity, seed)

# Aplicar Simulated Annealing
final_terrain , iteration_arr, energy_arr = simulated_annealing(initial_terrain, iterations, cooling_rate)
plt.figure(figsize=(12, 6))

plt.plot(iteration_arr, energy_arr)
plt.xlabel('Iteración')
plt.ylabel('Energía')
plt.title('Simulated Annealing/Perlin Noise - Resultados de Energía')
plt.yscale('log')
plt.show()

plt.imshow(initial_terrain, cmap='terrain', origin='lower')
plt.colorbar()
plt.title('Terreno Perlin Noise')

# Visualizar terreno generado
plt.figure()
plt.imshow(final_terrain, cmap='terrain', origin='lower')
plt.colorbar()
plt.title('Terreno Simulated Annealing / Perlin Noise')

ploteo3d(initial_terrain,terrain_size, 'Terreno Perlin Noise' )
ploteo3d(final_terrain,terrain_size, 'Terreno Simulated Annealing / Perlin Noise')
plt.tight_layout()

plt.show()