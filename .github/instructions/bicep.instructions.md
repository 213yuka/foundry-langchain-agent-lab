---
description: "Bicep / Bicep modules / Azure Verified Modules (AVM) / bicepparam / bicepconfig / what-if / az deployment による Azure IaC 作成・レビュー・検証を扱うときに使用する。"
applyTo: "**/*.bicep,**/*.bicepparam,**/bicepconfig.json,infra/**"
---

# Bicep IaC インストラクション

本リポジトリの Azure IaC は Bicep を主とする。Microsoft Learn の Bicep 公式ベスト プラクティスに沿って記述する。

## ファイル構成

- ルート テンプレート（例: `main.bicep`）と再利用可能な**モジュール**を分離する。
- ローカル モジュールのパスは**スラッシュ `/` のみ**を使用する。Windows のバックスラッシュ `\` は Bicep で非対応。
- 公開モジュールは **Azure Verified Modules (AVM)** を最優先で利用する。例: `br/public:avm/res/<service>/<resource>:<tag>`。
- 組織内共通モジュールは Private Bicep registry または Template Specs に発行して再利用する。

## パラメーター

- パラメーター名は **lower camel case**（例: `storageAccountName`）。
- 環境ごとに変える値だけパラメーター化する。固定値は変数またはハードコードに留める。
- 既定値は**安全側**（低コスト SKU、最小スケール）に設定する。
- `@description`、`@minLength` / `@maxLength`、`@minValue` / `@maxValue` を活用し、不正値を入口でブロックする。
- `@allowed` の使い過ぎに注意する。SKU 一覧の更新に追従できなくなるリスクがある。
- 機密値は `@secure()` を付ける。Key Vault 参照（`getSecret`）を優先する。

## リソース定義

- 比較的新しい API バージョンを選ぶ（公式 Reference で最新を確認）。
- 複雑な式は変数に切り出して可読性を上げる。
- リソース ID やプロパティは `<symbolicName>.id` / `<symbolicName>.properties.*` のように**シンボリック名**経由で参照し、`reference()` / `resourceId()` の利用は避ける。
- 依存関係は**暗黙の依存**を優先し、`dependsOn` の明示は最小限に留める。
- 既存リソースは `existing` キーワードで参照する。
- 子リソースは `parent` プロパティまたはネストで関係を明示する。名前を文字列連結で組み立てない。

## 命名

- グローバル一意リソース（Storage アカウントなど）は `uniqueString(resourceGroup().id)` などを組み合わせ、プレフィックスとして意味のある短い識別子を付ける。
- 命名・タグ規約は CAF の推奨に沿う。最低限、`environment` / `workload` / `owner` / `costCenter` を必須化することを検討する。

## 出力

- パスワード・接続文字列・キーは出力しない。必要なら `@secure()` 付きの output と Key Vault 経由を検討する。
- 他のテンプレートでキーが必要な場合、output で渡すのではなく `existing` で都度参照する方が安全。

## モジュール

- モジュール宣言には `@description` を付ける。
- 並列・条件・反復は `for` / `if` / `@batchSize()` を活用する。
- スコープ違いのデプロイは `scope:` プロパティで明示する。

## デプロイと検証

- 文法チェック: `az bicep build --file <file>.bicep` または VS Code Bicep 拡張のリンターを使う。
- 影響確認: `az deployment group what-if`、`az deployment sub what-if`、`az deployment mg what-if` を環境スコープに応じて使う。
- 検証: `az deployment ... validate` を CI で実行する。
- パラメーター ファイルは `.bicepparam` を優先する。
- CI/CD は OIDC フェデレーション + マネージド ID を優先し、長寿命シークレットを避ける。

## 参照（一次情報）

- Bicep ベスト プラクティス: <https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/best-practices>
- Bicep モジュール: <https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/modules>
- Azure Verified Modules (Bicep): <https://azure.github.io/Azure-Verified-Modules/indexes/bicep/>
- Bicep 言語リファレンス: <https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/>
- what-if 解析: <https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/deploy-what-if>
