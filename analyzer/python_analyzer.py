import ast
from radon.complexity import cc_visit
from radon.metrics import mi_visit
import networkx as nx
import matplotlib.pyplot as plt

# --- Top-level function: estimate time complexity ---
def estimate_time_complexity(code):
    """Estimate time complexity per function based on loop depth."""
    tree = ast.parse(code)
    complexities_list = []

    class LoopVisitor(ast.NodeVisitor):
        def __init__(self):
            self.max_depth = 0
            self.current_depth = 0

        def visit_For(self, node):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1

        def visit_While(self, node):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            visitor = LoopVisitor()
            visitor.visit(node)
            depth = visitor.max_depth
            if depth == 0:
                complexity = "O(1)"
            elif depth == 1:
                complexity = "O(n)"
            elif depth == 2:
                complexity = "O(n²)"
            else:
                complexity = f"O(n^{depth})"
            complexities_list.append((node.name, complexity, node.lineno))
    return complexities_list

# --- Main analyzer ---
def analyze_python_code(code):
    try:
        tree = ast.parse(code)
    except Exception as e:
        return {"error": f"Error parsing Python code: {e}"}

    # --- Maintainability Index ---
    try:
        mi = round(mi_visit(code, True), 2)
    except Exception:
        mi = "N/A"

    # --- Cyclomatic Complexity ---
    functions = cc_visit(code)
    complexities = [(f.name, f.complexity, f.lineno) for f in functions]
    avg_complexity = round(sum(f.complexity for f in functions) / len(functions), 2) if functions else 0

    # --- Loop detection ---
    loop_lines = [n.lineno for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While))]
    nested_loops = sum(
        isinstance(p, (ast.For, ast.While)) and any(isinstance(c, (ast.For, ast.While)) for c in ast.walk(p))
        for p in ast.walk(tree)
    )

    # --- Function size calculation ---
    function_sizes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            end = max([n.lineno for n in ast.walk(node) if hasattr(n, 'lineno')], default=start)
            function_sizes.append((node.name, end - start))

    total_lines = len(code.splitlines())
    comment_lines = sum(1 for l in code.splitlines() if l.strip().startswith("#"))
    comment_ratio = round((comment_lines / total_lines) * 100, 2) if total_lines else 0

    # --- Efficiency grade ---
    if avg_complexity <= 5:
        efficiency = "A"
    elif avg_complexity <= 10:
        efficiency = "B"
    elif avg_complexity <= 15:
        efficiency = "C"
    else:
        efficiency = "D"

    # --- Dead Code Detection ---
    assigned_vars, used_vars = set(), set()
    defined_funcs, called_funcs = set(), set()

    class UsageAnalyzer(ast.NodeVisitor):
        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned_vars.add(target.id)
            self.generic_visit(node)

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Load):
                used_vars.add(node.id)
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            defined_funcs.add(node.name)
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                called_funcs.add(node.func.id)
            self.generic_visit(node)

    UsageAnalyzer().visit(tree)
    unused_vars = sorted(list(assigned_vars - used_vars))
    unused_funcs = sorted(list(defined_funcs - called_funcs))

    # --- Function dependencies ---
    dependencies = {}
    class DependencyAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.current_func = None
        def visit_FunctionDef(self, node):
            self.current_func = node.name
            dependencies[self.current_func] = []
            self.generic_visit(node)
            self.current_func = None
        def visit_Call(self, node):
            if self.current_func and isinstance(node.func, ast.Name):
                dependencies[self.current_func].append(node.func.id)
            self.generic_visit(node)

    DependencyAnalyzer().visit(tree)

    # --- Refactoring suggestions ---
    suggestions = []
    if nested_loops > 0:
        suggestions.append("⚙️ Nested loops detected — consider using data structures or sets for optimization.")
    if comment_ratio < 5:
        suggestions.append("⚠️ Low comment ratio — add docstrings or comments for maintainability.")
    if mi != "N/A" and mi < 60:
        suggestions.append("❗ Low maintainability — consider refactoring long or complex functions.")
    if unused_vars:
        suggestions.append(f"⚠️ Unused variables detected: {', '.join(unused_vars)}")
    if unused_funcs:
        suggestions.append(f"⚙️ Unused functions: {', '.join(unused_funcs)} — consider removing dead code.")
    for name, size in function_sizes:
        if size > 50:
            suggestions.append(f"⚠️ Function '{name}' is too long ({size} lines) — consider splitting.")
    for name, comp, _ in complexities:
        if comp > 10:
            suggestions.append(f"❗ Function '{name}' has high cyclomatic complexity ({comp}) — consider refactoring.")

    # --- Time Complexity Estimation ---
    time_complexities = estimate_time_complexity(code)

    return {
        "maintainability_index": mi,
        "complexity": complexities,
        "avg_complexity": avg_complexity,
        "loops": len(loop_lines),
        "nested_loops": nested_loops,
        "function_sizes": function_sizes,
        "total_lines": total_lines,
        "comment_lines": comment_lines,
        "comment_ratio": comment_ratio,
        "function_count": len(function_sizes),
        "largest_function": max(function_sizes, key=lambda x: x[1]) if function_sizes else ("None", 0),
        "efficiency_grade": efficiency,
        "suggestions": suggestions,
        "loops_lines": loop_lines,
        "unused_vars": unused_vars,
        "unused_funcs": unused_funcs,
        "dependencies": dependencies,
        "time_complexity": time_complexities
    }

# --- Optional: Visualize function dependencies ---
def visualize_dependencies(dependencies):
    if not dependencies:
        print("No function dependencies to display.")
        return
    G = nx.DiGraph(dependencies)
    plt.figure(figsize=(10, 7))
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=2500, font_size=10, arrowsize=20)
    plt.title("Function Dependency Graph")
    plt.show()

# --- Example usage ---
if __name__ == "__main__":
    filepath = input("Enter path to Python file: ")
    with open(filepath, "r") as f:
        code = f.read()
    result = analyze_python_code(code)

    # Print a summary
    print("\n--- Analysis Summary ---")
    print(f"Maintainability Index: {result['maintainability_index']}")
    print(f"Average Cyclomatic Complexity: {result['avg_complexity']}")
    print(f"Nested Loops: {result['nested_loops']}")
    print(f"Function Count: {result['function_count']}")
    print(f"Efficiency Grade: {result['efficiency_grade']}")
    print("Suggestions:")
    for s in result["suggestions"]:
        print(f" - {s}")

    # Print time complexity per function
    print("\nTime Complexity Estimates:")
    for func, tc, line in result["time_complexity"]:
        print(f" - Function '{func}' (line {line}): {tc}")

    # Visualize dependencies
    visualize_dependencies(result["dependencies"])
