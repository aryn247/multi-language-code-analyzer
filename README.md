# 🚀 Multi-Language Code Analyzer Pro

A **Professional Full-Stack Code Analyzer** that statically analyzes your codebase to provide enterprise-grade metrics, dynamic dependency graphs, and an interactive IDE-like experience. 

Originally built as a Python prototype, this project has been fully re-engineered into a modern web application featuring a **FastAPI** backend and a **React (Vite)** frontend.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/backend-FastAPI-009688.svg?logo=fastapi)
![React](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB.svg?logo=react)

---

## ✨ Features

### 💻 Enterprise UI
- **Interactive Split-Pane Layout:** View your code in the embedded **Monaco Editor** (the engine behind VS Code) with full syntax highlighting.
- **Click-to-Highlight:** Clicking on a function metric or chart bar automatically scrolls and highlights the specific line in the code editor.
- **Dynamic Dashboards:** Beautiful, responsive glassmorphism UI built with modern CSS and Framer Motion animations.
- **PDF Exporting:** Export high-quality PDF reports of your code analysis with a single click.

### 🧠 Advanced Backend Engine
- **Universal Language Support:** Analyzes **Python, JavaScript, Java, C/C++, Go, Rust, PHP, Ruby, and C#**.
- **Real AST Parsing:** Uses Python's native `ast` module and `radon` to accurately calculate **Cyclomatic Complexity**, **Maintainability Index**, and **Time Complexity Estimations**.
- **Dead Code Detection:** Automatically identifies and flags unused variables and functions.
- **Dependency Graphs:** Dynamically scans your code for external imports and generates a visual node-link network graph of your file's dependencies.

---

## 🛠 Architecture

The project is split into a decoupled architecture:

* **`/backend`**: A high-performance REST API built with Python 3 and FastAPI. Uses `networkx` and `matplotlib` for dynamic graph generation.
* **`/frontend`**: A lightning-fast Single Page Application (SPA) built with React, Vite, and Recharts.
* **`/legacy`**: The original Tkinter/Streamlit prototypes and text reports are archived here for reference.

---

## 🚀 Getting Started

To run the application locally, you will need to start both the backend server and the frontend development environment.

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**

### 1. Start the Backend API

Open your terminal and run the following commands:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
*The FastAPI backend will now be running on `http://localhost:8000`.*

### 2. Start the Frontend App

Open a **second terminal window** and run:

```bash
cd frontend
npm install
npm run dev
```
*The Vite development server will start, and you can access the UI at `http://localhost:5173`.*

---

## 📸 Usage

1. Open `http://localhost:5173` in your browser.
2. **Drag and drop** a supported source code file (e.g., `.py`, `.js`, `.go`, `.rs`) into the upload zone.
3. Review the generated metrics, complexity charts, and your dynamically generated dependency graph.
4. Click on any function in the charts to locate it instantly within the embedded Monaco Editor.
5. Click **Export** to save a PDF copy of the analysis report.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check out the [issues page](https://github.com/aryn247/multi-language-code-analyzer/issues).

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
