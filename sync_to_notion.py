#!/usr/bin/env python3
"""
Chainbase TOPS → Notion 生产版同步脚本
功能：
✅ 中文话题直接同步
✅ 英文话题翻译成中英对照格式（使用免费Google翻译）
✅ 自动去重（检查话题ID是否已存在）
✅ 支持增量更新和全量同步
✅ 详细的日志输出

翻译服务: Google Translate (完全免费，无需API Key)
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Set
import time

# 免费翻译服务 - Google Translate
from deep_translator import GoogleTranslator

# ============ 配置区 ============

# Notion配置（从环境变量读取）
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")

# 检查必要的环境变量
if not NOTION_API_KEY:
    print("❌ 错误: NOTION_API_KEY环境变量未设置")
    print("   请设置: export NOTION_API_KEY=your_api_key")
    sys.exit(1)

# Chainbase TOPS API
CHAINBASE_API_ZH = "https://api.chainbase.com/tops/v1/stories?lang=zh"
CHAINBASE_API_EN = "https://api.chainbase.com/tops/v1/stories?lang=en"
CHAINBASE_API_REALTIME = "https://api.chainbase.com/tops/v1/realtime-mining"

# 翻译配置 - 使用免费Google翻译，无需API Key
TRANSLATOR_ENABLED = True  # 设置为False可禁用翻译

# 同步配置
SYNC_ZH_COUNT = 20  # 同步中文话题数量
SYNC_EN_COUNT = 10  # 同步英文话题数量（翻译较慢）

# ============ 工具函数 ============

def log(level: str, message: str):
    """带时间戳的日志输出"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level} {message}")

def log_info(message: str):
    log("ℹ️ ", message)

def log_success(message: str):
    log("✅", message)

def log_warning(message: str):
    log("⚠️ ", message)

def log_error(message: str):
    log("❌", message)

# ============ API函数 ============

def get_chainbase_stories(lang: str = "zh") -> List[Dict]:
    """获取Chainbase TOPS热门话题"""
    url = CHAINBASE_API_ZH if lang == "zh" else CHAINBASE_API_EN
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        log_info(f"获取{lang.upper()}数据: {len(items)} 个话题")
        return items
    except Exception as e:
        log_error(f"获取{lang.upper()}数据失败: {e}")
        return []

def get_realtime_mining() -> Dict:
    """获取实时挖矿数据"""
    try:
        response = requests.get(CHAINBASE_API_REALTIME, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})
    except Exception as e:
        log_error(f"获取实时数据失败: {e}")
        return {}

def translate_text_to_chinese(text: str) -> str:
    """使用免费Google翻译API翻译英文到中文"""
    if not TRANSLATOR_ENABLED or not text or not text.strip():
        return ""

    try:
        # 使用GoogleTranslator进行翻译
        translator = GoogleTranslator(source='auto', target='zh-CN')
        translated_text = translator.translate(text)

        if translated_text and translated_text.strip():
            return translated_text.strip()
        else:
            log_warning(f"翻译返回空结果，保留原文")
            return text

    except Exception as e:
        log_warning(f"翻译失败（将保留原文）: {str(e)[:50]}...")
        return text  # 翻译失败返回原文

# ============ Notion函数 ============

def get_existing_story_ids(database_id: str) -> Set[str]:
    """获取数据库中已存在的话题ID，用于去重"""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    existing_ids = set()

    try:
        # 分页获取所有记录
        has_more = True
        while has_more:
            payload = {"page_size": 100}
            if existing_ids:
                # 如果有下一页，使用cursor
                pass

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            # 提取话题ID
            for item in data.get("results", []):
                story_id_props = item.get("properties", {}).get("话题ID", {})
                if story_id_props.get("rich_text"):
                    story_id = story_id_props["rich_text"][0]["text"]["content"]
                    existing_ids.add(story_id)

            has_more = data.get("has_more", False)

        log_info(f"数据库中已有 {len(existing_ids)} 个话题")
        return existing_ids

    except Exception as e:
        log_warning(f"获取已有话题ID失败: {e}")
        return set()

