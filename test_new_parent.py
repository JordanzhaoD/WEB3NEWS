#!/usr/bin/env python3
"""
测试新的父页面配置
"""
import requests
import json
import os
from datetime import datetime

# 配置（从环境变量读取）
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "2e67c8ad0dbb8128add1fad9be96c1f6")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "2e67c8ad0dbb8173bbfed146339168cc")

if not NOTION_API_KEY:
    print("❌ 错误: NOTION_API_KEY环境变量未设置")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2025-09-03"
}

print("=" * 70)
print("🧪 测试新的父页面配置")
print("=" * 70)

# 1. 测试父页面是否可访问
print(f"\n1️⃣ 检查父页面...")
url = f"https://api.notion.com/v1/pages/{NOTION_PARENT_PAGE_ID}"
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✅ 父页面可访问")
    print(f"   标题: {data['properties']['Name']['title'][0]['text']['content']}")
    print(f"   URL: {data['url']}")
else:
    print(f"❌ 父页面访问失败: {response.status_code}")
    print(f"   {response.json()}")
    exit(1)

# 2. 测试在父页面添加新闻列表内容
print(f"\n2️⃣ 测试添加新闻列表...")
append_url = f"https://api.notion.com/v1/blocks/{NOTION_PARENT_PAGE_ID}/children"

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

news_blocks = [
    {
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": "📰 WEB3 新闻热点"}}]
        }
    },
    {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [
                {"type": "text", "text": {"content": f"⏰ 最后更新: {current_time} | "}},
                {"type": "text", "text": {"content": "🔄 每2小时自动同步 | "}},
                {"type": "text", "text": {"content": "💎 Less Noise, More Signal"}}
            ]
        }
    },
    {
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": "🔥 TOP 3 热点"}}]
        }
    },
    {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [
                {"type": "text", "text": {"content": "💎 1. "}},
                {
                    "type": "text",
                    "text": {"content": "测试新闻标题", "link": {"url": "https://chainbase.com"}}
                },
                {"type": "text", "text": {"content": " | 📊 1,234,567"}}
            ]
        }
    }
]

append_payload = {"children": news_blocks}
response = requests.patch(append_url, headers=headers, json=append_payload)

if response.status_code == 200:
    print(f"✅ 新闻列表添加成功")
else:
    print(f"❌ 添加失败: {response.status_code}")
    print(f"   {response.json()}")

print("\n" + "=" * 70)
print("✅ 测试完成！父页面配置正确")
print("=" * 70)
print(f"\n📝 配置信息:")
print(f"   NOTION_PARENT_PAGE_ID=\"{NOTION_PARENT_PAGE_ID}\"")
print(f"   NOTION_DATABASE_ID=\"{NOTION_DATABASE_ID}\"")
print(f"\n🔗 查看页面: https://www.notion.so/{NOTION_PARENT_PAGE_ID}")

