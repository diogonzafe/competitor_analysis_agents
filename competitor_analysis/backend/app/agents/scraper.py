"""
Agente para coleta de dados de concorrentes
"""
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import re
import asyncio
import logging
from datetime import datetime
from app.utils import scraping_client, deepseek_client

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def web_scraping_tool(url: str) -> str:
    """Coleta dados de uma URL usando ScrapingAnta"""
    try:
        documents = scraping_client.scrape_url(url)
        if not documents:
            return f"Erro: Dados não encontrados em {url}"
        
        content = _process_content_optimized(documents[0].page_content)
        return f"Dados coletados de {url}:\n{content}"
        
    except Exception as e:
        return f"Erro no scraping: {str(e)}"

def _process_content_optimized(content: str) -> str:
    """Processamento conteúdo"""
    # Remove HTML
    clean_text = re.sub(r'<[^>]+>', '', content)
    # Normaliza espaços
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    # Limita tamanho
    return clean_text[:3000] + "..." if len(clean_text) > 3000 else clean_text

class ScraperAgent:
    """Agente para coleta de dados"""
    
    def __init__(self):
        self.llm = deepseek_client.get_llm(temperature=0.2)
        self.agent = create_react_agent(
            model=self.llm,
            tools=[web_scraping_tool],
            prompt="""Você é um especialista em coleta de dados de concorrentes.
            
            Tarefas:
            1. Coletar dados de URLs fornecidas
            2. Extrair informações comerciais relevantes
            3. Identificar produtos, serviços, preços
            4. Retornar dados estruturados
            
            Seja conciso e focado em informações úteis para análise competitiva."""
        )
    
    
    def get_company_info(self, url: str) -> str:
        """Coleta básica síncrona"""
        try:
            logger.info(f"SCRAPER: Iniciando coleta de dados de {url}")
            documents = scraping_client.scrape_url(url)
            if not documents:
                logger.warning(f"SCRAPER: Nenhum documento encontrado para {url}")
                return "Dados não encontrados"
            
            logger.info(f"SCRAPER: Dados coletados com sucesso de {url}")
            logger.debug(f"SCRAPER: Tamanho do conteúdo: {len(documents[0].page_content)} caracteres")
            
            result = self._extract_key_info_optimized(documents[0].page_content)
            logger.info(f"SCRAPER: Extração de informações concluída para {url}")
            logger.debug(f"SCRAPER: Resultado extraído: {result[:200]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"SCRAPER: Erro ao coletar dados de {url}: {str(e)}")
            return f"Erro: {str(e)}"
    
    
    def _extract_key_info_optimized(self, content: str) -> str:
        """Extração otimizada para análise competitiva"""
        # Padrões melhorados para extração
        patterns = {
            "title": r'<title[^>]*>(.*?)</title>',
            "description": r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
            "h1": r'<h1[^>]*>(.*?)</h1>',
            "h2": r'<h2[^>]*>(.*?)</h2>',
            "keywords": r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']*)["\']',
            "og_title": r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']',
            "og_description": r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']*)["\']'
        }
        
        info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                clean_text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if clean_text:
                    info[key] = clean_text
        
        # Extrair texto principal (pular navegação, rodapé, etc.)
        main_content = self._extract_main_content(content)
        
        # Estruturar informações para análise competitiva
        result = []
        result.append(f"Título: {info.get('title', info.get('og_title', 'N/A'))}")
        result.append(f"Descrição: {info.get('description', info.get('og_description', 'N/A'))}")
        
        if info.get('h1'):
            result.append(f"Headline Principal: {info.get('h1')}")
        
        if info.get('keywords'):
            result.append(f"Palavras-chave: {info.get('keywords')}")
        
        result.append(f"\nConteúdo Principal:")
        result.append(main_content)
        
        return "\n".join(result)
    
    def _extract_main_content(self, content: str) -> str:
        """Extrai conteúdo principal da página"""
        # Remove scripts, styles, nav, footer
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<nav[^>]*>.*?</nav>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<footer[^>]*>.*?</footer>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<header[^>]*>.*?</header>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        clean_content = re.sub(r'<[^>]+>', ' ', content)
        
        # Normaliza espaços
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Remove texto muito comum (navegação, etc.)
        common_texts = [
            'pular para o conteúdo', 'pular para navegação', 'pular para rodapé',
            'menu', 'navegação', 'início', 'sobre', 'contato', 'login',
            'cadastro', 'buscar', 'pesquisar', 'cookie', 'privacidade'
        ]
        
        for text in common_texts:
            clean_content = re.sub(text, '', clean_content, flags=re.IGNORECASE)
        
        # Foca em parágrafos e headings
        sentences = clean_content.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Ignora frases muito curtas
                # Prioriza frases com palavras-chave de negócio
                business_keywords = [
                    'empresa', 'produto', 'serviço', 'solução', 'tecnologia',
                    'inovação', 'crescimento', 'resultado', 'eficiencia', 'produtividade',
                    'cliente', 'mercado', 'competitivo', 'estratégia', 'negócio'
                ]
                
                if any(keyword in sentence.lower() for keyword in business_keywords):
                    relevant_sentences.append(sentence)
                elif len(relevant_sentences) < 10:  # Limita a 10 frases relevantes
                    relevant_sentences.append(sentence)
        
        return '. '.join(relevant_sentences[:10]) + '...'
