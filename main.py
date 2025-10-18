import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
from multi_language_analyzer import analyze_code, visualize_dependencies
import threading

class CodeAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Language Code Analyzer")
        self.root.geometry("900x600")

        # Language selection
        self.lang_var = tk.StringVar(value="python")
        languages = ["Python", "Java", "JavaScript", "C", "C++"]
        tk.Label(root, text="Select Language:").pack(anchor="nw", padx=10, pady=5)
        self.lang_menu = ttk.Combobox(root, values=languages, textvariable=self.lang_var, state="readonly")
        self.lang_menu.pack(anchor="nw", padx=10)

        # Code input area
        tk.Label(root, text="Paste your code here:").pack(anchor="nw", padx=10, pady=5)
        self.code_area = scrolledtext.ScrolledText(root, width=100, height=20)
        self.code_area.pack(padx=10, pady=5)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Analyze Code", command=self.run_analysis).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Load File", command=self.load_file).pack(side="left", padx=5)

        # Output area
        tk.Label(root, text="Analysis Output:").pack(anchor="nw", padx=10, pady=5)
        self.output_area = scrolledtext.ScrolledText(root, width=100, height=15, state="disabled")
        self.output_area.pack(padx=10, pady=5)

    def load_file(self):
        file_path = filedialog.askopenfilename(title="Select Code File",
                                               filetypes=(("All files", "*.*"),))
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.code_area.delete(1.0, tk.END)
                self.code_area.insert(tk.END, f.read())

            # Auto-detect language from extension
            ext = file_path.split(".")[-1].lower()
            if ext in ["py", "java", "js", "c", "cpp"]:
                if ext == "cpp": ext = "c++"
                self.lang_var.set(ext.capitalize())

    def run_analysis(self):
        code = self.code_area.get(1.0, tk.END)
        lang = self.lang_var.get().lower()

        if not code.strip():
            messagebox.showwarning("Warning", "Please enter some code to analyze.")
            return

        # Run analysis in separate thread
        threading.Thread(target=self.analyze_thread, args=(code, lang), daemon=True).start()

    def analyze_thread(self, code, lang):
        try:
            result = analyze_code(code, lang)
        except Exception as e:
            result = {"error": str(e)}

        # Update output in main thread
        self.output_area.after(0, lambda: self.display_result(result))

        # Visualize dependencies in main thread
        self.output_area.after(0, lambda: visualize_dependencies(result.get("dependencies", {})))

    def display_result(self, result):
        self.output_area.config(state="normal")
        self.output_area.delete(1.0, tk.END)

        if "error" in result:
            self.output_area.insert(tk.END, f"Error: {result['error']}\n")
        else:
            for key, value in result.items():
                self.output_area.insert(tk.END, f"{key}: {value}\n")

        self.output_area.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeAnalyzerGUI(root)
    root.mainloop()
