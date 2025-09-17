"""
Controlador otimizado da API
Seguindo melhores práticas FastAPI 2025
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.agents.scraper import ScraperAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.evaluator import EvaluatorAgent

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos Pydantic
class AnalysisRequest(BaseModel):
    url: HttpUrl
    company_name: Optional[str] = None


# Router da API
router = APIRouter(prefix="/api/v1", tags=["analysis"])

# Instâncias dos agentes
agents = {
    "scraper": ScraperAgent(),
    "summarizer": SummarizerAgent(),
    "evaluator": EvaluatorAgent()
}



@router.post("/quick-analysis")
async def quick_analysis(request: AnalysisRequest):
    """Análise rápida síncrona"""
    try:
        logger.info(f"API: Iniciando análise rápida para {request.url}")
        logger.info(f"API: Empresa: {request.company_name or 'Não informada'}")
        
        # Coleta dados
        logger.info(f"API: Chamando Scraper Agent...")
        scraper_data = agents["scraper"].get_company_info(str(request.url))
        logger.info(f"API: Scraper Agent concluído")
        
        # Gera resumo
        logger.info(f"API: Chamando Summarizer Agent...")
        summary = agents["summarizer"].quick_summary(scraper_data)
        logger.info(f"API: Summarizer Agent concluído")
        
        # Validação
        logger.info(f"API: Chamando Evaluator Agent...")
        validation = agents["evaluator"].quick_validation(summary)
        logger.info(f"API: Evaluator Agent concluído")
        
        logger.info(f"API: Análise rápida concluída com sucesso para {request.url}")
        
        return {
            "success": True,
            "url": str(request.url),
            "data": scraper_data,
            "summary": summary,
            "validation": validation,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"API: Erro na análise rápida para {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {name: "active" for name in agents.keys()}
    }

