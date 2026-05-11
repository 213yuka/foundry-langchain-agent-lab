"""LangChain エージェントの評価スクリプト.

LangChain 単体には組み込み評価器が無いため、ここでは
2 種類の評価器を「自前で」実装する。Foundry 版 (`evaluation.py`) と
比較すると、評価器の組み込み度合いの差が分かる。

  1. 決定的評価 (deterministic)
     - 回答に「気温」「服装関連語」が含まれているかを Python の文字列判定で確認
     - 高速・無料・確定的だが、表現の揺れに弱い

  2. LLM-as-judge
     - もう一度 LLM に「この回答は質問に答えているか」を 1〜5 で採点させる
     - 柔軟だが、LLM 呼び出しコストがかかる
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from agent import build_agent

load_dotenv()


# [Point 1] テストデータセット
# 実運用では JSONL ファイルや LangSmith / Langfuse の Dataset 機能で管理する。
# ここでは最小構成として Python のリストで持つ。
TEST_CASES = [
    {"input": "東京の天気を調べて、服装をアドバイスして", "expected_city": "東京"},
    {"input": "札幌の天気を調べて、何を着ればいい？", "expected_city": "札幌"},
    {"input": "那覇の服装を教えて", "expected_city": "那覇"},
]


@dataclass
class EvalResult:
    case_id: int
    user_input: str
    response: str
    deterministic_pass: bool
    judge_score: int
    judge_reason: str


# [Point 2] 決定的評価
# LangChain 単体にはこの種のヘルパーすら無いため、自分で書く必要がある。
CLOTHING_KEYWORDS = ["シャツ", "ジャケット", "コート", "Tシャツ", "セーター",
                     "傘", "上着", "服", "靴", "スニーカー", "カーディガン", "パンツ"]


def evaluate_deterministic(response: str) -> bool:
    """回答に気温情報と服装関連語が含まれているかをチェック."""
    has_temp = "℃" in response or "度" in response
    has_clothing = any(word in response for word in CLOTHING_KEYWORDS)
    return has_temp and has_clothing


# [Point 3] LLM-as-judge
# Foundry の RelevanceEvaluator 相当を自分で実装している。
# プロンプトの品質が評価結果を左右するため、本来は校正と整合性検証が必要。
JUDGE_PROMPT_TEMPLATE = """\
あなたは AI 回答の品質を評価する審査員です。次の質問と回答を読み、
回答が「天気情報を踏まえた具体的な服装アドバイスになっているか」を
1〜5 で採点してください。

質問: {question}
回答: {response}

以下の JSON 形式のみで出力してください（説明文は禁止）:
{{"score": <1-5の整数>, "reason": "<採点理由を1文で>"}}
"""


def evaluate_with_judge(judge_model, question: str, response: str) -> tuple[int, str]:
    prompt = JUDGE_PROMPT_TEMPLATE.format(question=question, response=response)
    raw = judge_model.invoke(prompt).content.strip()
    # コードフェンスが付くことがあるので除去
    if raw.startswith("```"):
        raw = raw.strip("`").lstrip("json").strip()
    try:
        parsed = json.loads(raw)
        return int(parsed["score"]), str(parsed["reason"])
    except Exception as exc:
        return 0, f"判定パース失敗: {exc} / raw={raw!r}"


def run_agent(agent, user_input: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
    return result["messages"][-1].content


def main() -> None:
    agent = build_agent()
    # [Point 4] 審査員モデル
    # 評価対象と同じモデルでも可だが、別モデル（より強力な or 別ベンダーの）を
    # 使うとバイアスを軽減できる。コストとのトレードオフ。
    judge_model = init_chat_model(os.getenv("JUDGE_MODEL", "openai:gpt-5-mini"))

    results: list[EvalResult] = []
    for i, case in enumerate(TEST_CASES, start=1):
        print(f"\n--- Case {i}: {case['input']} ---")
        response = run_agent(agent, case["input"])
        print(f"応答: {response[:80]}...")

        det_pass = evaluate_deterministic(response)
        score, reason = evaluate_with_judge(judge_model, case["input"], response)

        results.append(
            EvalResult(
                case_id=i,
                user_input=case["input"],
                response=response,
                deterministic_pass=det_pass,
                judge_score=score,
                judge_reason=reason,
            )
        )

    # [Point 5] サマリ出力
    # LangSmith / Langfuse を使えば WebUI で可視化できるが、
    # 単体ではこのように print するか CSV/JSON に書き出すしかない。
    print("\n" + "=" * 60)
    print("評価サマリ")
    print("=" * 60)
    print(f"{'Case':<6}{'Deterministic':<16}{'Judge Score':<14}Reason")
    print("-" * 60)
    for r in results:
        print(f"{r.case_id:<6}{'PASS' if r.deterministic_pass else 'FAIL':<16}"
              f"{r.judge_score:<14}{r.judge_reason}")

    pass_rate = sum(1 for r in results if r.deterministic_pass) / len(results) * 100
    avg_score = sum(r.judge_score for r in results) / len(results)
    print("-" * 60)
    print(f"決定的評価 合格率: {pass_rate:.1f}%")
    print(f"LLM審査員 平均スコア: {avg_score:.2f} / 5")


if __name__ == "__main__":
    main()
