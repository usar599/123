from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="AI Profit Orchestrator V2", version="0.1.0")

class Candidate(BaseModel):
    name: str
    repo_url: str
    license_ok: bool = False
    japanese_ui_ready: bool = False
    monthly_price_yen: int = 0
    api_cost_per_use_yen: float = 0
    expected_uses_per_month: int = 0
    payment_fee_rate: float = 0.036
    infra_cost_monthly_yen: int = 0
    traffic_plan: List[str] = []

    @property
    def revenue(self) -> int:
        return self.monthly_price_yen

    @property
    def api_cost(self) -> float:
        return self.api_cost_per_use_yen * self.expected_uses_per_month

    @property
    def payment_fee(self) -> float:
        return self.revenue * self.payment_fee_rate

    @property
    def gross_profit(self) -> float:
        return self.revenue - self.api_cost - self.payment_fee - self.infra_cost_monthly_yen

    @property
    def gross_margin(self) -> float:
        return 0 if self.revenue <= 0 else self.gross_profit / self.revenue

    def blockers(self) -> List[str]:
        b=[]
        if not self.license_ok:
            b.append("ライセンス未確認")
        if not self.japanese_ui_ready:
            b.append("日本語UI未検収")
        if self.monthly_price_yen <= 0:
            b.append("販売価格未設定")
        if self.gross_margin < 0.60:
            b.append("粗利率60%未満")
        if not self.traffic_plan:
            b.append("集客導線なし")
        return b

candidates: List[Candidate] = []
metrics = {"impressions":0,"clicks":0,"signups":0,"purchases":0,"revenue":0,"api_cost":0}

@app.get("/api/health")
def health():
    return {"ok": True, "service": "v2"}

@app.post("/api/candidates")
def add_candidate(c: Candidate):
    candidates.append(c)
    return {"status":"accepted","candidate":c,"blockers":c.blockers(),"publishable":len(c.blockers())==0}

@app.get("/api/candidates")
def list_candidates():
    return [
        {
            **c.model_dump(),
            "gross_profit": round(c.gross_profit,2),
            "gross_margin": round(c.gross_margin,4),
            "blockers": c.blockers(),
            "publishable": len(c.blockers())==0,
        }
        for c in candidates
    ]

@app.post("/api/metrics")
def add_metrics(impressions:int=0, clicks:int=0, signups:int=0, purchases:int=0, revenue:int=0, api_cost:float=0):
    metrics["impressions"] += impressions
    metrics["clicks"] += clicks
    metrics["signups"] += signups
    metrics["purchases"] += purchases
    metrics["revenue"] += revenue
    metrics["api_cost"] += api_cost
    return {"metrics":metrics,"diagnosis":diagnose()}

@app.get("/api/diagnosis")
def diagnose():
    imp=metrics["impressions"]
    clk=metrics["clicks"]
    sig=metrics["signups"]
    pur=metrics["purchases"]
    rev=metrics["revenue"]
    cost=metrics["api_cost"]
    if imp < 100:
        return {"state":"流入不足","next":"SEO・SNS・販売プラットフォーム露出を増やす"}
    if clk / max(imp,1) < 0.03:
        return {"state":"訴求不足","next":"タイトル・サムネ・ベネフィットを改善"}
    if sig / max(clk,1) < 0.10:
        return {"state":"登録不足","next":"LP・無料体験・フォームを改善"}
    if pur / max(sig,1) < 0.05:
        return {"state":"購入率不足","next":"価格・オファー・証拠・返金条件を改善"}
    if rev <= cost:
        return {"state":"赤字","next":"価格引上げ・利用上限・安価APIへの切替"}
    return {"state":"勝ち筋候補","next":"関連商品・SEOページ・販路を拡張"}

@app.get("/", response_class=HTMLResponse)
def home():
    return """<!doctype html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>AI Profit Orchestrator V2</title><style>body{font-family:system-ui;margin:0;background:#f6f7f9;color:#111}.wrap{max-width:980px;margin:40px auto;padding:0 16px}.card{background:#fff;border:1px solid #ddd;border-radius:14px;padding:20px;margin:14px 0}h1{font-size:28px}.ok{color:#0a7}.ng{color:#c33}code{background:#f0f0f0;padding:2px 6px;border-radius:6px}</style></head><body><div class='wrap'><h1>AI Profit Orchestrator V2</h1><div class='card'><h2>基本方針</h2><p>新規開発より先に既存OSSを探索し、使えるOSSがある場合は流用を優先します。</p><p>公開条件：ライセンス確認、日本語UI、粗利率60%以上、集客導線あり。</p></div><div class='card'><h2>赤字防止</h2><p>API原価・決済手数料・インフラ費を販売前に計算し、条件未達は公開停止。</p></div><div class='card'><h2>自走ループ</h2><p>OSS探索 → 日本向け商品化 → 公開 → SEO/SNS/販売先展開 → 計測 → 原因分解 → 改善 → 勝ち筋拡張</p></div><div class='card'><h2>API</h2><p><code>POST /api/candidates</code> 商品候補を審査</p><p><code>POST /api/metrics</code> 実測値を追加</p><p><code>GET /api/diagnosis</code> 売れない原因を判定</p></div></div></body></html>"""
