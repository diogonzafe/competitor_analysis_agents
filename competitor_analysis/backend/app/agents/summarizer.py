"""
Agente para resumos e insights
"""
from typing import Dict, Any, List
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from datetime import datetime
import logging
from app.utils import deepseek_client

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def generate_summary_tool(content: str) -> str:
    """Gera resumo estruturado"""
    try:
        llm = deepseek_client.get_llm(temperature=0.2)
        
        prompt = f"""ANÁLISE COMPETITIVA ESTRATÉGICA

Dados coletados:
{content[:2000]}

Gere uma análise competitiva estruturada focada em:

**1. IDENTIFICAÇÃO DA EMPRESA**
- Nome/posicionamento da marca
- Setor de atuação
- Tamanho/estágio da empresa

**2. PROPOSTA DE VALOR**
- Produtos/serviços principais
- Diferenciais únicos
- Benefícios para clientes

**3. ESTRATÉGIA COMPETITIVA**
- Pontos fortes identificados
- Vantagens competitivas
- Posicionamento no mercado

**4. OPORTUNIDADES E AMEAÇAS**
- Oportunidades de crescimento
- Riscos competitivos
- Gaps no mercado

**5. INFORMAÇÕES TÁTICAS**
- Preços/planos mencionados
- Contato/comunicação
- Tecnologias utilizadas

Seja objetivo, estratégico e focado em insights acionáveis para análise competitiva."""
        
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        return f"Erro no resumo: {str(e)}"

@tool
def extract_insights_tool(content: str) -> str:
    """Extrai insights estratégicos"""
    try:
        llm = deepseek_client.get_llm(temperature=0.4)
        
        prompt = f"""Identifique insights estratégicos:

{content[:2000]}

Identifique:
1. Oportunidades de mercado
2. Ameaças competitivas
3. Pontos de melhoria
4. Tendências do setor
5. Recomendações estratégicas

Seja específico e acionável."""
        
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        return f"Erro nos insights: {str(e)}"

class SummarizerAgent:
    """Agente para resumos e insights"""
    
    def __init__(self):
        self.llm = deepseek_client.get_llm(temperature=0.3)
        self.agent = create_react_agent(
            model=self.llm,
            tools=[generate_summary_tool, extract_insights_tool],
            prompt="""Você é um especialista em análise estratégica.

Tarefas:
1. Analisar dados de concorrentes
2. Gerar resumos estruturados
3. Extrair insights estratégicos
4. Identificar oportunidades e ameaças

Use as ferramentas disponíveis de forma eficiente."""
        )
    
    
    def quick_summary(self, content: str) -> str:
        """Resumo rápido otimizado"""
        try:
            logger.info(f"SUMMARIZER: Iniciando análise estratégica")
            logger.debug(f"SUMMARIZER: Tamanho do conteúdo recebido: {len(content)} caracteres")
            
            llm = deepseek_client.get_llm(temperature=0.2)
            
            prompt = f"""ANÁLISE COMPETITIVA ESTRATÉGICA

Dados coletados:
{content[:2000]}

Gere uma análise competitiva estruturada focada em:

**1. IDENTIFICAÇÃO DA EMPRESA**
- Nome/posicionamento da marca
- Setor de atuação
- Tamanho/estágio da empresa

**2. PROPOSTA DE VALOR**
- Produtos/serviços principais
- Diferenciais únicos
- Benefícios para clientes

**3. ESTRATÉGIA COMPETITIVA**
- Pontos fortes identificados
- Vantagens competitivas
- Posicionamento no mercado

**4. OPORTUNIDADES E AMEAÇAS**
- Oportunidades de crescimento
- Riscos competitivos
- Gaps no mercado

**5. INFORMAÇÕES TÁTICAS**
- Preços/planos mencionados
- Contato/comunicação
- Tecnologias utilizadas

Seja objetivo, estratégico e focado em insights acionáveis para análise competitiva."""
            
            logger.info(f"SUMMARIZER: Enviando prompt para DeepSeek API")
            response = llm.invoke(prompt)
            logger.info(f"SUMMARIZER: Análise estratégica concluída")
            logger.debug(f"SUMMARIZER: Resumo gerado: {response.content[:200]}...")
            
            return response.content
            
        except Exception as e:
            logger.error(f"SUMMARIZER: Erro na análise estratégica: {str(e)}")
            return f"Erro: {str(e)}"
    
    def extract_key_points(self, content: str) -> List[str]:
        """Extração otimizada de pontos-chave"""
        try:
            llm = deepseek_client.get_llm(temperature=0.1)
            
            prompt = f"""Extraia 5 pontos-chave:

{content[:1000]}

Retorne apenas lista numerada."""
            
            response = llm.invoke(prompt)
            lines = response.content.strip().split('\n')
            points = [line.strip() for line in lines 
                     if line.strip() and line.strip()[0].isdigit()]
            
            return points[:5] if points else ["Nenhum ponto-chave"]
            
        except Exception as e:
            return [f"Erro: {str(e)}"]
    