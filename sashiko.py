import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QLineEdit
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt

class DrawingArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.v_bits = 12
        self.v_mask = 693
        self.h_bits = 7
        self.h_mask = 17
        self.grid_size = 20

    def set_data(self, v_bits, v_mask, h_bits, h_mask):
        self.v_bits = v_bits
        self.v_mask = v_mask
        self.h_bits = h_bits
        self.h_mask = h_mask
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        painter.fillRect(rect, QColor("white"))
        
        pen = QPen(QColor("black"), 3)
        painter.setPen(pen)
        
        v_binary = format(self.v_mask, f'0{self.v_bits}b')
        if len(v_binary) > self.v_bits:
            v_binary = v_binary[-self.v_bits:]
            
        h_binary = format(self.h_mask, f'0{self.h_bits}b')
        if len(h_binary) > self.h_bits:
            h_binary = h_binary[-self.h_bits:]
            
        v_bits_count = len(v_binary)
        h_bits_count = len(h_binary)
        width = rect.width()
        height = rect.height()
        
        current_x = self.grid_size
        column_index = 0
        while current_x < width:
            bit_index = column_index % v_bits_count
            bit = v_binary[bit_index]
            
            for y in range(0, height, self.grid_size):
                segment_index = y // self.grid_size
                if bit == '0':
                    if segment_index % 2 == 0:
                        painter.drawLine(current_x, y, current_x, min(y + self.grid_size, height))
                else:
                    if segment_index % 2 != 0:
                        painter.drawLine(current_x, y, current_x, min(y + self.grid_size, height))
            current_x += self.grid_size
            column_index += 1

        current_y = self.grid_size
        row_index = 0
        while current_y < height:
            bit_index = row_index % h_bits_count
            bit = h_binary[bit_index]
            
            for x in range(0, width, self.grid_size):
                segment_index = x // self.grid_size
                if bit == '0':
                    if segment_index % 2 == 0:
                        painter.drawLine(x, current_y, min(x + self.grid_size, width), current_y)
                else:
                    if segment_index % 2 != 0:
                        painter.drawLine(x, current_y, min(x + self.grid_size, width), current_y)
            current_y += self.grid_size
            row_index += 1

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sashiko Bit Mask Pattern")
        self.setFixedSize(700, 600)

        self.v_bits_input = QSpinBox()
        self.v_bits_input.setRange(1, 64)
        self.v_bits_input.setValue(12)
        self.v_bits_input.valueChanged.connect(self.update_binary_view)

        self.v_mask_input = QDoubleSpinBox()
        self.v_mask_input.setDecimals(0)
        self.v_mask_input.setRange(0, float(2**64 - 1))
        self.v_mask_input.setValue(693)
        self.v_mask_input.setSingleStep(1)
        self.v_mask_input.valueChanged.connect(self.update_binary_view)

        self.v_result_view = QLineEdit()
        self.v_result_view.setReadOnly(True)

        self.h_bits_input = QSpinBox()
        self.h_bits_input.setRange(1, 64)
        self.h_bits_input.setValue(7)
        self.h_bits_input.valueChanged.connect(self.update_binary_view)

        self.h_mask_input = QDoubleSpinBox()
        self.h_mask_input.setDecimals(0)
        self.h_mask_input.setRange(0, float(2**64 - 1))
        self.h_mask_input.setValue(17)
        self.h_mask_input.setSingleStep(1)
        self.h_mask_input.valueChanged.connect(self.update_binary_view)

        self.h_result_view = QLineEdit()
        self.h_result_view.setReadOnly(True)

        self.drawing_area = DrawingArea()

        v_input_layout = QHBoxLayout()
        v_input_layout.addWidget(QLabel("V-Bits:"))
        v_input_layout.addWidget(self.v_bits_input)
        v_input_layout.addWidget(QLabel("V-Mask:"))
        v_input_layout.addWidget(self.v_mask_input)

        h_input_layout = QHBoxLayout()
        h_input_layout.addWidget(QLabel("H-Bits:"))
        h_input_layout.addWidget(self.h_bits_input)
        h_input_layout.addWidget(QLabel("H-Mask:"))
        h_input_layout.addWidget(self.h_mask_input)

        main_layout = QVBoxLayout()
        main_layout.addLayout(v_input_layout)
        main_layout.addWidget(self.v_result_view)
        main_layout.addLayout(h_input_layout)
        main_layout.addWidget(self.h_result_view)
        main_layout.addWidget(self.drawing_area, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.update_binary_view()

    def update_binary_view(self):
        v_bits = self.v_bits_input.value()
        v_mask = int(self.v_mask_input.value())
        h_bits = self.h_bits_input.value()
        h_mask = int(self.h_mask_input.value())
        
        v_binary = format(v_mask, f'0{v_bits}b')
        if len(v_binary) > v_bits:
            v_binary = v_binary[-v_bits:]
            
        h_binary = format(h_mask, f'0{h_bits}b')
        if len(h_binary) > h_bits:
            h_binary = h_binary[-h_bits:]
            
        self.v_result_view.setText(f"Vertical: {v_mask} = {v_binary}₂")
        self.h_result_view.setText(f"Horizontal: {h_mask} = {h_binary}₂")
        
        self.drawing_area.set_data(v_bits, v_mask, h_bits, h_mask)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())