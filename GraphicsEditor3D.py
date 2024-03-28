from matplotlib import pyplot as plt
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Shape:
    def __init__(self, points):
        self.points = points
        self.update_center_point()

    def update_center_point(self):
        num_points = len(self.points)
        sum_x = sum(point.x for point in self.points)
        sum_y = sum(point.y for point in self.points)
        sum_z = sum(point.z for point in self.points)
        center_x = sum_x / num_points
        center_y = sum_y / num_points
        center_z = sum_z / num_points
        self.center_point = Point(center_x, center_y, center_z)
    
    def rotate(self, angle, axis):
        rotation_matrix = self.get_rotation_matrix(angle, axis)
        for point in self.points:
            point.x, point.y, point.z = np.dot(rotation_matrix, [point.x, point.y, point.z])
        self.update_center_point()

    def get_rotation_matrix(self, angle, axis):
        c = np.cos(angle)
        s = np.sin(angle)
        if axis == 'x':
            return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == 'y':
            return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        elif axis == 'z':
            return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        
    def scale(self, scale_factor):
        for point in self.points:
            point.x = (point.x - self.center_point.x) * scale_factor + self.center_point.x
            point.y = (point.y - self.center_point.y) * scale_factor + self.center_point.y
            point.z = (point.z - self.center_point.z) * scale_factor + self.center_point.z
        self.update_center_point()

