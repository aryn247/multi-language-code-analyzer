import sys
import json
from multi_language_analyzer import analyze_code

def main():
    # Analyze itself
    result = analyze_code("multi_language_analyzer.py", "python")
    print("Testing Python Analyzer on multi_language_analyzer.py:")
    
    # Don't print the huge b64 graph for cleanliness
    if "dependency_graph_b64" in result:
        result["dependency_graph_b64"] = "<B64 GRAPH OMITTED>"
    print(json.dumps(result, indent=2))
    
    # Test JS
    js_code = "import { x } from 'y';\nfunction hello() { var x = 1; return x; }"
    result_js = analyze_code(js_code, "js")
    if "dependency_graph_b64" in result_js:
        result_js["dependency_graph_b64"] = "<B64 GRAPH OMITTED>"
    print("\nTesting JS Analyzer:")
    print(json.dumps(result_js, indent=2))
    
    # Test Go
    go_code = """
    package main
    import "fmt"
    func main() {
        fmt.Println("Hello Go")
    }
    func helper() {}
    """
    result_go = analyze_code(go_code, "go")
    if "dependency_graph_b64" in result_go:
        result_go["dependency_graph_b64"] = "<B64 GRAPH OMITTED>"
    print("\nTesting Go Analyzer:")
    print(json.dumps(result_go, indent=2))

if __name__ == "__main__":
    main()
