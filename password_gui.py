"""Tkinter front end. Run with: python password_gui.py (no pip packages needed)."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor
from password_core import derive_password, validate_inputs


class PasswordApp:
    """Keep widget operations on the main thread and derivation on one worker."""
    def __init__(self, root):
        self.root = root
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.future = None
        root.title("COS738 | Reproducible Password Generator")
        root.geometry("720x480")
        root.minsize(660, 460)
        frame = ttk.Frame(root, padding=24)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text="Reproducible Password Generator",
                  font=("Segoe UI", 18, "bold")).grid(row=0, sticky="w", pady=(0, 10))
        ttk.Label(frame, text="Same memorable input + same length = same result.").grid(row=1, sticky="w")
        self.memorable, self.length, self.output = tk.StringVar(), tk.StringVar(value="24"), tk.StringVar()
        self.status = tk.StringVar(value="Ready. Use demonstration inputs only.")
        ttk.Label(frame, text="Memorable password").grid(row=2, sticky="w", pady=(18, 4))
        self.entry = ttk.Entry(frame, textvariable=self.memorable, show="*", width=65)
        self.entry.grid(row=3, sticky="ew")
        self.visible = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Show input and output", variable=self.visible,
                        command=self.toggle).grid(row=4, sticky="w", pady=5)
        ttk.Label(frame, text="Output length (8 to 128)").grid(row=5, sticky="w")
        ttk.Entry(frame, textvariable=self.length, width=10).grid(row=6, sticky="w", pady=5)
        self.generate_button = ttk.Button(frame, text="Generate password", command=self.generate)
        self.generate_button.grid(row=7, sticky="w", pady=8)
        ttk.Label(frame, text="Generated password").grid(row=8, sticky="w")
        self.result = ttk.Entry(frame, textvariable=self.output, state="readonly", show="*", width=65)
        self.result.grid(row=9, sticky="ew", pady=5)
        buttons = ttk.Frame(frame)
        buttons.grid(row=10, sticky="w", pady=6)
        ttk.Button(buttons, text="Copy", command=self.copy).pack(side="left")
        ttk.Button(buttons, text="Save to file", command=self.save).pack(side="left", padx=8)
        ttk.Button(buttons, text="Clear", command=self.clear).pack(side="left")
        ttk.Label(frame, textvariable=self.status, wraplength=650).grid(row=11, sticky="w", pady=5)
        ttk.Label(frame, text="Educational demo: weak inputs remain guessable. Saved files are plaintext.",
                  wraplength=650).grid(row=12, sticky="w", pady=5)
        self.memorable.trace_add("write", self.invalidate)
        self.length.trace_add("write", self.invalidate)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.entry.focus_set()

    def invalidate(self, *_):
        self.output.set("")
        self.status.set("Inputs changed. Generate a fresh result.")

    def toggle(self):
        for widget in (self.entry, self.result):
            widget.configure(show="" if self.visible.get() else "*")

    def generate(self):
        if self.future is not None:
            return
        self.output.set("")
        try:
            text = self.length.get()
            if not text.isascii() or not text.isdecimal():
                raise ValueError("Output length must be a whole number from 8 to 128.")
            self.input_text = (self.memorable.get(), text)
            self.inputs = (self.input_text[0], int(text))
            validate_inputs(*self.inputs)
        except ValueError as error:
            self.status.set(str(error))
            messagebox.showerror("Invalid input", str(error))
            return
        self.generate_button.configure(state="disabled")
        self.status.set("Generating...")
        self.future = self.pool.submit(derive_password, *self.inputs)
        self.root.after(50, self.poll)

    def poll(self):
        if not self.future.done():
            self.root.after(50, self.poll)
            return
        try:
            result = self.future.result()
            if (self.memorable.get(), self.length.get()) == self.input_text:
                self.output.set(result)
                self.status.set(f"Generated {len(result)} characters with all four character types.")
            else:
                self.status.set("Inputs changed during generation. Generate again.")
        except Exception:
            self.status.set("Generation failed. Try again.")
            messagebox.showerror("Generation failed", "Unable to derive a password. Try again.")
        finally:
            self.future = None
            self.generate_button.configure(state="normal")

    def copy(self):
        if not self.output.get():
            self.status.set("Generate a password before copying.")
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.output.get())
            self.status.set("Copied. Clipboard history may retain this password.")
        except tk.TclError:
            self.status.set("Clipboard unavailable. You can save instead.")

    def save(self):
        if not self.output.get():
            self.status.set("Generate a password before saving.")
            return
        if not messagebox.askyesno("Plaintext file", "The file will contain an unencrypted password. Continue?"):
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not path:
            self.status.set("Save cancelled.")
            return
        try:
            with open(path, "w", encoding="utf-8") as output_file:
                output_file.write(self.output.get())
            self.status.set("Password saved to the selected file.")
        except OSError:
            self.status.set("Save failed. Check the destination and permissions, then retry.")
            messagebox.showerror("Save failed", self.status.get())

    def clear(self):
        self.memorable.set("")
        self.output.set("")
        self.visible.set(False)
        self.toggle()
        self.status.set("Fields cleared. Clipboard and saved files are unchanged.")

    def close(self):
        self.pool.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()


if __name__ == "__main__":
    app_root = tk.Tk()
    PasswordApp(app_root)
    app_root.mainloop()
