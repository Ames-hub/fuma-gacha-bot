from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request, FastAPI
import importlib
import logging
import os

fastapi = FastAPI()
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# noinspection PyUnusedLocal
@fastapi.exception_handler(401)
async def unauthorized_handler(request: Request, exc):
    logging.info(f"IP {request.client.host} Attempted to connect but was Unauthorized")
    # A Basic web page with the entire purpose of redirecting the user away from the page.
    content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <title>REDIRECTING</title>
</head>
<body>
<h1>You are being redirected after an unauthorized connection.</h1>
<script>
    window.location.href = "/login";
</script>
</body>
    """
    return HTMLResponse(content, status_code=401)

@fastapi.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt(request: Request):
    with open('robots.txt') as f:
        data = f.read()
    return data

# noinspection PyUnusedLocal
@fastapi.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    with open("webpanel/404.html") as f:
        notfoundpage = f.read()

    return HTMLResponse(notfoundpage, status_code=404)

@fastapi.get("/favicon.ico", include_in_schema=False)
async def favicon():
    image_path = "webpanel/favicon.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            return HTMLResponse(content=image_file.read(), media_type="image/png")
    else:
        raise FileNotFoundError("No favicon.png found.")

modules_dir = os.path.join(os.getcwd(), "webpanel", "modules")

for module_name in os.listdir(modules_dir):
    module_path = os.path.join(modules_dir, module_name)

    if os.path.isdir(module_path):
        # 🔧 Mount static files if they exist
        static_path = os.path.join(module_path, "static")
        if os.path.isdir(static_path):
            mount_path = f"/static/{module_name}"
            fastapi.mount(mount_path, StaticFiles(directory=static_path), name=f"{module_name}_static")
            logging.info(f"[✓] Mounted static files for {module_name} at {mount_path}")

        # 📦 Import and register router
        routes_file = os.path.join(module_path, "routes.py")
        if os.path.exists(routes_file):
            try:
                module = importlib.import_module(f"webpanel.modules.{module_name}.routes")
                if hasattr(module, "router"):
                    fastapi.include_router(module.router)
                    logging.info(f"[✓] Loaded router from {module_name} module")
                else:
                    logging.info(f"[!] No 'router' found in {module_name}.routes")
            except Exception as err:
                logging.error(f"[✗] Failed to load {module_name}: {err}", exc_info=err)