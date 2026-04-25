import React, { useState, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, FileCode2, AlertTriangle, CheckCircle, BarChart3, Clock, AlertCircle, Code, Download, GitBranch } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import Editor from '@monaco-editor/react';
import { motion } from 'framer-motion';
import html2pdf from 'html2pdf.js';

function App() {
  const [file, setFile] = useState(null);
  const [codeContent, setCodeContent] = useState("");
  const [langStr, setLangStr] = useState("python");
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const fileInputRef = useRef(null);
  const editorRef = useRef(null);
  const dashboardRef = useRef(null);
  const [activeLine, setActiveLine] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const processFile = (selectedFile) => {
    setFile(selectedFile);
    setResult(null);
    setError(null);
    
    // Read contents for Monaco
    const reader = new FileReader();
    reader.onload = (e) => {
        setCodeContent(e.target.result);
    };
    reader.readAsText(selectedFile);

    const ext = selectedFile.name.split('.').pop().toLowerCase();
    const langMap = {
      'py': 'python',
      'java': 'java',
      'js': 'javascript',
      'c': 'c',
      'cpp': 'cpp',
      'cc': 'cpp',
      'cxx': 'cpp',
      'go': 'go',
      'rs': 'rust',
      'php': 'php',
      'rb': 'ruby',
      'cs': 'csharp'
    };
    setLangStr(langMap[ext] || 'javascript');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
  };

  const analyzeCode = async () => {
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    const langMapAPI = {
      'py': 'python',
      'java': 'java',
      'js': 'js',
      'c': 'c',
      'cpp': 'cpp',
      'cc': 'cpp',
      'cxx': 'cpp',
      'go': 'go',
      'rs': 'rust',
      'php': 'php',
      'rb': 'ruby',
      'cs': 'csharp'
    };
    const langAPI = langMapAPI[ext] || 'unknown';

    if (langAPI === 'unknown') {
      setError("Unsupported file format. Please upload Python, Java, JS, C/C++, Go, Rust, PHP, Ruby, or C#.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('lang', langAPI);

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8000/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (response.data.error) {
          setError(response.data.error);
      } else {
          setResult(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred while analyzing the code.");
    } finally {
      setLoading(false);
    }
  };

  const scrollToLine = (lineNumber) => {
      if (editorRef.current && lineNumber) {
          setActiveLine(lineNumber);
          editorRef.current.revealLineInCenter(lineNumber);
          editorRef.current.setPosition({ lineNumber: lineNumber, column: 1 });
          editorRef.current.focus();
          
          const monaco = window.monaco;
          if (monaco) {
              const decorations = editorRef.current.deltaDecorations([], [
                  {
                      range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                      options: { isWholeLine: true, className: 'line-highlight', marginClassName: 'margin-highlight' }
                  }
              ]);
              setTimeout(() => {
                  editorRef.current.deltaDecorations(decorations, []);
              }, 2000);
          }
      }
  };

  const exportPDF = () => {
      const element = dashboardRef.current;
      const opt = {
          margin:       0.5,
          filename:     `analysis_report_${file.name}.pdf`,
          image:        { type: 'jpeg', quality: 0.98 },
          html2canvas:  { scale: 2, useCORS: true, logging: false },
          jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
      };
      html2pdf().set(opt).from(element).save();
  };

  const chartData = result?.complexity?.map(item => ({
      name: item[0],
      complexity: item[1],
      line: item[2]
  })) || [];

  const containerVariants = {
      hidden: { opacity: 0 },
      visible: {
          opacity: 1,
          transition: { staggerChildren: 0.1 }
      }
  };

  const itemVariants = {
      hidden: { y: 20, opacity: 0 },
      visible: {
          y: 0,
          opacity: 1,
          transition: { type: "spring", stiffness: 100 }
      }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Code Analyzer Pro</h1>
        <p>Enterprise static analysis with multi-language and interactive diagnostics</p>
      </header>

      {!result && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-panel" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <div 
              className={`dropzone ${isDragging ? 'active' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadCloud size={48} className="dropzone-icon" />
              <div className="dropzone-text">
                {file ? file.name : "Drag & drop your code file here"}
              </div>
              <div className="dropzone-subtext">
                {file ? "Click to change file" : "or click to browse (.py, .java, .js, .cpp, .go, .rs, .php, .rb, .cs)"}
              </div>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                style={{ display: 'none' }} 
                accept=".py,.java,.js,.c,.cpp,.cc,.cxx,.go,.rs,.php,.rb,.cs"
              />
            </div>

            {error && (
                <div style={{ marginTop: '1rem', color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
                    <AlertTriangle size={18} /> {error}
                </div>
            )}

            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
              <button 
                className="btn" 
                onClick={analyzeCode} 
                disabled={!file || loading}
              >
                {loading ? <span className="loader"></span> : <FileCode2 size={20} />}
                {loading ? "Analyzing..." : "Analyze Code"}
              </button>
            </div>
          </motion.div>
      )}

      {result && (
        <div className="split-container">
            {/* Left Pane: Monaco Editor */}
            <motion.div initial={{ opacity: 0, x: -50 }} animate={{ opacity: 1, x: 0 }} className="editor-pane">
                <div style={{ padding: '1rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,0,0,0.2)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <FileCode2 size={18} color="var(--accent-color)" />
                        <span style={{ fontWeight: 600 }}>{file?.name}</span>
                    </div>
                    <div className="tag" style={{ margin: 0, padding: '0.1rem 0.5rem', fontSize: '0.75rem' }}>
                        {result.language}
                    </div>
                </div>
                <div style={{ flex: 1 }}>
                    <Editor
                        height="100%"
                        language={langStr}
                        theme="vs-dark"
                        value={codeContent}
                        onMount={handleEditorDidMount}
                        options={{
                            readOnly: true,
                            minimap: { enabled: true },
                            scrollBeyondLastLine: false,
                            fontSize: 14,
                            smoothScrolling: true,
                            cursorBlinking: "smooth"
                        }}
                    />
                </div>
            </motion.div>

            {/* Right Pane: Dashboard */}
            <motion.div 
                className="dashboard-pane" 
                variants={containerVariants} 
                initial="hidden" 
                animate="visible"
            >
                <div id="pdf-content" ref={dashboardRef}>
                    <motion.div variants={itemVariants} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', background: 'var(--glass-bg)', padding: '1rem', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
                        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.2rem', margin: 0 }}>
                            <CheckCircle color="var(--success)" size={20} /> Analysis Report
                        </h2>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button className="btn btn-secondary" onClick={exportPDF} style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }} data-html2canvas-ignore>
                                <Download size={16} /> Export
                            </button>
                            <button className="btn" onClick={() => { setResult(null); setFile(null); setCodeContent(""); }} style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }} data-html2canvas-ignore>
                                New Analysis
                            </button>
                        </div>
                    </motion.div>

                    <div className="dashboard-grid">
                        {result.maintainability_index !== undefined && result.maintainability_index > 0 && (
                            <motion.div variants={itemVariants} className="glass-card">
                                <div className="metric-label">Maintainability</div>
                                <div className={`metric-value grade-${result.efficiency_grade?.toLowerCase()}`}>
                                    {result.maintainability_index}
                                </div>
                                <div className="dropzone-subtext">Grade: {result.efficiency_grade}</div>
                            </motion.div>
                        )}
                        
                        {(result.avg_complexity !== undefined || result.function_count !== undefined) && (result.avg_complexity > 0 || result.function_count > 0) && (
                            <motion.div variants={itemVariants} className="glass-card">
                                <div className="metric-label">{result.avg_complexity !== undefined ? "Avg Complexity" : "Functions"}</div>
                                <div className="metric-value">{result.avg_complexity !== undefined ? result.avg_complexity : result.function_count}</div>
                                <div className="dropzone-subtext">{result.function_count !== undefined ? `${result.function_count} total functions` : 'Functions parsed'}</div>
                            </motion.div>
                        )}

                        {(result.total_lines !== undefined || result.lines !== undefined) && (
                            <motion.div variants={itemVariants} className="glass-card">
                                <div className="metric-label">Code Size</div>
                                <div className="metric-value">{result.total_lines || result.lines}</div>
                                <div className="dropzone-subtext">Lines of code</div>
                            </motion.div>
                        )}
                    </div>

                    {result.dependency_graph_b64 && (
                        <motion.div variants={itemVariants} className="glass-card" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
                            <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem', justifyContent: 'center' }}>
                                <GitBranch size={18} color="var(--accent-color)" /> Dependency Graph
                            </h3>
                            <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '1rem', display: 'inline-block' }}>
                                <img 
                                    src={`data:image/png;base64,${result.dependency_graph_b64}`} 
                                    alt="Dependency Graph" 
                                    style={{ maxWidth: '100%', height: 'auto', borderRadius: '4px' }} 
                                />
                            </div>
                        </motion.div>
                    )}

                    {result.complexity && result.complexity.length > 0 && (
                        <motion.div variants={itemVariants} className="glass-card" style={{ marginBottom: '1.5rem' }}>
                            <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
                                <BarChart3 size={18} color="var(--accent-color)" /> Cyclomatic Complexity
                            </h3>
                            <p className="dropzone-subtext" style={{ marginBottom: '1rem' }} data-html2canvas-ignore>Click a bar to view the function in the editor.</p>
                            <div style={{ height: '220px' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                                        <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fill: 'var(--text-secondary)', fontSize: 12}} />
                                        <YAxis stroke="var(--text-secondary)" tick={{fill: 'var(--text-secondary)', fontSize: 12}} />
                                        <Tooltip 
                                            contentStyle={{ backgroundColor: 'var(--bg-color)', borderColor: 'var(--glass-border)', borderRadius: '8px' }}
                                            itemStyle={{ color: 'var(--text-primary)' }}
                                            cursor={{fill: 'rgba(255,255,255,0.05)'}}
                                        />
                                        <Bar 
                                            dataKey="complexity" 
                                            onClick={(data) => {
                                                if(data && data.payload && data.payload.line) {
                                                    scrollToLine(data.payload.line);
                                                }
                                            }}
                                            radius={[4, 4, 0, 0]}
                                        >
                                            {chartData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.line === activeLine ? '#c084fc' : 'var(--accent-color)'} style={{ cursor: 'pointer', transition: 'fill 0.3s' }} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </motion.div>
                    )}

                    <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr' }}>
                        {((result.unused_vars && result.unused_vars.length > 0) || (result.unused_funcs && result.unused_funcs.length > 0)) && (
                            <motion.div variants={itemVariants} className="glass-card">
                                <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
                                    <Code size={18} color="var(--danger)" /> Dead Code Detected
                                </h3>
                                
                                {result.unused_vars && result.unused_vars.length > 0 && (
                                    <div style={{ marginBottom: '1.5rem' }}>
                                        <div className="metric-label">Unused Variables</div>
                                        <div className="tags-container">
                                            {result.unused_vars.map(v => <span key={v} className="tag tag-danger">{v}</span>)}
                                        </div>
                                    </div>
                                )}

                                {result.unused_funcs && result.unused_funcs.length > 0 && (
                                    <div>
                                        <div className="metric-label">Unused Functions</div>
                                        <div className="tags-container">
                                            {result.unused_funcs.map(f => <span key={f} className="tag tag-danger">{f}()</span>)}
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        )}
                        
                        {result.time_complexity && result.time_complexity.length > 0 && (
                            <motion.div variants={itemVariants} className="glass-card">
                                <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
                                    <Clock size={18} color="var(--warning)" /> Estimated Time Complexity
                                </h3>
                                <p className="dropzone-subtext" style={{ marginBottom: '1rem' }} data-html2canvas-ignore>Click a function to highlight it in the editor.</p>
                                <div className="suggestion-list">
                                    {result.time_complexity.map(item => (
                                        <div 
                                            key={item[0]} 
                                            className="suggestion-item clickable-row"
                                            onClick={() => scrollToLine(item[2])}
                                        >
                                            <div style={{ flex: 1 }}><strong>{item[0]}()</strong></div>
                                            <div className="tag" style={{ background: item[1].includes('^2') || item[1].includes('^3') ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)', color: item[1].includes('^2') || item[1].includes('^3') ? '#fca5a5' : '#6ee7b7', borderColor: 'transparent' }}>
                                                {item[1]}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>
                        )}

                        {result.suggestions && result.suggestions.length > 0 && (
                            <motion.div variants={itemVariants} className="glass-card">
                                <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
                                    <AlertCircle size={18} color="var(--accent-color)" /> Suggestions
                                </h3>
                                <ul className="suggestion-list">
                                    {result.suggestions.map((s, i) => (
                                        <li key={i} className="suggestion-item" style={{ paddingBottom: '0.75rem', marginBottom: '0.75rem' }}>
                                            <AlertTriangle size={16} className="suggestion-icon" />
                                            <span style={{ fontSize: '0.95rem' }}>{s}</span>
                                        </li>
                                    ))}
                                </ul>
                            </motion.div>
                        )}
                    </div>
                </div>
            </motion.div>
        </div>
      )}
    </div>
  );
}

export default App;
