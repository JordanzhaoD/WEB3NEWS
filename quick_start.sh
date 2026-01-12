#!/bin/bash
# Chainbase TOPS → Notion 快速启动脚本

echo "🚀 Chainbase TOPS → Notion 同步系统"
echo "======================================"
echo ""

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  未安装 requests，正在安装..."
    pip3 install requests
fi

echo "✅ 依赖检查完成"
echo ""

# 菜单
echo "请选择操作:"
echo "  1) 测试同步（前5个中文话题，无翻译）"
echo "  2) 完整同步（20个中文 + 10个英文+翻译）"
echo "  3) 仅中文（20个话题，无翻译）"
echo ""
read -p "请输入选项 [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "🧪 运行测试同步..."
        python3 test_sync.py
        ;;
    2)
        echo ""
        echo "🚀 运行完整同步..."

        # 检查是否配置了OpenAI API
        if [ -z "$OPENAI_API_KEY" ]; then
            echo "⚠️  未配置 OPENAI_API_KEY"
            echo "   将跳过英文话题翻译"
            echo "   如需翻译，请先设置: export OPENAI_API_KEY=your_key"
            echo ""
            read -p "继续吗？[y/N] " confirm
            if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
                exit 0
            fi
        fi

        python3 sync_to_notion.py
        ;;
    3)
        echo ""
        echo "🇨🇳 运行中文同步..."

        # 临时设置环境变量跳过英文
        OPENAI_API_KEY="" python3 sync_to_notion.py
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
