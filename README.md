# LangChain vs Microsoft Foundry チュートリアル

同一シナリオ（「指定された都市の天気を調べて、服装をアドバイスする AI エージェント」）を **LangChain** と **Microsoft Foundry** の両方で実装し、開発体験を比較するためのチュートリアル集です。

## ディレクトリ構成

```
.
├── langchain-tutorial/         LangChain でフルスクラッチ実装する手順
│   ├── tutorial.md
│   └── screenshots/
│
└── foundry-tutorial/           Microsoft Foundry（GUI＋マネージド）で実装する手順
    ├── tutorial.md
    └── screenshots/
```

両チュートリアルは相互にリンクしており、同じお題で比較しながら進められます。

## はじめかた

- LangChain 版から始める: [langchain-tutorial/tutorial.md](langchain-tutorial/tutorial.md)
- Microsoft Foundry 版から始める: [foundry-tutorial/tutorial.md](foundry-tutorial/tutorial.md)

## 付録（ローカル専用 / git 管理外）

過去の調査レポートとスライド・音声生成スクリプトは `appendix/` にローカル保管しており、`.gitignore` によりリポジトリには含めません。

```
appendix/                       （git 管理外）
├── migration-report/           旧 01_migration-report（LangChain → Foundry 移行調査）
├── multi-agent/                旧 02_multi-agent（Foundry マルチエージェント構築）
└── scripts/                    旧スライド・ナレーション生成スクリプト
```
