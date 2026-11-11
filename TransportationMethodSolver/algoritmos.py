import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import pulp

class algoritmos:
    def esquina_noroeste(matriz_costos):
        """
        Resuelve el problema de transporte por el método de la Esquina Noroeste.

        Argumentos:
            matriz_costos: Lista de listas con los costos.  Debe tener la forma
                            [[costo11, costo12, ..., costo1n, oferta1],
                            [costo21, costo22, ..., costo2n, oferta2],
                            ...
                            [costom1, costom2, ..., costomn, ofertam],
                            [demanda1, demanda2, ..., demandan, 0]]  <- La última fila son las demandas
        Retorna:
            Una tupla: (costo_total, pasos)
            donde 'pasos' es una lista de strings describiendo cada paso.
        """
        filas = len(matriz_costos) - 1  # Número de filas (orígenes)
        columnas = len(matriz_costos[0]) - 1  # Número de columnas (destinos)
        oferta = [matriz_costos[i][-1] for i in range(filas)]  # Ofertas de cada origen
        demanda = matriz_costos[-1][:-1]  # Demandas de cada destino
        asignaciones = [[0] * columnas for _ in range(filas)]  # Matriz para guardar las asignaciones
        pasos = []
        costo_total = 0
        i, j = 0, 0  # Empezamos en la esquina noroeste
        
        while i < filas and j < columnas:
            paso = f"Asignando a la celda ({i+1}, {j+1}): "
            cantidad = min(oferta[i], demanda[j])
            asignaciones[i][j] = cantidad
            oferta[i] -= cantidad
            demanda[j] -= cantidad
            costo_total += cantidad * matriz_costos[i][j]
            paso += f"Min({matriz_costos[i][-1]}, {matriz_costos[-1][j]}) = {cantidad}.  Costo: {cantidad} * {matriz_costos[i][j]} = {cantidad * matriz_costos[i][j]}"
            pasos.append(paso)

            if oferta[i] == 0:
                i += 1  # Siguiente fila (origen)
            elif demanda[j] == 0:
                j += 1  # Siguiente columna (destino)
            #No hay un else, si oferta[i] == 0 y demanda[j] == 0, se avanza a la siguiente fila y columna.
        return costo_total, pasos
    
    def costo_minimo(matriz_costos):
        """
        Resuelve el problema de transporte por el método del Costo Mínimo.

        Argumentos:
            matriz_costos: La matriz de costos (ver formato en esquina_noroeste).

        Retorna:
            Una tupla: (costo_total, pasos)
        """
        filas = len(matriz_costos) - 1
        columnas = len(matriz_costos[0]) - 1
        oferta = [matriz_costos[i][-1] for i in range(filas)]
        demanda = matriz_costos[-1][:-1]
        asignaciones = [[0] * columnas for _ in range(filas)]
        pasos = []
        costo_total = 0

        costos_ordenados = []  # (costo, fila, columna)
        for i in range(filas):
            for j in range(columnas):
                costos_ordenados.append((matriz_costos[i][j], i, j))
        costos_ordenados.sort()  # Ordenar por costo ascendente


        for costo, i, j in costos_ordenados:
            if oferta[i] > 0 and demanda[j] > 0:
                paso = f"Asignando a la celda ({i+1}, {j+1}) con costo {costo}: "
                cantidad = min(oferta[i], demanda[j])
                asignaciones[i][j] = cantidad
                oferta[i] -= cantidad
                demanda[j] -= cantidad
                costo_total += cantidad * costo
                paso += f"Min({matriz_costos[i][-1]}, {matriz_costos[-1][j]}) = {cantidad}. Costo: {cantidad} * {costo} = {cantidad * costo}"
                pasos.append(paso)

        return costo_total, pasos
    
    def voguel(matriz_costos):
        
        """
        Método de Aproximación de Vogel para problemas de transporte.

        Argumentos:
            matriz_costos: Matriz de costos (ver formato en esquina_noroeste).

        Retorna:
            Una tupla: (costo_total, pasos)
        """
        filas = len(matriz_costos) - 1
        columnas = len(matriz_costos[0]) - 1
        oferta = [matriz_costos[i][-1] for i in range(filas)]
        demanda = matriz_costos[-1][:-1]
        asignaciones = [[0] * columnas for _ in range(filas)]
        pasos = []
        costo_total = 0

        while sum(oferta) > 0 and sum(demanda) > 0:  # Mientras haya oferta y demanda
            # 1. Calcular penalizaciones
            penalizaciones_filas = []
            for i in range(filas):
                if oferta[i] > 0:
                    costos_fila = [matriz_costos[i][j] for j in range(columnas) if demanda[j] > 0]
                    costos_fila.sort()
                    if len(costos_fila) >= 2:
                        penalizaciones_filas.append((costos_fila[1] - costos_fila[0], i))
                    elif len(costos_fila) == 1:
                        penalizaciones_filas.append((costos_fila[0], i)) #Si solo hay un elemento
                    else:
                        penalizaciones_filas.append((0,i)) #Si no hay elementos
                else:
                    penalizaciones_filas.append((-1, i))  # Origen agotado, penalización negativa

            penalizaciones_columnas = []
            for j in range(columnas):
                if demanda[j] > 0:
                    costos_columna = [matriz_costos[i][j] for i in range(filas) if oferta[i] > 0]
                    costos_columna.sort()
                    if len(costos_columna) >= 2:
                        penalizaciones_columnas.append((costos_columna[1] - costos_columna[0], j))
                    elif len(costos_columna) == 1:
                        penalizaciones_columnas.append((costos_columna[0], j))
                    else:
                        penalizaciones_columnas.append((0,j))
                else:
                    penalizaciones_columnas.append((-i,j))
                # 2. Encontrar la máxima penalización
            max_penalizacion_fila = max(penalizaciones_filas)
            max_penalizacion_columna = max(penalizaciones_columnas)

            if max_penalizacion_fila[0] >= max_penalizacion_columna[0]:
                # Asignar en la fila con máxima penalización
                i = max_penalizacion_fila[1]
                costos_en_fila = [(matriz_costos[i][j], j) for j in range(columnas) if demanda[j] > 0]
                if not costos_en_fila:
                    continue #Si no hay costos, continuamos
                min_costo_columna = min(costos_en_fila)[1]  # Columna con el mínimo costo en esa fila
                j = min_costo_columna
            else:
                # Asignar en la columna con máxima penalización
                j = max_penalizacion_columna[1]
                costos_en_columna = [(matriz_costos[i][j], i) for i in range(filas) if oferta[i] > 0]
                if not costos_en_columna:
                    continue
                min_costo_fila = min(costos_en_columna)[1]  # Fila con el mínimo costo en esa columna
                i = min_costo_fila

            # 3. Asignar la máxima cantidad posible
            paso = f"Asignando a la celda ({i+1}, {j+1}) (Vogel): "
            cantidad = min(oferta[i], demanda[j])
            asignaciones[i][j] = cantidad
            oferta[i] -= cantidad
            demanda[j] -= cantidad
            costo_total += cantidad * matriz_costos[i][j]
            paso += f"Min({matriz_costos[i][-1]}, {matriz_costos[-1][j]}) = {cantidad}. Costo: {cantidad} * {matriz_costos[i][j]} = {cantidad * matriz_costos[i][j]}"
            pasos.append(paso)

        return costo_total, pasos
    
    def Hungaro(matriz_costos):
        """
        Resuelve el problema de transporte utilizando el método húngaro.

        Argumentos:
            matriz_costos: Matriz de costos (ver formato en esquina_noroeste).

        Retorna:
            Una tupla: (costo_total, pasos)
        """
        filas = len(matriz_costos) - 1
        columnas = len(matriz_costos[0]) - 1
        oferta = [matriz_costos[i][-1] for i in range(filas)]
        demanda = matriz_costos[-1][:-1]

        # Asegurar que la oferta y la demanda sean iguales
        total_oferta = sum(oferta)
        total_demanda = sum(demanda)
        if total_oferta != total_demanda:
            diferencia = abs(total_oferta - total_demanda)
            if total_oferta < total_demanda:
                # Agregar una fila ficticia (origen) con costos 0
                matriz_costos = [fila[:-1] + [0] for fila in matriz_costos[:-1]] + [[0] * columnas + [diferencia]]
                oferta.append(diferencia)
            else:
                # Agregar una columna ficticia (destino) con costos 0
                for fila in matriz_costos[:-1]:
                    fila.append(0)
                matriz_costos[-1].append(diferencia)
                demanda.append(diferencia)

        # Resolver el problema con el método húngaro
        prob = pulp.LpProblem("Transporte", pulp.LpMinimize)
        variables = [[pulp.LpVariable(f"x{i}{j}", lowBound=0, cat="Continuous") for j in range(len(demanda))] for i in range(len(oferta))]

        # Función objetivo
        prob += pulp.lpSum(matriz_costos[i][j] * variables[i][j] for i in range(len(oferta)) for j in range(len(demanda)))

        # Restricciones de oferta
        for i in range(len(oferta)):
            prob += pulp.lpSum(variables[i][j] for j in range(len(demanda))) == oferta[i]

        # Restricciones de demanda
        for j in range(len(demanda)):
            prob += pulp.lpSum(variables[i][j] for i in range(len(oferta))) == demanda[j]

        # Resolver el problema
        prob.solve()

        # Obtener las asignaciones y calcular el costo total
        asignaciones = [[variables[i][j].varValue for j in range(len(demanda))] for i in range(len(oferta))]
        costo_total = sum(matriz_costos[i][j] * asignaciones[i][j] for i in range(len(oferta)) for j in range(len(demanda)))

        # Crear los pasos
        pasos = []
        for i in range(len(oferta)):
            for j in range(len(demanda)):
                if asignaciones[i][j] > 0:
                    pasos.append(f"Asignando {asignaciones[i][j]} unidades a la celda ({i+1}, {j+1}) con costo {matriz_costos[i][j]}")

        return costo_total, pasos

    @staticmethod
    def encontrar_ciclo(asignaciones, i, j):
        """
        Encuentra un ciclo cerrado en la tabla de asignaciones que incluye la celda (i, j).

        Argumentos:
            asignaciones: Matriz de asignaciones actuales.
            i, j: Coordenadas de la celda inicial.

        Retorna:
            Una lista de coordenadas que forman el ciclo.
        """
        visitados = set()
        camino = []

        def dfs(x, y):
            if (x, y) in visitados:
                return False
            visitados.add((x, y))
            camino.append((x, y))
            for nx, ny in algoritmos.vecinos(asignaciones, x, y):
                if (nx, ny) == (i, j) and len(camino) > 3:
                    camino.append((nx, ny))
                    return True
                if dfs(nx, ny):
                    return True
            camino.pop()
            return False

        if dfs(i, j):
            return camino
        return None

    @staticmethod
    def vecinos(asignaciones, x, y):
        """
        Encuentra las celdas vecinas con asignaciones positivas.

        Argumentos:
            asignaciones: Matriz de asignaciones actuales.
            x, y: Coordenadas de la celda actual.

        Retorna:
            Una lista de coordenadas de celdas vecinas.
        """
        vecinos = []
        for i in range(len(asignaciones)):
            if asignaciones[i][y] > 0 and i != x:
                vecinos.append((i, y))
        for j in range(len(asignaciones[0])):
            if asignaciones[x][j] > 0 and j != y:
                vecinos.append((x, j))
        return vecinos