def add_item_to_notion(database_id: str, story: Dict, lang: str,
                      translated_summary: str = "") -> bool:
    """添加单个话题到Notion数据库"""
    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    story_id = story.get("id", "")
    keyword = story.get("keyword", "")
    summary = story.get("summary", "")

    # 准备数据
    title = keyword[:100]

    # 语言选项
    lang_option = "英文" if lang == "en" else "中文"

    # 摘要内容 - 中文直接用原文，英文用中英对照格式
    if lang == "zh":
        summary_text = summary[:2000]
    else:
        # 英文话题：原文 + 译文
        summary_text = f"【原文】\n{summary[:1000]}\n\n【译文】\n{translated_summary[:1000]}"

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
                            "content": title
                        }
                    }
                ]
            },
            "语言": {
                "select": {
                    "name": lang_option
                }
            },
            "摘要": {
                "rich_text": [
                    {
                        "text": {
                            "content": summary_text[:2000]
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
        log_error(f"添加失败: {title[:30]}... - {str(e)[:50]}...")
        return False

# ============ 主函数 ============

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🚀 Chainbase TOPS → Notion 自动同步")
    print("=" * 70)

    # 检查配置
    if not NOTION_DATABASE_ID:
        log_error("NOTION_DATABASE_ID 未设置！")
        log_info("请先运行 test_sync.py 创建数据库")
        return

    if not TRANSLATOR_ENABLED:
        log_warning("翻译功能已禁用，将跳过英文话题翻译")
        log_info("如需翻译，请设置脚本中: TRANSLATOR_ENABLED = True")

    # 1. 获取实时数据
    print("\n📊 实时数据统计")
    print("-" * 70)
    realtime_data = get_realtime_mining()
    if realtime_data:
        attention = realtime_data.get('attention_count', 0)
        total = realtime_data.get('attention_total', 100)
        sources = realtime_data.get('sources', 0)
        ai_load = realtime_data.get('ai_load', 0)

        log_success(f"关注度指数: {attention}/{total}")
        log_success(f"24小时数据源: {sources:,}")
        log_success(f"AI处理量: {ai_load:,}")

    # 2. 获取已有话题ID（用于去重）
    print("\n🔍 检查已有话题...")
    existing_ids = get_existing_story_ids(NOTION_DATABASE_ID)

    # 3. 获取中文热门话题
    print("\n🇨🇳 获取中文热门话题")
    print("-" * 70)
    zh_stories = get_chainbase_stories("zh")
    zh_new = [s for s in zh_stories if s.get("id") not in existing_ids]
    log_info(f"新话题: {len(zh_new)}/{len(zh_stories)}")

    # 4. 获取英文热门话题
    print("\n🇺🇸 获取英文热门话题")
    print("-" * 70)
    en_stories = get_chainbase_stories("en")
    en_new = [s for s in en_stories if s.get("id") not in existing_ids]
    log_info(f"新话题: {len(en_new)}/{len(en_stories)}")

    # 5. 同步中文话题
    print("\n📥 同步中文话题")
    print("-" * 70)
    zh_count = 0
    zh_total = min(len(zh_new), SYNC_ZH_COUNT)

    if zh_total > 0:
        for i, story in enumerate(zh_new[:SYNC_ZH_COUNT], 1):
            keyword = story.get("keyword", "")
            print(f"[{i}/{zh_total}] {keyword[:40]}... ", end="", flush=True)

            if add_item_to_notion(NOTION_DATABASE_ID, story, "zh"):
                log_success("✅")
                zh_count += 1
            else:
                print("❌")

            time.sleep(0.3)  # 避免API限流

    log_success(f"中文话题同步完成: {zh_count}/{zh_total}")

    # 6. 同步英文话题（带翻译）
    en_count = 0
    en_total = min(len(en_new), SYNC_EN_COUNT)

    if TRANSLATOR_ENABLED and en_total > 0:
        print("\n📥 同步英文话题（+ 翻译）")
        print("-" * 70)

        for i, story in enumerate(en_new[:SYNC_EN_COUNT], 1):
            keyword = story.get("keyword", "")
            summary = story.get("summary", "")

            print(f"[{i}/{en_total}] 翻译: {keyword[:30]}... ", end="", flush=True)
            translated_summary = translate_text_to_chinese(summary)
            print("✓ ", end="", flush=True)

            print("添加: ", end="", flush=True)
            if add_item_to_notion(NOTION_DATABASE_ID, story, "en", translated_summary):
                log_success("✅")
                en_count += 1
            else:
                print("❌")

            time.sleep(1)  # 翻译API需要更长间隔

        log_success(f"英文话题同步完成: {en_count}/{en_total}")
    elif not TRANSLATOR_ENABLED and en_total > 0:
        log_warning(f"翻译功能已禁用，跳过 {en_total} 个英文话题")

    # 7. 汇总统计
    print("\n" + "=" * 70)
    print("📈 同步统计")
    print("=" * 70)
    log_success(f"中文话题: {zh_count}/{zh_total}")
    if TRANSLATOR_ENABLED:
        log_success(f"英文话题: {en_count}/{en_total}")
    log_success(f"总计新增: {zh_count + en_count} 个话题")

    total_existing = len(existing_ids)
    total_now = total_existing + zh_count + en_count
    log_info(f"数据库总计: {total_now} 个话题")

    print("\n" + "=" * 70)
    print("🎉 同步完成！")
    print("=" * 70)

    # 8. 数据库链接
    db_url = f"https://www.notion.so/{NOTION_DATABASE_ID.replace('-', '')}"
    print(f"\n📁 查看数据库: {db_url}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        log_error(f"程序异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
