#!/usr/bin/env python3
"""
测试Notion两列布局 - Twitter Embed对齐
使用column_block实现整齐的图文排列
"""

import requests
import json
import os
import sys

# Notion配置（从环境变量读取）
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")

if not NOTION_API_KEY:
    print("❌ 错误: 请设置NOTION_API_KEY环境变量")
    sys.exit(1)

# 测试推文URL（4条推文用于测试）
TEST_TWEETS = [
    ("王短鸟", "https://x.com/wanghebbf/status/2010723316630474797"),
    ("土澳大狮兄", "https://x.com/BroLeon/status/2010736640986665082"),
    ("子时", "https://x.com/wangzj789/status/2010722459090477407"),
    ("EnHeng", "https://x.com/EnHeng456/status/2010719877755765057")
]

def create_two_column_test():
    """创建两列布局测试页面"""
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # 准备children
    children = [
        # 标题
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🧪 Twitter Embed 两列布局测试"}}]
            }
        },
        # 说明
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": "测试Notion column功能，实现整齐的两列布局"}}]
            }
        }
    ]

    # 尝试方案1: 使用column_block（如果API支持）
    print("\n📊 尝试方案1: 使用column_block...")

    try:
        # 创建第一组两列（推文1 + 推文2）
        column_row = {
            "object": "block",
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [{"type": "text", "text": {"content": f"📌 {TEST_TWEETS[0][0]}"}}]
                                    }
                                },
                                {
                                    "object": "block",
                                    "type": "embed",
                                    "embed": {
                                        "url": TEST_TWEETS[0][1]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [{"type": "text", "text": {"content": f"📌 {TEST_TWEETS[1][0]}"}}]
                                    }
                                },
                                {
                                    "object": "block",
                                    "type": "embed",
                                    "embed": {
                                        "url": TEST_TWEETS[1][1]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        children.append(column_row)

        # 添加分隔
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "---"}}]
            }
        })

        # 创建第二组两列（推文3 + 推文4）
        column_row2 = {
            "object": "block",
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [{"type": "text", "text": {"content": f"📌 {TEST_TWEETS[2][0]}"}}]
                                    }
                                },
                                {
                                    "object": "block",
                                    "type": "embed",
                                    "embed": {
                                        "url": TEST_TWEETS[2][1]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [{"type": "text", "text": {"content": f"📌 {TEST_TWEETS[3][0]}"}}]
                                    }
                                },
                                {
                                    "object": "block",
                                    "type": "embed",
                                    "embed": {
                                        "url": TEST_TWEETS[3][1]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        children.append(column_row2)

    except Exception as e:
        print(f"❌ column_block可能不支持: {e}")
        print("\n📊 尝试方案2: 使用简单的分隔布局...")

        # 方案2: 简单布局（备用）
        for i, (name, url) in enumerate(TEST_TWEETS, 1):
            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": f"{i}. {name}"}}]
                }
            })
            children.append({
                "object": "block",
                "type": "embed",
                "embed": {
                    "url": url
                }
            })
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "---"}}]
                }
            })

    # 创建页面
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": NOTION_PARENT_PAGE_ID
        },
        "properties": {
            "title": {
                "title": [{"text": {"content": "🧪 Twitter 两列布局测试"}}]
            }
        },
        "children": children
    }

    try:
        print(f"\n正在创建测试页面...")
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
    print("🧪 Notion Twitter 两列布局测试")
    print("=" * 70)

    page_url = create_two_column_test()

    if page_url:
        print("\n" + "=" * 70)
        print("✅ 测试完成！")
        print("=" * 70)
        print(f"\n📝 请访问以下URL查看两列布局效果:")
        print(f"   {page_url}")
        print()
