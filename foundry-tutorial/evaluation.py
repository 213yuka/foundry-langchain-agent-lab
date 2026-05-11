"""Microsoft Foundry のエージェント回答を Azure AI Evaluation SDK で評価するスクリプト.

LangChain 版 (`../langchain-tutorial/evals.py`) と同じデータセットを評価し、
評価器の組み込み度合いの差を比較できるようにしている。

LangChain 版では決定的評価と LLM-as-judge を **自前実装** する必要があったが、
Foundry / Azure AI Evaluation SDK には Groundedness / Relevance / Coherence /
Fluency / Safety などの **業界標準の評価器が組み込み済み** で、import するだけで使える。

参考:
- Azure AI Evaluation SDK
  https://learn.microsoft.com/python/api/overview/azure/ai-evaluation-readme
- 組み込み評価器一覧
  https://learn.microsoft.com/azure/ai-foundry/concepts/evaluation-metrics-built-in
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

# [Point 1] 組み込み評価器を import するだけ
# LangChain 単体には相当するクラスが無い。Foundry の優位ポイント。
from azure.ai.evaluation import (
    RelevanceEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
    evaluate,
)

load_dotenv()


# [Point 2] 評価器が利用する Judge モデルの設定
# Foundry にデプロイした gpt-5-mini などの接続情報を渡す。
# `.env` には以下を記載しておく:
#   AZURE_OPENAI_ENDPOINT=https://<resource>.services.ai.azure.com
#   AZURE_OPENAI_API_KEY=<key>
#   AZURE_OPENAI_DEPLOYMENT=gpt-5-mini
MODEL_CONFIG = {
    "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
    "api_key": os.environ["AZURE_OPENAI_API_KEY"],
    "azure_deployment": os.environ["AZURE_OPENAI_DEPLOYMENT"],
}


# [Point 3] 評価データセット (JSONL)
# 1 行 1 ケース。query / response / context をスクリプト側で作るのが
# 「ローカル評価」のパターン。本番では Foundry portal の Datasets に
# アップロードしてクラウド評価することも可能。
DATASET_PATH = "evaluation_data.jsonl"


def build_sample_dataset() -> None:
    """LangChain 版と同じ 3 ケースをローカルで評価できるよう JSONL を生成."""
    samples = [
        {
            "query": "東京の天気を調べて、服装をアドバイスして",
            "response": "東京は晴れで25℃です。半袖シャツにチノパン、薄手のカーディガンを羽織ると快適です。",
        },
        {
            "query": "札幌の天気を調べて、何を着ればいい？",
            "response": "札幌は雨で15℃です。長袖にフリース、防水のレインジャケットと滑りにくい靴をおすすめします。",
        },
        {
            "query": "那覇の服装を教えて",
            "response": "那覇は晴れで30℃です。通気性の良い半袖Tシャツと短パン、帽子と日焼け止めを忘れずに。",
        },
    ]
    import json
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"データセットを {DATASET_PATH} に書き出しました（{len(samples)} 件）")


def main() -> None:
    build_sample_dataset()

    # [Point 4] 評価器の初期化
    # 1 行で複数の業界標準メトリクスを準備できる。
    # 他にも GroundednessEvaluator / SimilarityEvaluator / F1ScoreEvaluator /
    # ViolenceEvaluator / HateUnfairnessEvaluator などが用意されている。
    evaluators = {
        "relevance": RelevanceEvaluator(model_config=MODEL_CONFIG),
        "coherence": CoherenceEvaluator(model_config=MODEL_CONFIG),
        "fluency": FluencyEvaluator(model_config=MODEL_CONFIG),
    }

    # [Point 5] 一括評価
    # `evaluate()` が
    #   - データセット読み込み
    #   - 各行に対する全評価器の並列実行
    #   - 結果集計 (mean / pass-rate)
    #   - Foundry portal への結果アップロード（azure_ai_project 指定時）
    # を一括で行う。LangChain 版で自前実装していたループが不要。
    result = evaluate(
        data=DATASET_PATH,
        evaluators=evaluators,
        # azure_ai_project={"subscription_id": "...", "resource_group_name": "...",
        #                   "project_name": "..."}  # 指定すると Foundry portal に結果アップロード
    )

    # [Point 6] 結果サマリ
    # `result["metrics"]` に各評価器のスコア平均が入る。
    # `result["rows"]` に行ごとの詳細スコアが入る。
    print("\n" + "=" * 60)
    print("評価サマリ (Azure AI Evaluation SDK)")
    print("=" * 60)
    for metric_name, value in result["metrics"].items():
        print(f"{metric_name:<40} {value}")

    if "studio_url" in result:
        print(f"\nFoundry portal で詳細を確認: {result['studio_url']}")


if __name__ == "__main__":
    main()
