from statistics import multimode

# Leer el tamaño de la lista
n = int(input("Introduce el tamaño de la lista: "))

# Leer los números y almacenarlos en una lista
numeros = [float(input(f"Introduce el número {i+1}: ")) for i in range(n)]

# Calcular la moda
modas = multimode(numeros)

# Mostrar la moda con dos decimales
if len(modas) == len(numeros):
    print("No hay moda (todos los elementos son únicos).")
else:
    print("Moda(s):")
    for moda in modas:
        print(f"{moda:.2f}")
