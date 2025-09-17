"""
Utilitários e configurações do sistema
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from scrapingant_client import ScrapingAntClient as ScrapingAnt
from langchain_community.document_loaders import ScrapingAntLoader
import httpx

# Carrega variáveis do .env
load_dotenv()

class Config:
    """Configurações da aplicação"""
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    SCRAPINGANT_API_KEY = os.getenv("SCRAPINGANT_API_KEY")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

class DeepSeekClient:
    """Cliente para integração com DeepSeek API"""
    
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1"
        
    def get_llm(self, temperature=0.7, model="deepseek-chat"):
        """Retorna instância do LLM configurada"""
        return ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=model,
            temperature=temperature
        )

class ScrapingAntWrapper:
    """Cliente para integração com ScrapingAnt usando LangChain ScrapingAntLoader"""
    
    def __init__(self):
        self.api_key = Config.SCRAPINGANT_API_KEY
        
    def scrape_url(self, url: str, render_js: bool = True):
        """
        Faz scraping de uma URL usando ScrapingAntLoader do LangChain
        
        Args:
            url: URL para fazer scraping
            render_js: Se deve renderizar JavaScript
            
        Returns:
            Conteúdo da página em formato de documento
        """
        try:
            # Configuração do ScrapingAnt conforme documentação oficial
            scrape_config = {
                "browser": render_js,  # Habilita renderização de JavaScript
                "proxy_type": "datacenter",  # Tipo de proxy
                "proxy_country": "us"  # País do proxy
            }
            
            # Usa ScrapingAntLoader do LangChain conforme documentação
            loader = ScrapingAntLoader(
                urls=[url],
                api_key=self.api_key,
                scrape_config=scrape_config,
                continue_on_failure=True
            )
            
            # Carrega documentos
            documents = loader.load()
            
            if not documents:
                print(f"Nenhum documento encontrado para {url}")
                return []
            
            return documents
            
        except Exception as e:
            print(f"Erro ao fazer scraping de {url}: {e}")
            return []

# Instâncias globais dos clientes
deepseek_client = DeepSeekClient()
scraping_client = ScrapingAntWrapper()
