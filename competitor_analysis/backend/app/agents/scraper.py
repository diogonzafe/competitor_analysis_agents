"""
Scraper Agent - Coleta e análise de dados de websites

"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import re
import json
from app.utils import scraping_client, deepseek_client


class CompanyAnalysis(BaseModel):
    """
    Modelo de dados para análise de empresa.
    
    """
    name: str = Field(default="", description="Nome da empresa ou marca")
    offerings: List[str] = Field(default_factory=list, description="Produtos/serviços oferecidos")
    pricing: Optional[str] = Field(None, description="Informações sobre preços")
    segments: List[str] = Field(default_factory=list, description="Segmentos de mercado atendidos")
    differentiators: List[str] = Field(default_factory=list, description="Diferenciais competitivos")
    contact: Optional[str] = Field(None, description="Informações de contato")
    links: List[str] = Field(default_factory=list, description="Links relevantes encontrados")


@tool("web_scraping_tool")
def web_scraping_tool(url: str) -> Dict[str, Any]:
    """
    Tool para coleta de dados de websites usando ScrapingAnt.
  
    """
    # Validação básica da URL
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return {"ok": False, "url": url, "title": None, "text": None, "error": "URL inválida"}
    
    try:
        # Executa scraping com timeout de 25 segundos
        docs = scraping_client.scrape_url(url, timeout=25)
        if not docs:
            return {"ok": False, "url": url, "title": None, "text": None, "error": "Sem conteúdo"}
        
        # Extrai e limpa o conteúdo da página
        content = (docs[0].page_content or "")[:12000]  # Limita a 12k caracteres
        clean = re.sub(r"\s+", " ", content).strip()[:5000]  # Remove espaços extras e limita a 5k
        
        # Extrai título dos metadados
        title = getattr(docs[0], "metadata", {}).get("title") if hasattr(docs[0], "metadata") else None
        
        return {"ok": True, "url": url, "title": title, "text": clean, "error": None}
    except Exception as e:
        return {"ok": False, "url": url, "title": None, "text": None, "error": str(e)}


class ScraperAgent:
    """
    Agente responsável por coleta e análise de dados de websites.
    
    Utiliza LangChain/LangGraph ReAct Agent para análise inteligente de conteúdo,
    combinando web scraping com extração estruturada de dados.
    """
    
    def __init__(self):
        """Inicializa o agente com LLM e configuração de ReAct."""
        self.llm = deepseek_client.get_llm(temperature=0.2)
        
        # Configura agente ReAct para análise inteligente
        self.agent = create_react_agent(
            model=self.llm,
            tools=[web_scraping_tool],
            prompt=(
                "Você é especialista em coleta competitiva. "
                "Sempre que receber uma URL, chame web_scraping_tool(url). "
                "Se ok=false, explique o erro e pare. "
                "Se ok=true, analise o conteúdo e extraia informações estruturadas sobre a empresa."
            ),
        )


    def scrape_and_analyze(self, url: str) -> Dict[str, Any]:
        """
        Método unificado que combina scraping e análise.
        
        Usa o ReAct Agent para fazer scraping e análise em uma única operação.
        
        Args:
            url: URL a ser processada
            
        Returns:
            Dict com resultado completo: {ok, url, title, text, analysis, error}
        """
        try:
            # Usa o ReAct Agent para análise completa
            result = self.agent.invoke({
                "messages": [HumanMessage(content=f"Analise esta URL: {url}")]
            })
            
            # Extrai dados do resultado do agente
            if hasattr(result, 'messages') and result.messages:
                agent_content = result.messages[-1].content
            elif hasattr(result, 'content'):
                agent_content = result.content
            else:
                agent_content = str(result)
            
            # Extrai dados estruturados diretamente
            analysis = self._extract_analysis_from_content(agent_content)
            
            # Retorna resultado para compatibilidade com API
            return {
                "ok": True,
                "url": url,
                "title": analysis.name or "Título não encontrado",
                "text": f"Empresa: {analysis.name}\nOfertas: {', '.join(analysis.offerings)}\nDiferenciais: {', '.join(analysis.differentiators)}",
                "analysis": analysis,
                "error": None
            }
            
        except Exception as e:
            print(f"Erro no scraping e análise: {e}")
            return {
                "ok": False,
                "url": url,
                "title": None,
                "text": None,
                "analysis": CompanyAnalysis(),
                "error": str(e)
            }

    def _extract_analysis_from_content(self, content: str) -> CompanyAnalysis:
        """
        Extrai dados estruturados do conteúdo do agente.
        
        Args:
            content: Conteúdo da resposta do agente
            
        Returns:
            CompanyAnalysis: Dados estruturados extraídos
        """
        try:
            from app.utils import json_call
            prompt = (
                "Com base na análise do agente abaixo, extraia SOMENTE JSON válido conforme CompanyAnalysis:\n"
                '{"name": "nome da empresa", "offerings": ["oferta1", "oferta2"], '
                '"pricing": "info preços", "segments": ["segmento1", "segmento2"], '
                '"differentiators": ["diferencial1", "diferencial2"], '
                '"contact": "info contato", "links": ["link1", "link2"]}\n\n'
                f"ANÁLISE DO AGENTE:\n{content}"
            )
            return json_call(self.llm, prompt, CompanyAnalysis)
        except Exception as e:
            print(f"Erro na extração da análise: {e}")
            return CompanyAnalysis()