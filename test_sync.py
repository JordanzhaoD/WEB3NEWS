#!/usr/bin/env python3
"""
Chainbase TOPS → Notion 测试脚本（无翻译版本）
只同步中文话题，测试基础功能
"""

import requests
import json
import os
import sys
from datetime import datetime

# ============ 配置 ============

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")

if not NOTION_API_KEY:
    print("❌ 错误: 请设置NOTION_API_KEY环境变量")
    sys.exit(1)

CHAINBASE_API_ZH = "https://api.chainbase.com/tops/v1/stories?lang=zh"

# ============ 函数 ============

def get_chainbase_stories():
    """获取Chainbase TOPS中文热门话题"""
    try:
        response = requests.get(CHAINBASE_API_ZH, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        return []

def create_notion_database():
    """创建Notion数据库"""
    url = "https://api.notion.com/v1/databases"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    payload = {
        "parent": {
            "type": "page_id",
            "page_id": NOTION_PARENT_PAGE_ID
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Chainbase TOPS 热门话题"
                }
            }
        ],
        "properties": {
            "Name": {
                "title": {}
            },
            "语言": {
                "select": {
                    "options": [
                        {"name": "中文", "color": "blue"},
                        {"name": "英文", "color": "green"}
                    ]
                }
            },
            "摘要": {
                "rich_text": {}
            },
            "话题ID": {
                "rich_text": {}
            },
            "状态": {
                "select": {
                    "options": [
                        {"name": "🔥 热门", "color": "red"},
                        {"name": "⚡ 上升", "color": "orange"},
                        {"name": "📊 稳定", "color": "gray"}
                    ]
                }
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Notion数据库创建成功！")
        print(f"   Database ID: {data['id']}")
        print(f"   URL: {data['url']}")
        return data['id']
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        if response:
            print(f"   响应: {response.text}")
        return ""

def add_item_to_notion(database_id, story):
    """添加单个话题到Notion"""
    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    story_id = story.get("id", "")
    keyword = story.get("keyword", "")
    summary = story.get("summary", "")

    payload = {
        "parent": {
            "type": "database_id",
            "database_id": database_id
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": keyword[:100]
                        }
                    }
                ]
            },
            "语言": {
                "select": {
                    "name": "中文"
                }
            },
            "摘要": {
                "rich_text": [
                    {
                        "text": {
                            "content": summary[:2000]
                        }
                    }
                ]
            },
            "话题ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": story_id
                        }
                    }
                ]
            },
            "状态": {
                "select": {
                    "name": "🔥 热门"
                }
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ 添加失败: {keyword[:30]}... - {e}")
        return False

# ============ 主函数 ============

def main():
    print("=" * 60)
    print("🧪 Chainbase TOPS → Notion 测试脚本")
    print("=" * 60)

    # 1. 获取中文数据
    print("\n📥 获取Chainbase TOPS中文数据...")
    stories = get_chainbase_stories()
    print(f"✅ 成功获取 {len(stories)} 个话题")

    if not stories:
        print("❌ 没有数据，退出")
        return

    # 显示前3个示例
    print("\n📋 示例话题（前3个）:")
    for i, story in enumerate(stories[:3], 1):
        print(f"\n{i}. {story.get('keyword', 'Unknown')}")
        print(f"   {story.get('summary', '')[:80]}...")

    # 2. 创建数据库
    print("\n📁 创建Notion数据库...")
    database_id = create_notion_database()

    if not database_id:
        print("❌ 无法创建数据库，退出")
        return

    # 3. 同步前5个话题作为测试
    print(f"\n📊 同步前5个话题到Notion...")
    count = 0
    for i, story in enumerate(stories[:5], 1):
        keyword = story.get('keyword', '')
        print(f"\n[{i}/5] 添加: {keyword[:40]}... ", end="")
        if add_item_to_notion(database_id, story):
            print("✅")
            count += 1
        else:
            print("❌")

    print(f"\n✅ 测试完成！成功添加 {count}/5 个话题")
    print(f"\n💡 Database ID: {database_id}")
    print(f"   请保存此ID，用于后续同步")

if __name__ == "__main__":
    main()
