---
description: "リポジトリ内の日本語 Markdown レポート、チュートリアル、比較表、手順書、スライド原稿の作成・編集を扱うときに使用する。"
applyTo: "**/*.md,**/*.mdx"
---

# 日本語ドキュメント インストラクション

本リポジトリの Markdown は日本語で書かれた調査レポート・チュートリアル・比較資料が中心。既存の文体・構成と整合させる。

## 文体

- 「です・ます調」と「である調」を文書単位で統一する。既存ファイルの調子に合わせる。
- 専門用語・固有名詞は**正式名称**を使う。例: `Microsoft Foundry`、`Azure OpenAI Service`、`Azure AI Services`、`Microsoft Entra ID`、`GitHub Copilot`、`Visual Studio Code`。
- 英数字と日本語の間にはスペースを入れない（混在で見づらいときのみ最低限）。
- コード識別子・コマンド・ファイルパス・URL は原文のまま、バッククオートで囲む。

## 構成

- チュートリアルや手順書は **Step ベース**で番号付けし、各 Step の冒頭に目的を 1〜2 文で書く。
- 比較・対照は**表（Markdown table）**で示す。LangChain と Foundry の比較は軸を揃える。
- スクリーンショットは `screenshots/` 等の相対パスで参照する。
- 長い Markdown は H2 / H3 で章立てし、目次が自動的に追えるようにする。
- 出典は脚注または末尾の「参照」セクションに URL でまとめる。

## 表現と正確性

- 公式公開資料を一次情報として参照し、出典 URL を明示する。
- 料金・SKU・クォータ・地域可用性・モデル一覧などの**変動情報は断定しない**。「執筆時点」「最新情報は公式ドキュメントを参照」を併記する。
- Preview / GA を区別し、Preview 機能はその旨を明記する。
- Foundry の新 portal と classic（hub-based）が混在しやすいので、文中でどちらを指すか明示する。

## ファイル別の方針

- `01_migration-report/report.md`: LangChain → Foundry 移行の意思決定資料。コスト・アーキテクチャ・確信度を保つ。
- `02_multi-agent/report.md`: Foundry マルチエージェントのアーキテクチャ・評価・注意点。
- `03_langchain-tutorial/tutorial.md` と `03_foundry-tutorial/tutorial.md`: 同一シナリオを比較できるよう、Step 番号と章立てを揃える。
- `README.md`: ディレクトリ構成と再生成手順の正確性を維持する。

## 守るべきこと

1. ユーザーが指示していない章の追加・削除・大規模リライトは行わない。
2. 既存のスクリーンショット参照や脚注番号を壊さない。
3. 機械翻訳調を避け、自然な日本語にする。
4. Microsoft / GitHub / VS Code 公式の用語・表記を優先する。

## 参照（一次情報）

- Microsoft Learn: <https://learn.microsoft.com/>
- GitHub Docs: <https://docs.github.com/>
- Visual Studio Code Docs: <https://code.visualstudio.com/docs>
- Microsoft Foundry: <https://learn.microsoft.com/en-us/azure/ai-foundry/>
