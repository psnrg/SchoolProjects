# Leer el tamaño de la lista
n = int(input("Introduce el tamaño de la lista: "))

# Leer los números y almacenarlos en una lista
numeros = [float(input(f"Introduce el número {i+1}: ")) for i in range(n)]

# Calcular la media
media = sum(numeros) / n

# Mostrar la media con dos decimales
print(f"{media:.2f}")
