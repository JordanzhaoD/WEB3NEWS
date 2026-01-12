# GitHub Actions 自动同步配置

## 📋 功能说明

通过GitHub Actions实现每小时自动同步Chainbase TOPS数据到Notion。

## 🚀 设置步骤

### 1. 创建GitHub仓库

```bash
# 初始化git仓库（已完成）
git init

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/WEB3NEWS.git

# 提交代码
git add .
git commit -m "feat: 添加GitHub Actions每小时自动同步"
git branch -M main
git push -u origin main
```

### 2. 配置GitHub Secrets

在GitHub仓库中设置以下Secrets：

**路径**: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

#### 必需的Secrets：

| Secret名称 | 值 | 说明 |
|-----------|---|------|
| `NOTION_API_KEY` | `你的Notion API密钥` | 从memory.md或Notion集成页面获取 |
| `NOTION_DATABASE_ID` | `你的数据库ID` | 从Notion数据库URL获取 |
| `NOTION_PARENT_PAGE_ID` | `你的父页面ID` | 从Notion页面URL获取 |

### 3. 验证配置

#### 方法1: 手动触发
1. 进入GitHub仓库
2. 点击 `Actions` 标签
3. 选择 `Chainbase TOPS 定时同步` workflow
4. 点击 `Run workflow` → `Run workflow`

#### 方法2: 查看定时任务
1. 进入GitHub仓库
2. 点击 `Actions` 标签
3. 查看 `Chainbase TOPS 定时同步` 的运行历史
4. 查看下次运行时间（预计每小时）

## ⏰ 定时计划

**当前配置**: 每小时运行一次（UTC时间）

| 时区 | 运行时间 |
|------|---------|
| UTC | 每小时0分 |
| 北京时间 (UTC+8) | 8:00, 9:00, 10:00, ... |

**示例**:
- UTC 00:00 → 北京时间 08:00
- UTC 01:00 → 北京时间 09:00
- UTC 13:00 → 北京时间 21:00

## 📊 同步配置

当前同步设置（可在`enhanced_sync.py`中修改）：

```python
SYNC_ZH_COUNT = 20  # 中文话题数量
SYNC_EN_COUNT = 10  # 英文话题数量
TRANSLATOR_ENABLED = True  # 启用翻译
```

## 🔍 监控和日志

### 查看运行日志

1. 进入GitHub仓库的 `Actions` 页面
2. 点击最近的workflow run
3. 展开步骤查看详细日志
4. 下载日志文件（如有错误）

### 本地日志

同步过程中的日志会输出到GitHub Actions控制台。

## ⚙️ 高级配置

### 修改同步频率

编辑 `.github/workflows/hourly-sync.yml`:

```yaml
on:
  schedule:
    # 每小时
    - cron: '0 * * * *'
    # 每2小时
    # - cron: '0 */2 * * *'
    # 每6小时
    # - cron: '0 */6 * * *'
    # 每天早上8点（北京时间）
    # - cron: '0 0 * * *'
```

### 修改同步数量

编辑 `enhanced_sync.py`:

```python
SYNC_ZH_COUNT = 20  # 修改中文话题数量
SYNC_EN_COUNT = 10  # 修改英文话题数量
```

## 📝 注意事项

1. **GitHub Actions限制**:
   - 免费账户：每月2000分钟
   - 每次同步约需2-3分钟
   - 估算：每小时运行 = 每天24次 = 每月720次 = 约2160分钟
   - **建议**: 如需降低频率，可改为每2小时或每6小时

2. **Notion API限制**:
   - 免费账户无明确限制
   - 建议避免过于频繁的请求

3. **Chainbase API**:
   - 免费使用
   - 建议添加延迟避免限流

## 🛠️ 故障排除

### Workflow运行失败

1. **检查Secrets配置**:
   - 确保所有3个Secrets已正确设置
   - 确保Secret名称完全匹配（区分大小写）

2. **检查Python依赖**:
   - 查看 `requirements.txt` 是否包含所有依赖
   - 查看 `Install dependencies` 步骤的日志

3. **检查脚本错误**:
   - 查看 `Run sync script` 步骤的详细日志
   - 本地测试脚本：`python3 enhanced_sync.py`

### 定时任务不运行

1. **确认workflow已启用**:
   - Settings → Actions → General → Workflow permissions
   - 选择 `Read and write permissions`

2. **确认cron表达式**:
   - 使用UTC时间
   - 验证cron语法：https://crontab.guru/

## 📚 相关文档

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [GitHub Secrets文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Crontab Guru](https://crontab.guru/) - Cron表达式验证

## 💡 提示

- 首次设置建议先手动触发一次，确认配置正确
- 定时任务基于UTC时间，注意时区转换
- 可以通过查看Actions页面了解运行状态
- 日志会保留90天，可随时查看

---

**配置完成时间**: 2026-01-13
**状态**: 待部署
