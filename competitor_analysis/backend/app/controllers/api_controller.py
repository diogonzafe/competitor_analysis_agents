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
        url = str(request.url)
        logger.info(f"API: Iniciando análise rápida para {url} | Empresa: {request.company_name or 'N/D'}")

        # 1) Raspagem — use a tool diretamente (determinístico)
        from app.agents.scraper import web_scraping_tool  # importa a tool
        scrape = web_scraping_tool.invoke(url)
        if not scrape.get("ok"):
            return {
                "success": False,
                "url": url,
                "error": scrape.get("error") or "Falha na raspagem",
                "timestamp": datetime.now().isoformat(),
            }

        raw_text = (scrape.get("text") or "")[:5000]
        if not raw_text:
            return {
                "success": False,
                "url": url,
                "error": "Conteúdo vazio após raspagem",
                "timestamp": datetime.now().isoformat(),
            }

        # 2) Estruturado (Scraper opcional) — se quiser extrair empresa/ofertas etc.
        logger.info(f"API: Chamando Scraper Agent...")
        scraper_analysis = agents["scraper"].extract_structured_info(raw_text)
        logger.info(f"API: Scraper Agent concluído")

        # 3) Resumo/insights — Summarizer trabalha em cima do TEXTO
        #    (injete o company_name no prompt implicitamente: prepend no texto)
        prefix = f"Empresa alvo: {request.company_name}\n" if request.company_name else ""
        logger.info(f"API: Chamando Summarizer Agent...")
        analysis = agents["summarizer"].analyze(prefix + raw_text)
        
        # Reforçar nome da empresa quando não detectado
        if request.company_name and not analysis.empresa:
            analysis.empresa = request.company_name
            
        summary = agents["summarizer"].quick_summary(prefix + raw_text)
        logger.info(f"API: Summarizer Agent concluído")

        # 4) Avaliador — avalie o summary (ou o JSON serializado)
        logger.info(f"API: Chamando Evaluator Agent...")
        validation = agents["evaluator"].quick_validation(summary)
        logger.info(f"API: Evaluator Agent concluído")
        
        logger.info(f"API: Análise rápida concluída com sucesso para {url}")
        
        return {
            "success": True,
            "url": url,
            "scrape": {"title": scrape.get("title"), "chars": len(raw_text)},
            "data": scraper_analysis.model_dump(),        # CompanyAnalysis -> dict
            "analysis": analysis.model_dump(),            # CompetitiveAnalysis -> dict
            "summary": summary,                           # human-readable
            "validation": validation.model_dump(),        # EvaluationResult -> dict
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.exception("API: Erro na análise rápida")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {name: "active" for name in agents.keys()}
    }

