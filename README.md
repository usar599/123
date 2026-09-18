# AI Profit Orchestrator V2

V2の最初の実装です。

## 目的
ゼロから作る前に既存OSSを探索し、使えるものがあれば流用して最短で販売検証する。

## 実装済み
- OSS優先
- ライセンス確認ゲート
- 日本語UIゲート
- API原価・決済手数料・インフラ費を含む粗利判定
- 粗利60%未満の公開停止
- 集客導線必須
- 表示→クリック→登録→購入→売上→API費の計測
- 売れない原因の自動診断
- 日本語UI

## 起動
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

http://127.0.0.1:8000/
