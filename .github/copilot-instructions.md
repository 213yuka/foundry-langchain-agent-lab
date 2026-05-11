# リポジトリ カスタムインストラクション

このリポジトリは、LangChain でフルスクラッチ開発していたエージェント環境を Microsoft Foundry へ移行する検討、Foundry でのマルチエージェント構築、LangChain と Foundry のチュートリアル比較、それらを補助する Python スクリプト（スライド・音声生成）で構成される調査ドキュメント集です。

## 全体方針

- 回答・ドキュメント・コメントは原則として日本語で記述する。コード識別子・公式用語・コマンド・ファイルパス・URL は原文のまま扱う。
- Azure / Microsoft / GitHub / VS Code に関する事項は、必ず Microsoft Learn・GitHub Docs・VS Code Docs などの**公式公開資料**を一次情報として参照し、出典 URL を明示する。
- 推測で Azure の SKU・料金・クォータ・API バージョン・地域可用性を断定しない。最新情報は公式ドキュメントで確認するよう促す。
- Foundry については、新しい Foundry portal と classic（hub-based）docs で仕様が異なる場合があるため、どちらの体系の話かを明示する。
- 既存ドキュメントの文体（Step ベース・比較表・脚注引用）と整合させる。

## 詳細インストラクションの分担

タスクに応じて、`.github/instructions/` 配下のファイルが自動または手動で読み込まれる。詳細ルールはそちらに従う。

- Azure アーキテクチャ・Landing Zone・ガバナンス・セキュリティ・ネットワーク・運用設計 → `.github/instructions/azure-architecture.instructions.md`
- Bicep / IaC / デプロイ検証 → `.github/instructions/bicep.instructions.md`
- Microsoft Foundry / Azure OpenAI / AI Services / マルチエージェント / 評価 → `.github/instructions/foundry-ai.instructions.md`
- 日本語 Markdown・チュートリアル・レポート編集 → `.github/instructions/docs-japanese.instructions.md`

## リポジトリ構成（要点）

- `01_migration-report/` LangChain → Foundry 移行調査レポート。
- `02_multi-agent/` Foundry マルチエージェント構築の調査レポート。
- `03_langchain-tutorial/` LangChain 側のチュートリアル（コードファースト）。
- `03_foundry-tutorial/` Foundry 側のチュートリアル（GUI ファースト）。`03_langchain-tutorial/` と同一シナリオで比較できるよう構成されている。
- `scripts/` レポートから PPTX スライドと gTTS 音声を生成する Python スクリプト。

## ビルド・再生成

- スライド・音声の再生成は `README.md` に記載の手順に従う。
- 既知の依存: `python-pptx`、`gTTS`。Python 環境は事前に整備されている前提。

## 守るべき原則

1. 公式公開資料を優先し、出典を明示する。
2. 既存ドキュメントの構成・文体を破壊しない。
3. ユーザーが明示的に依頼していない大規模リファクタや機能追加は行わない。
4. 設定ファイル（`.vscode/settings.json` など）の既存値を不必要に変更しない。

## 参照（一次情報）

- GitHub Copilot リポジトリ カスタムインストラクション: <https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions>
- VS Code カスタムインストラクション: <https://code.visualstudio.com/docs/copilot/customization/custom-instructions>
- Azure Well-Architected Framework: <https://learn.microsoft.com/en-us/azure/well-architected/>
- Azure Landing Zone: <https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/>
