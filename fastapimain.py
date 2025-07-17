from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import yaml
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

YAML_FILE = "crm_transform.yaml"

@app.get("/")
async def load_editor(request: Request):
    if not os.path.exists(YAML_FILE):
        with open(YAML_FILE, "w") as f:
            yaml.dump({}, f)
    with open(YAML_FILE, "r") as f:
        content = f.read()
    return templates.TemplateResponse("editor.html", {
        "request": request,
        "yaml_content": content,
        "error": None
    })

@app.post("/save")
async def save_yaml(request: Request, yaml_content: str = Form(...)):
    try:
        parsed = yaml.safe_load(yaml_content)
        with open(YAML_FILE, "w") as f:
            yaml.dump(parsed, f)
        return RedirectResponse("/", status_code=303)
    except yaml.YAMLError as e:
        return templates.TemplateResponse("editor.html", {
            "request": request,
            "yaml_content": yaml_content,
            "error": str(e)
        })
