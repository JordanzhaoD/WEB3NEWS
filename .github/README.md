# WEB3NEWS 自动同步系统

Chainbase TOPS → Notion 自动同步工具，支持定时任务。

## ✨ 特性

- ✅ 自动获取中英文热门话题
- ✅ 推文时间线和作者信息
- ✅ 英文话题自动翻译（免费）
- ✅ Twitter Embed两列布局
- ✅ GitHub Actions每小时自动同步

## 🚀 快速开始

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行同步
python3 enhanced_sync.py
```

### GitHub Actions（推荐）

1. Fork或创建GitHub仓库
2. 配置GitHub Secrets（见下方）
3. 推送代码，自动启用定时任务

## 🔑 GitHub Secrets配置

在仓库的 `Settings` → `Secrets and variables` → `Actions` 中添加：

| Secret名称 | 值 |
|-----------|---|
| `NOTION_API_KEY` | 从memory.md获取 |
| `NOTION_DATABASE_ID` | 从Notion数据库URL获取 |
| `NOTION_PARENT_PAGE_ID` | 从Notion页面URL获取 |

详细配置说明：[GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)

## 📊 数据库

**Notion数据库**: https://www.notion.so/2e67c8ad0dbb8128add1fad9be96c1f6

## 📝 文件说明

```
├── enhanced_sync.py          # 主脚本（含两列布局）
├── sync_to_notion.py          # 基础脚本（v2.0）
├── requirements.txt           # Python依赖
├── .github/workflows/         # GitHub Actions配置
│   └── hourly-sync.yml       # 每小时自动同步
├── GITHUB_ACTIONS_SETUP.md    # GitHub配置详细说明
├── TWITTER_EMBED_IMPLEMENTATION.md  # Embed实施文档
└── README.md                  # 本文件
```

## ⏰ 定时任务

- **频率**: 每2小时运行一次
- **时区**: UTC时间
- **北京时区**: 8:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00, 22:00
- **资源使用**: 每月约1080分钟（免费额度2000分钟）

## 📈 同步配置

编辑 `enhanced_sync.py`:

```python
SYNC_ZH_COUNT = 20  # 中文话题数量
SYNC_EN_COUNT = 10  # 英文话题数量
TRANSLATOR_ENABLED = True  # 启用翻译
```

## 💰 成本

**完全免费！**
- Notion API: 免费
- Chainbase API: 免费
- Google翻译: 免费
- GitHub Actions: 免费账户每月2000分钟

## 📄 许可证

MIT License

---

**最后更新**: 2026-01-13
**状态**: ✅ 生产运行中
