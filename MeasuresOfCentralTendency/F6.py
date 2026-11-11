# Leer el tamaño de la lista
n = int(input("Introduce el tamaño de la lista: "))

# Leer los números y almacenarlos en una lista
numeros = [float(input(f"Introduce el número {i+1}: ")) for i in range(n)]

# Calcular el mínimo y el máximo
minimo = min(numeros)
maximo = max(numeros)

# Mostrar resultados con dos decimales
print(f"MIN {minimo:.2f}")
print(f"MAX {maximo:.2f}")
