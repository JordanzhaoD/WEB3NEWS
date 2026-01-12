#!/usr/bin/env python3
"""
测试Notion embed功能
"""

import requests
import json
import os
import sys
from datetime import datetime

# Notion配置（从环境变量读取）
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")

if not NOTION_API_KEY:
    print("❌ 错误: 请设置NOTION_API_KEY环境变量")
    sys.exit(1)

# 测试推文URL
TEST_TWEET_URL = "https://x.com/joakja/status/2010729816170053982"

def create_test_page():
    """创建测试页面"""
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    children = [
        # 标题
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🧪 Twitter Embed 测试"}}]
            }
        },
        # 说明
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": "测试Notion embed功能是否支持Twitter卡片"}}]
            }
        },
        # Embed推文
        {
            "object": "block",
            "type": "embed",
            "embed": {
                "url": TEST_TWEET_URL
            }
        }
    ]

    payload = {
        "parent": {
            "type": "page_id",
            "page_id": NOTION_PARENT_PAGE_ID
        },
        "properties": {
            "title": {
                "title": [{"text": {"content": "🧪 Twitter Embed 测试页面"}}]
            }
        },
        "children": children
    }

    try:
        print(f"正在创建测试页面...")
        print(f"测试推文URL: {TEST_TWEET_URL}")

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        page_data = response.json()

        page_id = page_data["id"]
        page_url = page_data["url"]

        print(f"✅ 页面创建成功!")
        print(f"   Page ID: {page_id}")
        print(f"   Page URL: {page_url}")

        return page_url
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   错误详情: {e.response.text[:500]}")
        return ""

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Notion Twitter Embed 功能测试")
    print("=" * 70)

    page_url = create_test_page()

    if page_url:
        print("\n" + "=" * 70)
        print("✅ 测试完成！")
        print("=" * 70)
        print(f"\n📝 请手动访问以下URL，查看Twitter embed是否正常显示:")
        print(f"   {page_url}")
        print()
