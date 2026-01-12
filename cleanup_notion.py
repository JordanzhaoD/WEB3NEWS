#!/usr/bin/env python3
"""
清理Notion数据库中的所有测试数据
- 删除所有数据库记录
- 删除所有详细页面
"""

import requests
import json
import os
import sys

# 从环境变量读取
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not NOTION_API_KEY:
    print("❌ 错误: 请设置NOTION_API_KEY环境变量")
    sys.exit(1)

print("=" * 70)
print("🗑️  清理Notion测试数据")
print("=" * 70)

# Notion API配置
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 1. 查询数据库中的所有记录
print("\n📊 正在查询数据库记录...")
url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

all_records = []
has_more = True
start_cursor = None

while has_more:
    payload = {}
    if start_cursor:
        payload["start_cursor"] = start_cursor

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        all_records.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

    except Exception as e:
        print(f"❌ 查询失败: {e}")
        sys.exit(1)

print(f"✅ 找到 {len(all_records)} 条记录")

if len(all_records) == 0:
    print("📭 数据库为空，无需清理")
    sys.exit(0)

# 2. 删除每条记录（包含详细页面）
print(f"\n🗑️  开始删除记录...")

deleted_count = 0
failed_count = 0

for i, record in enumerate(all_records, 1):
    page_id = record.get("id")
    title = ""

    # 获取标题
    if "properties" in record and "Name" in record["properties"]:
        title_obj = record["properties"]["Name"]["title"]
        if title_obj:
            title = title_obj[0].get("text", {}).get("content", "")

    print(f"[{i}/{len(all_records)}] 删除: {title[:50]}...")

    # 删除页面（包含所有子内容）
    try:
        delete_url = f"https://api.notion.com/v1/blocks/{page_id}"
        response = requests.delete(delete_url, headers=headers, timeout=10)
        response.raise_for_status()
        deleted_count += 1
        print(f"  ✅ 删除成功")

    except Exception as e:
        failed_count += 1
        print(f"  ❌ 删除失败: {e}")

# 3. 总结
print("\n" + "=" * 70)
print("📊 清理完成")
print("=" * 70)
print(f"✅ 成功删除: {deleted_count} 条")
print(f"❌ 删除失败: {failed_count} 条")
print(f"📊 总记录数: {len(all_records)} 条")

if deleted_count == len(all_records):
    print("\n🎉 所有测试数据已清理完成！")
else:
    print(f"\n⚠️  有 {failed_count} 条记录删除失败，请手动检查")
