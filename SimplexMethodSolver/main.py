from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QMessageBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
)
from PyQt6.QtCore import Qt
import numpy as np
import re
from scipy.optimize import linprog


class SimplexApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Método Simplex")
        self.setGeometry(100, 100, 900, 600)

        # Diseño principal
        main_layout = QVBoxLayout()

        # --- Selección de Modo (Maximización/Minimización) ---
        mode_group = QGroupBox("Tipo de Problema")
        mode_layout = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Maximización", "Minimización"])
        mode_layout.addWidget(self.mode_combo)
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        # --- Entrada de la Función Objetivo ---
        obj_func_group = QGroupBox("Función Objetivo")
        obj_func_layout = QHBoxLayout()
        self.obj_func_input = QLineEdit()
        self.obj_func_input.setPlaceholderText("Ej: 3x1 + 5x2 - 2x3")
        obj_func_layout.addWidget(self.obj_func_input)
        obj_func_group.setLayout(obj_func_layout)
        main_layout.addWidget(obj_func_group)

        # --- Entrada de Restricciones ---
        restrictions_group = QGroupBox("Restricciones")
        restrictions_layout = QVBoxLayout()
        self.restrictions_input = QTextEdit()
        self.restrictions_input.setPlaceholderText(
            "Ej: 2x1 + 3x2 <= 6\n   x1 - x3 >= 2"
        )
        restrictions_layout.addWidget(self.restrictions_input)
        restrictions_group.setLayout(restrictions_layout)
        main_layout.addWidget(restrictions_group)

        # --- Botones ---
        buttons_layout = QHBoxLayout()
        self.solve_button = QPushButton("Resolver")
        self.solve_button.clicked.connect(self.solveSimplex)
        self.clear_button = QPushButton("Limpiar")
        self.clear_button.clicked.connect(self.clearInputs)
        buttons_layout.addWidget(self.solve_button)
        buttons_layout.addWidget(self.clear_button)
        main_layout.addLayout(buttons_layout)

        # --- Tabla de Resultados (Iteraciones) ---
        self.result_table = QTableWidget()
        self.result_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        main_layout.addWidget(self.result_table)

        # --- Resultado Final (Solución Óptima) ---
        result_group = QGroupBox("Resultado")
        result_layout = QVBoxLayout()
        self.result_label = QLabel("Solución óptima:")
        self.result_output = QLabel("")
        self.result_output.setStyleSheet("font-weight: bold;")
        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.result_output)
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)

        self.setLayout(main_layout)
    
    def solveSimplex(self):
        if not self.obj_func_input.text().strip():
            QMessageBox.warning(self, "Error", "Ingresa una función objetivo.")
            return
        if not self.restrictions_input.toPlainText().strip():
            QMessageBox.warning(self, "Error", "Ingresa al menos una restricción.")
            return

        try:
            obj_func = self.parseObjectiveFunction(self.obj_func_input.text())
            restrictions = self.parseRestrictions(self.restrictions_input.toPlainText())
            mode = self.mode_combo.currentText()

            if obj_func is None or any(r is None for r in restrictions):
                raise ValueError(
                    "Error en el formato de la función objetivo o restricciones."
                )

            solution, iterations, variable_values = self.calculateSimplex(
                obj_func, restrictions, mode
            )

            if solution is None:
                QMessageBox.critical(
                    self, "Error", "El problema no tiene solución finita."
                )
                return

            self.displayIterations(iterations)  # Pass the full tableau
            self.result_output.setText(f"{', '.join(variable_values)}")

        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, "Error", "Ocurrió un error inesperado: " + str(e)
            )

    def parseObjectiveFunction(self, text):
        try:
            text = text.replace(" ", "").lower()
            terms = re.findall(r"([-+]?\d*\.?\d*)x(\d+)", text)

            num_vars = 0
            for _, var_index_str in terms:
                num_vars = max(num_vars, int(var_index_str))

            coefficients = [0.0] * num_vars
            for coeff_str, var_index_str in terms:
                var_index = int(var_index_str)
                if var_index > num_vars:
                    raise ValueError(
                        "Índice de variable fuera de rango en función objetivo."
                    )

                if not coeff_str:
                    coeff = 1.0
                elif coeff_str == "+":
                    coeff = 1.0
                elif coeff_str == "-":
                    coeff = -1.0
                else:
                    try:
                        coeff = float(coeff_str)
                    except ValueError:
                        raise ValueError("Coeficiente inválido en función objetivo.")
                coefficients[var_index - 1] = coeff
            return coefficients

        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))
            return None

    def parseRestrictions(self, text):
        restrictions = []
        try:
            lines = text.splitlines()
            num_vars = 0

            # Determinar el número máximo de variables (más robusto)
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                terms = re.findall(
                    r"([-+]?\d*\.?\d*)x(\d+)", line.replace(" ", "").lower()
                )
                for _, var_index_str in terms:
                    num_vars = max(num_vars, int(var_index_str))

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                match = re.match(
                    r"(.+?)\s*([<>=]+)\s*(.+)", line.replace(" ", "").lower()
                )  # Espacios opcionales alrededor del operador
                if not match:
                    raise ValueError(f"Formato de restricción inválido: {line}")

                lhs, operator, rhs = match.groups()
                try:
                    rhs_value = float(rhs)
                except ValueError:
                    raise ValueError(f"Lado derecho inválido en restricción: {line}")

                coeffs = [0.0] * num_vars
                terms = re.findall(
                    r"([-+]?\d*\.?\d*)x(\d+)", lhs
                )  # Expresión regular mejorada

                for coeff_str, var_index_str in terms:
                    var_index = int(var_index_str)
                    if var_index > num_vars:
                        raise ValueError(
                            f"Índice de variable fuera de rango en: {line}"
                        )  # Más validación

                    if not coeff_str:  # Coeficiente implícito (ej. "x1")
                        coeff = 1.0
                    elif coeff_str == "+":
                        coeff = 1.0
                    elif coeff_str == "-":
                        coeff = -1.0
                    else:
                        try:
                            coeff = float(coeff_str)
                        except ValueError:
                            raise ValueError(
                                f"Coeficiente inválido en restricción: {line}"
                            )
                    coeffs[var_index - 1] = coeff

                restrictions.append((coeffs, operator, rhs_value))

            return restrictions

        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))  # Mostrar el error específico
            return None

    def calculateSimplex(self, obj_func, restrictions, mode):
        A_ub, b_ub, A_eq, b_eq = [], [], [], []

        for coeffs, operator, rhs in restrictions:
            if operator == "<=":
                A_ub.append(coeffs)
                b_ub.append(rhs)
            elif operator == ">=":
                A_ub.append([-x for x in coeffs])
                b_ub.append(-rhs)
            else:
                A_eq.append(coeffs)
                b_eq.append(rhs)

        A_ub = np.array(A_ub) if A_ub else None
        b_ub = np.array(b_ub) if b_ub else None
        A_eq = np.array(A_eq) if A_eq else None
        b_eq = np.array(b_eq) if b_eq else None
        c = -np.array(obj_func) if mode == "Maximización" else np.array(obj_func)

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, method="highs")

        if res.success:
            solution = res.fun
            variable_values = [f"x{i+1}={val:.4f}" for i, val in enumerate(res.x)]
            variable_values.append(f"z={solution:.4f}")
            return solution, [], variable_values
        else:
            return solution, iterations, variable_values


    def displayIterations(self, iterations):
        """Muestra las iteraciones en la tabla."""
        if not iterations:
            return

        num_iterations = len(iterations)
        if num_iterations == 0:
            return

        num_rows, num_cols = iterations[0].shape
        self.result_table.setColumnCount(num_cols)

        # Obtener el número de variables, holgura/exceso y artificiales
        num_vars = 0
        for r in self.parseRestrictions(self.restrictions_input.toPlainText()):
            num_vars = max(num_vars, len(r[0]))
        num_slack_excess = 0
        num_artificial = 0
        # 1. Contar variables de holgura y artificiales
        for _, operator, _ in self.parseRestrictions(
            self.restrictions_input.toPlainText()
        ):
            if operator == "<=":
                num_slack_excess += 1
            elif operator == ">=":
                num_slack_excess += 1
                num_artificial += 1
            elif operator == "=":
                num_artificial += 1

        # Crear encabezados dinámicos
        headers = ["Base"]
        for i in range(num_vars):
            headers.append(f"x{i + 1}")
        for i in range(num_slack_excess):
            headers.append(f"s{i + 1}")
        for i in range(num_artificial):
            headers.append(f"a{i + 1}")

        headers.append("b")

        self.result_table.setHorizontalHeaderLabels(headers)

        for i, iteration in enumerate(iterations):
            # Determinar la variable básica para cada fila (excluyendo la última fila)
            basic_vars = []
            for row in range(num_rows - 1):
                col_indices = np.where(iteration[row, :-1] == 1)[0]
                if len(col_indices) == 1:
                    col_index = col_indices[0]
                    if col_index < num_vars:
                        basic_vars.append(f"x{col_index + 1}")
                    elif col_index < num_vars + num_slack_excess:
                        basic_vars.append(f"s{col_index + 1-num_vars}")
                    else:
                        basic_vars.append(
                            f"a{col_index + 1-(num_vars+num_slack_excess)}"
                        )

                else:
                    basic_vars.append("-")

            # Llenar la tabla
            self.result_table.setRowCount(
                num_iterations * num_rows
            )  # Importante: Aquí se corrige el error
            for row in range(num_rows):
                for col in range(num_cols):
                    item = QTableWidgetItem(f"{iteration[row, col]:.2f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    # Corrección del índice: i * num_rows + row
                    self.result_table.setItem(i * num_rows + row, col, item)

            # Columna "Base"
            # La columna base se asigna en cada iteración, no por fila.
            for j, var in enumerate(basic_vars):
                base_item = QTableWidgetItem(var)
                base_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Corrección del índice:  i * num_rows + j
                self.result_table.setItem(i * num_rows + j, 0, base_item)

    def clearInputs(self):
        self.obj_func_input.clear()
        self.restrictions_input.clear()
        self.result_table.clearContents()
        self.result_table.setRowCount(0)
        self.result_output.setText("")


if __name__ == "__main__":
    app = QApplication([])
    window = SimplexApp()
    window.show()
    app.exec()
