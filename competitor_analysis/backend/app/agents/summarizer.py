"""
Summarizer Agent - Análise competitiva e geração de insights

Este módulo contém o agente responsável por gerar análises competitivas
estruturadas a partir de conteúdo de texto, extraindo insights sobre
proposta de valor, fortalezas, ameaças, oportunidades e recomendações.

Dependências extras: phonenumbers, urlfinderlib, price-parser
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import phonenumbers
from urlfinderlib import find_urls
from price_parser import Price
from urllib.parse import urlparse
import json
from app.utils import deepseek_client


class CompetitiveAnalysis(BaseModel):
    """
    Modelo de dados para análise competitiva completa.
    
    Representa uma análise competitiva estruturada incluindo:
    - Informações básicas da empresa
    - Análise SWOT (fortalezas, ameaças, oportunidades)
    - Proposta de valor e diferenciais
    - Táticas e recomendações estratégicas
    """
    empresa: str = Field(default="", description="Nome da empresa")
    proposta_valor: str = Field(default="", description="Proposta de valor principal")
    fortalezas: List[str] = Field(default_factory=list, description="Pontos fortes da empresa")
    ameacas: List[str] = Field(default_factory=list, description="Ameaças identificadas")
    oportunidades: List[str] = Field(default_factory=list, description="Oportunidades de mercado")
    taticas: Dict[str, Any] = Field(default_factory=dict, description="Táticas identificadas (preços, contatos, etc.)")
    recomendacoes: List[str] = Field(default_factory=list, description="Recomendações estratégicas")

# -------- Tools de Extração de Dados --------

@tool("extract_contact_info")
def extract_contact_info(content: str) -> Dict[str, Any]:
    """
    Tool para extrair informações de contato de texto.
    
    Extrai telefones (formato brasileiro), URLs e domínios de um texto.
    Utiliza bibliotecas especializadas para parsing robusto.
    
    Args:
        content: Texto a ser analisado
        
    Returns:
        Dict com estrutura: {
            "phones": List[str],    # Lista de telefones encontrados
            "urls": List[str],      # Lista de URLs encontradas
            "domains": List[str]    # Lista de domínios extraídos
        }
    """
    text = (content or "").strip()[:4000]
    if not text:
        return {"phones": [], "urls": [], "domains": []}
    
    # Extrai telefones brasileiros
    phones = []
    for m in phonenumbers.PhoneNumberMatcher(text, "BR"):
        phones.append(phonenumbers.format_number(m.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
    
    # Extrai URLs e domínios
    urls = list(dict.fromkeys(list(find_urls(text))))[:20]  # Remove duplicatas e limita a 20
    domains = list(dict.fromkeys([urlparse(u).netloc for u in urls if u]))[:20]
    
    return {
        "phones": list(dict.fromkeys(phones))[:20],  # Remove duplicatas
        "urls": urls,
        "domains": domains
    }

@tool("extract_pricing_info")
def extract_pricing_info(content: str) -> Dict[str, Any]:
    """
    Tool para extrair informações de preços de texto.
    
    Identifica e normaliza valores monetários encontrados no texto,
    extraindo valores, moedas e contexto.
    
    Args:
        content: Texto a ser analisado
        
    Returns:
        Dict com estrutura: {
            "prices": List[Dict]  # Lista de preços com amount, currency e raw
        }
    """
    text = (content or "").strip()[:4000]
    if not text:
        return {"prices": []}
    
    prices, seen = [], set()
    
    # Processa cada token do texto em busca de preços
    for tok in text.replace("\n", " ").split():
        p = Price.fromstring(tok)
        if p.amount is not None:
            cur = (p.currency or "").upper()
            key = (float(p.amount), cur)
            
            # Evita duplicatas baseadas em valor e moeda
            if key not in seen:
                seen.add(key)
                prices.append({"amount": key[0], "currency": cur, "raw": tok})
        
        # Limita a 50 preços para evitar sobrecarga
        if len(prices) >= 50:
            break
    
    return {"prices": prices}

# -------- Agente Principal --------

class SummarizerAgent:
    """
    Agente responsável por análise competitiva e geração de insights.
    
    Este agente combina ferramentas de extração de dados (contatos, preços)
    com análise de LLM para gerar análises competitivas estruturadas.
    
    Funcionalidades principais:
    - Extração de dados específicos (contatos, preços)
    - Análise SWOT (fortalezas, ameaças, oportunidades)
    - Geração de recomendações estratégicas
    - Análise de proposta de valor
    """
    
    def __init__(self):
        """Inicializa o agente com LLM e ferramentas de extração."""
        self.llm = deepseek_client.get_llm(temperature=0.2)  # Temperatura moderada para análise consistente
        
        # Configura agente ReAct com ferramentas de extração
        self.agent = create_react_agent(
            model=self.llm,
            tools=[extract_contact_info, extract_pricing_info],
            prompt=(
                "Você é analista competitivo. Use as ferramentas para extrair CONTATOS e PREÇOS quando houver texto. "
                "Não invente dados; se faltar, deixe vazio. A análise final será JSON (CompetitiveAnalysis)."
            ),
        )

    def analyze(self, content: str) -> CompetitiveAnalysis:
        """
        Gera análise competitiva completa a partir de conteúdo de texto.
        
        Processo:
        1. Executa agente ReAct para extrair dados específicos
        2. Chama ferramentas de extração (contatos, preços)
        3. Combina dados extraídos com análise de LLM
        4. Gera análise competitiva estruturada
        
        Args:
            content: Conteúdo de texto a ser analisado
            
        Returns:
            CompetitiveAnalysis: Análise competitiva estruturada
        """
        text = (content or "").strip()[:4000]

        try:
            # Executa agente ReAct para análise inicial
            _ = self.agent.invoke({"messages": [HumanMessage(content=f"Analise este conteúdo: {text}")]})
        except Exception:
            pass  # Continua mesmo se o agente falhar

        # Extrai dados específicos usando ferramentas
        contacts = extract_contact_info.invoke(text)
        prices = extract_pricing_info.invoke(text)

        try:
            from app.utils import json_call
            # Prompt estruturado para análise competitiva
            prompt = (
                "Com base no TEXTO e DADOS abaixo, retorne APENAS um JSON válido com as seguintes chaves:\n"
                '{"empresa": "nome da empresa", "proposta_valor": "proposta de valor", '
                '"fortalezas": ["fortaleza1", "fortaleza2"], "ameacas": ["ameaça1", "ameaça2"], '
                '"oportunidades": ["oportunidade1", "oportunidade2"], "taticas": {"precos": "info preços", "contatos": "info contatos"}, '
                '"recomendacoes": ["recomendação1", "recomendação2"]}\n\n'
                f"DADOS_CONTATOS: {json.dumps(contacts, ensure_ascii=False)}\n"
                f"DADOS_PREÇOS: {json.dumps(prices, ensure_ascii=False)}\n"
                f"TEXTO: {text}"
            )
            return json_call(self.llm, prompt, CompetitiveAnalysis)
        except Exception as e:
            print(f"Erro na análise estruturada: {e}")
            return CompetitiveAnalysis()
    
    def quick_summary(self, content: str) -> str:
        """
        Gera resumo executivo da análise competitiva.
        
        Método de compatibilidade com API existente que retorna
        um resumo legível das principais informações da análise.
        
        Args:
            content: Conteúdo a ser analisado
            
        Returns:
            str: Resumo executivo formatado
        """
        a = self.analyze(content)
        forts = ", ".join(a.fortalezas[:3]) if a.fortalezas else "—"
        empresa = a.empresa or "—"
        prop = a.proposta_valor or "—"
        return f"Análise Competitiva: {empresa}\nProposta de Valor: {prop}\nFortalezas: {forts}"