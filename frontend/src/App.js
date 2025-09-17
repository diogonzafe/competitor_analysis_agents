import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [analysisType, setAnalysisType] = useState('quick');

  // Verificar status do backend
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/health');
      if (response.ok) {
        const data = await response.json();
        setHealthStatus(data);
      }
    } catch (err) {
      console.error('Backend não está respondendo:', err);
    }
  };

  const handleQuickAnalysis = async (url, companyName) => {
    setLoading(true);
    setError(null);
    setAnalysisType('quick');
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/quick-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          company_name: companyName
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Erro na análise rápida');
      }

      if (!data.success) {
        throw new Error(data.error || 'Falha na análise');
      }

      setAnalysisData(data);
    } catch (err) {
      setError(err.message);
      console.error('Erro na análise:', err);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="App">
      <header className="App-header">
        <h1>Análise de Concorrentes</h1>
        <p>Sistema inteligente para análise competitiva</p>
        {healthStatus && (
          <div className="health-status">
            <div className="status-indicator"></div>
            <span>Backend Online - {healthStatus.agents ? Object.keys(healthStatus.agents).length : 0} agentes ativos</span>
          </div>
        )}
      </header>
      
      <main className="App-main">
        <Dashboard 
          onQuickAnalysis={handleQuickAnalysis}
          analysisData={analysisData}
          loading={loading}
          error={error}
          analysisType={analysisType}
          healthStatus={healthStatus}
        />
      </main>
    </div>
  );
}

export default App;
