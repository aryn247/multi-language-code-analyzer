import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
from multi_language_analyzer import analyze_code, visualize_dependencies
import datetime
import threading

# Helper: color codes for Tkinter Text widget
COLORS = {
    "good": "green",
    "warn": "orange",
    "bad": "red",
    "info": "black"
}

class CodeAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Language Code Analyzer & Optimizer")
        self.root.geometry("950x750")

        # --- File Selection ---
        self.file_label = tk.Label(root, text="Select code file:")
        self.file_label.pack(pady=5)
        self.file_frame = tk.Frame(root)
        self.file_frame.pack()
        self.file_entry = tk.Entry(self.file_frame, width=70)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        self.browse_btn = tk.Button(self.file_frame, text="Browse", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, padx=5)

        # --- Language Selection ---
        self.lang_label = tk.Label(root, text="Select language:")
        self.lang_label.pack(pady=5)
        self.lang_var = tk.StringVar(value="python")
        self.lang_dropdown = ttk.Combobox(root, textvariable=self.lang_var, values=["python","java","js"], state="readonly")
        self.lang_dropdown.pack(pady=5)

        # --- Analyze Button ---
        self.analyze_btn = tk.Button(root, text="Analyze Code", command=self.analyze_code_thread)
        self.analyze_btn.pack(pady=10)

        # --- Scrollable Text Output ---
        self.output_area = scrolledtext.ScrolledText(root, width=110, height=35)
        self.output_area.pack(padx=10, pady=10)
        # Add tags for colors
        for k,v in COLORS.items():
            self.output_area.tag_configure(k, foreground=v)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Select code file")
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def analyze_code_thread(self):
        thread = threading.Thread(target=self.analyze_code)
        thread.start()

    def color_text(self, text, level="info"):
        self.output_area.insert(tk.END, text, level)

    def analyze_code(self):
        path = self.file_entry.get()
        lang = self.lang_var.get()
        if not path:
            messagebox.showerror("Error", "Please select a file!")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read file: {e}")
            return

        result = analyze_code(code, lang)
        if "error" in result:
            messagebox.showerror("Error", result["error"])
            return

        self.output_area.delete(1.0, tk.END)
        self.color_text(f"Language Detected: {result['language']}\n\n", "info")

        # --- Critical Functions ---
        critical_funcs = []
        size_lookup = dict(result.get("function_sizes", []))
        for f in result.get("complexity", []):
            name, comp, _ = f if len(f)==3 else (f[0],0,0)
            size_val = size_lookup.get(name,0)
            if comp > 10 or size_val > 20:
                critical_funcs.append((name, comp, size_val))

        if critical_funcs:
            self.color_text("⚠️ Critical Functions Detected:\n", "bad")
            for name, comp, size in critical_funcs:
                self.color_text(f" - {name}: complexity={comp}, lines={size}\n", "bad")
        else:
            self.color_text("✅ No critical functions detected!\n", "good")

        # --- Function Complexity Graph ---
        self.color_text("\n📊 Function Complexity Graph:\n", "info")
        for f in result.get("complexity", []):
            name, comp, _ = f if len(f)==3 else (f[0],0,0)
            bar = "█" * (comp if comp > 0 else 2)
            if comp <= 5:
                color = "good"
            elif comp <= 10:
                color = "warn"
            else:
                color = "bad"
            self.color_text(f"{name.ljust(20)} | ", "info")
            self.color_text(bar, color)
            self.color_text(f" {comp}\n", "info")

        # --- Time Complexity Estimation ---
        if result['language'].lower() == "python":
            self.color_text("\n⏱️ Time Complexity Estimation:\n", "info")
            for name, complexity, _ in result.get("time_complexity", []):
                self.color_text(f" - {name}: {complexity}\n", "info")

        # --- Summary ---
        self.color_text("\n--- Analysis Report ---\n", "info")
        if result['language'].lower() == "python":
            mi = result.get("maintainability_index",0)
            mi_level = "good" if mi >=80 else "warn" if mi >=60 else "bad"
            self.color_text(f"Maintainability Index: {mi}\n", mi_level)
            self.color_text(f"Comment Lines: {result.get('comment_lines',0)} ({result.get('comment_ratio',0)}%)\n", "info")
        self.color_text(f"Average Complexity: {result.get('avg_complexity',0)}\n", "info")
        self.color_text(f"Total Lines: {result.get('total_lines',0)}\n", "info")
        self.color_text(f"Number of Functions: {result.get('function_count',0)}\n", "info")
        self.color_text(f"Largest Function: {result.get('largest_function',('None',0))[0]} ({result.get('largest_function',('None',0))[1]} lines)\n", "info")
        self.color_text(f"Efficiency Grade: {result.get('efficiency_grade','A')}\n", "info")
        self.color_text(f"Loops Detected: {result.get('loops',0)}\n", "info")
        self.color_text(f"Nested Loops: {result.get('nested_loops',0)}\n", "info")

        # --- Dead Code Analysis ---
        self.color_text("\n🧠 Dead Code Analysis:\n", "info")
        unused_vars = result.get("unused_vars", [])
        unused_funcs = result.get("unused_funcs", [])
        if unused_vars:
            self.color_text(f" - Unused Variables: {', '.join(unused_vars)}\n", "warn")
        else:
            self.color_text(" - No unused variables found!\n", "good")
        if unused_funcs:
            self.color_text(f" - Unused Functions: {', '.join(unused_funcs)}\n", "warn")
        else:
            self.color_text(" - No unused functions found!\n", "good")

        # --- Suggestions ---
        self.color_text("\nSuggestions:\n", "info")
        for s in result.get("suggestions", []):
            if '❗' in s or '⚠️' in s:
                color = "bad"
            elif '⚙️' in s:
                color = "warn"
            else:
                color = "good"
            self.color_text(f" - {s}\n", color)

        # --- Save report ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_name = f"analysis_report_{timestamp}.txt"
        with open(report_name,"w",encoding="utf-8") as report_file:
            report_file.write(self.output_area.get(1.0, tk.END))
        self.color_text(f"\n📄 Report saved as: {report_name}\n", "info")

        # --- Optional: visualize dependencies ---
        visualize_dependencies(result.get("dependencies", {}))


if __name__ == "__main__":
    root = tk.Tk()
    app = CodeAnalyzerGUI(root)
    root.mainloop()
