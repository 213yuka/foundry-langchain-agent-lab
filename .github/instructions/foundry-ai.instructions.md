---
description: "Microsoft Foundry / Azure AI Foundry / Azure OpenAI / Azure AI Services / マルチエージェント / RAG / 評価 / トレーシング / Foundry hub・project / マネージド ID / プライベート エンドポイント を扱うときに使用する。"
applyTo: "01_migration-report/**/*.md,02_multi-agent/**/*.md,03_foundry-tutorial/**/*.md,**/*.bicep,**/*.py"
---

# Microsoft Foundry / Azure AI ワークロード インストラクション

Foundry / Azure OpenAI / Azure AI Services を扱うときの遵守事項。

## 用語と前提の明示

- **Foundry の系統に注意する**。新しい **Microsoft Foundry portal** と従来の **Foundry (classic) / hub-based プロジェクト** では、概念・URL・機能・セキュリティ設定が異なる。回答時は対象を明示する。
- 機能が **GA / Preview** のいずれかを記載する。Preview は本番採用条件を併記する。
- 料金・地域可用性・モデル一覧・クォータは公式ドキュメントの最新情報を確認するよう促す。

## ID と認可

- **マネージド ID（システム割り当て / ユーザー割り当て）** を既定とする。`AZURE_OPENAI_API_KEY` などのキーをコードに埋め込まない。
- Azure OpenAI / AI Services の RBAC ロール（例: `Cognitive Services OpenAI User`、`Azure AI Developer`）を必要最小で付与する。
- ローカル開発は `DefaultAzureCredential` を使用する（`Azure CLI` / `Visual Studio Code` / `Managed Identity` の順にフォールバック）。

## ネットワークとセキュリティ

- 本番環境では Public network access を**無効化**し、**プライベート エンドポイント**経由で接続する設計を既定とする。
- Foundry hub を使う場合は **Managed Virtual Network**（`Allow internet outbound` か `Allow only approved outbound`）を要件に応じて選択する。
- 依存リソース（Storage / Key Vault / Container Registry / Application Insights）も同様にプライベート化を検討する。
- データ保管・データ取り扱い（プロンプト・補完・トレース・評価データセット）の場所と暗号化を要件に照らす。CMK が必要なら Key Vault と統合する。

## 観測と評価

- アプリケーション計装は **OpenTelemetry** を優先し、**Application Insights** へ送信する。
- Foundry 上のエージェント評価（バッチ評価・継続評価）は公式ガイダンスに沿って構成する。データセットは PII を含めないか、含める場合は管理ポリシーを明示する。

## マルチエージェント設計

- オーケストレーションのパターン（Sequential / Concurrent / Handoff など）を明示する。
- ツール呼び出し（function tools / MCP）はスキーマ・副作用・冪等性・タイムアウトを定義する。
- 失敗時のフォールバックとループ抑止（最大ステップ数）を必ず設計に含める。
- 参考: Microsoft の `microsoft/multi-agent-reference-architecture` など、公式・準公式のリファレンスを確認する。

## LangChain との比較を扱うとき

- 機能比較は「コードファースト vs GUI / マネージド」「自前運用 vs Azure 統合（ID・監視・コスト）」の観点で整理する。
- LangChain 側のコードは原典に忠実に扱い、Foundry 側は公式 SDK / portal の現行仕様に合わせる。
- 移行レポート（`01_migration-report/`）の構成・文体を踏襲する。

## 参照（一次情報）

- Microsoft Foundry: <https://learn.microsoft.com/en-us/azure/ai-foundry/>
- Azure OpenAI Service: <https://learn.microsoft.com/en-us/azure/ai-services/openai/>
- Azure AI Services: <https://learn.microsoft.com/en-us/azure/ai-services/>
- Foundry セキュア化（classic / hub-based）: <https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/create-secure-ai-hub>
- Application Insights / OpenTelemetry: <https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-overview>
