# Leer el tamaño de la lista
n = int(input("Introduce el tamaño de la lista: "))

# Leer los números y almacenarlos en una lista
numeros = [float(input(f"Introduce el número {i+1}: ")) for i in range(n)]

# Imprimir la cantidad de asteriscos para cada número
for num in numeros:
    asteriscos = "*" * round(num)  # Convertir a entero redondeando
    print(asteriscos)
