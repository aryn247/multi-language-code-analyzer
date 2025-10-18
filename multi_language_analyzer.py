import ast
import networkx as nx
import matplotlib.pyplot as plt
from radon.complexity import cc_visit
from radon.metrics import mi_visit
import javalang
import esprima
import re  # for simple C/C++ parsing
from io import BytesIO

# ------------------ Python Analysis ------------------
def analyze_python(code):
    try:
        tree = ast.parse(code)
    except Exception as e:
        return {"error": f"Error parsing Python code: {e}"}

    # Maintainability Index
    try:
        mi = round(mi_visit(code, True), 2)
    except Exception:
        mi = "N/A"

    # Cyclomatic Complexity
    functions = cc_visit(code)
    complexities = [(f.name, f.complexity, f.lineno) for f in functions]
    avg_complexity = round(sum(f.complexity for f in functions) / len(functions), 2) if functions else 0

    # Loop detection
    loop_lines = [n.lineno for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While))]
    nested_loops = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            for child in ast.walk(node):
                if isinstance(child, (ast.For, ast.While)) and child != node:
                    nested_loops += 1

    # Function size
    function_sizes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            end = max([n.lineno for n in ast.walk(node) if hasattr(n, 'lineno')], default=start)
            function_sizes.append((node.name, end - start))

    # Dead code detection
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

    # Dependencies
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

    # Time complexity (approx. nested loops)
    time_complexities = []
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
            time_complexities.append((node.name, complexity, node.lineno))

    # Efficiency grade
    if avg_complexity <= 5: efficiency = "A"
    elif avg_complexity <= 10: efficiency = "B"
    elif avg_complexity <= 15: efficiency = "C"
    else: efficiency = "D"

    # Suggestions
    suggestions = []
    if nested_loops > 0: suggestions.append("⚙️ Nested loops detected — consider using data structures or sets for optimization.")
    if sum(1 for l in code.splitlines() if l.strip().startswith("#")) / max(len(code.splitlines()),1)*100 < 5:
        suggestions.append("⚠️ Low comment ratio — add docstrings or comments for maintainability.")
    if mi != "N/A" and mi < 60:
        suggestions.append("❗ Low maintainability — consider refactoring long or complex functions.")
    if unused_vars: suggestions.append(f"⚠️ Unused variables detected: {', '.join(unused_vars)}")
    if unused_funcs: suggestions.append(f"⚙️ Unused functions: {', '.join(unused_funcs)} — consider removing dead code.")
    for name, size in function_sizes:
        if size > 50: suggestions.append(f"⚠️ Function '{name}' is too long ({size} lines) — consider splitting.")
    for name, comp, _ in complexities:
        if comp > 10: suggestions.append(f"❗ Function '{name}' has high cyclomatic complexity ({comp}) — consider refactoring.")

    return {
        "language": "Python",
        "maintainability_index": mi,
        "complexity": complexities,
        "avg_complexity": avg_complexity,
        "loops": len(loop_lines),
        "nested_loops": nested_loops,
        "function_sizes": function_sizes,
        "total_lines": len(code.splitlines()),
        "comment_lines": sum(1 for l in code.splitlines() if l.strip().startswith("#")),
        "comment_ratio": round(sum(1 for l in code.splitlines() if l.strip().startswith("#")) / max(len(code.splitlines()),1)*100,2),
        "function_count": len(function_sizes),
        "largest_function": max(function_sizes, key=lambda x:x[1]) if function_sizes else ("None",0),
        "efficiency_grade": efficiency,
        "suggestions": suggestions,
        "loops_lines": loop_lines,
        "unused_vars": unused_vars,
        "unused_funcs": unused_funcs,
        "dependencies": dependencies,
        "time_complexity": time_complexities
    }

# ------------------ JavaScript Analysis ------------------
def analyze_js(code):
    try:
        tree = esprima.parseScript(code, {"tolerant": True, "loc": True})
    except:
        return {"error": "Error parsing JavaScript code"}

    functions, dependencies = [], {}
    loops, nested_loops = 0, 0
    for node in tree.body:
        if node.type == "FunctionDeclaration":
            functions.append((node.id.name, 1, node.loc.end.line - node.loc.start.line))
            dependencies[node.id.name] = []

    function_sizes = [(f, s) for f, _, s in functions]
    complexities = [(f, c, 0) for f, c, _ in functions]

    return {
        "language": "JavaScript",
        "function_count": len(functions),
        "function_sizes": function_sizes,
        "complexity": complexities,
        "avg_complexity": 0,
        "loops": loops,
        "nested_loops": nested_loops,
        "largest_function": (functions[0][0] if functions else "None",0),
        "dependencies": dependencies,
        "unused_funcs": [],
        "time_complexity": [],
        "suggestions": []
    }

# ------------------ Java Analysis ------------------
def analyze_java(code):
    try:
        tree = javalang.parse.parse(code)
    except:
        return {"error": "Error parsing Java code"}

    methods, dependencies = [], {}
    loops, nested_loops = 0, 0
    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        methods.append((node.name, 1, len(node.body) if node.body else 0))
        dependencies[node.name] = []

    function_sizes = [(m, s) for m, _, s in methods]
    complexities = [(m, c, 0) for m, c, _ in methods]

    return {
        "language": "Java",
        "function_count": len(methods),
        "function_sizes": function_sizes,
        "complexity": complexities,
        "avg_complexity": 0,
        "loops": loops,
        "nested_loops": nested_loops,
        "largest_function": (methods[0][0] if methods else "None",0),
        "dependencies": dependencies,
        "unused_funcs": [],
        "time_complexity": [],
        "suggestions": []
    }

# ------------------ C/C++ Analysis ------------------
def analyze_c_cpp(code, language):
    functions = re.findall(r'\b(?:int|void|char|float|double)\s+(\w+)\s*\(', code)
    loops = re.findall(r'\b(for|while|do)\b', code)
    function_sizes = [(f, 0) for f in functions]
    complexities = [(f, 0, 0) for f in functions]
    dependencies = {f: [] for f in functions}
    for i in range(len(functions)-1):
        dependencies[functions[i]].append(functions[i+1])
    return {
        "language": language,
        "function_count": len(functions),
        "function_sizes": function_sizes,
        "complexity": complexities,
        "avg_complexity": 0,
        "loops": len(loops),
        "nested_loops": 0,
        "largest_function": (functions[0] if functions else "None",0),
        "unused_vars": [],
        "unused_funcs": [],
        "dependencies": dependencies,
        "time_complexity": [],
        "suggestions": ["⚠️ Regex-based analysis used. For accurate results, integrate libclang."]
    }

# ------------------ Generic Analyzer ------------------
def analyze_code(code, lang):
    lang = lang.lower()
    if lang=="python": return analyze_python(code)
    if lang=="java": return analyze_java(code)
    if lang=="js": return analyze_js(code)
    if lang in ["c","cpp"]: return analyze_c_cpp(code, lang)
    return {"error":"Unsupported language"}

# ------------------ Dependency Visualization ------------------
def visualize_dependencies(dependencies):
    if not dependencies:
        print("No function dependencies to display.")
        return
    G = nx.DiGraph(dependencies)
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')  # hierarchical layout
    except:
        pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8,6))
    # Color nodes by number of dependencies
    colors = []
    for node in G.nodes():
        dep_count = len(dependencies.get(node, []))
        if dep_count == 0: colors.append('green')
        elif dep_count <= 2: colors.append('yellow')
        else: colors.append('red')
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=2000,
            font_size=10, arrowsize=20, arrowstyle='-|>')
    plt.title("Function Dependency Graph")
    plt.show()
