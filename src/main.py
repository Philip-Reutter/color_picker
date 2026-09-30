import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class RGBPicker:
    def __init__(self, root, image_path=None):
        self.root = root
        self.root.title("RGB Color Picker")
        self.root.configure(bg="#1a1a1a")
        self.saved_colors = []

        top = tk.Frame(root, bg="#1a1a1a")
        top.pack(fill="x", padx=10, pady=(10, 0))

        tk.Button(
            top, text="Open Image", command=self.open_image,
            bg="#333", fg="white", relief="flat", padx=12, pady=6,
            cursor="hand2", font=("Courier", 11, "bold")
        ).pack(side="left")

        tk.Button(
            top, text="Save Colors (txt)", command=self.save_colors,
            bg="#333", fg="white", relief="flat", padx=12, pady=6,
            cursor="hand2", font=("Courier", 11, "bold")
        ).pack(side="left", padx=(8, 0))

        self.status = tk.Label(
            top, text="Open an image to begin",
            bg="#1a1a1a", fg="#888", font=("Courier", 11)
        )
        self.status.pack(side="right")

        self.canvas = tk.Canvas(root, bg="#111", cursor="crosshair",
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        info = tk.Frame(root, bg="#222", pady=10)
        info.pack(fill="x", padx=10, pady=(0, 10))

        self.swatch = tk.Label(info, text="  ", bg="#1a1a1a",
                               width=6, relief="flat")
        self.swatch.pack(side="left", padx=(16, 12))

        self.rgb_label = tk.Label(
            info, text="RGB: —", bg="#222", fg="white",
            font=("Courier", 14, "bold")
        )
        self.rgb_label.pack(side="left")

        self.hex_label = tk.Label(
            info, text="HEX: —", bg="#222", fg="#aaa",
            font=("Courier", 14)
        )
        self.hex_label.pack(side="left", padx=(20, 0))

        self.pos_label = tk.Label(
            info, text="X: —  Y: —", bg="#222", fg="#666",
            font=("Courier", 11)
        )
        self.pos_label.pack(side="right", padx=16)

        self.click_hint = tk.Label(
            info, text="Click to save color", bg="#222", fg="#555",
            font=("Courier", 10)
        )
        self.click_hint.pack(side="right", padx=4)

        self.pil_image = None
        self.tk_image = None
        self.img_offset = (0, 0)

        # Bindings
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", self.on_resize)
        root.bind("<q>", lambda e: root.destroy())
        root.bind("<Escape>", lambda e: root.destroy())

        if image_path:
            self.load_image(image_path)

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff"),
                       ("All files", "*.*")]
        )
        if path:
            self.load_image(path)

    def load_image(self, path):
        try:
            self.pil_image = Image.open(path).convert("RGB")
            self.root.title(f"RGB Color Picker — {path.split('/')[-1]}")
            self.status.config(text=f"{self.pil_image.width}×{self.pil_image.height}px")
            self.render_image()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image:\n{e}")

    def render_image(self):
        if self.pil_image is None:
            return
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 600
        img = self.pil_image.copy()
        img.thumbnail((cw, ch), Image.LANCZOS)
        self.display_image = img
        self.tk_image = ImageTk.PhotoImage(img)
        # Centre on canvas
        ox = (cw - img.width) // 2
        oy = (ch - img.height) // 2
        self.img_offset = (ox, oy)
        self.canvas.delete("all")
        self.canvas.create_image(ox, oy, anchor="nw", image=self.tk_image)

    def on_resize(self, event):
        self.render_image()

    def canvas_to_image(self, cx, cy):
        """Convert canvas coords → original image pixel coords."""
        ox, oy = self.img_offset
        dx = cx - ox
        dy = cy - oy
        if self.display_image is None or self.pil_image is None:
            return None, None
        scale_x = self.pil_image.width / self.display_image.width
        scale_y = self.pil_image.height / self.display_image.height
        px = int(dx * scale_x)
        py = int(dy * scale_y)
        if 0 <= px < self.pil_image.width and 0 <= py < self.pil_image.height:
            return px, py
        return None, None

    def on_mouse_move(self, event):
        if self.pil_image is None:
            return
        px, py = self.canvas_to_image(event.x, event.y)
        if px is None:
            return
        r, g, b = self.pil_image.getpixel((px, py))
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        # Update labels
        self.rgb_label.config(text=f"RGB: {r:3d}, {g:3d}, {b:3d}")
        self.hex_label.config(text=f"HEX: {hex_color}")
        self.pos_label.config(text=f"X: {px}  Y: {py}")
        self.swatch.config(bg=hex_color)

    def on_click(self, event):
        if self.pil_image is None:
            return
        px, py = self.canvas_to_image(event.x, event.y)
        if px is None:
            return
        r, g, b = self.pil_image.getpixel((px, py))
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        entry = f"RGB({r:3d},{g:3d},{b:3d})  HEX {hex_color}  @ ({px},{py})"
        self.saved_colors.append(entry)
        self.status.config(text=f"Saved: {hex_color}  ({len(self.saved_colors)} total)")
        self.canvas.config(highlightthickness=2, highlightbackground=hex_color)
        self.root.after(300, lambda: self.canvas.config(highlightthickness=0))

    def save_colors(self):
        if not self.saved_colors:
            messagebox.showinfo("Nothing saved", "Click on pixels first to save colors.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")],
            initialfile="colors.txt"
        )
        if path:
            with open(path, "w") as f:
                f.write("\n".join(self.saved_colors) + "\n")
            messagebox.showinfo("Saved", f"{len(self.saved_colors)} colors saved to:\n{path}")

def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    root.geometry("900x650")
    root.minsize(500, 400)
    app = RGBPicker(root, image_path)
    root.mainloop()


if __name__ == "__main__":
    main()
