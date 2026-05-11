# LangChain チュートリアル手順書

## 🎯 お題（共通シナリオ）

> **「指定された都市の天気を調べて、それに合った服装をアドバイスするAIエージェント」**

このシナリオを LangChain と Microsoft Foundry の両方で実装し、開発体験の違いを比較します。

| 項目 | 内容 |
|---|---|
| 入力 | `"東京の天気を調べて、服装をアドバイスして"` |
| 使うツール | `get_weather(city)` — 天気を返すモック関数 |
| LLM | OpenAI GPT-5-mini（または Azure OpenAI） |
| 出力 | 「東京は晴れ・25℃です。半袖シャツに薄手の上着を…」のような自然文 |

---

## 📋 LangChain版：開発の流れ（コードファースト）

```
[1] 環境構築 → [2] コード記述 → [3] 実行 → [4] デバッグ
   pip install      .pyファイル        python      print/loggingで追う
```

**特徴:** すべて自分でコードを書く。GUI は無し。スクリプト実行で完結。

---

## ✅ 前提条件

- Python 3.10 以上
- OpenAI API キー（または Azure OpenAI のエンドポイント＋キー）
- VS Code などのエディタ
- ターミナル

---

## 📝 手順

### Step 1. 仮想環境を作る

```powershell
cd langchain-tutorial
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**着目点:** Python の標準機能だけで完結。Foundry のような GUI ベースの「プロジェクト作成」ステップは存在せず、ディレクトリと venv 等をユーザー自身が用意する。

---

### Step 2. 必要なパッケージをインストール

```powershell
pip install langchain langchain-openai python-dotenv
```

**着目点:** ランタイムも SDK も自分で選定・バージョン管理する必要がある（本チュートリアルは `langchain>=1.0` を前提）。

---

### Step 3. APIキーを設定

`.env` ファイルを作成（**Git にコミットしないこと**。`.gitignore` に要追加）:

```env
OPENAI_API_KEY=sk-...your-key-here...
```

**着目点:** シークレット管理は完全に自己責任。Foundry のようにマネージド ID／RBAC で API キー無し運用にする仕組みは LangChain 単体には無い。

---

### Step 4. エージェントコードを理解する

エージェント本体は同ディレクトリの [`agent.py`](./agent.py) に同梱済みです。コード内のコメントで各構成要素を解説しています。

要点:
- `@tool` デコレータで `get_weather` 関数をツール化
- `init_chat_model("openai:gpt-5-mini")` で LLM を初期化（環境変数 `MODEL_NAME` で上書き可）
- LangChain v1 の `create_agent(model, tools, system_prompt=...)` でエージェント生成
- `agent.invoke({"messages": [...]})` で実行し、`result["messages"]` から中間ステップと最終回答を取り出す

> 注: 旧 API の `create_tool_calling_agent` + `AgentExecutor` は `langchain<1.0` 系の書き方です。本チュートリアルは `langchain>=1.0` の `create_agent` を採用しています。

**着目点:** Tool・Prompt・Model・Agent を **すべて自前のコード**として組み立てる必要がある。Foundry の「ポータルでツール追加→デプロイ」のようなノーコード手段は無い。

---

### Step 5. 実行する

```powershell
python agent.py
```

期待される出力（実行時の例）:

```text
=== ユーザー入力 ===
東京の天気を調べて、服装をアドバイスして

=== 中間メッセージ ===
[human] 東京の天気を調べて、服装をアドバイスして
[ai] tool_calls=[{'name': 'get_weather', 'args': {'city': '東京'}, ...}]
[tool] 晴れ、気温 25℃、湿度 50%
[ai] 東京は晴れ、気温25℃・湿度50%です。半袖の通気性の良いトップス…

=== 最終回答 ===
東京は晴れ、気温25℃・湿度50%です。半袖の通気性の良いトップス…
```

ログから「LLM がツール呼び出しを判断 → ツール実行 → ツール結果を踏まえて再度 LLM が回答」という ReAct ループが追えます。

**着目点:** デバッグはターミナルのテキストログ頼り。Foundry portal の Playground のような GUI トレースは既定で無い（次の Step 6 で外部 SaaS や OSS をオプトインすれば可視化可能）。

---

### Step 6. （オプション）トレース可視化 — LangSmith / Langfuse

ターミナルログだけでは複雑なエージェントの追跡が辛くなるため、外部の **LLM オブザーバビリティ基盤** を入れるのが定石です。LangChain アプリでよく使われる選択肢は次の 2 つ。

| | **LangSmith** | **Langfuse** |
|---|---|---|
| 提供元 | LangChain 社（公式） | Langfuse 社（独立） |
| ライセンス | プロプライエタリ SaaS | MIT（OSS） |
| セルフホスト | Enterprise プランのみ | 誰でも無料利用可能・全機能 self-host 可 |
| 対応フレームワーク | LangChain / LangGraph に最深統合 | フレームワーク非依存（OpenAI / Anthropic / LlamaIndex 等も） |
| OpenTelemetry | 限定的 | OTel ネイティブ |
| 向いているケース | LangChain 中心スタックを SaaS で素早く可視化 | データ主権重視・OSS 優先 |

#### A. LangSmith を使う場合

[LangSmith](https://smith.langchain.com) で API キーを発行し、`.env` に追加:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_xxxxx
LANGSMITH_PROJECT=langchain-tutorial
```

`python agent.py` を再実行 → <https://smith.langchain.com> でトレースを確認。

