# Multi-Language Code Analyzer & Optimizer

A **Python-based code analyzer** that supports **Python, Java, and JavaScript**.  
It analyzes code for **maintainability, complexity, loops, nested loops, unused code**, and provides **time complexity estimation** for Python functions.  

This project includes both a **Command-Line Interface (CLI)** and a **Tkinter GUI** for easy interaction.

---

## Features

### General
- Supports **Python, Java, and JavaScript** code.
- Detects **critical functions** based on complexity and function size.
- Identifies **loops and nested loops**.
- Finds **unused variables and functions** (dead code analysis).
- Generates **visual function dependency graphs**.
- Saves **analysis reports** as timestamped `.txt` files.
- Provides **suggestions** for improving code quality.

### Python-specific
- Computes **Maintainability Index (MI)**.
- Estimates **time complexity** of functions.
- Highlights **low-comment ratio** and complex functions.

### Java/JavaScript-specific
- Analyzes **methods/functions**, loop counts, and dependencies.
- Provides **basic complexity insights** (Cyclomatic complexity for Java partially, future updates planned for JS).

### GUI (Tkinter)
- Interactive GUI to browse and analyze files.
- Displays results with **color-coded analysis**.
- Optional **visual dependency graph** window.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/aryn247/multi-language-code-analyzer.git
cd multi-language-code-analyzer
