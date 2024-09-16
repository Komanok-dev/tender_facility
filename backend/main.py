# from fastapi import FastAPI
# from contextlib import asynccontextmanager

# from backend.endpoints import router
# from backend.database import create_tables


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     create_tables()
#     yield

# app = FastAPI(lifespan=lifespan)
# app.include_router(router)


from backend.app_factory import create_app

app = create_app()
