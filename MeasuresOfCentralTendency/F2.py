# Leer el tamaño de la lista
n = int(input("Introduce el tamaño de la lista: "))

# Leer los números y almacenarlos en una lista
numeros = [float(input(f"Introduce el número {i+1}: ")) for i in range(n)]

# Ordenar la lista de menor a mayor
numeros.sort()

# Mostrar la lista ordenada
print("Lista ordenada de menor a mayor:")
for numero in numeros:
    print(f"{numero:.2f}")
