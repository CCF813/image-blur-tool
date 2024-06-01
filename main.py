import tkinter as tk
from image_blur_tool import ImageBlurTool

# 初始化tkinter視窗
root = tk.Tk()
root.title("Select Areas to Blur")

# 創建 ImageBlurTool 實例
blur_tool = ImageBlurTool(root)

root.mainloop()
