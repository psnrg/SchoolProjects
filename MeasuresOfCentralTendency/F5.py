# Leer el tamaño de la lista
n = int(input("Introduce el tamaño de la lista: "))

# Leer los números y almacenarlos en una lista
numeros = [float(input(f"Introduce el número {i+1}: ")) for i in range(n)]

# Ordenar la lista
numeros.sort()

# Calcular la mediana
if n % 2 == 0:
    # Si el tamaño es par, es el promedio de los dos números centrales
    mediana = (numeros[n // 2 - 1] + numeros[n // 2]) / 2
else:
    # Si el tamaño es impar, es el número central
    mediana = numeros[n // 2]

# Mostrar la mediana con dos decimales
print(f"Mediana: {mediana:.2f}")