#### B. Langfuse を使う場合

[Langfuse Cloud](https://cloud.langfuse.com) で API キーを発行（または `docker compose up` で self-host）し、追加パッケージをインストール:

```powershell
pip install langfuse
```

`.env` に追加:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

`agent.py` の冒頭で Langfuse のコールバックハンドラを LangChain に渡します（既存コードに数行追加するだけ）:

```python
from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler()
result = agent.invoke(
    {"messages": [{"role": "user", "content": user_input}]},
    config={"callbacks": [langfuse_handler]},
)
```

実行後、Langfuse の UI でトレースを確認できます。

#### 着目点

- **Microsoft Foundry の場合、Connect ボタンで Application Insights を接続するだけで観測性が立ち上がる**。接続後は [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) に沿ってトレースが**自動送信**され、コード側に `callbacks=` を仕込む必要すら無い。
- 閲覧は **Foundry portal の Tracing / Monitoring タブからそのまま**でき、別 UI に飛ばなくてよい。トークン消費・レイテンシ・例外・回答品質まで Azure Workbooks ベースで一画面に集約される（[Application analytics](https://learn.microsoft.com/azure/foundry-classic/how-to/monitor-applications)）。
- データは **Azure サブスクリプション内に閉じる**ため、データ主権・コンプライアンス要件にもそのまま乗る（外部 SaaS にトレースを送らない）。
- App Insights リソース自体の作成は別途必要だが、Foundry portal のウィザードから新規作成まで完結するため、**実質ワンクリックでプロダクション級のオブザーバビリティが手に入る**。
- LangChain コードを Foundry に持ち込む場合も、`langchain-azure-ai` 経由で同じ App Insights 連携の恩恵を受けられる（[LangChain / LangGraph 用トレース設定](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-framework#configure-tracing-for-langchain-and-langgraph)）。


参考:
- [LangSmith 公式](https://www.langchain.com/langsmith)
- [Langfuse 公式（OSS）](https://langfuse.com/) / [GitHub](https://github.com/langfuse/langfuse)
- [LangChain 公式の比較記事](https://www.langchain.com/articles/langsmith-vs-langfuse)

---

### Step 7. （オプション）評価（Evaluation）

回答品質を継続的に測るためのスクリプトを同梱しています: [`evals.py`](./evals.py)

LangChain 単体には組み込みの評価器が無いため、このサンプルでは **2 種類の評価器を自前で実装** しています:

1. **決定的評価**: 回答に「気温」「服装関連語」が含まれるかを Python の文字列判定でチェック
2. **LLM-as-judge**: もう一度 LLM に「この回答は質問に答えているか」を 1〜5 で採点させる

実行:

```powershell
python evals.py
```

期待される出力（例）:

```text
============================================================
評価サマリ
============================================================
Case  Deterministic   Judge Score   Reason
------------------------------------------------------------
1     PASS            5             気温と具体的な服装提案が含まれている
2     PASS            5             札幌の雨を踏まえた防寒・防水の提案が適切
3     PASS            4             那覇の暑さに対する提案だが小物の言及がやや薄い
------------------------------------------------------------
決定的評価 合格率: 100.0%
LLM審査員 平均スコア: 4.67 / 5
```

**着目点:**

- LangChain では **評価データセット管理・評価器・実行ループ・サマリ出力** を **すべて自前で書く必要がある**。
- LangSmith を契約すれば `evaluate()` API でこれらを SaaS 側に寄せられるが、**外部サービス依存** が発生する。
- 一方 Foundry では `azure-ai-evaluation` SDK に **Groundedness / Relevance / Coherence / Fluency / Safety などの評価器が標準搭載**。さらに portal の Evaluations タブから **no-code で同じデータセットを評価**でき、結果は Foundry portal で履歴比較・チーム共有まで完結する（Foundry 版の Step 9 を参照）。

参考:
- [LangSmith Evaluations 公式](https://docs.smith.langchain.com/evaluation)
- [LLM-as-a-judge パターン解説](https://docs.smith.langchain.com/evaluation/concepts#llm-as-a-judge)

---

## 🔍 比較ポイント（あとで Foundry版と並べる）

| 観点 | LangChain での体験 |
|---|---|
| **インフラ** | ローカル or 自前ホスティング |
| **GUI** | 無し。すべてコード |
| **シークレット管理** | `.env` ファイルを自分で管理 |
| **ツール定義** | `@tool` デコレータでPython関数を直接登録 |
| **モデル切替** | コードの `init_chat_model` の引数を書き換え |
| **トレース** | LangSmith / Langfuse など外部サービスを別途設定 |
| **評価** | 評価器・データセット・実行ループを自前実装、または LangSmith を別契約 |
| **デプロイ** | FastAPI 等で自前API化 → 自分でホスティング |
| **学習コスト** | LangChain の概念（Chain/Agent/Runnable）の理解が必要 |
| **柔軟性** | ◎（コードなので何でもできる） |

---

## 📂 完成イメージ

```
langchain-tutorial/
├── tutorial.md           ← このファイル
├── agent.py              ← エージェント本体（同梱済み）
├── evals.py              ← 評価スクリプト（同梱済み）
├── .env                  ← (Step 3 で作成、コミット禁止)
└── requirements.txt      ← (任意)
```

---

## 次のアクション

1. `python agent.py` で動作確認
2. Foundry版（`../foundry-tutorial/tutorial.md`）と並べてデモ実施
