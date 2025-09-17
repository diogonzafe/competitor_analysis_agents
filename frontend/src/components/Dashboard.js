import React, { useState } from 'react';
import { Search, Loader2, CheckCircle, AlertCircle, FileText, Shield, Server, TrendingUp } from 'lucide-react';

const Dashboard = ({ onQuickAnalysis, analysisData, loading, error, analysisType, healthStatus }) => {
  const [url, setUrl] = useState('');
  const [companyName, setCompanyName] = useState('');

  const handleQuickSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onQuickAnalysis(url.trim(), companyName.trim() || 'Empresa');
    }
  };


  return (
    <div className="dashboard">
      {/* Status do Backend */}
      {healthStatus && (
        <div className="backend-status">
          <Server size={20} />
          <span>Backend: {healthStatus.status}</span>
          <span>•</span>
          <span>Agentes: {Object.keys(healthStatus.agents || {}).join(', ')}</span>
        </div>
      )}

      {/* Seção de Input */}
      <div className="input-section">
        <h2>Análise de Concorrente</h2>
        <p>Digite a URL da empresa para análise competitiva</p>
        
        <div className="input-group">
          <input
            type="url"
            className="input-field"
            placeholder="https://exemplo.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
          <input
            type="text"
            className="input-field"
            placeholder="Nome da empresa (opcional)"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
          />
        </div>

        <div className="analysis-buttons">
          <button 
            onClick={handleQuickSubmit}
            className="analyze-btn quick-btn"
            disabled={loading}
          >
            {loading ? <Loader2 className="spinner" /> : <Search size={20} />}
            {loading ? 'Analisando...' : 'Analisar Concorrente'}
          </button>
        </div>

        <div className="analysis-info">
          <div className="info-item">
            <Search size={16} />
            <span>Análise: Scraper → Summarizer → Evaluator</span>
          </div>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="loading">
          <Loader2 className="spinner" />
          <span>Agentes trabalhando na análise...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="error">
          <AlertCircle size={20} />
          <span>Erro: {error}</span>
        </div>
      )}

      {/* Results */}
      {analysisData && !loading && (
        <div className="results">
          <h2>Resultados da Análise</h2>
          
          {/* Dados Coletados */}
          <div className="result-section">
            <h3>
              <FileText size={20} />
              Dados Coletados
            </h3>
            <div className="result-content">
              {analysisData.data}
            </div>
          </div>

          {/* Resumo Estratégico */}
          <div className="result-section">
            <h3>
              <TrendingUp size={20} />
              Análise Estratégica
            </h3>
            <div className="result-content">
              {analysisData.summary}
            </div>
          </div>

          {/* Validação */}
          <div className="result-section">
            <h3>
              <Shield size={20} />
              Validação do Sistema
            </h3>
            <div className="result-content">
              {analysisData.validation}
            </div>
          </div>


          {/* Informações da Análise */}
          <div className="result-section">
            <h3>
              <CheckCircle size={20} />
              Informações da Análise
            </h3>
            <div className="result-content">
              URL: {analysisData.url}
              Timestamp: {new Date(analysisData.timestamp).toLocaleString('pt-BR')}
              Status: {analysisData.success ? 'Sucesso' : 'Erro'}
            </div>
          </div>
        </div>
      )}

      {/* Instruções */}
      {!analysisData && !loading && (
        <div className="result-section">
          <h3>Como usar</h3>
          <div className="result-content">
            1. Digite a URL da empresa que deseja analisar
            2. Opcionalmente, informe o nome da empresa
            3. Clique em "Analisar Concorrente"
            4. Aguarde os agentes processarem os dados
            5. Visualize os resultados da análise competitiva
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
