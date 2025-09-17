"""
Summarizer Agent - Análise competitiva e geração de insights

"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import phonenumbers
from price_parser import Price
from urllib.parse import urlparse
import json
from app.utils import deepseek_client


class CompetitiveAnalysis(BaseModel):
    """
    Modelo de dados.
 
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
    """
    text = (content or "").strip()[:3000]  
    if not text:
        return {"phones": [], "urls": [], "domains": []}
    
    # Extrai telefones brasileiros
    phones = []
    try:
        for m in phonenumbers.PhoneNumberMatcher(text, "BR"):
            phones.append(phonenumbers.format_number(m.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
            if len(phones) >= 10:
                break
    except Exception:
        pass  # Continua mesmo se falhar
    
    # Extrai URLs e domínios
    try:
        urls = list(dict.fromkeys(list(find_urls(text))))[:15] 
        domains = list(dict.fromkeys([urlparse(u).netloc for u in urls if u]))[:15]
    except Exception:
        urls, domains = [], []
    
    return {
        "phones": list(dict.fromkeys(phones))[:10],  
        "urls": urls,
        "domains": domains
    }

@tool("extract_pricing_info")
def extract_pricing_info(content: str) -> Dict[str, Any]:
    """
    Tool para extrair informações de preços de texto (otimizada).
    """
    text = (content or "").strip()[:3000] 
    if not text:
        return {"prices": []}
    
    prices, seen = [], set()
    
    # Processa tokens de forma mais eficiente
    tokens = text.replace("\n", " ").split()[:500]  
    
    for tok in tokens:
        try:
            p = Price.fromstring(tok)
            if p.amount is not None:
                cur = (p.currency or "").upper()
                key = (float(p.amount), cur)
                
                # Evita duplicatas baseadas em valor e moeda
                if key not in seen:
                    seen.add(key)
                    prices.append({"amount": key[0], "currency": cur, "raw": tok})
            
            # Limita a 25 preços para melhor performance
            if len(prices) >= 25:
                break
        except Exception:
            continue  # Pula tokens problemáticos
    
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
        self.llm = deepseek_client.get_llm(temperature=0.2) 
        
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
        Gera análise competitiva usando ReAct Agent.
        """
        text = (content or "").strip()[:3500] 

        try:
            # Usa o ReAct Agent para análise completa
            result = self.agent.invoke({
                "messages": [HumanMessage(content=f"Analise este conteúdo competitivo: {text}")]
            })
            
            # Extrai dados do resultado do agente
            if hasattr(result, 'messages') and result.messages:
                agent_content = result.messages[-1].content
            elif hasattr(result, 'content'):
                agent_content = result.content
            else:
                agent_content = str(result)
            
            # Extrai dados estruturados diretamente
            return self._extract_analysis_from_content(agent_content, text)
            
        except Exception as e:
            print(f"Erro na análise com ReAct Agent: {e}")
            return CompetitiveAnalysis()

    def _extract_analysis_from_content(self, agent_content: str, original_text: str) -> CompetitiveAnalysis:
        """
        Extrai dados estruturados do conteúdo do agente.
        """
        try:
            from app.utils import json_call
            prompt = (
                "Com base na análise do agente abaixo, extraia SOMENTE JSON válido conforme CompetitiveAnalysis:\n"
                '{"empresa": "nome da empresa", "proposta_valor": "proposta de valor", '
                '"fortalezas": ["fortaleza1", "fortaleza2"], "ameacas": ["ameaça1", "ameaça2"], '
                '"oportunidades": ["oportunidade1", "oportunidade2"], "taticas": {"precos": "info preços", "contatos": "info contatos"}, '
                '"recomendacoes": ["recomendação1", "recomendação2"]}\n\n'
                f"ANÁLISE DO AGENTE:\n{agent_content}\n\n"
                f"TEXTO ORIGINAL:\n{original_text}"
            )
            return json_call(self.llm, prompt, CompetitiveAnalysis)
        except Exception as e:
            print(f"Erro na extração da análise: {e}")
            return CompetitiveAnalysis()
    
    def quick_summary(self, content: str) -> str:
        """
        Gera resumo executivo da análise competitiva.
        """
        a = self.analyze(content)
        forts = ", ".join(a.fortalezas[:3]) if a.fortalezas else "—"
        empresa = a.empresa or "—"
        prop = a.proposta_valor or "—"
        return f"Análise Competitiva: {empresa}\nProposta de Valor: {prop}\nFortalezas: {forts}"
