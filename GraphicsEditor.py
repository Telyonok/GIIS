import keyboard
from MatrixFunctions import MatrixFunctions 
import numpy as np
import tkinter as tk

def fractional_part(num):
    return num - int(num)

class GraphicsEditor:
    def __init__(self, width, height, grid_size):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.window = tk.Tk()
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()
        self.canvas.configure(bg="white")
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.window.bind("<Return>", self.on_enter_press)
        self.canvas.bind('<ButtonRelease-1>', self.on_drag_end)
        self.lines = []
        self.current_line = None
        self.debug_mode = False
        self.grid_toggled = False
        self.curve_correction_mode = False
        self.dragged_point = None

        self.create_debug_mode_button()
        self.create_delete_button()
        self.create_mode_menu()
        self.create_line_algorithm_menu()
        self.create_second_order_line_algorithm_menu()
        self.create_curve_algorithm_menu()
        self.create_toggle_grid_button()
        self.create_change_grid_size_menu()

    def on_drag_end(self, event):
        if self.dragged_point is not None:
            self.current_line[self.dragged_point[0]] = event.x
            self.current_line[self.dragged_point[1]] = event.y
            self.canvas.delete("ghost")
            if (self.curve_algorithm_var.get() == 'Bezier'):
                self.draw_bezier_curve(self.current_line, "ghost")
            elif (self.curve_algorithm_var.get() == 'Hermite'):
                self.draw_hermite_curve(self.current_line, "ghost")
            elif (self.curve_algorithm_var.get() == 'B-spline'):
                self.draw_b_spline_curve(self.current_line, "ghost")
            self.redraw_markers()
            self.dragged_point = None

    def on_drag_start(self, event):
        i = 0
        while i < len(self.current_line):
            x_center = ((self.current_line[i] // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            y_center = ((self.current_line[i + 1] // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            x_event_center = ((event.x // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            y_event_center = ((event.y // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            if x_event_center == x_center and y_event_center == y_center:
                self.dragged_point = i, i + 1
            i += 2

    def on_enter_press(self, event):
        if self.curve_correction_mode:
            self.canvas.delete("marker")
            self.canvas.delete("ghost")
            if (self.curve_algorithm_var.get() == 'Bezier'):
                self.draw_bezier_curve(self.current_line)
            elif (self.curve_algorithm_var.get() == 'Hermite'):
                self.draw_hermite_curve(self.current_line)
            elif (self.curve_algorithm_var.get() == 'B-spline'):
                self.draw_b_spline_curve(self.current_line)
            self.current_line = None
            self.curve_correction_mode = False
        elif (self.mode_var.get() == 'Curve' and self.current_line != None and len(self.current_line) >= 8):# and ):
            if (self.curve_algorithm_var.get() == 'Bezier' and (len(self.current_line) == 8 or (len(self.current_line) - 8) % 6 == 0)):
                self.draw_bezier_curve(self.current_line, "ghost")
            elif (self.curve_algorithm_var.get() == 'Hermite' and len(self.current_line) % 4 == 0):
                self.draw_hermite_curve(self.current_line, "ghost")
            elif (self.curve_algorithm_var.get() == 'B-spline' and len(self.current_line) % 4 == 0):
                self.draw_b_spline_curve(self.current_line, "ghost")
            else:
                return
            self.redraw_markers()
            self.curve_correction_mode = True

    def create_debug_mode_button(self):
        debug_mode_button = tk.Button(self.window, text="Debug Mode", command=self.toggle_debug_mode)
        debug_mode_button.configure(bg="grey")
        debug_mode_button.pack(side="left")
        self.debug_mode_button = debug_mode_button

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        if self.debug_mode:
            self.debug_mode_button.configure(bg="green")
        else:
            self.debug_mode_button.configure(bg="grey")

    def create_delete_button(self):
        delete_button = tk.Button(self.window, text="Delete All Lines", command=self.delete_all_lines)
        delete_button.pack(side="left")

    def create_toggle_grid_button(self):
        toggle_grid_button = tk.Button(self.window, text="Toggle grid", command=self.toggle_grid)
        toggle_grid_button.pack(side="left")

    def update_grid_size(self, *args):
        new_size = self.grid_size_var.get()
        if self.grid_toggled:
            self.erase_grid()
        self.grid_size = int(new_size)
        if self.grid_toggled:
            self.draw_grid()
            
    def create_change_grid_size_menu(self):
        self.grid_size_var = tk.StringVar(self.window)
        self.grid_size_var.set("10")
        self.grid_size_var.trace_add("write", self.update_grid_size)
        grid_size_menu = tk.OptionMenu(self.window, self.grid_size_var, "10", "5", "3", "1")
        grid_size_menu.pack(side="left")

    def create_line_algorithm_menu(self):
        self.line_algorithm_var = tk.StringVar(self.window)
        self.line_algorithm_var.set("DDA")

        line_algorithm_menu = tk.OptionMenu(self.window, self.line_algorithm_var, "DDA", "Bresenham", "Wu")
        line_algorithm_menu.pack(side="left")
    
    def create_second_order_line_algorithm_menu(self):
        self.second_order_line_algorithm_var = tk.StringVar(self.window)
        self.second_order_line_algorithm_var.set("Circle")

        second_order_line_algorithm_menu = tk.OptionMenu(self.window, self.second_order_line_algorithm_var, "Circle", "Ellipse", "Hyperbola", "Parabola")
        second_order_line_algorithm_menu.pack(side="left")    

    def create_curve_algorithm_menu(self):
        self.curve_algorithm_var = tk.StringVar(self.window)
        self.curve_algorithm_var.set("Hermite")

        curve_algorithm_menu = tk.OptionMenu(self.window, self.curve_algorithm_var, "Hermite", "Bezier", "B-spline")
        curve_algorithm_menu.pack(side="left")

    def create_mode_menu(self):
        self.mode_var = tk.StringVar(self.window)
        self.mode_var.set("Line")

        mode_menu = tk.OptionMenu(self.window, self.mode_var, "Line", "Second-order line", "Curve")
        mode_menu.pack(side="left")

    def redraw_markers(self):
        self.canvas.delete("marker")
        i = 0
        while i < len(self.current_line):
            x_center = ((self.current_line[i] // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            y_center = ((self.current_line[i + 1] // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            self.canvas.create_rectangle(x_center - self.grid_size / 2, y_center - self.grid_size / 2, x_center + self.grid_size / 2, y_center + self.grid_size / 2, fill="green", tags="marker")
            i += 2

    def draw_grid(self):
        for x in range(0, self.width, self.grid_size):
            self.canvas.create_line(x, 0, x, self.height, fill="lightgray", tags="grid_line")
        for y in range(0, self.height, self.grid_size):
            self.canvas.create_line(0, y, self.width, y, fill="lightgray", tags="grid_line")
        self.canvas.tag_lower("grid_line")

    def erase_grid(self):
        self.canvas.delete("grid_line")\
    
    def delete_all_lines(self):
        self.canvas.delete("all")
        if self.grid_toggled:
            self.draw_grid()
        self.lines = []
        self.dragged_point = None
        self.curve_correction_mode = False
        self.current_line = None
    
    def toggle_grid(self):
        if self.grid_toggled:
            self.erase_grid()
            self.grid_toggled = False
        else:
            self.draw_grid()
            self.grid_toggled = True

    def on_canvas_click(self, event):
        if self.curve_correction_mode:
            return self.on_drag_start(event)
        x = event.x
        y = event.y

        x_center = ((x // self.grid_size) * self.grid_size) + (self.grid_size // 2)
        y_center = ((y // self.grid_size) * self.grid_size) + (self.grid_size // 2)

        self.canvas.create_rectangle(x_center - self.grid_size / 2, y_center - self.grid_size / 2, x_center + self.grid_size / 2, y_center + self.grid_size / 2, fill="green", tags="marker")

        if self.current_line is None:
            self.current_line = [x_center, y_center]
        elif((len(self.current_line) < 4 and self.mode_var.get() == 'Second-order line' and self.second_order_line_algorithm_var.get() == 'Parabola') or (self.mode_var.get() == 'Curve')):
            self.current_line.extend([x_center, y_center])
        else:
            self.current_line.extend([x_center, y_center])
            self.lines.append(self.current_line)
            line = self.current_line
            self.current_line = None
            self.draw(line)
            self.canvas.delete("marker")

    def show_error_message(self, message):
        error_label = tk.Label(self.canvas, text=message, fg="red")
        error_label.place(x=10, y=10)
        self.canvas.after(5000, lambda: error_label.destroy())

    def draw(self, line):
        x1, y1, x2, y2, x3, y3 = line + [None] * (6 - len(line))

        mode = self.mode_var.get()
        if (mode == "Line"):
            algorithm = self.line_algorithm_var.get()
            if algorithm == "DDA":
                self.draw_line_dda(x1, y1, x2, y2)
            elif algorithm == "Bresenham":
                self.draw_line_bresenham(x1, y1, x2, y2)
            elif algorithm == "Wu":
                self.draw_line_wu(x1, y1, x2, y2)
        if (mode == "Second-order line"):
            algorithm = self.second_order_line_algorithm_var.get()
            if algorithm == "Circle":
                self.draw_circle(x1, y1, x2, y2)
            elif algorithm == "Ellipse":
                self.draw_ellipse(x1, y1, x2, y2)
            elif algorithm == "Hyperbola":
                self.draw_hyperbola(x1, y1, x2, y2)
            elif algorithm == "Parabola":
                self.draw_parabola(x1, y1, x2, y2, x3, y3)

    def draw_circle(self, x1, y1, x2, y2):
        radius = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        x = 0
        y = ((radius // self.grid_size) * self.grid_size)
        delta = 1 - 2 * radius
        error = 0

        while y >= x:
            self.draw_circle_pixels(x1, y1, x, y)
            if self.debug_mode:
                self.canvas.update()
                keyboard.wait('space')
            error = 2 * (delta + y) - 1

            if delta < 0 and error <= 0:
                x += 1 * self.grid_size
                delta += 2 * x * self.grid_size + 1 * self.grid_size
                continue

            error = 2 * (delta - x) - 1

            if delta > 0 and error > 0:
                y -= 1 * self.grid_size
                delta += 1 * self.grid_size - 2 * y * self.grid_size
                continue

            x += 1 * self.grid_size
            delta += 2 * (x - y) * self.grid_size
            y -= 1 * self.grid_size

    def draw_circle_pixels(self, x1, y1, x, y):
        self.canvas.create_rectangle(x1 + x - self.grid_size / 2, y1 + y - self.grid_size / 2, x1 + x + self.grid_size / 2, y1 + y + self.grid_size / 2, fill="black")
        self.canvas.create_rectangle(x1 - x - self.grid_size / 2, y1 + y - self.grid_size / 2, x1 - x + self.grid_size / 2, y1 + y + self.grid_size / 2, fill="black")
        self.canvas.create_rectangle(x1 + x - self.grid_size / 2, y1 - y - self.grid_size / 2, x1 + x + self.grid_size / 2, y1 - y + self.grid_size / 2, fill="black")
        self.canvas.create_rectangle(x1 - x - self.grid_size / 2, y1 - y - self.grid_size / 2, x1 - x + self.grid_size / 2, y1 - y + self.grid_size / 2, fill="black")
        self.canvas.create_rectangle(x1 + y - self.grid_size / 2, y1 + x - self.grid_size / 2, x1 + y + self.grid_size / 2, y1 + x + self.grid_size / 2, fill="black")
        self.canvas.create_rectangle(x1 - y - self.grid_size / 2, y1 + x - self.grid_size / 2, x1 - y + self.grid_size / 2, y1 + x + self.grid_size / 2, fill="black")
        self.canvas.create_rectangle(x1 + y - self.grid_size / 2, y1 - x - self.grid_size / 2, x1 + y + self.grid_size / 2, y1 - x + self.grid_size / 2, fill="black")
        self.canvas.create_rectangle(x1 - y - self.grid_size / 2, y1 - x - self.grid_size / 2, x1 - y + self.grid_size / 2, y1 - x + self.grid_size / 2, fill="black") 
    
    def draw_ellipse_pixels(self, x, y, _x, _y):
        self.canvas.create_rectangle(x + _x - self.grid_size / 2, y + _y - self.grid_size / 2, x + _x + self.grid_size / 2, y + _y + self.grid_size / 2, fill="black")
        self.canvas.create_rectangle(x + _x - self.grid_size / 2, y - _y - self.grid_size / 2, x + _x + self.grid_size / 2, y - _y + self.grid_size / 2, fill="black")
        self.canvas.create_rectangle(x - _x - self.grid_size / 2, y - _y - self.grid_size / 2, x - _x + self.grid_size / 2, y - _y + self.grid_size / 2, fill="black")
        self.canvas.create_rectangle(x - _x - self.grid_size / 2, y + _y - self.grid_size / 2, x - _x + self.grid_size / 2, y + _y + self.grid_size / 2, fill="black")

    def draw_ellipse(self, x1, y1, x2, y2):
        a = abs(x2 - x1) / 2
        b = abs(y2 - y1) / 2 
        _x = 0
        _y = b
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        a_sqr = a * a
        b_sqr = b * b
        delta = 4 * b_sqr * ((_x + 1 * self.grid_size) * (_x + 1 * self.grid_size)) + a_sqr * ((2 * _y - 1 * self.grid_size) * (2 * _y - 1 * self.grid_size)) - 4 * a_sqr * b_sqr
        while a_sqr * (2 * _y - self.grid_size) > 2 * b_sqr * (_x + self.grid_size):
            self.draw_ellipse_pixels(center_x, center_y, _x, _y)
            if self.debug_mode:
                self.canvas.update()
                keyboard.wait('space')
            if delta < 0:
                _x += 1 * self.grid_size
                delta += 4 * b_sqr * (2 * _x + 3 * self.grid_size)
            else:
                _x += 1 * self.grid_size
                delta = delta - 8 * a_sqr * (_y - 1 * self.grid_size) + 4 * b_sqr * (2 * _x + 3 * self.grid_size)
                _y -= 1 * self.grid_size
        delta = b_sqr * ((2 * _x + 1 * self.grid_size) * (2 * _x + 1 * self.grid_size)) + 4 * a_sqr * ((_y + 1 * self.grid_size) * (_y + 1 * self.grid_size)) - 4 * a_sqr * b_sqr
        while _y + self.grid_size / 2 > 0:
            self.draw_ellipse_pixels(center_x, center_y, _x, _y)
            if self.debug_mode:
                self.canvas.update()
                keyboard.wait('space')
            if delta < 0:
                _y -= 1 * self.grid_size
                delta += 4 * a_sqr * (2 * _y + 3 * self.grid_size)
            else:
                _y -= 1 * self.grid_size
                delta = delta - 8 * b_sqr * (_x + 1 * self.grid_size) + 4 * a_sqr * (2 * _y + 3 * self.grid_size)
                _x += 1 * self.grid_size

    def draw_hyperbola(self, x0, y0, x1, y1):
        c = (x1*y1 - x0*y0)/(y0 - y1)
        k = y0*y1*(x1 - x0)/(y0 - y1)
        x = 0
        while x < self.width:
            x = x + 0.02 * self.grid_size
            y = k / (x + c)
            x_center = ((x // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            y_center = ((y // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            self.canvas.create_rectangle(x_center - self.grid_size / 2, y_center - self.grid_size / 2, x_center + self.grid_size / 2, y_center + self.grid_size / 2, fill = "black")
            if self.debug_mode:
                self.canvas.update()
                keyboard.wait('space')

    def draw_parabola(self, x0, y0, x1, y1, x2, y2):
        A = [[x0**2, x0, 1],
            [x1**2, x1, 1],
            [x2**2, x2, 1]]
        Y = [y0, y1, y2]
        a, b, c = np.linalg.solve(A, Y)

        x = 0
        while x <= self.width:
            y = int(a * x**2 + b * x + c)
            x_center = ((x // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            y_center = ((y // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            self.canvas.create_rectangle(x_center - self.grid_size / 2, y_center - self.grid_size / 2, x_center + self.grid_size / 2, y_center + self.grid_size / 2, fill='black')
            x += 0.1 * self.grid_size
            if self.debug_mode:
                self.canvas.update()
                keyboard.wait('space')

    def draw_b_spline_curve(self, points, tag=""):
        j = 0
        while j < len(points) - 6:
            for k in range(101):
                t = k / 100.0
                a = (1 - t) ** 3 / 6.0
                b = (3 * t ** 3 - 6 * t ** 2 + 4) / 6.0
                c = (3 * t * (1 + t - t ** 2) + 1) / 6.0
                d = t ** 3 / 6.0
                x = a * points[j] + b * points[j + 2] + c * points[j + 4] + d * points[j + 6]
                y = a * points[j + 1] + b * points[j + 3] + c * points[j + 5] + d * points[j + 7]
                x_center = ((x // self.grid_size) * self.grid_size) + (self.grid_size // 2)
                y_center = ((y // self.grid_size) * self.grid_size) + (self.grid_size // 2)
                self.canvas.create_rectangle(x_center - self.grid_size / 2, y_center - self.grid_size / 2, x_center + self.grid_size / 2, y_center + self.grid_size / 2, fill="black", tags=tag)
            j += 2

    def draw_bezier_curve(self, line, tag=""):
        i = 0
        while i < len(line) - 6:
            x0 = line[i]
            y0 = line[i + 1] 
            x1 = line[i + 2]
            y1 = line[i + 3]
            x2 = line[i + 4]
            y2 = line[i + 5]
            x3 = line[i + 6]
            y3 = line[i + 7]
            curve_points = []

            for t in range(1001):
                t = t / 1000
                x = int((1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t ** 2 * x2 + t ** 3 * x3)
                y = int((1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t ** 2 * y2 + t ** 3 * y3)
                curve_points.append((x, y))

            for x, y in curve_points:
                x_center = ((x // self.grid_size) * self.grid_size) + (self.grid_size // 2)
                y_center = ((y // self.grid_size) * self.grid_size) + (self.grid_size // 2)
                self.canvas.create_rectangle(x_center - self.grid_size / 2, y_center - self.grid_size / 2, x_center + self.grid_size / 2, y_center + self.grid_size / 2, fill="black", tags=tag)
            i += 6
   
    def draw_hermite_curve(self, line, tag = ""):
        i = 0
        while i < len(line) - 4:
            x0, y0 = line[i], line[i + 1]
            x1, y1 = line[i + 4], line[i + 5]
            cx0, cy0 = line[i + 2], line[i + 3]
            cx1, cy1 = line[i + 6], line[i + 7]
            
            num_segments = int(max(abs(x1 - x0), abs(y1 - y0)))
            t_step = 1.0 / num_segments

            j = 0
            while j < num_segments:
                t = j * t_step
                t2 = t * t
                t3 = t2 * t

                h1 = 2 * t3 - 3 * t2 + 1
                h2 = -2 * t3 + 3 * t2
                h3 = t3 - 2 * t2 + t
                h4 = t3 - t2

                x = h1 * x0 + h2 * x1 + h3 * cx0 + h4 * cx1
                y = h1 * y0 + h2 * y1 + h3 * cy0 + h4 * cy1
                x_center = ((x // self.grid_size) * self.grid_size) + (self.grid_size // 2)
                y_center = ((y // self.grid_size) * self.grid_size) + (self.grid_size // 2)
                self.canvas.create_rectangle(x_center - self.grid_size / 2, y_center - self.grid_size / 2, x_center + self.grid_size / 2, y_center + self.grid_size / 2, fill="black", tags=tag)
                j += 0.1 * self.grid_size
            i += 4

    def draw_line_dda(self, x1, y1, x2, y2):
        dx = int((x2 - x1) / self.grid_size)
        dy = int((y2 - y1) / self.grid_size)
        steps = max(abs(dx), abs(dy))

        x_increment = (dx / steps) * self.grid_size
        y_increment = (dy / steps) * self.grid_size

        x = x1
        y = y1

        for _ in range(int(steps) + 1):
            pixel_x = int(x)
            pixel_y = int(y)
            pixel_x = ((pixel_x // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            pixel_y = ((pixel_y // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            self.canvas.create_rectangle(pixel_x - self.grid_size / 2, pixel_y - self.grid_size / 2, pixel_x + self.grid_size / 2, pixel_y + self.grid_size / 2, fill="black")
            if self.debug_mode:
                self.canvas.update()
                keyboard.wait('space')
            x += x_increment
            y += y_increment

    def draw_line_bresenham(self, x1, y1, x2, y2):
        dx = int(abs(x2 - x1) / self.grid_size)
        dy = int(abs(y2 - y1) / self.grid_size)
        sx = -1 * self.grid_size if x1 > x2 else self.grid_size
        sy = -1 * self.grid_size if y1 > y2 else self.grid_size
        err = dx - dy

        while x1 != x2 or y1 != y2:
            x1 = ((x1 // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            x2 = ((x2 // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            self.canvas.create_rectangle(x1 - self.grid_size / 2, y1 - self.grid_size / 2, x1 + self.grid_size / 2, y1 + self.grid_size / 2, fill="black")
            if self.debug_mode:
                self.canvas.update()
                keyboard.wait('space')
            err2 = 2 * err
            if err2 > -dy:
                err -= dy
                x1 += sx

            if err2 < dx:
                err += dx
                y1 += sy
    
    def draw_line_wu(self, x1, y1, x2, y2):
        steep = abs(y2 - y1) > abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        self.draw_pixel_wu(steep, x1, y1, 0)
        self.draw_pixel_wu(steep, x2, y2, 0)
        dx = int((x2 - x1) / self.grid_size)
        dy = int((y2 - y1) / self.grid_size)
        gradient = dy / dx
        y = y1 + gradient * self.grid_size
        steps = int((x2 - x1) / self.grid_size)
        x = x1 + self.grid_size
        for _ in range(steps):
            if self.debug_mode:
                self.canvas.update()
                keyboard.wait('space')
            if (y % self.grid_size != y % (self.grid_size / 2)):
                if (y % (self.grid_size / 2) < 0.2 * self.grid_size):
                    self.draw_pixel_wu(steep, x, int(y), 0)
                else:
                    self.draw_pixel_wu(steep, x, int(y), y % (self.grid_size / 2) / self.grid_size)
                    self.draw_pixel_wu(steep, x, int(y) + self.grid_size, 1 - y % (self.grid_size / 2) / self.grid_size)
            else:
                if (self.grid_size / 2 - y % (self.grid_size / 2) < 0.2 * self.grid_size):
                    self.draw_pixel_wu(steep, x, int(y), 0)
                else:
                    self.draw_pixel_wu(steep, x, int(y), (self.grid_size / 2 - y % (self.grid_size / 2)) / self.grid_size)
                    self.draw_pixel_wu(steep, x, int(y) - self.grid_size, (self.grid_size / 2 - 1 + y % (self.grid_size / 2)) / self.grid_size)

            y += gradient * self.grid_size
            x += self.grid_size

    def draw_pixel_wu(self, steep, x, y, intensity):
        if steep:
            x, y = y, x
        x = ((x // self.grid_size) * self.grid_size) + (self.grid_size // 2)
        y = ((y // self.grid_size) * self.grid_size) + (self.grid_size // 2)
        intensity = max(0, min(intensity, 1))
        color = "#" + "{:02x}{:02x}{:02x}".format(int(255 * intensity), int(255 * intensity), int(255 * intensity))
        self.canvas.create_rectangle(x - self.grid_size / 2, y - self.grid_size / 2, x + self.grid_size / 2, y + self.grid_size / 2, fill=color, outline=color)

    def run(self):
        self.window.mainloop()
    
editor = GraphicsEditor(800, 600, 10)
editor.run()