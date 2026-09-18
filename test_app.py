from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_block_unready_candidate():
    payload = {
        "name": "テスト商品",
        "repo_url": "https://github.com/example/example",
        "license_ok": False,
        "japanese_ui_ready": False,
        "monthly_price_yen": 980,
        "api_cost_per_use_yen": 10,
        "expected_uses_per_month": 10,
        "payment_fee_rate": 0.036,
        "infra_cost_monthly_yen": 100,
        "traffic_plan": []
    }
    r = client.post("/api/candidates", json=payload)
    data = r.json()
    assert data["publishable"] is False
    assert "ライセンス未確認" in data["blockers"]
    assert "日本語UI未検収" in data["blockers"]
    assert "集客導線なし" in data["blockers"]

def test_publishable_candidate():
    payload = {
        "name": "販売可能商品",
        "repo_url": "https://github.com/example/example",
        "license_ok": True,
        "japanese_ui_ready": True,
        "monthly_price_yen": 1980,
        "api_cost_per_use_yen": 2,
        "expected_uses_per_month": 20,
        "payment_fee_rate": 0.036,
        "infra_cost_monthly_yen": 100,
        "traffic_plan": ["SEO", "ココナラ"]
    }
    r = client.post("/api/candidates", json=payload)
    data = r.json()
    assert data["publishable"] is True
