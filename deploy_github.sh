#!/bin/bash
# WEB3NEWS GitHub部署脚本

echo "=================================="
echo "🚀 WEB3NEWS GitHub部署向导"
echo "=================================="
echo ""

# 检查是否已配置remote
if git remote | grep -q "origin"; then
    echo "✅ Git remote已配置"
    git remote -v
else
    echo "📝 请按照以下步骤操作："
    echo ""
    echo "1. 在GitHub上创建新仓库"
    echo "   访问: https://github.com/new"
    echo "   仓库名称: WEB3NEWS"
    echo "   选择: Public或Private"
    echo "   不要初始化README"
    echo ""
    echo "2. 添加远程仓库（替换YOUR_USERNAME）:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/WEB3NEWS.git"
    echo ""
    echo "3. 推送代码:"
    echo "   git push -u origin main"
    echo ""
    read -p "按回车继续配置GitHub Secrets..."
fi

echo ""
echo "=================================="
echo "📋 GitHub Secrets配置清单"
echo "=================================="
echo ""
echo "在GitHub仓库中配置以下Secrets:"
echo ""
echo "路径: Settings → Secrets and variables → Actions → New repository secret"
echo ""
echo "Secret 1:"
echo "  Name: NOTION_API_KEY"
echo "  Value: 你的Notion API密钥（从memory.md获取）"
echo ""
echo "Secret 2:"
echo "  Name: NOTION_DATABASE_ID"
echo "  Value: 你的数据库ID（从Notion数据库URL获取）"
echo ""
echo "Secret 3:"
echo "  Name: NOTION_PARENT_PAGE_ID"
echo "  Value: 你的父页面ID（从Notion页面URL获取）"
echo ""
echo "详细说明: 查看 GITHUB_ACTIONS_SETUP.md"
echo ""

read -p "是否已配置完GitHub Secrets? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "✅ 太棒了！现在可以推送代码了"
    echo ""

    if git remote | grep -q "origin"; then
        echo "执行推送命令:"
        echo "  git push -u origin main"
        echo ""
        git push -u origin main
    else
        echo "请先添加remote仓库:"
        echo "  git remote add origin https://github.com/YOUR_USERNAME/WEB3NEWS.git"
        echo "  git push -u origin main"
    fi

    echo ""
    echo "=================================="
    echo "✅ 部署完成！"
    echo "=================================="
    echo ""
    echo "下一步操作:"
    echo "1. 访问你的GitHub仓库"
    echo "2. 点击 'Actions' 标签"
    echo "3. 选择 'Chainbase TOPS 定时同步' workflow"
    echo "4. 点击 'Run workflow' 手动测试一次"
    echo "5. 等待定时任务自动运行（每小时）"
    echo ""
    echo "🎉 祝贺！你的自动同步系统已就绪！"
    echo ""
else
    echo ""
    echo "💡 先配置GitHub Secrets，然后重新运行此脚本"
    echo ""
fi
