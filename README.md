# Chainbase TOPS → Notion 自动同步系统

## 📖 功能说明

自动将Chainbase TOPS的热门Crypto话题同步到你的Notion数据库：

✅ **中文话题** - 直接同步，无需翻译
✅ **英文话题** - 使用**免费Google翻译**翻译成中英对照格式
✅ **Twitter Embed** - 两列横排布局，整齐美观
✅ **推文时间线** - 获取TOP 6高评分推文
✅ **作者信息** - 相关作者热度排行
✅ **自动去重** - 避免重复创建相同话题
✅ **实时数据** - 同步注意力指数、数据源等指标
✅ **完全免费** - 无需任何付费API Key
✅ **GitHub Actions** - 每小时自动同步，无需手动运行

## 🎯 两种运行方式

### 方式1: GitHub Actions（推荐）⭐

**优点**:
- ✅ 完全自动，无需手动运行
- ✅ 每2小时同步一次，数据实时更新
- ✅ 无需本地Python环境
- ✅ 运行在云端，不占用本地资源
- ✅ 每月仅使用1080分钟（免费额度2000分钟）

**快速部署**:
```bash
# 运行部署向导
./deploy_github.sh
```

详细说明: [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)

### 方式2: 本地运行

适合：
- 手动控制同步时机
- 测试和调试
- 不想使用GitHub

## 🚀 快速开始

### 1. 安装依赖

```bash
cd WEB3NEWS
pip install requests deep-translator
```

### 2. 直接运行（无需配置）

翻译功能已内置，**无需任何API Key配置**：

```bash
python3 sync_to_notion.py
```

会自动同步：
- 前20个中文话题
- 前10个英文话题（自动翻译）

### 3. 首次运行（创建数据库）

```bash
python3 chainbase_sync.py
```

首次运行会：
1. ✅ 在你的Notion WEB3页面下创建新数据库
2. ✅ 返回Database ID
3. ✅ 同步前20个中文话题 + 前10个英文话题（带翻译）

### 4. 保存Database ID

首次运行后，会看到类似输出：

```
💡 请将以下内容保存到环境变量：
   export NOTION_DATABASE_ID=2e67c8ad0dbb81378a90ddd0133b5a94
```

执行这个命令，然后重新运行脚本：

```bash
export NOTION_DATABASE_ID=your_database_id_here
python3 chainbase_sync.py
```

## 📅 设置定时自动同步

### macOS (使用launchd)

创建 `~/Library/LaunchAgents/com.chainbase.notion.sync.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.chainbase.notion.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/ziwind/my-vibe-project/WEB3NEWS/chainbase_sync.py</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>  <!-- 每小时执行一次 -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>OPENAI_API_KEY</key>
        <string>your_openai_api_key_here</string>
        <key>NOTION_DATABASE_ID</key>
        <string>your_database_id_here</string>
    </dict>
</dict>
</plist>
```

加载并启动：

```bash
launchctl load ~/Library/LaunchAgents/com.chainbase.notion.sync.plist
launchctl start com.chainbase.notion.sync
```

### 查看日志

```bash
log stream --predicate 'process == "chainbase_sync"' --level debug
```

## 📊 Notion数据库结构

创建的数据库包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| **Name** | 标题 | 话题标题（中文或翻译后的中文） |
| **语言** | 选择 | 中文🔵 / 英文🟢 |
| **原文标题** | 文本 | 英文话题的原始标题 |
| **摘要** | 文本 | 话题详细描述 |
| **翻译摘要** | 文本 | 英文摘要的中文翻译 |
| **话题ID** | 文本 | Chainbase TOPS的唯一标识 |
| **创建时间** | 日期 | 自动记录创建时间 |
| **状态** | 选择 | 🔥热门 / ⚡上升 / 📊稳定 |

## 🎯 使用建议

### 同步频率

- **高频模式** (1小时): 适合交易员，追踪最新热点
- **中频模式** (6小时): 适合PM/研究员，平衡及时性
- **低频模式** (24小时): 适合长期投资者，避免信息过载

### 内容筛选

脚本默认：
- 中文话题: 前20个
- 英文话题: 前10个（使用免费翻译）

可在脚本中修改 `sync_to_notion.py` 的这些值：

```python
SYNC_ZH_COUNT = 20  # 中文话题数量
SYNC_EN_COUNT = 10  # 英文话题数量
```

### 翻译成本

**✅ 完全免费！**

使用Google翻译免费版（通过`deep-translator`库）：
- 无需API Key
- 无使用次数限制
- 完全免费使用

质量对比：
- Google翻译: 85-90%准确率（日常使用足够）
- OpenAI翻译: 95%+准确率（专业术语更准确）

## 🔧 高级配置

### 使用其他翻译服务

编辑 `chainbase_sync.py` 中的 `translate_text_to_chinese()` 函数，可以替换为：

- DeepL API
- Google Translate API
- Azure Translator
- 本地翻译模型（如ChatGLM）

### 自定义数据库字段

修改 `create_notion_database()` 函数，添加更多字段：
- 关注度分数
- 相关推文链接
- 话题标签
- 作者信息

## 📈 数据分析

在Notion中可以这样分析数据：

1. **按语言筛选** - 查看中文/英文话题
2. **按状态排序** - 找到🔥热门话题
3. **按创建时间分组** - 追踪每日热点
4. **创建视图** - 如"今日热点"、"本周热门"等

## 🐛 故障排除

### 问题1: 创建数据库失败

**原因**: Notion API权限不足
**解决**: 确认 `NOTION_API_KEY` 有权限访问父页面

### 问题2: 翻译失败

**原因**: OpenAI API配置错误或余额不足
**解决**:
1. 检查 `OPENAI_API_KEY` 是否正确
2. 访问 https://platform.openai.com/usage 查看余额
3. 临时不翻译英文内容（不设置OPENAI_API_KEY）

### 问题3: 重复创建话题

**原因**: 当前版本不支持去重
**解决**: 手动在Notion中删除重复项，或等下个版本

## 📝 TODO

- [ ] 添加去重逻辑（检查话题ID是否已存在）
- [ ] 支持增量更新（只同步新话题）
- [ ] 添加数据统计（每天同步多少话题）
- [ ] 支持Webhook通知（新话题时推送到Telegram/微信）
- [ ] 添加数据可视化（关注度趋势图）

## 📄 许可

MIT License

---

**创建时间**: 2026-01-13
**版本**: v1.0
**作者**: Jordan + Claude
