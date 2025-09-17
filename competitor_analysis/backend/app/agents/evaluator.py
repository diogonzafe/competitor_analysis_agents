"""
Evaluator Agent - Validação de qualidade das análises competitivas

"""
from typing import List, Union
from pydantic import BaseModel, Field
from app.utils import deepseek_client


class EvaluationResult(BaseModel):
    """
    Modelo de dados para resultados de avaliação de qualidade.
    """
    completo: bool = Field(description="A análise cobre os pontos-chave?")
    relevante: bool = Field(description="A análise é relevante para a tarefa?")
    acionavel: bool = Field(description="Traz recomendações práticas?")
    pontos_fortes: List[str] = Field(default_factory=list, description="Pontos fortes identificados na análise")
    melhorias: List[str] = Field(default_factory=list, description="Sugestões de melhoria para a análise")


class EvaluatorAgent:
    """
    Agente responsável por validar a qualidade das análises competitivas.(Chamada API somente, em prod usar outro provedor se LLM para o design pattern evaluator)
    To-do: corrigir resposta após avaliação negativa
    """
    
    def __init__(self):
        """Inicializa"""
        self.llm = deepseek_client.get_llm(temperature=0.1)

    def quick_validation(self, content: str) -> EvaluationResult:
        """
        Valida a qualidade da análise.
        """
        # limita o tamanho do texto de entrada
        text = (content or "").strip()[:1200]
        if not text:
            return EvaluationResult(completo=False, relevante=False, acionavel=False)
        
        try:
            from app.utils import json_call
            # métricas de qualidade
            prompt = (
                "Avalie a análise competitiva abaixo e retorne APENAS um JSON válido com as seguintes chaves:\n"
                '{"completo": true/false, "relevante": true/false, "acionavel": true/false, '
                '"pontos_fortes": ["ponto1", "ponto2"], "melhorias": ["melhoria1", "melhoria2"]}\n\n'
                f"{text}"
            )
            return json_call(self.llm, prompt, EvaluationResult)
        except Exception as e:
            print(f"Erro na avaliação estruturada: {e}")
            return EvaluationResult(completo=False, relevante=False, acionavel=False)
