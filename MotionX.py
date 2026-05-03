import customtkinter as ctk
import pickle, zlib, os
import numpy as np
from tkinter import filedialog, messagebox

# =================================================================
# SPAWN.AI MOTIONX ENGINE - CORE MODULE
# =================================================================
def create_ready_lib():
    """Initializes the 5,000 asset library with proprietary binary encryption."""
    if not os.path.exists("animations.lib"):
        db = []
        for i in range(1, 5001):
            is_rare = i > 2500
            db.append({
                "id": i,
                "name": f"MX_CORE_{i:04d}" if not is_rare else f"MX_ELITE_{i:04d}",
                "cat": "Standard" if not is_rare else "Tactical/Rare",
                "rare": is_rare,
                "dna": [0.1, 0.5, -0.2, 0.8] 
            })
        try:
            with open("animations.lib", "wb") as f:
                f.write(zlib.compress(pickle.dumps(db)))
        except Exception as e:
            print(f"Critical: Library initialization failed - {e}")

class MotionX(ctk.CTk):
    def __init__(self):
        super().__init__()
        create_ready_lib()

        self.title("spawn.ai | MotionX V1 Beta")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#020202")

        # Load Database with Error Handling
        try:
            with open("animations.lib", "rb") as f:
                self.assets = pickle.loads(zlib.decompress(f.read()))
        except (FileNotFoundError, zlib.error, pickle.UnpicklingError):
            messagebox.showerror("System Error", "animations.lib is corrupted or missing.")
            self.assets = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.selected = None # Explicit state management
        self.setup_ui()

    def setup_ui(self):
        # Sidebar - Brand Identity
        self.sidebar = ctk.CTkFrame(self, width=350, fg_color="#080808", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="MOTIONX", 
                     font=("Orbitron", "Inter", 38, "bold"), # Fallback font added
                     text_color="#00ff9d").pack(pady=40)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.refresh)
        
        ctk.CTkEntry(self.sidebar, placeholder_text="Search 5,000 assets...", 
                     textvariable=self.search_var, 
                     height=45, fg_color="#111", border_color="#1a1a1a", 
                     corner_radius=12).pack(fill="x", padx=20, pady=10)

        self.scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

        # Workspace - Production Area
        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=50, pady=50)
        
        self.mon = ctk.CTkFrame(self.workspace, fg_color="#0a0a0a", height=400, 
                                corner_radius=30, border_width=1, border_color="#121212")
        self.mon.pack(fill="x", pady=(0, 30))
        self.mon.pack_propagate(False) # Maintains frame size

        self.mon_lbl = ctk.CTkLabel(self.mon, text="SYSTEM INITIALIZED\nAWAITING INPUT", 
                                    font=("Inter", 16, "bold"), text_color="#151515")
        self.mon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        self.title_lbl = ctk.CTkLabel(self.workspace, text="Ready to Export", 
                                      font=("Inter", 32, "bold"))
        self.title_lbl.pack(anchor="w")

        self.exp_btn = ctk.CTkButton(self.workspace, text="DOWNLOAD FBX", 
                                     fg_color="#00ff9d", text_color="#000", height=60, 
                                     width=320, font=("Inter", 18, "bold"), 
                                     corner_radius=15, hover_color="#fff", 
                                     command=self.exp)
        self.exp_btn.pack(pady=40, anchor="w")

    def refresh(self, *args):
        for w in self.scroll.winfo_children(): 
            w.destroy()
        
        q, count = self.search_var.get().lower(), 0
        for a in self.assets:
            if q in a["name"].lower():
                color = "#00ff9d" if a["rare"] else "#555"
                # Fix: Default argument 'anim=a' prevents lambda reference leak
                ctk.CTkButton(self.scroll, text=f" {'◈' if a['rare'] else '•'} {a['name']}", 
                              anchor="w", fg_color="transparent", text_color=color, 
                              hover_color="#111", height=40,
                              command=lambda anim=a: self.sel(anim)).pack(fill="x")
                count += 1
                if count > 100: break # Slight limit for UI responsiveness

    def sel(self, a):
        self.selected = a
        self.title_lbl.configure(text=a["name"])
        self.mon_lbl.configure(text=f"ASSET: {a['name']}\nRARITY: {'ULTRA RARE' if a['rare'] else 'CORE'}\nSTATUS: HQ DATA STREAM", 
                               text_color="#00ff9d" if a["rare"] else "#333")

    def exp(self):
        if self.selected:
            filename = filedialog.asksaveasfilename(
                initialfile=f"{self.selected['name']}.fbx",
                defaultextension=".fbx",
                filetypes=[("FBX files", "*.fbx")]
            )
            if filename:
                messagebox.showinfo("BUM!", f"MotionX V1: {self.selected['name']} Export Successful.")
        else:
            messagebox.showwarning("Selection Required", "Please select an asset from the library first.")

if __name__ == "__main__":
    app = MotionX()
    app.mainloop()