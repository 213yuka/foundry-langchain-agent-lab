# Microsoft Foundry チュートリアル手順書

## 🎯 お題（共通シナリオ）

> **「指定された都市の天気を調べて、それに合った服装をアドバイスするAIエージェント」**

LangChain版（`../langchain-tutorial/tutorial.md`）と**まったく同じお題**を、Microsoft Foundry で実装して比較します。

| 項目 | 内容 |
|---|---|
| 入力 | `"東京の天気を調べて、服装をアドバイスして"` |
| 使うツール | `get_weather(city)` — 天気を返す関数（Function Tool として登録） |
| LLM | Azure OpenAI（gpt-5-mini など Foundry にデプロイ済みモデル） |
| 出力 | 「東京は晴れ・25℃です。半袖シャツに薄手の上着を…」のような自然文 |

---

## 📋 Foundry版：開発の流れ（GUI ＋ マネージド）

```
[1] ポータルで       [2] モデルを       [3] エージェント    [4] Playgroundで    [5] スレッドと
   プロジェクト作成 → デプロイ        → をGUIで作成      → テスト          → トレース確認
   (Azure portal)    (Foundry portal) (ノーコード)        (チャット画面)     (自動収集)
```

**特徴:** GUI 中心でセットアップ完了。インフラ・観測性・認証が**最初から組み込み済み**。

---

## ✅ 前提条件

- Azure サブスクリプション（無料枠でも可）
- Azure ロール: 対象リソースグループに `Contributor` または `Azure AI Developer`
- ブラウザ（Edge / Chrome）
- （オプション）SDK 経由でも触る場合：Python 3.10+ と Azure CLI

---

## 📝 手順

### Step 1. Azure AI Foundry portal を開く

ブラウザで https://ai.azure.com にアクセスし、Azure アカウントでサインイン。

📸 **スクリーンショット①：`screenshots/01_foundry_portal_top.png`**
- Foundry ポータルのトップ画面
- **着目点:** インストール作業ゼロ。**ブラウザを開いた瞬間から開発開始**できる

---

### Step 2. プロジェクトを作成

`+ Create project` をクリックし、以下を入力:
- Project name: `weather-advisor-demo`
- Hub: 新規作成（リージョンは `Japan East` 推奨）

📸 **スクリーンショット②：`screenshots/02_create_project.png`**
- プロジェクト作成ダイアログ
- **着目点:** プロジェクト作成と同時に **Storage / Key Vault / Application Insights** が自動でプロビジョニングされる（LangChain版は全部手動）

---

### Step 3. モデルをデプロイ

左メニュー `Models + endpoints` → `+ Deploy model` → `gpt-5-mini` を選択 → デプロイ。

📸 **スクリーンショット③：`screenshots/03_model_deploy.png`**
- モデルデプロイ完了画面（Endpoint URL が表示されている状態）
- **着目点:** モデルのホスティング・スケーリングは Foundry が管理。**APIキーをコードに埋める必要なし**（Managed Identity 利用可）

---

### Step 4. エージェントを作成（ノーコード）

左メニュー `Agents` → `+ New agent`:
- Name: `weather-advisor`
- Instructions:
  ```
  あなたは天気アドバイザーです。
  ユーザーが指定した都市の天気を get_weather ツールで取得し、
  その天気に合った服装を日本語で提案してください。
  ```
- Model: 先ほどデプロイした `gpt-5-mini`

📸 **スクリーンショット④：`screenshots/04_agent_basic_setup.png`**
- エージェント基本設定画面
- **着目点:** **コードを1行も書かずに**エージェントの骨格が完成する

---

### Step 5. Function Tool を追加

エージェント編集画面 → `Tools` → `+ Add` → `Function`:

```json
{
  "name": "get_weather",
  "description": "指定された都市の現在の天気を返す",
  "parameters": {
    "type": "object",
    "properties": {
      "city": { "type": "string", "description": "都市名" }
    },
    "required": ["city"]
  }
}
```

📸 **スクリーンショット⑤：`screenshots/05_function_tool_added.png`**
- ツール一覧に `get_weather` が登録された状態
- **着目点:** ツールスキーマは **JSON で宣言**。実装は別途 SDK 側で `tool_outputs` を返す（GUI とコードのハイブリッド）

---

### Step 6. Playground でテスト

エージェント画面右側の Playground で `"東京の天気を調べて、服装をアドバイスして"` と入力 → 送信。

ツール呼び出しが発生すると `Required action` が表示されるので、
- 簡易テストの場合: `Submit tool outputs` で `{"weather":"晴れ","temp":25}` を手で返す
- 本番想定の場合: SDK で実装した tool ハンドラを起動

📸 **スクリーンショット⑥：`screenshots/06_playground_test.png`**
- Playground のチャット画面（ユーザー入力＋エージェント応答＋ツール呼び出しの吹き出し）
- **着目点:** **対話テストが GUI で完結**。`verbose=True` のテキストログを目で追う必要なし

---

### Step 7. トレース／観測性を確認

左メニュー `Tracing` または接続済みの Application Insights を開く。

📸 **スクリーンショット⑦：`screenshots/07_tracing_view.png`**
- スレッド・ラン・ツール呼び出しがツリー状に可視化された画面
- **着目点:** **観測性は何も設定せずに最初から有効**。LangChain版は LangSmith を別途契約・設定する必要があった

---

