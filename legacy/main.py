import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
from multi_language_analyzer import analyze_code, visualize_dependencies
import datetime
import threading
import re  # for cleaning ANSI escape sequences

class CodeAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Language Code Analyzer & Optimizer")
        self.root.geometry("900x700")

        # --- File Selection ---
        file_frame = tk.Frame(root)
        file_frame.pack(pady=5)

        self.file_label = tk.Label(file_frame, text="Select code file:")
        self.file_label.pack(side=tk.LEFT, padx=5)

        self.file_entry = tk.Entry(file_frame, width=60)
        self.file_entry.pack(side=tk.LEFT, padx=5)

        self.browse_btn = tk.Button(file_frame, text="Browse", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, padx=5)

        # --- Language Selection ---
        lang_frame = tk.Frame(root)
        lang_frame.pack(pady=5)

        self.lang_label = tk.Label(lang_frame, text="Select language:")
        self.lang_label.pack(side=tk.LEFT, padx=5)

        self.lang_var = tk.StringVar(value="python")
        self.lang_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=["python", "java", "js", "c", "cpp"],
            state="readonly",
            width=15
        )
        self.lang_dropdown.pack(side=tk.LEFT, padx=5)

        # --- Analyze Button ---
        self.analyze_btn = tk.Button(root, text="Analyze Code", command=self.analyze_code_thread)
        self.analyze_btn.pack(pady=10)

        # --- Scrollable Text Output ---
        self.output_area = scrolledtext.ScrolledText(root, width=100, height=30)
        self.output_area.pack(padx=10, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Select code file")
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def analyze_code_thread(self):
        # Run analysis in a separate thread to avoid freezing the GUI
        thread = threading.Thread(target=self.analyze_code)
        thread.start()

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
        self.output_area.insert(tk.END, f"Language Detected: {result['language']}\n\n")

        # Critical Functions
        critical_funcs = []
        size_lookup = dict(result.get("function_sizes", []))
        for f in result.get("complexity", []):
            name, comp, _ = f if len(f) == 3 else (f[0], 0, 0)
            size_val = size_lookup.get(name, 0)
            if comp > 10 or size_val > 20:
                critical_funcs.append((name, comp, size_val))

        if critical_funcs:
            self.output_area.insert(tk.END, "⚠️ Critical Functions Detected:\n")
            for name, comp, size in critical_funcs:
                self.output_area.insert(tk.END, f" - {name}: complexity={comp}, lines={size}\n")
        else:
            self.output_area.insert(tk.END, "✅ No critical functions detected!\n")

        # Function Complexity Graph
        self.output_area.insert(tk.END, "\n📊 Function Complexity Graph:\n")
        for f in result.get("complexity", []):
            name, comp, _ = f if len(f) == 3 else (f[0], 0, 0)
            bar = "█" * (comp if comp > 0 else 2)
            self.output_area.insert(tk.END, f"{name.ljust(20)} | {bar} {comp}\n")

        # Time Complexity
        self.output_area.insert(tk.END, "\n⏱️ Time Complexity Estimation:\n")
        for name, complexity, _ in result.get("time_complexity", []):
            self.output_area.insert(tk.END, f" - {name}: {complexity}\n")

        # Summary
        self.output_area.insert(tk.END, "\n--- Analysis Report ---\n")
        if result['language'].lower() == "python":
            self.output_area.insert(tk.END, f"Maintainability Index: {result.get('maintainability_index', 0)}\n")
            self.output_area.insert(tk.END, f"Comment Lines: {result.get('comment_lines', 0)} ({result.get('comment_ratio', 0)}%)\n")

        self.output_area.insert(tk.END, f"Average Complexity: {result.get('avg_complexity', 0)}\n")
        self.output_area.insert(tk.END, f"Total Lines: {result.get('total_lines', 0)}\n")
        self.output_area.insert(tk.END, f"Number of Functions: {result.get('function_count', 0)}\n")
        self.output_area.insert(tk.END, f"Largest Function: {result.get('largest_function', ('None', 0))[0]} ({result.get('largest_function', ('None', 0))[1]} lines)\n")
        self.output_area.insert(tk.END, f"Efficiency Grade: {result.get('efficiency_grade', 'A')}\n")
        self.output_area.insert(tk.END, f"Loops Detected: {result.get('loops', 0)}\n")
        self.output_area.insert(tk.END, f"Nested Loops: {result.get('nested_loops', 0)}\n")

        # Dead Code Analysis
        self.output_area.insert(tk.END, "\n🧠 Dead Code Analysis:\n")
        unused_vars = result.get("unused_vars", [])
        unused_funcs = result.get("unused_funcs", [])
        if unused_vars:
            self.output_area.insert(tk.END, f" - Unused Variables: {', '.join(unused_vars)}\n")
        else:
            self.output_area.insert(tk.END, " - No unused variables found!\n")
        if unused_funcs:
            self.output_area.insert(tk.END, f" - Unused Functions: {', '.join(unused_funcs)}\n")
        else:
            self.output_area.insert(tk.END, " - No unused functions found!\n")

        # Suggestions
        self.output_area.insert(tk.END, "\nSuggestions:\n")
        for s in result.get("suggestions", []):
            self.output_area.insert(tk.END, f" - {s}\n")

        # Save report automatically
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_name = f"analysis_report_{timestamp}.txt"
        report_text = self.output_area.get(1.0, tk.END)

        # Clean text (remove ANSI codes) before saving
        clean_text = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', report_text)

        with open(report_name, "w", encoding="utf-8") as report_file:
            report_file.write(clean_text)

        self.output_area.insert(tk.END, f"\n📄 Report saved as: {report_name}\n")

        # Visualize dependencies
        visualize_dependencies(result.get("dependencies", {}))


if __name__ == "__main__":
    root = tk.Tk()
    app = CodeAnalyzerGUI(root)
    root.mainloop()
