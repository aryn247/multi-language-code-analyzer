import ast
from unicodedata import name
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
    comment_ratio = sum(1 for l in code.splitlines() if l.strip().startswith("#")) / max(len(code.splitlines()), 1) * 100
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
        "comment_ratio": round(comment_ratio, 2),
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
        "largest_function": (functions[0][0] if functions else "None", 0),
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
        "largest_function": (methods[0][0] if methods else "None", 0),
        "dependencies": dependencies,
        "unused_funcs": [],
        "time_complexity": [],
        "suggestions": []
    }

# ------------------ C/C++ Analysis ------------------

def analyze_c_cpp(code, language):
    """
    Improved regex-based C/C++ analyzer (best-effort).
    - Finds function definitions and their bodies
    - Computes lines per function
    - Counts loops and nested loop depth per function
    - Produces simple dependencies (sequential link) for visualization
    Note: still heuristic; libclang is recommended for full accuracy.
    """
    lines = code.splitlines()
    total_lines = len(lines)

    # Regex to find probable function definitions (avoid prototypes ending with ;)
    func_def_re = re.compile(
        r'([a-zA-Z_][\w\*\s\<\>\:]*?)'    # return type (approx)
        r'\s+([a-zA-Z_]\w*)'              # function name (capture)
        r'\s*\([^;{]*\)\s*'               # params (no ; or { inside)
        r'\{',                            # opening brace of function body
        re.MULTILINE
    )

    functions = []
    for m in func_def_re.finditer(code):
        name = m.group(2)
        start_pos = m.end() - 1
        brace_count, idx, n = 0, start_pos, len(code)
        while idx < n:
            ch = code[idx]
            if ch == '{':
                brace_count += 1
            elif ch == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = idx
                    break
            idx += 1
        else:
            continue
        body = code[start_pos+1:end_pos]  # exclude outer braces
        start_line = code[:m.start()].count('\n') + 1
        end_line = code[:end_pos].count('\n') + 1
        functions.append((name, start_line, end_line, body))

    # Deduplicate by name while keeping first occurrence order
    seen = set()
    dedup_funcs = []
    for name, sline, eline, body in functions:
        if name not in seen:
            seen.add(name)
            dedup_funcs.append((name, sline, eline, body))
    functions = dedup_funcs

    function_sizes, complexities, dependencies, time_complexity = [], [], {}, []
    total_loops, nested_loops_global = 0, 0

    def loop_nesting_depth(body_text):
        tokens = re.split(r'(\{|\})', body_text)
        depth, max_depth = 0, 0
        for t in tokens:
            if re.search(r'\b(for|while|do)\b', t):
                depth += 1
                max_depth = max(max_depth, depth)
            if t == '}':
                if depth > 0:
                    depth -= 1
        return max_depth

    for i, (name, sline, eline, body) in enumerate(functions):
        lines_count = max(0, eline - sline + 1)
        function_sizes.append((name, lines_count))

        # Estimate cyclomatic complexity
        decisions = len(re.findall(r'\b(if|else if|for|while|case|&&|\|\|)\b', body))
        complexity = max(1, 1 + decisions)
        complexities.append((name, complexity, sline))

        loops_here = len(re.findall(r'\b(for|while|do)\b', body))
        total_loops += loops_here
        nested_depth = loop_nesting_depth(body)
        nested_loops_global = max(nested_loops_global, nested_depth)

        # time complexity heuristic
        is_recursive = re.search(r'\b' + re.escape(name) + r'\s*\(', body)
        if is_recursive:
            tc = "O(n)"  # assume simple linear recursion
        elif nested_depth == 0:
            tc = "O(1)"
        elif nested_depth == 1:
            tc = "O(n)"
        elif nested_depth == 2:
            tc = "O(n²)"
        else:
            tc = f"O(n^{nested_depth})"
        time_complexity.append((name, tc, sline))

        dependencies[name] = []

    # simple sequential linking so graph is connected (demo only)
    names = [n for n,_,_,_ in functions]
    for i in range(len(names)-1):
        dependencies[names[i]].append(names[i+1])

    avg_complexity = round(sum(c for _, c, _ in complexities) / len(complexities), 2) if complexities else 0

    # Efficiency grade based on avg_complexity
    if avg_complexity <= 5: efficiency = "A"
    elif avg_complexity <= 10: efficiency = "B"
    elif avg_complexity <= 15: efficiency = "C"
    else: efficiency = "D"

    return {
        "language": language,
        "function_count": len(functions),
        "function_sizes": function_sizes,
        "complexity": complexities,
        "avg_complexity": avg_complexity,
        "total_lines": total_lines,
        "largest_function": max(function_sizes, key=lambda x: x[1]) if function_sizes else ("None", 0),
        "efficiency_grade": efficiency,
        "loops": total_loops,
        "nested_loops": nested_loops_global,
        "unused_vars": [],
        "unused_funcs": [],
        "dependencies": dependencies,
        "time_complexity": time_complexity,
        "suggestions": []
    }

# ------------------ Generic Analyzer ------------------

def analyze_code(code, lang):
    lang = lang.lower()
    if lang == "python": return analyze_python(code)
    if lang == "java": return analyze_java(code)
    if lang == "js": return analyze_js(code)
    if lang in ["c", "cpp"]: return analyze_c_cpp(code, lang)
    return {"error": "Unsupported language"}

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
        if dep_count == 0:
            colors.append('green')
        elif dep_count <= 2:
            colors.append('yellow')
        else:
            colors.append('red')
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=2000,
            font_size=10, arrowsize=20, arrowstyle='-|>')
    plt.title("Function Dependency Graph")
    plt.show()
