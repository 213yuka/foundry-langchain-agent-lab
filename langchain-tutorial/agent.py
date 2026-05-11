"""指定された都市の天気を調べて服装をアドバイスする LangChain エージェント.

LangChain v1 系 (`langchain>=1.0`) の `create_agent` API を使用する。
コードを上から読むと、LangChain でエージェントを組む際の構成要素
（Tool / Model / System Prompt / Agent / Invoke ループ）がそのまま現れる。
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

# [Point 1] シークレット管理
# `.env` から OPENAI_API_KEY などを読み込む。Foundry のようなマネージド ID
# 連携は LangChain 単体には無いため、シークレットは自前で管理する必要がある。
load_dotenv()


# [Point 2] ツール定義
# `@tool` デコレータで Python 関数をそのまま LLM ツール化できる。
# 関数の docstring と型ヒントが LLM に渡される「ツールの仕様」になるため、
# 引数名・型・docstring は LLM が読む前提で丁寧に書く。
# 実運用では OpenWeatherMap などの実 API 呼び出しに差し替える。
@tool
def get_weather(city: str) -> str:
    """指定された都市の現在の天気と気温を返すモック関数."""
    mock_db = {
        "東京": "晴れ、気温 25℃、湿度 50%",
        "大阪": "曇り、気温 22℃、湿度 60%",
        "札幌": "雨、気温 15℃、湿度 80%",
        "那覇": "晴れ、気温 30℃、湿度 70%",
    }
    return mock_db.get(
        city,
        f"{city} の天気データは未登録です（晴れ・気温 20℃と仮定してください）",
    )


def build_agent():
    # [Point 3] モデル初期化
    # `init_chat_model("<provider>:<model>")` で provider 切り替えが容易。
    # 例: "openai:gpt-5-mini" / "azure_ai:gpt-5-mini" / "anthropic:claude-..."
    # 環境変数 MODEL_NAME で上書きできるようにしておくと検証がしやすい。
    model_name = os.getenv("MODEL_NAME", "openai:gpt-5-mini")
    model = init_chat_model(model_name)

    # [Point 4] System Prompt
    # エージェントの役割・出力フォーマット・ツール利用方針をここで宣言する。
    # 「必ず get_weather を使う」と明示することで暴走（hallucination）を抑制。
    system_prompt = (
        "あなたは天気に応じた服装をアドバイスする日本語アシスタントです。"
        "ユーザーから都市名が示されたら、必ず get_weather ツールで天気を調べてから、"
        "気温・天候に合った具体的な服装（上下・羽織り物・靴・小物）を1〜2文で提案してください。"
    )

    # [Point 5] エージェント生成
    # LangChain v1 の `create_agent` は内部的に LangGraph で
    # 「LLM → tool → LLM → ...」のループ（ReAct パターン）を構築する。
    # 旧 API の `create_tool_calling_agent` + `AgentExecutor` の置き換え。
    return create_agent(
        model=model,
        tools=[get_weather],
        system_prompt=system_prompt,
    )


def main() -> None:
    agent = build_agent()
    user_input = "東京の天気を調べて、服装をアドバイスして"

    print(f"=== ユーザー入力 ===\n{user_input}\n")

    # [Point 6] 実行
    # 入力は `messages` 配列（OpenAI Chat Completions と同じ形）。
    # `invoke` は同期実行。ストリーミングしたい場合は `stream` を使う。
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]}
    )

    # [Point 7] 中間ステップの可視化
    # `result["messages"]` には human / ai / tool の全メッセージが時系列で入る。
    # tool_calls 属性を見ることで「LLM がどのツールをどう呼んだか」を追跡できる。
    # Foundry portal の Playground のような GUI トレースは無いため、
    # こうした自前ログが LangChain 単体での主要なデバッグ手段になる。
    print("=== 中間メッセージ ===")
    for msg in result["messages"]:
        role = getattr(msg, "type", msg.__class__.__name__)
        content = getattr(msg, "content", "")
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            print(f"[{role}] tool_calls={tool_calls}")
        if content:
            print(f"[{role}] {content}")

    # [Point 8] 最終回答
    # 最後の AI メッセージがユーザーに返す回答になる。
    final = result["messages"][-1].content
    print("\n=== 最終回答 ===")
    print(final)


if __name__ == "__main__":
    main()
