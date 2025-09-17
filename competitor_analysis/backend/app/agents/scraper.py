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

    
    Funcionalidades principais:
    - Web scraping de URLs específicas
    - Extração de dados estruturados (nome, ofertas, preços, etc.)
    - Análise de conteúdo com LLM
    - Tratamento de erros e fallbacks
    """
    
    def __init__(self):
        """Inicializa o agente com LLM e configuração de ReAct."""
        self.llm = deepseek_client.get_llm(temperature=0.2)  # Temperatura moderada para criatividade controlada
        
        # Configura agente ReAct para uso da tool de scraping
        self.agent = create_react_agent(
            model=self.llm,
            tools=[web_scraping_tool],
            prompt=(
                "Você é especialista em coleta competitiva. "
                "Sempre que receber uma URL, chame web_scraping_tool(url). "
                "Se ok=false, explique o erro e pare. "
                "Se ok=true, resuma pontos comerciais (nome, ofertas, preços, segmentos, diferenciais, contato, links)."
            ),
        )

    def analyze_url(self, url: str) -> CompanyAnalysis:
        """
        Analisa uma URL e extrai informações estruturadas sobre a empresa.
        
        Processo:
        1. Executa web scraping da URL
        2. Se bem-sucedido, analisa o conteúdo com LLM
        3. Extrai dados estruturados usando parsing JSON manual
        
        Args:
            url: URL do website a ser analisado
            
        Returns:
            CompanyAnalysis: Dados estruturados da empresa
        """
        # Executa scraping da URL
        res = web_scraping_tool.invoke(url)
        if not res.get("ok"):
            return CompanyAnalysis()
        
        # Prepara dados para análise
        text = (res.get("text") or "")[:5000]
        title = res.get("title") or ""
        source = res.get("url") or url
        
        # Prompt estruturado para extração de dados
        prompt = (
            "Extraia SOMENTE JSON válido conforme CompanyAnalysis do conteúdo abaixo.\n"
            "Preencha apenas o que estiver evidente no texto.\n\n"
            f"TÍTULO: {title}\nFONTE: {source}\n\nCONTEÚDO:\n{text}"
        )
        
        try:
            from app.utils import json_call
            return json_call(self.llm, prompt, CompanyAnalysis)
        except Exception as e:
            print(f"Erro na análise estruturada do scraper: {e}")
            return CompanyAnalysis()
    
    def fetch(self, url: str) -> Dict[str, Any]:
        """
        Helper para obter dados brutos de scraping sem análise.
        
        Args:
            url: URL a ser processada
            
        Returns:
            Dict com resultado do scraping (ok, url, title, text, error)
        """
        return web_scraping_tool.invoke(url)
    
    def get_company_info(self, url: str) -> str:
        """
        Método de compatibilidade com API existente.
        
        Retorna informações da empresa em formato de string legível.
        
        Args:
            url: URL a ser analisada
            
        Returns:
            str: Informações formatadas da empresa
        """
        analysis = self.analyze_url(url)
        return f"Empresa: {analysis.name}\nOfertas: {', '.join(analysis.offerings[:3])}\nDiferenciais: {', '.join(analysis.differentiators[:3])}"
    
    def extract_structured_info(self, content: str) -> CompanyAnalysis:
        """
        Extrai informações estruturadas de conteúdo de texto.
        
        Útil quando já se tem o conteúdo da página e não precisa fazer scraping.
        
        Args:
            content: Conteúdo de texto a ser analisado
            
        Returns:
            CompanyAnalysis: Dados estruturados extraídos do conteúdo
        """
        text = (content or "").strip()[:5000]
        if not text:
            return CompanyAnalysis()
        
        try:
            from app.utils import json_call
            prompt = "Extraia SOMENTE JSON válido conforme CompanyAnalysis do conteúdo abaixo.\n\n" + text
            return json_call(self.llm, prompt, CompanyAnalysis)
        except Exception as e:
            print(f"Erro na análise estruturada do scraper (conteúdo bruto): {e}")
            return CompanyAnalysis()