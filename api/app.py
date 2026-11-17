from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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
    if not index.exists():
        return {"detail": "Frontend not built. Run: cd frontend && npm run build"}

    # Root-level static files from frontend/public (robots.txt, sitemap.xml, favicons, og-image).
    if path:
        candidate = (dist / path).resolve()
        if candidate.is_relative_to(dist.resolve()) and candidate.is_file():
            return FileResponse(str(candidate))
        if path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        # The app has a single page; unknown URLs get the app with a real 404 so they aren't indexed.
        return FileResponse(str(index), status_code=404)

    return FileResponse(str(index))
