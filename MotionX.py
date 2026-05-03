import customtkinter as ctk
import pickle, zlib, os, time, threading
import numpy as np
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

# =================================================================
# SPAWN.AI MOTIONX ENGINE - 3D EVOLUTION
# =================================================================
def create_ready_lib():
    if not os.path.exists("animations.lib"):
        db = []
        moves = ["Run", "Sprint", "Walk", "Idle", "Jump", "Crouch", "Vault", "Slide", "Takedown"]
        for i in range(1, 5001):
            is_rare = i > 2500
            m = np.random.choice(moves)
            db.append({
                "id": i,
                "name": f"MX_{m.upper()}_{i:04d}",
                "cat": "Standard" if not is_rare else "Tactical/Elite",
                "rare": is_rare,
                "type": m.lower()
            })
        with open("animations.lib", "wb") as f:
            f.write(zlib.compress(pickle.dumps(db)))

class MotionX(ctk.CTk):
    def __init__(self):
        super().__init__()
        create_ready_lib()
        self.title("spawn.ai | MotionX V1.3 - 3D Intelligence")
        self.geometry("1400x900")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#020202")

        with open("animations.lib", "rb") as f:
            self.assets = pickle.loads(zlib.decompress(f.read()))

        self.selected = None
        self.preview_active = False
        self.frame_idx = 0
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=380, fg_color="#080808", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="MOTIONX 3D", font=ctk.CTkFont(size=32, weight="bold"), text_color="#00ff9d").pack(pady=30)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.queue_refresh)
        ctk.CTkEntry(self.sidebar, placeholder_text="Search assets...", textvariable=self.search_var, height=40).pack(fill="x", padx=20)

        self.scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

        # Workspace
        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

        # 3D Viewport
        self.fig = Figure(figsize=(5, 5), dpi=100, facecolor='#020202')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#020202')
        self.canvas_3d = FigureCanvasTkAgg(self.fig, master=self.workspace)
        self.canvas_3d.get_tk_widget().pack(fill="both", expand=True)

        self.title_lbl = ctk.CTkLabel(self.workspace, text="Select Motion Data", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_lbl.pack(pady=20)

        ctk.CTkButton(self.workspace, text="EXPORT FBX", fg_color="#00ff9d", text_color="#000", font=("Inter", 16, "bold"), height=50, command=self.exp).pack()

    def queue_refresh(self, *args):
        # Donmayı engellemek için refresh işlemini geciktiriyoruz
        if hasattr(self, '_timer'): self.after_cancel(self._timer)
        self._timer = self.after(300, self.refresh)

    def refresh(self):
        for w in self.scroll.winfo_children(): w.destroy()
        q, count = self.search_var.get().lower(), 0
        for a in self.assets:
            if q in a["name"].lower():
                color = "#00ff9d" if a["rare"] else "#888"
                ctk.CTkButton(self.scroll, text=a["name"], anchor="w", fg_color="transparent", text_color=color,
                              command=lambda anim=a: self.sel(anim)).pack(fill="x")
                count += 1
                if count > 50: break

    def sel(self, a):
        self.selected = a
        self.title_lbl.configure(text=a["name"])
        if not self.preview_active:
            self.preview_active = True
            self.animate_3d()

    def animate_3d(self):
        if not self.preview_active or not self.selected: return
        
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_xlim(-1, 1); self.ax.set_ylim(-1, 1); self.ax.set_zlim(0, 2)
        
        t = time.time() * 10
        # Basit 3D İnsan İskeleti Simülasyonu
        # Gövde ve Kafa
        self.ax.plot([0, 0], [0, 0], [0.8, 1.5], color='white', lw=3)
        self.ax.scatter([0], [0], [1.6], color='#00ff9d', s=100) # Kafa
        
        # Hareket Mantığı (Koşma/Yürüme)
        offset = np.sin(t) * 0.4
        # Bacaklar
        self.ax.plot([0, offset], [0, 0.5], [0.8, 0], color='#00ff9d', lw=2)
        self.ax.plot([0, -offset], [0, -0.5], [0.8, 0], color='#00ff9d', lw=2)
        # Kollar
        self.ax.plot([0, -offset*0.5], [0, 0.4], [1.3, 0.8], color='white', lw=2)
        self.ax.plot([0, offset*0.5], [0, -0.4], [1.3, 0.8], color='white', lw=2)

        self.canvas_3d.draw_idle()
        self.after(16, self.animate_3d) # ~60 FPS

    def exp(self):
        if self.selected: messagebox.showinfo("BUM!", "3D Motion Data Exported.")

if __name__ == "__main__":
    MotionX().mainloop()