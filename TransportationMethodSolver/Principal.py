import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import algoritmos

class InputDialog(QDialog):
    def __init__(self, rows, cols, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ingresar Datos de la Matriz")
        self.setGeometry(100, 100, 700, 350)
        self.rows = rows
        self.cols = cols

        self.table = QTableWidget(rows, cols)
        self.accept_button = QPushButton("Aceptar")
        self.accept_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.accept_button)
        self.setLayout(layout)

    def get_data(self):
        data = []
        for row in range(self.rows):
            row_data = []
            for col in range(self.cols):
                item = self.table.item(row, col)
                if item and item.text().strip():
                    try:
                        row_data.append(float(item.text()))
                    except ValueError:
                        return None
                else:
                    return None
            data.append(row_data)
        return data


class Principal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resolución de Problemas de Transporte y Asignación")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        options_layout = QVBoxLayout()
        options_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        method_label = QLabel("Seleccionar Método:")
        self.method_combo = QComboBox()
        self.method_combo.addItems(
            [
                "Esquina Noroeste",
                "Costo Mínimo",
                "Aproximación de Vogel",
                "Método de Asignación (Húngaro)",
            ]
        )
        options_layout.addWidget(method_label)
        options_layout.addWidget(self.method_combo)

        self.input_button = QPushButton("Ingresar Datos")
        self.input_button.clicked.connect(self.input_data_manually)
        options_layout.addWidget(self.input_button)

        self.solve_button = QPushButton("Resolver")
        self.solve_button.clicked.connect(self.solve)
        options_layout.addWidget(self.solve_button)

        results_layout = QVBoxLayout()

        self.input_table = QTableWidget()
        self.input_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        results_layout.addWidget(QLabel("Matriz de Entrada:"))
        results_layout.addWidget(self.input_table)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        results_layout.addWidget(QLabel("Solución:"))
        results_layout.addWidget(self.result_text)

        main_layout.addLayout(options_layout)
        main_layout.addLayout(results_layout)
        self.setLayout(main_layout)

    def input_data_manually(self):
        rows, ok1 = QInputDialog.getInt(
            self, "Dimensiones", "Número de filas (orígenes):", 2, 1, 100, 1
        )
        cols, ok2 = QInputDialog.getInt(
            self, "Dimensiones", "Número de columnas (destinos):", 2, 1, 100, 1
        )

        if ok1 and ok2:
            # Diálogo para los costos
            cost_dialog = InputDialog(rows, cols, self)
            cost_dialog.setWindowTitle("Ingresar Costos")
            if cost_dialog.exec() == QDialog.DialogCode.Accepted:
                cost_data = cost_dialog.get_data()
                if cost_data is None:
                    QMessageBox.warning(self, "Error", "Datos de costos inválidos.")
                    return

                # Diálogo para las ofertas
                supply_dialog = InputDialog(rows, 1, self)  # Una columna para las ofertas
                supply_dialog.setWindowTitle("Ingresar Ofertas")
                if supply_dialog.exec() == QDialog.DialogCode.Accepted:
                    supply_data = supply_dialog.get_data()
                    if supply_data is None:
                        QMessageBox.warning(self, "Error", "Datos de oferta inválidos.")
                        return

                    # Diálogo para las demandas
                    demand_dialog = InputDialog(1, cols, self)  # Una fila para las demandas
                    demand_dialog.setWindowTitle("Ingresar Demandas")
                    if demand_dialog.exec() == QDialog.DialogCode.Accepted:
                        demand_data = demand_dialog.get_data()
                        if demand_data is None:
                            QMessageBox.warning(self, "Error", "Datos de demanda inválidos.")
                            return

                        # Combinar costos, ofertas y demandas en la estructura correcta
                        combined_data = []
                        for i in range(rows):
                            combined_row = cost_data[i] + [supply_data[i][0]]  # Añadir oferta
                            combined_data.append(combined_row)
                        combined_data.append(demand_data[0] + [0])  # Añadir demanda y un 0 final

                        self.display_data(combined_data, rows, cols)
                    else:
                        return
                else:
                    return
            else:
                return

    def display_data(self, data, rows, cols):
        self.input_table.clear()
        self.input_table.setRowCount(rows + 1)  # +1 para la fila de demanda
        self.input_table.setColumnCount(cols + 1)  # +1 para la columna de oferta

        # Etiquetas para que el usuario sepa qué está viendo (opcional, pero recomendado)
        row_labels = [f"Origen {i+1}" for i in range(rows)] + ["Demanda"]
        col_labels = [f"Destino {j+1}" for j in range(cols)] + ["Oferta"]
        self.input_table.setVerticalHeaderLabels(row_labels)
        self.input_table.setHorizontalHeaderLabels(col_labels)


        for i, row in enumerate(data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.input_table.setItem(i, j, item)
                #Hacer que las ofertas y demandas no sean editables:
                if i == rows or j == cols:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)



    def solve(self):
        try:
            data = []
            for row in range(self.input_table.rowCount()):
                row_data = []
                for col in range(self.input_table.columnCount()):
                    item = self.input_table.item(row, col)
                    if item:
                        row_data.append(float(item.text()))
                    else:
                        row_data.append(0.0)
                data.append(row_data)

            if not data:
                QMessageBox.warning(
                    self, "Error", "No hay datos para resolver. Ingrese o cargue datos."
                )
                return

            selected_method = self.method_combo.currentText()
            self.result_text.clear()

            if selected_method == "Esquina Noroeste":
                result, steps = algoritmos.algoritmos.esquina_noroeste(data)
                self.result_text.append("Método de la Esquina Noroeste:\n")
            elif selected_method == "Costo Mínimo":
                result, steps = algoritmos.algoritmos.costo_minimo(data)
                self.result_text.append("Método del Costo Mínimo:\n")
            elif selected_method == "Aproximación de Vogel":
                result, steps = algoritmos.algoritmos.voguel(data)
                self.result_text.append("Método de Aproximación de Vogel:\n")
            elif selected_method == "Método de Asignación (Húngaro)":
                """ rows = self.input_table.rowCount() - 1  # Quitar la fila de demanda
                cols = self.input_table.columnCount() - 1 # Quitar la columna de oferta
                cost_data = [row[:cols] for row in data[:rows]] """
                result, steps = algoritmos.algoritmos.metodo_hungaro(data) # Pasar cost_data
                self.result_text.append("Método de Aproximación Hungaro:\n")
            else:
                QMessageBox.warning(self, "Error", "Método no válido.")
                return

            for step in steps:
                self.result_text.append(step)
            self.result_text.append(f"\nCosto total: {result}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Principal()
    window.show()
    sys.exit(app.exec())