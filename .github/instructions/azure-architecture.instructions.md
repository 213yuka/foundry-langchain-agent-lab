---
description: "Azure 構築・アーキテクチャ設計、Azure Landing Zone、Well-Architected Framework、RBAC、ID/ネットワーク/セキュリティ/監視/コスト/ガバナンス設計、サブスクリプション設計、AI ワークロードの配置を扱うときに使用する。"
applyTo: "**/*.bicep,**/*.bicepparam,infra/**,**/azure.yaml"
---

# Azure アーキテクチャ設計インストラクション

Azure 上のシステム構築・設計レビュー・IaC 設計を行うときの遵守事項。すべて Microsoft Learn の公式公開資料を一次情報とすること。

## 設計原則

- **Azure Well-Architected Framework の 5 本柱**を必ず意識する: Reliability / Security / Cost Optimization / Operational Excellence / Performance Efficiency。設計判断はどの柱に基づくかを言語化する。
- **Azure Landing Zone**の 8 つのデザインエリアに沿って整理する: Azure 課金 と Microsoft Entra テナント、ID とアクセス管理、管理グループとサブスクリプション、ネットワーク トポロジと接続、セキュリティ、管理、ガバナンス、プラットフォーム自動化と DevOps。
- **Platform landing zone** と **Application landing zone** の責務を分離する。共有サービス（ID・接続・管理）はプラットフォーム側、ワークロードはアプリケーション側に配置する。
- **AI ワークロードの配置**: 公式ガイダンスに従い、AI 専用の landing zone を新設するのではなく、既存の Azure landing zone のアプリケーション landing zone 内に AI ワークロードを配置することを既定とする。

## ID とアクセス

- ヒューマン認証は **Microsoft Entra ID** を使用する。サービス間認証は**マネージド ID（システム割り当て / ユーザー割り当て）**を最優先で選び、シークレット・接続文字列の埋め込みを避ける。
- 認可は **Azure RBAC** によって最小権限で割り当てる。組み込みロールを優先し、必要なときだけカスタム ロールを定義する。
- シークレット・キー・証明書は **Azure Key Vault** に集約し、参照は Key Vault references またはマネージド ID 経由のデータプレーンアクセスで行う。

## ネットワーク

- 既定で**プライベート接続**を選び、必要な公開だけを限定的に許可する。
- 内部通信は **Azure Private Link / プライベート エンドポイント**、外向き制御は Azure Firewall / NAT Gateway / NSG / UDR を組み合わせて設計する。
- 設計初期にハブ＆スポーク または Virtual WAN のいずれを採用するかを決定し、根拠を明示する。

## セキュリティ

- **Microsoft Defender for Cloud** を有効化し、規制コンプライアンス・セキュア スコアを継続的に確認する。
- 監査・診断ログは **Azure Monitor / Log Analytics** に集約し、保持期間を要件に基づいて設定する。
- 公開リソース（Storage、Cosmos DB、AI Services など）は Public network access の既定値を確認し、必要なら無効化または制限する。

## 監視・運用

- メトリクス・ログ・トレースは **Azure Monitor / Application Insights** に集約する。アプリケーションは OpenTelemetry を優先する。
- アラートは SLO に基づいて定義し、ノイズを抑える。
- ライフサイクルとバックアップ（Azure Backup / geo-redundancy / soft delete）を要件と照らして設計する。

## コスト

- 既定値は安全側（低コスト SKU）にし、本番要件は別途パラメーター化する。
- タグ戦略（環境・所有者・コストセンター・ワークロード）を最初に決め、IaC 側で必須化する。
- リザーブド インスタンス、Savings Plan、Spot などの適用可否は要件確認後に提案する。

## ガバナンス

- **Azure Policy** で組織標準を強制し、必要に応じて Initiative にまとめる。
- 命名規則とタグ規則は Cloud Adoption Framework のガイドに沿って統一する。
- 環境分離（dev / test / prod）は別サブスクリプションを既定とする。

## デプロイと自動化

- IaC は本リポジトリでは **Bicep** を主とする。詳細ルールは `.github/instructions/bicep.instructions.md` に従う。
- デプロイ前に **what-if** 解析を実行し、変更影響を確認する。
- CI/CD（GitHub Actions など）はマネージド ID（OIDC フェデレーション）を優先し、長寿命のサービス プリンシパル シークレットを避ける。

## 出力に含めるべき要素

Azure 設計の回答では、可能な限り以下を含める。

1. 対象ワークロードと前提（地域・SLA・データ分類など）。
2. 採用したリファレンス アーキテクチャと参照 URL。
3. Well-Architected の各柱に対する考慮点。
4. ID / ネットワーク / セキュリティ / 監視 / コストの観点。
5. 確認が必要な未確定事項（クォータ、規制、料金、地域可用性 など）。

## 参照（一次情報）

- Azure Well-Architected Framework: <https://learn.microsoft.com/en-us/azure/well-architected/>
- Azure Landing Zone（CAF Ready）: <https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/>
- Azure Landing Zone デザインエリア: <https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-areas>
- Cloud Adoption Framework: <https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/>
- Azure Architecture Center: <https://learn.microsoft.com/en-us/azure/architecture/>