class GraphicsEditor3D:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Graphic Editor")

        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.axis('on')

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=4)

        self.points = []
        self.shapes = []

        self.selected_shape = None

        self.preview_point = Point(x=0, y=0, z=0)

        self.point_frame = tk.Frame(self.root)
        self.point_frame.grid(row=0, column=1, padx=10, pady=10)

        self.x_label = tk.Label(self.point_frame, text="X:")
        self.x_label.grid(row=0, column=0, padx=5, pady=5)
        self.x_entry = tk.Entry(self.point_frame, width=10)
        self.x_entry.grid(row=0, column=1, padx=5, pady=5)
        self.x_entry.bind("<KeyRelease>", self.x_changed)

        self.y_label = tk.Label(self.point_frame, text="Y:")
        self.y_label.grid(row=1, column=0, padx=5, pady=5)
        self.y_entry = tk.Entry(self.point_frame, width=10)
        self.y_entry.grid(row=1, column=1, padx=5, pady=5)
        self.y_entry.bind("<KeyRelease>", self.y_changed)

        self.z_label = tk.Label(self.point_frame, text="Z:")
        self.z_label.grid(row=2, column=0, padx=5, pady=5)
        self.z_entry = tk.Entry(self.point_frame, width=10)
        self.z_entry.grid(row=2, column=1, padx=5, pady=5)
        self.z_entry.bind("<KeyRelease>", self.z_changed)

        self.add_button = tk.Button(self.point_frame, text="Add Point", command=self.add_point)
        self.add_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.create_shape_button = tk.Button(self.point_frame, text="Create Shape", command=self.create_shape)
        self.create_shape_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.clear_button = tk.Button(self.point_frame, text="Clear", command=self.clear_all)
        self.clear_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        self.shapes_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE)
        self.shapes_listbox.grid(row=1, column=1, padx=10, pady=10)
        self.shapes_listbox.bind("<<ListboxSelect>>", self.select_shape)

        self.root.bind("<KeyPress-a>", self.move_shape_x_plus)
        self.root.bind("<KeyPress-z>", self.move_shape_x_minus)
        self.root.bind("<KeyPress-s>", self.move_shape_y_plus)
        self.root.bind("<KeyPress-x>", self.move_shape_y_minus)
        self.root.bind("<KeyPress-d>", self.move_shape_z_plus)
        self.root.bind("<KeyPress-c>", self.move_shape_z_minus)

        self.root.bind("<KeyPress-q>", self.rotate_selected_shape_x)
        self.root.bind("<KeyPress-w>", self.rotate_selected_shape_y)
        self.root.bind("<KeyPress-e>", self.rotate_selected_shape_z)

        self.root.bind("<KeyPress-r>", self.scale_selected_shape_plus_ten_percent)
        self.root.bind("<KeyPress-f>", self.scale_selected_shape_minus_ten_percent)
        
        self.file_menu = tk.Menu(root, tearoff=False)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Help", command=self.show_help)
        root.config(menu=self.file_menu) 

    def save_file(self):
        if self.shapes:
            with open("shapes.txt", "w") as file:
                for shape in self.shapes:
                    points_str = " ".join(f"{point.x},{point.y},{point.z}" for point in shape.points)
                    file.write(f"{len(shape.points)} {points_str}\n")

    def open_file(self):
        self.clear_all()
        try:
            with open("shapes.txt", "r") as file:
                for line in file:
                    num_points, *points_str = line.strip().split(" ")
                    num_points = int(num_points)
                    points = [Point(*map(float, point.split(","))) for point in points_str]
                    self.shapes.append(Shape(points))
            self.update_plot()
            self.update_shapes_listbox()
        except FileNotFoundError:
            print("Error: File not found")
    
    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Keybindings")

        help_text = """
        **Movement:**
        * 'a': Move selected shape +1 on X-axis
        * 'z': Move selected shape -1 on X-axis
        * 's': Move selected shape +1 on Y-axis
        * 'x': Move selected shape -1 on Y-axis
        * 'd': Move selected shape +1 on Z-axis
        * 'c': Move selected shape -1 on Z-axis

        **Rotation:**
        * 'q': Rotate selected shape +45 degrees around X-axis
        * 'w': Rotate selected shape +45 degrees around Y-axis
        * 'e': Rotate selected shape +45 degrees around Z-axis

        **Scaling:**
        * 'r': Scale selected shape up by 10%
        * 'f': Scale selected shape down by 10%

        **Other:**
        * 'Esc': Close this help window
        """

        help_label = tk.Label(help_window, text=help_text, justify=tk.LEFT)
        help_label.configure(font=("Arial", 11))
        help_label.pack(padx=10, pady=10)

        help_window.bind("<KeyPress-Escape>", lambda event: help_window.destroy())

    def scale_selected_shape_plus_ten_percent(self, *args):
        if self.selected_shape:
            self.selected_shape.scale(1.1)
            self.update_plot()

    def scale_selected_shape_minus_ten_percent(self, *args):
        if self.selected_shape:
            self.selected_shape.scale(0.9)
            self.update_plot()

    def rotate_selected_shape_x(self, *args):
        if self.selected_shape:
            self.selected_shape.rotate(np.pi/4, 'x')
            self.update_plot()

    def rotate_selected_shape_y(self, *args):
        if self.selected_shape:
            self.selected_shape.rotate(np.pi/4, 'y')
            self.update_plot()

    def rotate_selected_shape_z(self, *args):
        if self.selected_shape:
            self.selected_shape.rotate(np.pi/4, 'z')
            self.update_plot()

    def move_shape_x_plus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.x += 1
            self.update_plot()

    def move_shape_x_minus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.x -= 1
            self.update_plot()

    def move_shape_y_plus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.y += 1
            self.update_plot()

    def move_shape_y_minus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.y -= 1
            self.update_plot()

    def move_shape_z_plus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.z += 1
            self.update_plot()

    def move_shape_z_minus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.z -= 1
            self.update_plot()

    def select_shape(self, event):
        selected_index = self.shapes_listbox.curselection()
        if selected_index:
            self.selected_shape = self.shapes[selected_index[0]]
        self.update_shapes_listbox()
        self.update_plot()

    def clear_all(self):
        self.points = []
        self.selection_points = []
        self.selected_shape = None
        self.shapes = []
        self.update_plot()
        self.update_shapes_listbox()

    def x_changed(self, *args):
        self.preview_point.x = float(self.x_entry.get())
        self.update_plot()

    def y_changed(self, *args):
        self.preview_point.y = float(self.y_entry.get())
        self.update_plot()

    def z_changed(self, *args):
        self.preview_point.z = float(self.z_entry.get())
        self.update_plot()

    def add_point(self):
        x = float(self.x_entry.get())
        y = float(self.y_entry.get())
        z = float(self.z_entry.get())

        point = Point(x, y, z)
        self.points.append(point)
        self.update_plot()

    def draw_shape(self, x_values, y_values, z_values):
        num_steps = 20
        if len(x_values) >= 3:
            lines = []
            for i in range(len(x_values)):
                for j in range(i + 1, len(x_values)):
                    lines.append([i, j])

            interpolated_lines = []
            for line in lines:
                x_interp = np.linspace(x_values[line[0]], x_values[line[1]], num_steps)
                y_interp = np.linspace(y_values[line[0]], y_values[line[1]], num_steps)
                z_interp = np.linspace(z_values[line[0]], z_values[line[1]], num_steps)
                interpolated_lines.append(list(zip(x_interp, y_interp, z_interp)))

            for line in interpolated_lines:
                x, y, z = zip(*line)
                self.ax.plot(x, y, z, color='black', linewidth=1)
        else:
            self.ax.plot(x_values, y_values, z_values)

    def create_shape(self):
        shape = Shape(self.points)
        self.shapes.append(shape)
        self.points = []
        self.update_plot()
        self.update_shapes_listbox()

    def update_plot(self):
        self.ax.clear()

        for shape in self.shapes:
            points = shape.points
            x_values = [point.x for point in points]
            y_values = [point.y for point in points]
            z_values = [point.z for point in points]
            self.draw_shape(x_values, y_values, z_values)

        if self.points:
            marked_x = [point.x for point in self.points]
            marked_y = [point.y for point in self.points]
            marked_z = [point.z for point in self.points]
            self.ax.scatter(marked_x, marked_y, marked_z, color='red', s=50)

        if self.preview_point:
            self.ax.scatter(self.preview_point.x, self.preview_point.y, self.preview_point.z, color='green', s=50)

        if self.selected_shape:
            self.selected_shape.update_center_point()
            for point in self.selected_shape.points:
                self.ax.scatter(point.x, point.y, point.z, color='cyan', s=50)
            self.ax.scatter(self.selected_shape.center_point.x, self.selected_shape.center_point.y, self.selected_shape.center_point.z, color = 'purple', s = 20)

        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.set_zlim(-10, 10)
        self.canvas.draw()

    def update_shapes_listbox(self):
        self.shapes_listbox.delete(0, tk.END)
        for shape in self.shapes:
            self.shapes_listbox.insert(tk.END, f"Shape {self.shapes.index(shape) + 1}")

    def is_degenerate(x_values, y_values, points):
        p1 = np.array([x_values[points[0]], y_values[points[0]]])
        p2 = np.array([x_values[points[1]], y_values[points[1]]])
        p3 = np.array([x_values[points[2]], y_values[points[2]]])
        area = 0.5 * np.linalg.det(np.vstack([p2 - p1, p3 - p1]))
        return abs(area) < 1e-6

if __name__ == "__main__":
    root = tk.Tk()
    editor = GraphicsEditor3D(root)
    root.mainloop()