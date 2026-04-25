import os
import ast
import tempfile
import esprima
import networkx as nx
import matplotlib.pyplot as plt
import base64
import io
import re

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
    from radon.raw import analyze as radon_analyze
except ImportError:
    cc_visit = None

try:
    import javalang
except ImportError:
    javalang = None

def generate_dependency_graph_b64(base_name, dependencies):
    if not dependencies:
        return None
    try:
        G = nx.DiGraph()
        for dep in set(dependencies):
            # Clean up the dependency name if needed
            clean_dep = str(dep).replace('"', '').replace("'", '').strip()
            if clean_dep:
                G.add_edge(base_name, clean_dep)
            
        plt.figure(figsize=(6, 4))
        plt.style.use('dark_background')
        pos = nx.spring_layout(G, seed=42)
        nx.draw(G, pos, with_labels=True, node_color="#3b82f6", edge_color="gray", node_size=1500, font_size=9, font_weight="bold", font_color="white", alpha=0.9)
        
        buf = io.BytesIO()
        plt.savefig(buf, format="png", transparent=True, bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    except Exception as e:
        print(f"Graph error: {e}")
        return None

def analyze_code(code_or_path, lang):
    lang = lang.lower()

    if os.path.exists(code_or_path):
        base_name = os.path.basename(code_or_path)
        with open(code_or_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
    else:
        base_name = "snippet." + lang
        code = code_or_path

    # Dispatch to specific analyzer
    if lang == "python":
        result = analyze_python(code)
    elif lang == "java":
        result = analyze_java(code)
    elif lang in ["js", "javascript"]:
        result = analyze_js(code)
    elif lang in ["c", "cpp"]:
        result = analyze_c_cpp(code, lang)
    elif lang == "go":
        result = analyze_go(code)
    elif lang == "rust":
        result = analyze_rust(code)
    elif lang == "php":
        result = analyze_php(code)
    elif lang == "ruby":
        result = analyze_ruby(code)
    elif lang == "csharp":
        result = analyze_csharp(code)
    else:
        return {"error": f"Unsupported language: {lang}"}

    # Generate graph if dependencies exist
    if "dependencies_list" in result and result["dependencies_list"]:
        b64 = generate_dependency_graph_b64(base_name, result["dependencies_list"])
        if b64:
            result["dependency_graph_b64"] = b64

    return result

def analyze_python(code):
    result = {
        "language": "Python",
        "functions": 0,
        "classes": 0,
        "imports": 0,
        "maintainability_index": 0,
        "efficiency_grade": "A",
        "function_sizes": [],
        "complexity": [],
        "time_complexity": [],
        "comment_lines": 0,
        "comment_ratio": 0,
        "avg_complexity": 0,
        "total_lines": 0,
        "function_count": 0,
        "largest_function": ("None", 0),
        "loops": 0,
        "nested_loops": 0,
        "unused_vars": [],
        "unused_funcs": [],
        "suggestions": [],
        "dependencies_list": []
    }

    if not cc_visit:
        result["error"] = "radon is not installed. Python analysis requires radon."
        return result

    try:
        raw_metrics = radon_analyze(code)
        result["total_lines"] = raw_metrics.loc
        result["comment_lines"] = raw_metrics.comments + raw_metrics.multi
        if raw_metrics.loc > 0:
            result["comment_ratio"] = round((result["comment_lines"] / raw_metrics.loc) * 100, 2)

        mi = mi_visit(code, multi=True)
        result["maintainability_index"] = round(mi, 2)
        if mi > 80: result["efficiency_grade"] = "A"
        elif mi > 60: result["efficiency_grade"] = "B"
        elif mi > 40: result["efficiency_grade"] = "C"
        else: result["efficiency_grade"] = "D"

        blocks = cc_visit(code)
        total_cc = 0
        cc_count = 0
        for block in blocks:
            if block.__class__.__name__ in ['Function', 'Method']:
                result["complexity"].append((block.name, block.complexity, block.lineno))
                result["function_count"] += 1
                total_cc += block.complexity
                cc_count += 1
            elif block.__class__.__name__ == 'Class':
                result["classes"] += 1
                
        if cc_count > 0:
            result["avg_complexity"] = round(total_cc / cc_count, 2)
            
        tree = ast.parse(code)
        
        assigned_vars = set()
        used_vars = set()
        defined_funcs = set()
        called_funcs = set()
        
        largest_size = 0
        largest_name = "None"
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["dependencies_list"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result["dependencies_list"].append(node.module)
            elif isinstance(node, ast.FunctionDef):
                defined_funcs.add(node.name)
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    size = node.end_lineno - node.lineno + 1
                    result["function_sizes"].append((node.name, size))
                    if size > largest_size:
                        largest_size = size
                        largest_name = node.name
                
                loops_in_func = 0
                max_depth = 0
                def traverse_depth(n, current_depth):
                    nonlocal loops_in_func, max_depth
                    if isinstance(n, (ast.For, ast.While)):
                        loops_in_func += 1
                        current_depth += 1
                        if current_depth > max_depth:
                            max_depth = current_depth
                    for child in ast.iter_child_nodes(n):
                        traverse_depth(child, current_depth)
                traverse_depth(node, 0)
                
                result["loops"] += loops_in_func
                if max_depth > 1:
                    result["nested_loops"] += (max_depth - 1)
                
                if max_depth == 0: tc = "O(1)"
                elif max_depth == 1: tc = "O(N)"
                elif max_depth == 2: tc = "O(N^2)"
                else: tc = f"O(N^{max_depth})"
                result["time_complexity"].append((node.name, tc, getattr(node, 'lineno', 0)))

            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    assigned_vars.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_funcs.add(node.func.id)
        
        result["largest_function"] = (largest_name, largest_size)
        result["unused_vars"] = list(assigned_vars - used_vars - {'_'})
        result["unused_funcs"] = list(defined_funcs - called_funcs - {'__init__', 'main'})

    except Exception as e:
        result["error"] = f"Error parsing Python code: {e}"

    return result

def analyze_java(code):
    lines = code.splitlines()
    result = {"language": "Java", "classes": 0, "methods": 0, "total_lines": len(lines), "dependencies_list": []}
    
    # Extract imports
    for line in lines:
        if line.strip().startswith("import "):
            dep = line.strip().split("import ")[1].replace(";", "").strip()
            result["dependencies_list"].append(dep)

    if javalang:
        try:
            tree = javalang.parse.parse(code)
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                result["classes"] += 1
            for path, node in tree.filter(javalang.tree.MethodDeclaration):
                result["methods"] += 1
        except Exception as e:
            result["error"] = f"Javalang parse error: {e}"
    else:
        result["classes"] = sum("class " in line for line in lines)
        result["methods"] = sum("(" in line and ")" in line and "{" in line for line in lines)
    return result

def analyze_js(code):
    lines = code.splitlines()
    result = {"language": "JavaScript", "functions": 0, "variables": 0, "total_lines": len(lines), "dependencies_list": []}
    
    # Simple regex for imports
    import_re = re.compile(r'import\s+.*?\s+from\s+[\'"](.*?)[\'"]')
    require_re = re.compile(r'require\([\'"](.*?)[\'"]\)')
    
    for line in lines:
        m1 = import_re.search(line)
        if m1: result["dependencies_list"].append(m1.group(1))
        m2 = require_re.search(line)
        if m2: result["dependencies_list"].append(m2.group(1))

    try:
        try:
            tree = esprima.parseModule(code)
        except:
            tree = esprima.parseScript(code)
        num_funcs = 0
        num_vars = 0
        def walk(node):
            nonlocal num_funcs, num_vars
            if isinstance(node, esprima.nodes.FunctionDeclaration):
                num_funcs += 1
            elif isinstance(node, esprima.nodes.VariableDeclaration):
                num_vars += len(node.declarations)
            
            for key, val in vars(node).items():
                if isinstance(val, esprima.nodes.Node):
                    walk(val)
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, esprima.nodes.Node):
                            walk(item)
        walk(tree)
        result["functions"] = num_funcs
        result["variables"] = num_vars
    except Exception as e:
        result["error"] = f"Error parsing JS code: {e}"
    return result

def analyze_c_cpp(code, lang):
    lines = code.splitlines()
    result = {
        "language": lang.upper(),
        "function_count": sum("(" in line and ")" in line and "{" in line for line in lines),
        "total_lines": len(lines),
        "dependencies_list": []
    }
    for line in lines:
        if line.strip().startswith("#include"):
            dep = line.strip().split("#include")[1].replace("<", "").replace(">", "").replace('"', '').strip()
            result["dependencies_list"].append(dep)
    return result

# --- New Languages (Heuristics) ---

def analyze_go(code):
    lines = code.splitlines()
    result = {"language": "Go", "function_count": 0, "total_lines": len(lines), "dependencies_list": []}
    in_import_block = False
    
    for line in lines:
        clean = line.strip()
        if clean.startswith("func "):
            result["function_count"] += 1
        elif clean.startswith("import ("):
            in_import_block = True
        elif in_import_block and clean == ")":
            in_import_block = False
        elif in_import_block and clean:
            result["dependencies_list"].append(clean.replace('"', ''))
        elif clean.startswith("import "):
            result["dependencies_list"].append(clean.split("import ")[1].replace('"', '').strip())
            
    return result

def analyze_rust(code):
    lines = code.splitlines()
    result = {"language": "Rust", "function_count": 0, "total_lines": len(lines), "dependencies_list": []}
    for line in lines:
        clean = line.strip()
        if clean.startswith("fn ") or " fn " in clean:
            result["function_count"] += 1
        elif clean.startswith("use "):
            dep = clean.split("use ")[1].split("::")[0].replace(";", "").strip()
            result["dependencies_list"].append(dep)
    return result

def analyze_php(code):
    lines = code.splitlines()
    result = {"language": "PHP", "function_count": 0, "classes": 0, "total_lines": len(lines), "dependencies_list": []}
    for line in lines:
        clean = line.strip()
        if "function " in clean:
            result["function_count"] += 1
        elif "class " in clean:
            result["classes"] += 1
        elif clean.startswith("use ") and "\\" in clean:
            dep = clean.split("use ")[1].split("\\")[0].strip()
            result["dependencies_list"].append(dep)
        elif clean.startswith("require") or clean.startswith("include"):
            dep = clean.split(" ")[1].replace("'", "").replace('"', '').replace(';', '')
            result["dependencies_list"].append(dep)
    return result

def analyze_ruby(code):
    lines = code.splitlines()
    result = {"language": "Ruby", "function_count": 0, "classes": 0, "total_lines": len(lines), "dependencies_list": []}
    for line in lines:
        clean = line.strip()
        if clean.startswith("def "):
            result["function_count"] += 1
        elif clean.startswith("class "):
            result["classes"] += 1
        elif clean.startswith("require "):
            dep = clean.split("require ")[1].replace("'", "").replace('"', '').strip()
            result["dependencies_list"].append(dep)
    return result

def analyze_csharp(code):
    lines = code.splitlines()
    result = {"language": "C#", "classes": 0, "total_lines": len(lines), "dependencies_list": []}
    for line in lines:
        clean = line.strip()
        if "class " in clean:
            result["classes"] += 1
        elif clean.startswith("using "):
            dep = clean.split("using ")[1].replace(";", "").strip()
            result["dependencies_list"].append(dep)
    return result
