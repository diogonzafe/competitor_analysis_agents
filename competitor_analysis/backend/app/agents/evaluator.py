"""
Evaluator
"""
from typing import Dict, Any
import logging
from datetime import datetime
from app.utils import deepseek_client

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvaluatorAgent:
    """Evaluator com design pattern de melhoria"""
    
    def __init__(self):
        self.llm = deepseek_client.get_llm(temperature=0.1)
    
    
    
    def quick_validation(self, content: str) -> str:
        """Validação rápida"""
        try:
            logger.info(f"EVALUATOR: Iniciando validação do sistema")
            logger.debug(f"EVALUATOR: Tamanho do conteúdo para validação: {len(content)} caracteres")
            
            llm = deepseek_client.get_llm(temperature=0.1)
            
            prompt = f"""Validação da análise competitiva:

{content[:600]}

Avalie a qualidade da análise:
1. Completo? (Sim/Não)
2. Relevante? (Sim/Não) 
3. Acionável? (Sim/Não)
4. Pontos fortes identificados?
5. Sugestões de melhoria?

Seja objetivo e construtivo."""
            
            logger.info(f"EVALUATOR: Enviando prompt de validação para DeepSeek API")
            response = llm.invoke(prompt)
            logger.info(f"EVALUATOR: Validação concluída")
            logger.debug(f"EVALUATOR: Resultado da validação: {response.content[:200]}...")
            
            return response.content
            
        except Exception as e:
            logger.error(f"EVALUATOR: Erro na validação: {str(e)}")
            return f"Erro: {str(e)}"
    
    def check_completeness(self, data: Dict[str, Any]) -> bool:
        """Verifica completude"""
        return (data.get("success", False) and 
                "data" in data and 
                "timestamp" in data)