### Step 8. （オプション）SDK から呼び出す

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="<PROJECT_CONNECTION_STRING>"
)
agent = client.agents.get_agent("asst_xxxxx")  # ポータルで作ったエージェントID
thread = client.agents.create_thread()
client.agents.create_message(thread.id, role="user", content="東京の天気を…")
run = client.agents.create_and_process_run(thread.id, agent.id)
```

📸 **スクリーンショット⑧：`screenshots/08_sdk_call.png`**
- SDK 経由で同じエージェントを呼び出した実行結果
- **着目点:** GUIで作ったエージェントを **コードからもそのまま呼べる**（GUI とコードの分断なし）

---

### Step 9. （オプション）評価（Evaluation）

#### A. portal で no-code 評価

Foundry portal 左メニュー `Evaluation` → `+ New evaluation`:

1. データセットをアップロード（`query` / `response` / `context` 列を含む JSONL）
2. 評価器を選択（`Relevance` / `Groundedness` / `Coherence` / `Fluency` / `Safety` などが**チェックボックスで選べる**）
3. Judge モデル（評価者役の LLM）を選択
4. `Run` をクリック

実行結果は portal 内で **行ごとのスコア・全体平均・履歴比較** まで一画面で確認できる。チームメンバーへの共有も RBAC で完結。

#### B. SDK で評価（CI/CD 組み込み向け）

同ディレクトリの [`evaluation.py`](./evaluation.py) を参照。`azure-ai-evaluation` SDK で同じ評価器をコードから呼び出せる。

セットアップ:

```powershell
pip install azure-ai-evaluation azure-identity python-dotenv
```

`.env` に追加:

```env
AZURE_OPENAI_ENDPOINT=https://<resource>.services.ai.azure.com
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_DEPLOYMENT=gpt-5-mini
```

実行:

```powershell
python evaluation.py
```

#### 着目点

- **評価器が組み込み済み**: `RelevanceEvaluator` / `GroundednessEvaluator` / `CoherenceEvaluator` / `FluencyEvaluator` / `SimilarityEvaluator` / `ViolenceEvaluator` / `HateUnfairnessEvaluator` / `SelfHarmEvaluator` / `ProtectedMaterialEvaluator` など、業界標準のメトリクスを **import するだけ** で使える（[組み込み評価器一覧](https://learn.microsoft.com/azure/ai-foundry/concepts/evaluation-metrics-built-in)）。
- **no-code から code まで一貫**: portal で試行 → 良ければ SDK で CI/CD に組み込む、という導線が揃っている。
- **本番継続評価**: [Continuous Evaluation](https://learn.microsoft.com/azure/foundry-classic/how-to/continuous-evaluation-agents) で本番トラフィックを自動的に評価し続け、品質劣化を検知できる。
- **データ・結果が Azure 内に閉じる**: Foundry project に紐づく Application Insights / Storage に保存される。

LangChain 版（`../langchain-tutorial/evals.py`）では **評価器・実行ループ・サマリ集計をすべて自前で書く必要があった** のと対照的。「**評価まで含めてマネージド**」が Foundry の強み。

---

## 🔍 比較ポイント（LangChain版と並べて）

| 観点 | Foundry での体験 | LangChain との違い |
|---|---|---|
| **インフラ** | フルマネージド | LangChain: 自前ホスティング |
| **GUI** | あり（ポータル＋Playground） | LangChain: 無し |
| **シークレット管理** | Managed Identity / Key Vault が自動接続 | LangChain: `.env` を自前管理 |
| **ツール定義** | JSON Schema で宣言（GUI で編集可） | LangChain: `@tool` デコレータでコード |
| **モデル切替** | ポータルで `Deployment` を変更 | LangChain: コード書き換え |
| **トレース** | App Insights が**最初から有効** | LangChain: LangSmith等を別契約 |
| **評価** | **組み込み評価器を import or portalで選択** | LangChain: 評価器を自前実装 or LangSmith 契約 |
| **デプロイ** | 作成した瞬間に**エンドポイントが完成** | LangChain: 自分でAPI化＆ホスティング |
| **学習コスト** | ポータル操作＋少しのSDK | LangChain: 概念＋ライブラリAPI多数 |
| **柔軟性** | ○（マネージドの範囲内） | LangChain: ◎（何でもできる） |
| **エンタープライズ要件** | RBAC / Private Endpoint / 監査ログが標準装備 | LangChain: 自分で実装する必要あり |

---

## 📂 完成イメージ

```
foundry-tutorial/
├── tutorial.md                ← このファイル
├── tool_handler.py            ← (Step 5/8 で作成予定。get_weather の実装)
├── sdk_client.py              ← (Step 8 で作成予定。SDK呼び出し)
├── evaluation.py              ← 評価スクリプト（同梱済み）
└── screenshots/
    ├── 01_foundry_portal_top.png
    ├── 02_create_project.png
    ├── 03_model_deploy.png
    ├── 04_agent_basic_setup.png
    ├── 05_function_tool_added.png
    ├── 06_playground_test.png
    ├── 07_tracing_view.png
    └── 08_sdk_call.png
```

---

## 🆚 ひとことサマリ

> **LangChain は「自分で全部組み立てる自由」。**
> **Foundry は「最初から揃っている安心」。**
>
> PoC でロジックをガッツリ作り込みたいなら LangChain、
> エンタープライズ運用までを最短で見据えるなら Foundry が強い。

---

## 次のアクション

1. この手順書をレビュー → OKなら実装ファイル（`tool_handler.py`, `sdk_client.py`）を作成
2. 実際にAzureポータルで操作しながら8枚のスクリーンショットを撮影
3. LangChain版と並べて、両者の違いをデモで実演
