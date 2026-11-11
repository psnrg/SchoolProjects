# Inicializar la lista vacía para almacenar productos
inventario = []


# Función para registrar un producto
def registrar_producto():
    nombre = input("Nombre del producto: ")
    cantidad = int(input("Cantidad inicial: "))
    costo = float(input("Costo unitario: "))
    inventario.append({"nombre": nombre, "cantidad": cantidad, "costo": costo})
    print(f"Producto '{nombre}' registrado exitosamente.")


# Función para consultar el inventario actual
def consultar_inventario_actual():
    if not inventario:
        print("El inventario está vacío.")
    else:
        print("\n*** INVENTARIO ACTUAL ***")
        for producto in inventario:
            costo_total = producto["cantidad"] * producto["costo"]
            print(
                f"- {producto['nombre']} | Cantidad: {producto['cantidad']} | Costo total: ${costo_total:.2f}"
            )


# Función para consultar el inventario crítico
def consultar_inventario_critico():
    critico = [p for p in inventario if p["cantidad"] < 5]
    if not critico:
        print("No hay productos en inventario crítico.")
    else:
        print("\n*** INVENTARIO CRÍTICO ***")
        for producto in critico:
            sugerencia = producto["cantidad"] * 2.5
            print(
                f"- {producto['nombre']} | Cantidad: {producto['cantidad']} | Sugerencia de compra: {sugerencia:.0f} unidades"
            )


# Función para actualizar la cantidad de un producto
def actualizar_producto():
    nombre = input("Nombre del producto a actualizar: ")
    for producto in inventario:
        if producto["nombre"] == nombre:
            print(f"Cantidad actual: {producto['cantidad']}")
            cambio = int(input("Ingresa la cantidad a sumar (+) o restar (-): "))
            nueva_cantidad = producto["cantidad"] + cambio
            if nueva_cantidad < 0:
                print("Error: La cantidad no puede ser negativa.")
            else:
                producto["cantidad"] = nueva_cantidad
                print(
                    f"La cantidad de '{nombre}' ha sido actualizada a {nueva_cantidad}."
                )
            return
    print(f"El producto '{nombre}' no está en el inventario.")


# Menú principal
while True:
    print("\nOpciones:")
    print("1. Registrar producto")
    print("2. Consultar inventario actual")
    print("3. Consultar inventario crítico")
    print("4. Actualizar producto")
    print("5. Salir")
    opcion = input("Selecciona una opción (1-5): ")

    if opcion == "1":
        registrar_producto()
    elif opcion == "2":
        consultar_inventario_actual()
    elif opcion == "3":
        consultar_inventario_critico()
    elif opcion == "4":
        actualizar_producto()
    elif opcion == "5":
        print("\n¡Gracias por usar el programa! ¡Hasta luego!")
        break
    else:
        print("\nOpción no válida, intenta de nuevo.")
