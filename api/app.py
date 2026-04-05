from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from api.models import CalculateRequest, GraphResponse, SummaryResponse
from api.services import build_graph_response, build_summary_response

app = FastAPI(title="Kalkulacka refinancovani hypoteky")


@app.post("/api/graph", response_model=GraphResponse)
def api_graph(req: CalculateRequest):
    return build_graph_response(req)


@app.post("/api/summary", response_model=SummaryResponse)
def api_summary(req: CalculateRequest):
    return build_summary_response(req)


# Serve Vue built files if they exist
dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if (dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(dist / "assets")), name="assets")


@app.get("/{path:path}")
async def spa(path: str):
    index = dist / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"detail": "Frontend not built. Run: cd frontend && npm run build"}
