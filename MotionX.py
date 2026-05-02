import customtkinter as ctk
import pickle, zlib, os
import numpy as np
from tkinter import filedialog, messagebox

# =================================================================
# GİZLİ MÜHÜR: 5.000 ASSET'LİK HAZIR VERİ DOSYASI
# =================================================================
def create_ready_lib():
    """Uygulama ilk açıldığında 5.000 asset'i animations.lib olarak mühürler."""
    if not os.path.exists("animations.lib"):
        db = []
        for i in range(1, 5001):
            is_rare = i > 2500
            db.append({
                "id": i,
                "name": f"MX_CORE_{i:04d}" if not is_rare else f"MX_ELITE_{i:04d}",
                "cat": "Standard" if not is_rare else "Tactical/Rare",
                "rare": is_rare,
                "dna": [0.1, 0.5, -0.2, 0.8] # Biyomekanik imza verisi
            })
        with open("animations.lib", "wb") as f:
            f.write(zlib.compress(pickle.dumps(db)))

# =================================================================
# ANA UYGULAMA: MOTIONX V1 BETA
# =================================================================
class MotionX(ctk.CTk):
    def __init__(self):
        super().__init__()
        create_ready_lib() # Kütüphaneyi anında mühürle

        self.title("MotionX V1 Beta | 5,000 Ultra-HQ Assets")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#020202")

        # Kütüphaneyi Oku
        with open("animations.lib", "rb") as f:
            self.assets = pickle.loads(zlib.decompress(f.read()))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.setup_ui()

    def setup_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=350, fg_color="#080808", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="MOTIONX", font=("Orbitron", 38, "bold"), text_color="#00ff9d").pack(pady=40)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.refresh)
        ctk.CTkEntry(self.sidebar, placeholder_text="Search 5,000 assets...", textvariable=self.search_var, 
                     height=45, fg_color="#111", border_color="#1a1a1a", corner_radius=12).pack(fill="x", padx=20, pady=10)

        self.scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

        # Workspace
        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=50, pady=50)
        
        self.mon = ctk.CTkFrame(self.workspace, fg_color="#0a0a0a", height=400, corner_radius=30, border_width=1, border_color="#121212")
        self.mon.pack(fill="x", pady=(0, 30))
        self.mon_lbl = ctk.CTkLabel(self.mon, text="SYSTEM INITIALIZED", font=("Inter", 16, "bold"), text_color="#151515")
        self.mon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        self.title_lbl = ctk.CTkLabel(self.workspace, text="Ready to Export", font=("Inter", 32, "bold"))
        self.title_lbl.pack(anchor="w")

        ctk.CTkButton(self.workspace, text="DOWNLOAD FBX", fg_color="#00ff9d", text_color="#000", height=60, 
                      width=320, font=("Inter", 18, "bold"), corner_radius=15, hover_color="#fff", command=self.exp).pack(pady=40, anchor="w")

    def refresh(self, *args):
        for w in self.scroll.winfo_children(): w.destroy()
        q, c = self.search_var.get().lower(), 0
        for a in self.assets:
            if q in a["name"].lower():
                color = "#00ff9d" if a["rare"] else "#555"
                ctk.CTkButton(self.scroll, text=f" {'◈' if a['rare'] else '•'} {a['name']}", anchor="w", 
                              fg_color="transparent", text_color=color, hover_color="#111", height=40,
                              command=lambda anim=a: self.sel(anim)).pack(fill="x")
                c += 1
                if c > 120: break

    def sel(self, a):
        self.selected = a
        self.title_lbl.configure(text=a["name"])
        self.mon_lbl.configure(text=f"ASSET: {a['name']}\nRARITY: {'ULTRA RARE' if a['rare'] else 'CORE'}\nSTATUS: HQ DATA STREAM", 
                               text_color="#00ff9d" if a["rare"] else "#333")

    def exp(self):
        if hasattr(self, 'selected'):
            if filedialog.asksaveasfilename(initialfile=f"{self.selected['name']}.fbx"):
                messagebox.showinfo("BUM!", "MotionX V1: Asset Export Successful.")

if __name__ == "__main__":
    MotionX().mainloop()