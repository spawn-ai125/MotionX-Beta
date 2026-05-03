import customtkinter as ctk
import pickle, zlib, os, time
import numpy as np
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# =================================================================
# SPAWN.AI MOTIONX ENGINE - SKELETON EVOLUTION
# =================================================================
def create_ready_lib():
    if not os.path.exists("animations.lib"):
        db = []
        moves = ["Run", "Sprint", "Walk", "Idle", "Jump", "Slide", "Takedown"]
        for i in range(1, 5001):
            is_rare = i > 2500
            m = np.random.choice(moves)
            db.append({
                "id": i,
                "name": f"MX_{m.upper()}_{i:04d}",
                "cat": "Standard" if not is_rare else "Tactical/Elite",
                "rare": is_rare,
                "type": m.lower() # Kritik: Hareket tipi artık saklanıyor
            })
        with open("animations.lib", "wb") as f:
            f.write(zlib.compress(pickle.dumps(db)))

class MotionX(ctk.CTk):
    def __init__(self):
        super().__init__()
        create_ready_lib()
        self.title("spawn.ai | MotionX V1.4 - Professional Engine")
        self.geometry("1400x900")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#020202")

        with open("animations.lib", "rb") as f:
            self.assets = pickle.loads(zlib.decompress(f.read()))

        self.selected = None
        self.preview_active = False
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=380, fg_color="#080808", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="MOTIONX PRO", font=ctk.CTkFont(size=32, weight="bold"), text_color="#00ff9d").pack(pady=30)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.queue_refresh)
        ctk.CTkEntry(self.sidebar, placeholder_text="Search 5,000+ motions...", textvariable=self.search_var, height=40).pack(fill="x", padx=20)

        self.scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

        # Workspace
        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

        # 3D Viewport
        self.fig = Figure(figsize=(6, 6), dpi=100, facecolor='#020202')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas_3d = FigureCanvasTkAgg(self.fig, master=self.workspace)
        self.canvas_3d.get_tk_widget().pack(fill="both", expand=True)

        self.title_lbl = ctk.CTkLabel(self.workspace, text="Awaiting Selection...", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_lbl.pack(pady=20)

        ctk.CTkButton(self.workspace, text="EXPORT FBX", fg_color="#00ff9d", text_color="#000", font=("Inter", 16, "bold"), height=50, corner_radius=12, command=self.exp).pack()

    def queue_refresh(self, *args):
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
        
        t = time.time() * 8
        m_type = self.selected["type"]

        # --- Hareket Denklemleri ---
        if m_type in ["run", "sprint", "walk"]:
            speed = 1.5 if m_type == "sprint" else (1.0 if m_type == "run" else 0.5)
            swing = np.sin(t * speed) * 0.5
            body_z = 1.2 + np.abs(np.sin(t * speed)) * 0.1 # Koşarken hafif zıplama
            leg_l, leg_r = swing, -swing
            arm_l, arm_r = -swing, swing
        elif m_type == "jump":
            jump_h = np.maximum(0, np.sin(t * 0.5) * 1.5)
            body_z = 1.2 + jump_h
            leg_l, leg_r = 0.2, -0.2
            arm_l, arm_r = 0.8, -0.8
        else: # Idle / Bekleme
            body_z = 1.2 + np.sin(t * 0.2) * 0.02
            leg_l, leg_r = 0.1, -0.1
            arm_l, arm_r = 0.1, -0.1

        # --- Skeleton Rendering ---
        # Omurga ve Kafa
        self.ax.plot([0, 0], [0, 0], [body_z - 0.4, body_z + 0.3], color='white', lw=4)
        self.ax.scatter([0], [0], [body_z + 0.4], color='#00ff9d', s=150) # Kafa

        # Omuz Hattı
        self.ax.plot([-0.3, 0.3], [0, 0], [body_z + 0.2, body_z + 0.2], color='white', lw=2)
        # Kollar
        self.ax.plot([-0.3, -0.3 + arm_l], [0, 0.4], [body_z + 0.2, body_z - 0.3], color='white', lw=2)
        self.ax.plot([0.3, 0.3 + arm_r], [0, -0.4], [body_z + 0.2, body_z - 0.3], color='white', lw=2)

        # Kalça Hattı ve Bacaklar
        hip_z = body_z - 0.4
        self.ax.plot([-0.2, 0.2], [0, 0], [hip_z, hip_z], color='white', lw=2)
        self.ax.plot([-0.2, -0.2 + leg_l], [0, 0.5], [hip_z, np.maximum(0, hip_z - 0.8)], color='#00ff9d', lw=3)
        self.ax.plot([0.2, 0.2 + leg_r], [0, -0.5], [hip_z, np.maximum(0, hip_z - 0.8)], color='#00ff9d', lw=3)

        self.canvas_3d.draw_idle()
        self.after(16, self.animate_3d)

    def exp(self):
        if self.selected: messagebox.showinfo("BUM!", f"{self.selected['name']} Exported.")

if __name__ == "__main__":
    MotionX().mainloop()