import matplotlib.pyplot as plt
import numpy as np

# 設置圖形的大小
fig, ax = plt.subplots(figsize=(6, 6))

# 繪製背景
ax.set_facecolor('#f0f0f0')
circle = plt.Circle((0.5, 0.5), 0.4, color='blue', fill=True)
ax.add_artist(circle)

# 繪製文字
plt.text(0.5, 0.6, 'Blur', color='white', fontsize=80, ha='center', va='center', fontweight='bold')
plt.text(0.5, 0.35, 'Tool', color='white', fontsize=80, ha='center', va='center', fontweight='bold')

# 移除坐標軸
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# 保存圖像
plt.savefig('logo.png', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.show()
