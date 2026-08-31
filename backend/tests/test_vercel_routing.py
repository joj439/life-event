import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from api.index import app


def test_vercel_json_structure():
    """Verify that vercel.json contains correct build command, output directory, and rewrites."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    vercel_file = root_dir / "vercel.json"
    assert vercel_file.exists(), "vercel.json must exist at repository root"

    data = json.loads(vercel_file.read_text(encoding="utf-8"))
    assert data.get("outputDirectory") == "frontend/dist"
    assert "npm --prefix frontend" in data.get("buildCommand")

    rewrites = data.get("rewrites", [])
    assert len(rewrites) >= 2

    # Check API rewrite rule comes before SPA catch-all
    api_rule = next(r for r in rewrites if "/api/" in r["source"])
    assert api_rule["destination"] == "/api/index.py"

    spa_rule = rewrites[-1]
    assert spa_rule["destination"] == "/index.html"
    assert spa_rule["source"] in ["/(.*)", "/:match*", "/:path*"]


def test_frontend_dist_contains_spa_index():
    """Verify frontend/dist/index.html is built and ready for SPA routing."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    dist_html = root_dir / "frontend" / "dist" / "index.html"
    assert dist_html.exists(), "frontend/dist/index.html must exist after build"

    content = dist_html.read_text(encoding="utf-8")
    assert "root" in content
    assert "<script" in content


def test_api_routes_resolve_via_vercel_app():
    """Verify that FastAPI resolves /api/v1 routes through the Vercel app instance."""
    client = TestClient(app)
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_services = client.get("/api/v1/services")
    assert res_services.status_code == 200
    assert len(res_services.json()) >= 4
