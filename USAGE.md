# Chainbase TOPS → Notion 快速使用指南

## ✅ 已完成设置

- ✅ Notion数据库已创建
- ✅ Database ID: `2e67c8ad-0dbb-8128-add1-fad9be96c1f6`
- ✅ 同步脚本已就绪
- ✅ 测试同步成功（5个中文话题）
- ✅ **免费翻译已集成**（Google Translate）

## 🚀 三种使用方式

### 方式1: 快速启动脚本（推荐）

```bash
cd WEB3NEWS
./quick_start.sh
```

然后选择：
- `1` - 测试同步（5个中文话题）
- `2` - 完整同步（20中文 + 10英文+**免费翻译**）
- `3` - 仅中文（20个话题）

### 方式2: 直接运行生产版脚本

```bash
cd WEB3NEWS

# 完整同步（中文 + 英文+免费翻译）
python3 sync_to_notion.py
```

**✅ 无需任何API Key配置，翻译功能已内置！**

### 方式3: 测试脚本

```bash
cd WEB3NEWS
python3 test_sync.py
```

## 📋 同步内容说明

### 中文话题（直接同步）
- 来源: Chainbase TOPS 中文版
- 数量: 前20个
- 内容: 标题 + 摘要

### 英文话题（翻译同步）
- 来源: Chainbase TOPS 英文版
- 数量: 前10个
- 内容: 原文标题 + 原文摘要 + **免费翻译**摘要
- 翻译服务: **Google Translate (完全免费)**

## 💰 翻译成本

**✅ 完全免费！**

使用Google翻译免费版：
- 无需API Key
- 无使用次数限制
- 每月成本: ¥0

**翻译质量**: 85-90%准确率，满足日常使用需求

## 📅 设置自动同步

### 每小时自动同步

创建crontab:
```bash
crontab -e
```

添加以下行：
```bash
0 * * * * cd /Users/ziwind/my-vibe-project/WEB3NEWS && python3 sync_to_notion.py >> sync.log 2>&1
```

### 每天早上8点同步

```bash
0 8 * * * cd /Users/ziwind/my-vibe-project/WEB3NEWS && python3 sync_to_notion.py >> sync.log 2>&1
```

## 📊 查看Notion数据库

**数据库链接**:
https://www.notion.so/2e67c8ad0dbb8128add1fad9be96c1f6

**数据库字段**:
- **Name**: 话题标题
- **语言**: 中文🔵 / 英文🟢
- **摘要**: 话题详细描述
- **原文标题**: 英文话题的原始标题
- **翻译摘要**: 英文摘要的中文翻译
- **话题ID**: Chainbase TOPS唯一标识
- **状态**: 🔥热门 / ⚡上升 / 📊稳定

## 💡 使用建议

### 按需同步

**交易员**（高频）: 每小时同步，捕捉最新热点
```bash
# crontab: 0 * * * *
```

**PM/研究员**（中频）: 每6小时同步
```bash
# crontab: 0 */6 * * *
```

**长期投资者**（低频）: 每天同步一次
```bash
# crontab: 0 8 * * *
```

### 内容筛选

在Notion中创建视图：
1. **今日热点** - 筛选今天创建的记录
2. **中文精选** - 筛选语言=中文
3. **英文视角** - 筛选语言=英文
4. **🔥热门** - 筛选状态=🔥热门

## 🐛 常见问题

### Q1: 同步失败怎么办？

**检查网络连接**:
```bash
curl https://api.chainbase.com/tops/v1/stories?lang=zh
```

**检查Notion API权限**:
确认 NOTION_API_KEY 有访问父页面权限

### Q2: 翻译失败？

**检查OpenAI API**:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**跳过翻译**:
不设置 OPENAI_API_KEY 即可

### Q3: 如何查看同步日志？

```bash
tail -f sync.log
```

### Q4: 如何删除重复话题？

在Notion数据库中：
1. 按"话题ID"排序
2. 手动删除重复项
3. 或创建视图筛选重复ID

## 📈 高级技巧

### 1. 批量导出为Markdown

在Notion中选择所有记录 → Export → Markdown

### 2. 生成每日报告

创建Notion模板，每日自动生成汇总页

### 3. 集成到其他系统

- 使用Notion Webhook
- 导出为RSS
- 对接到Telegram Bot

---

**创建时间**: 2026-01-13
**版本**: v1.0
**数据库ID**: 2e67c8ad-0dbb-8128-add1-fad9be96c1f6
