import logging
import os
import sys
from contextlib import asynccontextmanager

import yaml
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from fastapi_versionizer.versionizer import Versionizer
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.exceptions import HTTPException as StarletteHTTPException

# Add the project root directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.apis import api_router
from app.configs import APP_SETTINGS
from app.database.postgres.session import init_db
from app.exceptions import (NeedLoginException,
                            need_login_exception_handler,
                            validate_exception_handler,
                            endpoint_not_found_exception_handler)
from app.middlewares import CustomAuthMiddleware
from app.otel import OTELInstrumentInitializer

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    instrumentator.expose(app)
    await init_db()
    yield


app = FastAPI(
    title=APP_SETTINGS.APP_TITLE,
    version=APP_SETTINGS.APP_VERSION,
    description=APP_SETTINGS.APP_DESCRIPTION,
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.add_middleware(CustomAuthMiddleware, whitelist=APP_SETTINGS.API_WHITELIST)

# This should be the last middleware, if any custom middleware, add before this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=APP_SETTINGS.CORS_ALLOW_ORIGINS,
    allow_credentials=APP_SETTINGS.CORS_ALLOW_CREDENTIALS,
    max_age=APP_SETTINGS.CORS_MAX_AGE,
    allow_methods=APP_SETTINGS.CORS_ALLOW_METHODS,
    allow_headers=APP_SETTINGS.CORS_ALLOW_HEADERS,
)

app.include_router(api_router)

# add exception handlers
app.add_exception_handler(StarletteHTTPException, endpoint_not_found_exception_handler)
app.add_exception_handler(NeedLoginException, need_login_exception_handler)
app.add_exception_handler(RequestValidationError, validate_exception_handler)

add_pagination(app)

versions = Versionizer(
    app=app,
    prefix_format="/api/v{major}",
    semantic_version_format="{major}",
    include_versions_route=True,
    sort_routes=True,
).versionize()


def init_otel(app):
    if APP_SETTINGS.OTEL_ENABLED is False:
        return

    otel_initializer = OTELInstrumentInitializer(service_name=APP_SETTINGS.APP_TITLE)
    otel_trace_provider = otel_initializer.init_trace_provider(mode=APP_SETTINGS.OTEL_MODE,
                                                               endpoint=APP_SETTINGS.OTEL_ENDPOINT)
    FastAPIInstrumentor.instrument_app(app=app,
                                       tracer_provider=otel_trace_provider,
                                       excluded_urls=", ".join(APP_SETTINGS.OTEL_EXCLUDED_URLS))


init_otel(app)

instrumentator = Instrumentator(should_group_status_codes=False,
                                should_ignore_untemplated=True,
                                should_instrument_requests_inprogress=True,
                                inprogress_name="inprogress",
                                excluded_handlers=["/metrics"],
                                inprogress_labels=True).instrument(app,
                                                                   metric_namespace="portal_backend",
                                                                   metric_subsystem="backend")


@app.get("/")
async def index():
    return {"success": True}


if __name__ == "__main__":
    openapi_schema = app.openapi()
    openapi_schema["openapi"] = "3.0.3"
    with open("docs/swagger.yaml", "w") as yamlfile:
        yaml.dump(openapi_schema, yamlfile, allow_unicode=True)

    # config = uvicorn.Config(app, port=8000, log_level="info")
    # server = uvicorn.Server(config)
    # server.run()
