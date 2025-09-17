"""
Utilitários e configurações do sistema

Este módulo contém classes utilitárias para integração com APIs externas
(DeepSeek e ScrapingAnt) e funções auxiliares para parsing de JSON.
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
    """
    Configurações centralizadas da aplicação.
    
    Carrega todas as configurações necessárias a partir de variáveis de ambiente,
    incluindo chaves de API, configurações de servidor e flags de debug.
    """
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    SCRAPINGANT_API_KEY = os.getenv("SCRAPINGANT_API_KEY")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

class DeepSeekClient:
    """
    Cliente para integração com DeepSeek API.
    
    Fornece uma interface simplificada para criar instâncias de LLM
    configuradas para trabalhar com a API do DeepSeek, incluindo
    configurações otimizadas para evitar erros de response_format.
    """
    
    def __init__(self):
        """Inicializa o cliente com configurações da API."""
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1"
        
    def get_llm(self, temperature=0.7, model="deepseek-chat"):
        """
        Cria e retorna uma instância de LLM configurada para DeepSeek.
        
        Configurações otimizadas:
        - Sem response_format (evita erro 400)
        - Timeout de 60 segundos
        - Máximo 1 retry para evitar loops
        - model_kwargs vazio para compatibilidade
        
        Args:
            temperature: Temperatura para controle de criatividade (0.0-1.0)
            model: Nome do modelo DeepSeek a ser usado
            
        Returns:
            ChatOpenAI: Instância configurada do LLM
            
        Raises:
            ValueError: Se a chave da API não estiver configurada
        """
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY não configurada")
        
        return ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=model,
            temperature=temperature,
            timeout=60.0,
            max_retries=1,  # evita loop de tentativas
            model_kwargs={}  # sem response_format
        )

class ScrapingAntWrapper:
    """
    Cliente para integração com ScrapingAnt usando LangChain ScrapingAntLoader.
    
    Fornece uma interface simplificada para web scraping usando o serviço
    ScrapingAnt, com suporte a renderização de JavaScript e configurações
    de proxy para contornar bloqueios de websites.
    """
    
    def __init__(self):
        """Inicializa o wrapper com a chave da API do ScrapingAnt."""
        self.api_key = Config.SCRAPINGANT_API_KEY
        
    def scrape_url(self, url: str, render_js: bool = True, timeout: int = 25):
        """
        Executa web scraping de uma URL usando ScrapingAnt.
        
        Utiliza o ScrapingAntLoader do LangChain para fazer scraping
        de websites, incluindo renderização de JavaScript quando necessário.
        
        Args:
            url: URL do website a ser analisado
            render_js: Se deve renderizar JavaScript (útil para SPAs)
            timeout: Timeout em segundos para a operação
            
        Returns:
            List[Document]: Lista de documentos LangChain com o conteúdo da página
            
        Note:
            Retorna lista vazia em caso de erro ou se nenhum conteúdo for encontrado
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

def strip_code_fences(s: str) -> str:
    """
    Remove code fences (```json, ```) de uma string.
    
    Função auxiliar para limpar respostas de LLM que podem vir
    envolvidas em code fences, facilitando o parsing de JSON.
    
    Args:
        s: String que pode conter code fences
        
    Returns:
        str: String limpa sem code fences
    """
    s = s.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()

def json_call(llm, prompt: str, fallback_class):
    """
    Helper para chamar LLM e fazer parsing JSON robusto.
    
    Combina chamada de LLM com parsing de JSON e tratamento de erros,
    retornando uma instância da classe fallback em caso de falha.
    
    Args:
        llm: Instância do LLM para fazer a chamada
        prompt: Prompt a ser enviado para o LLM
        fallback_class: Classe para instanciar em caso de erro
        
    Returns:
        Instância da fallback_class com dados parseados ou valores padrão
    """
    try:
        response = llm.invoke(prompt)
        content = strip_code_fences(response.content)
        import json
        data = json.loads(content)
        return fallback_class(**data)
    except Exception as e:
        print(f"Erro no parsing JSON: {e}")
        return fallback_class()

# Instâncias globais dos clientes para uso em toda a aplicação
deepseek_client = DeepSeekClient()
scraping_client = ScrapingAntWrapper()
