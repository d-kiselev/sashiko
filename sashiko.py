import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QLineEdit
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt

DEFAULT_V_BITS = 12
DEFAULT_V_MASK = 693
DEFAULT_H_BITS = 7
DEFAULT_H_MASK = 17
GRID_SIZE = 20
LINE_THICKNESS = 3
MIN_WINDOW_WIDTH = 450
MIN_WINDOW_HEIGHT = 400
INITIAL_WINDOW_WIDTH = 700
INITIAL_WINDOW_HEIGHT = 600

class DrawingArea(QWidget):
    def __init__(self, on_resize_callback):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.v_bits = DEFAULT_V_BITS
        self.v_mask = DEFAULT_V_MASK
        self.h_bits = DEFAULT_H_BITS
        self.h_mask = DEFAULT_H_MASK
        self.on_resize_callback = on_resize_callback

    def set_data(self, v_bits, v_mask, h_bits, h_mask):
        self.v_bits = v_bits
        self.v_mask = v_mask
        self.h_bits = h_bits
        self.h_mask = h_mask
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        cols = rect.width() // GRID_SIZE
        rows = rect.height() // GRID_SIZE
        self.on_resize_callback(cols, rows)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        painter.fillRect(rect, QColor("white"))
        
        pen = QPen(QColor("black"), LINE_THICKNESS)
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
        
        current_x = GRID_SIZE
        column_index = 0
        while current_x < width:
            bit_index = column_index % v_bits_count
            bit = v_binary[bit_index]
            
            for y in range(0, height, GRID_SIZE):
                segment_index = y // GRID_SIZE
                if bit == '0':
                    if segment_index % 2 == 0:
                        painter.drawLine(current_x, y, current_x, min(y + GRID_SIZE, height))
                else:
                    if segment_index % 2 != 0:
                        painter.drawLine(current_x, y, current_x, min(y + GRID_SIZE, height))
            current_x += GRID_SIZE
            column_index += 1

        current_y = GRID_SIZE
        row_index = 0
        while current_y < height:
            bit_index = row_index % h_bits_count
            bit = h_binary[bit_index]
            
            for x in range(0, width, GRID_SIZE):
                segment_index = x // GRID_SIZE
                if bit == '0':
                    if segment_index % 2 == 0:
                        painter.drawLine(x, current_y, min(x + GRID_SIZE, width), current_y)
                else:
                    if segment_index % 2 != 0:
                        painter.drawLine(x, current_y, min(x + GRID_SIZE, width), current_y)
            current_y += GRID_SIZE
            row_index += 1

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sashiko Bit Mask Pattern")
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.resize(INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT)

        self.v_bits_input = QSpinBox()
        self.v_bits_input.setRange(1, 64)
        self.v_bits_input.setValue(DEFAULT_V_BITS)
        self.v_bits_input.valueChanged.connect(self.update_binary_view)

        self.v_mask_input = QDoubleSpinBox()
        self.v_mask_input.setDecimals(0)
        self.v_mask_input.setRange(0, float(2**64 - 1))
        self.v_mask_input.setValue(DEFAULT_V_MASK)
        self.v_mask_input.setSingleStep(1)
        self.v_mask_input.valueChanged.connect(self.update_binary_view)

        self.v_result_view = QLineEdit()
        self.v_result_view.setReadOnly(True)

        self.h_bits_input = QSpinBox()
        self.h_bits_input.setRange(1, 64)
        self.h_bits_input.setValue(DEFAULT_H_BITS)
        self.h_bits_input.valueChanged.connect(self.update_binary_view)

        self.h_mask_input = QDoubleSpinBox()
        self.h_mask_input.setDecimals(0)
        self.h_mask_input.setRange(0, float(2**64 - 1))
        self.h_mask_input.setValue(DEFAULT_H_MASK)
        self.h_mask_input.setSingleStep(1)
        self.h_mask_input.valueChanged.connect(self.update_binary_view)

        self.h_result_view = QLineEdit()
        self.h_result_view.setReadOnly(True)

        self.stats_label = QLabel()
        
        self.drawing_area = DrawingArea(self.update_stats)

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
        main_layout.addWidget(self.stats_label)
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

    def update_stats(self, cols, rows):
        total_squares = cols * rows
        self.stats_label.setText(f"Grid size: {cols}x{rows} (Total squares fit: {total_squares})")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())