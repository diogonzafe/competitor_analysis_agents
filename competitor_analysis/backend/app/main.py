"""
Aplicação principal FastAPI para análise de concorrentes
Seguindo melhores práticas FastAPI 2025
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.controllers.api_controller import router as api_router
from app.utils import Config

# Configuração da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle da aplicação"""
    print("Iniciando Competitor Analysis API...")
    print("Agentes: Scraper, Summarizer, Evaluator")
    print("DeepSeek API: Configurada")
    print("ScrapingAnt: Configurado")
    yield
    print("Encerrando Competitor Analysis API...")

# Cria aplicação FastAPI
app = FastAPI(
    title="Competitor Analysis API",
    description="API para análise de concorrentes com agentes IA",
    version="1.0.0",
    lifespan=lifespan
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui rotas da API
app.include_router(api_router)

# Rota raiz
@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Competitor Analysis API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Handler de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global de exceções"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )

# Função para executar a aplicação
def run_app():
    """Executa a aplicação com uvicorn"""
    uvicorn.run(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info" if not Config.DEBUG else "debug"
    )

if __name__ == "__main__":
    run_app()
