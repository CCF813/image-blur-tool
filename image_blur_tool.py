import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFilter, ImageTk
import numpy as np
import cv2

class ImageBlurTool:
    def __init__(self, root):
        self.root = root
        self.points = []
        self.rectangles = []
        self.circles = []
        self.image = None
        self.photo = None
        self.draw = None
        self.current_circle = None
        self.mode = "circle"

        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame, cursor="cross")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar_x = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(yscrollcommand=scrollbar_y.set)
        self.canvas.configure(xscrollcommand=scrollbar_x.set)

        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.set_mode_rectangle()

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X)

        load_btn = tk.Button(btn_frame, text="Load Image", command=self.load_image)
        load_btn.pack(side=tk.LEFT, padx=5, pady=5)

        blur_btn = tk.Button(btn_frame, text="Blur Areas", command=self.blur_areas)
        blur_btn.pack(side=tk.LEFT, padx=5, pady=5)

        save_btn = tk.Button(btn_frame, text="Save Image", command=self.save_image)
        save_btn.pack(side=tk.LEFT, padx=5, pady=5)

        circle_mode_btn = tk.Button(btn_frame, text="Circle Mode", command=self.set_mode_circle)
        circle_mode_btn.pack(side=tk.LEFT, padx=5, pady=5)

        rectangle_mode_btn = tk.Button(btn_frame, text="Rectangle Mode", command=self.set_mode_rectangle)
        rectangle_mode_btn.pack(side=tk.LEFT, padx=5, pady=5)

    def select_points(self, event):
        if self.mode == "rectangle":
            self.points.append((self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)))
            if len(self.points) == 4:
                self.rectangles.append(self.points.copy())
                self.points = []
                self.draw_points()

    def draw_points(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        for rect in self.rectangles:
            for point in rect:
                self.canvas.create_oval(point[0] - 2, point[1] - 2, point[0] + 2, point[1] + 2, fill='red')
            self.canvas.create_polygon(rect, outline='red', fill='', width=2)
        for circle in self.circles:
            center_x = (circle[0][0] + circle[1][0]) / 2
            center_y = (circle[0][1] + circle[1][1]) / 2
            radius = ((circle[0][0] - circle[1][0]) ** 2 + (circle[0][1] - circle[1][1]) ** 2) ** 0.5 / 2
            self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline='blue')

    def blur_areas(self):
        image_cv = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
        for rect in self.rectangles:
            mask = np.zeros(image_cv.shape[:2], dtype=np.uint8)
            points_array = np.array([rect], dtype=np.int32)
            cv2.fillPoly(mask, points_array, 255)
            blurred_image_cv = cv2.GaussianBlur(image_cv, (21, 21), 0)
            image_cv = np.where(mask[:, :, np.newaxis] == 255, blurred_image_cv, image_cv)

        for circle in self.circles:
            center_x = (circle[0][0] + circle[1][0]) / 2
            center_y = (circle[0][1] + circle[1][1]) / 2
            radius = int(((circle[0][0] - circle[1][0]) ** 2 + (circle[0][1] - circle[1][1]) ** 2) ** 0.5 / 2)
            mask = np.zeros(image_cv.shape[:2], dtype=np.uint8)
            cv2.circle(mask, (int(center_x), int(center_y)), radius, 255, -1)
            blurred_image_cv = cv2.GaussianBlur(image_cv, (21, 21), 0)
            image_cv = np.where(mask[:, :, np.newaxis] == 255, blurred_image_cv, image_cv)

        image_pil = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
        self.update_image_display(image_pil)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")])
        if file_path:
            self.image.save(file_path)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        self.image = Image.open(file_path)
        self.draw = ImageDraw.Draw(self.image)
        self.update_image_display(self.image)

    def update_image_display(self, img=None):
        if img:
            self.image = img
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.draw_points()

    def on_mouse_wheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        else:
            self.canvas.yview_scroll(-1 * event.num, "units")

    def on_left_button_press(self, event):
        self.points = [(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))]
        if self.mode == "circle":
            self.current_circle = self.canvas.create_oval(self.points[0][0], self.points[0][1], self.points[0][0], self.points[0][1], outline='blue')

    def on_left_button_drag(self, event):
        if self.mode == "circle" and len(self.points) == 1:
            end_point = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
            center_x = (self.points[0][0] + end_point[0]) / 2
            center_y = (self.points[0][1] + end_point[1]) / 2
            radius = ((self.points[0][0] - end_point[0]) ** 2 + (self.points[0][1] - end_point[1]) ** 2) ** 0.5 / 2
            if self.current_circle:
                self.canvas.coords(self.current_circle, center_x - radius, center_y - radius, center_x + radius, center_y + radius)

    def on_left_button_release(self, event):
        if self.mode == "circle" and len(self.points) == 1:
            self.points.append((self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)))
            self.circles.append(self.points.copy())
            self.points = []
            self.current_circle = None
            self.draw_points()

    def set_mode_circle(self):
        self.mode = "circle"
        self.canvas.bind("<Button-1>", self.on_left_button_press)
        self.canvas.bind("<B1-Motion>", self.on_left_button_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_button_release)

    def set_mode_rectangle(self):
        self.mode = "rectangle"
        self.canvas.bind("<Button-1>", self.select_points)
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
