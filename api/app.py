from fastapi import FastAPI
from api.routes import router
from utils.logger import setup_logger
from api.mtproto.startup import init_mtproto
import asyncio


def create_app() -> FastAPI:
    # Loglarni sozlaymiz
    setup_logger()

    app = FastAPI(title="Scraping API")

    # Startup event — backend ishga tushganda Telethon clientni avtomatik ishlatadi
    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(init_mtproto())  # MTProto client async rejimda start bo‘ladi

    # Routerlarni ulaymiz
    app.include_router(router)
    
    return app


# FastAPI app obyektini yaratyapmiz
app = create_app()
