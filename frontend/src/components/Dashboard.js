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
          
          {/* Informações de Raspagem */}
          {analysisData.scrape && (
            <div className="result-section">
              <h3>
                <FileText size={20} />
                Informações de Raspagem
              </h3>
              <div className="result-content">
                <div className="info-grid">
                  <div className="info-item">
                    <strong>Título:</strong> {analysisData.scrape.title || 'Não disponível'}
                  </div>
                  <div className="info-item">
                    <strong>Caracteres coletados:</strong> {analysisData.scrape.chars.toLocaleString()}
                  </div>
                  <div className="info-item">
                    <strong>URL:</strong> {analysisData.url}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Análise da Empresa */}
          {analysisData.data && (
            <div className="result-section">
              <h3>
                <FileText size={20} />
                Análise da Empresa
              </h3>
              <div className="result-content">
                <div className="structured-data">
                  <div className="data-item">
                    <strong>Nome:</strong> {analysisData.data.name || 'Não identificado'}
                  </div>
                  {analysisData.data.offerings && analysisData.data.offerings.length > 0 && (
                    <div className="data-item">
                      <strong>Ofertas:</strong>
                      <ul>
                        {analysisData.data.offerings.map((offering, index) => (
                          <li key={index}>{offering}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {analysisData.data.pricing && (
                    <div className="data-item">
                      <strong>Preços:</strong> {analysisData.data.pricing}
                    </div>
                  )}
                  {analysisData.data.segments && analysisData.data.segments.length > 0 && (
                    <div className="data-item">
                      <strong>Segmentos:</strong>
                      <ul>
                        {analysisData.data.segments.map((segment, index) => (
                          <li key={index}>{segment}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {analysisData.data.differentiators && analysisData.data.differentiators.length > 0 && (
                    <div className="data-item">
                      <strong>Diferenciais:</strong>
                      <ul>
                        {analysisData.data.differentiators.map((diff, index) => (
                          <li key={index}>{diff}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {analysisData.data.contact && (
                    <div className="data-item">
                      <strong>Contato:</strong> {analysisData.data.contact}
                    </div>
                  )}
                  {analysisData.data.links && analysisData.data.links.length > 0 && (
                    <div className="data-item">
                      <strong>Links:</strong>
                      <ul>
                        {analysisData.data.links.map((link, index) => (
                          <li key={index}>
                            <a href={link} target="_blank" rel="noopener noreferrer">
                              {link}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Análise Competitiva */}
          {analysisData.analysis && (
            <div className="result-section">
              <h3>
                <TrendingUp size={20} />
                Análise Competitiva
              </h3>
              <div className="result-content">
                <div className="structured-data">
                  <div className="data-item">
                    <strong>Empresa:</strong> {analysisData.analysis.empresa || 'Não identificada'}
                  </div>
                  <div className="data-item">
                    <strong>Proposta de Valor:</strong> {analysisData.analysis.proposta_valor || 'Não especificada'}
                  </div>
                  
                  {analysisData.analysis.fortalezas && analysisData.analysis.fortalezas.length > 0 && (
                    <div className="data-item">
                      <strong>Fortalezas:</strong>
                      <ul>
                        {analysisData.analysis.fortalezas.map((fortaleza, index) => (
                          <li key={index}>{fortaleza}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysisData.analysis.ameacas && analysisData.analysis.ameacas.length > 0 && (
                    <div className="data-item">
                      <strong>Ameaças:</strong>
                      <ul>
                        {analysisData.analysis.ameacas.map((ameaca, index) => (
                          <li key={index}>{ameaca}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysisData.analysis.oportunidades && analysisData.analysis.oportunidades.length > 0 && (
                    <div className="data-item">
                      <strong>Oportunidades:</strong>
                      <ul>
                        {analysisData.analysis.oportunidades.map((oportunidade, index) => (
                          <li key={index}>{oportunidade}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysisData.analysis.taticas && Object.keys(analysisData.analysis.taticas).length > 0 && (
                    <div className="data-item">
                      <strong>Táticas:</strong>
                      <ul>
                        {Object.entries(analysisData.analysis.taticas).map(([key, value]) => (
                          <li key={key}><strong>{key}:</strong> {value}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysisData.analysis.recomendacoes && analysisData.analysis.recomendacoes.length > 0 && (
                    <div className="data-item">
                      <strong>Recomendações:</strong>
                      <ul>
                        {analysisData.analysis.recomendacoes.map((recomendacao, index) => (
                          <li key={index}>{recomendacao}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Resumo Executivo */}
          {analysisData.summary && (
            <div className="result-section">
              <h3>
                <CheckCircle size={20} />
                Resumo Executivo
              </h3>
              <div className="result-content">
                {analysisData.summary}
              </div>
            </div>
          )}

          {/* Validação do Sistema */}
          {analysisData.validation && (
            <div className="result-section">
              <h3>
                <Shield size={20} />
                Validação do Sistema
              </h3>
              <div className="result-content">
                <div className="structured-data">
                  <div className="data-item">
                    <strong>Análise Completa:</strong> 
                    <span className={`status-badge ${analysisData.validation.completo ? 'success' : 'warning'}`}>
                      {analysisData.validation.completo ? 'Sim' : 'Não'}
                    </span>
                  </div>
                  <div className="data-item">
                    <strong>Relevante:</strong> 
                    <span className={`status-badge ${analysisData.validation.relevante ? 'success' : 'warning'}`}>
                      {analysisData.validation.relevante ? 'Sim' : 'Não'}
                    </span>
                  </div>
                  <div className="data-item">
                    <strong>Acionável:</strong> 
                    <span className={`status-badge ${analysisData.validation.acionavel ? 'success' : 'warning'}`}>
                      {analysisData.validation.acionavel ? 'Sim' : 'Não'}
                    </span>
                  </div>
                  
                  {analysisData.validation.pontos_fortes && analysisData.validation.pontos_fortes.length > 0 && (
                    <div className="data-item">
                      <strong>Pontos Fortes:</strong>
                      <ul>
                        {analysisData.validation.pontos_fortes.map((ponto, index) => (
                          <li key={index}>{ponto}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysisData.validation.melhorias && analysisData.validation.melhorias.length > 0 && (
                    <div className="data-item">
                      <strong>Sugestões de Melhoria:</strong>
                      <ul>
                        {analysisData.validation.melhorias.map((melhoria, index) => (
                          <li key={index}>{melhoria}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Informações da Análise */}
          <div className="result-section">
            <h3>
              <CheckCircle size={20} />
              Informações da Análise
            </h3>
            <div className="result-content">
              <div className="info-grid">
                <div className="info-item">
                  <strong>URL:</strong> {analysisData.url}
                </div>
                <div className="info-item">
                  <strong>Timestamp:</strong> {new Date(analysisData.timestamp).toLocaleString('pt-BR')}
                </div>
                <div className="info-item">
                  <strong>Status:</strong> 
                  <span className={`status-badge ${analysisData.success ? 'success' : 'error'}`}>
                    {analysisData.success ? 'Sucesso' : 'Erro'}
                  </span>
                </div>
              </div>
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
