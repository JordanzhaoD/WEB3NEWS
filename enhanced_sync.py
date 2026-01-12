#!/usr/bin/env python3
"""
Chainbase TOPS → Notion 增强版同步脚本
功能：
✅ 获取推文时间线数据
✅ 获取相关作者信息
✅ 为每个话题创建详细的Notion子页面
✅ 数据库视图简洁，点击查看详情
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Set
import time

# 免费翻译服务
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

# 同步配置
TRANSLATOR_ENABLED = True
SYNC_ZH_COUNT = 5  # 测试：只同步前5个中文话题（创建页面较慢）
SYNC_EN_COUNT = 5  # 测试：只同步前5个英文话题

# ============ 工具函数 ============

def log(level: str, message: str):
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

def get_story_timeline(story_id: str) -> List[Dict]:
    """获取故事推文时间线"""
    try:
        url = f"https://api.chainbase.com/tops/api/hotspot/{story_id}/timeline"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        timeline = response.json()
        log_info(f"  推文时间线: {len(timeline)} 条")
        return timeline
    except Exception as e:
        log_warning(f"  获取时间线失败: {e}")
        return []

def get_story_authors(story_id: str) -> List[Dict]:
    """获取故事相关作者"""
    try:
        url = f"https://api.chainbase.com/tops/api/hotspot/{story_id}/authors"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        authors = response.json()
        log_info(f"  相关作者: {len(authors)} 位")
        return authors
    except Exception as e:
        log_warning(f"  获取作者失败: {e}")
        return []

def translate_text_to_chinese(text: str) -> str:
    """使用免费Google翻译API翻译英文到中文"""
    if not TRANSLATOR_ENABLED or not text or not text.strip():
        return ""
    try:
        translator = GoogleTranslator(source='auto', target='zh-CN')
        translated_text = translator.translate(text)
        if translated_text and translated_text.strip():
            return translated_text.strip()
        else:
            return text
    except Exception as e:
        log_warning(f"翻译失败: {str(e)[:30]}...")
        return text

# ============ Notion函数 ============

def create_story_page(parent_page_id: str, story: Dict, lang: str,
                       timeline: List[Dict], authors: List[Dict],
                       translated_summary: str = "") -> str:
    """
    为故事创建详细的Notion页面（简化版，兼容Notion API）

    页面结构：
    1. 标题（heading_2）
    2. 元数据区
    3. 摘要区
    4. TOP QUOTES（推文列表）
    5. 相关作者
    """

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    story_id = story.get("id", "")
    keyword = story.get("keyword", "")
    summary = story.get("summary", "")

    # 准备页面内容
    children = []

    # 1. 页面标题（使用heading_2而不是heading_1）
    children.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{
                "type": "text",
                "text": {"content": f"📰 {keyword}"}
            }]
        }
    })

    # 2. 元数据区
    lang_emoji = "🇨🇳" if lang == "zh" else "🇺🇸"
    metadata = f"{lang_emoji} 语言: {('中文' if lang == 'zh' else '英文')} | "
    metadata += f"📊 话题ID: {story_id} | "
    metadata += f"🔗 Chainbase: https://tops.chainbase.com/s/{story_id}"

    children.append({
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": metadata}}]
        }
    })

    # 3. 摘要区
    children.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "📝 摘要"}}]
        }
    })

    if lang == "zh":
        summary_text = summary
    else:
        summary_text = f"【原文】\n{summary}\n\n【译文】\n{translated_summary}"

    children.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": summary_text[:2000]}}]
        }
    })

    # 4. 关注度趋势（如果有时序数据）
    if timeline and len(timeline) >= 2:
        children.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📈 关注度趋势"}}]
            }
        })

        earliest = min(timeline, key=lambda x: x.get("timestamp", ""))
        latest = max(timeline, key=lambda x: x.get("timestamp", ""))

        trend_text = f"⏰ 最早讨论: {earliest.get('timestamp', 'N/A')}\n"
        trend_text += f"⏰ 最新讨论: {latest.get('timestamp', 'N/A')}\n"
        trend_text += f"📊 推文总数: {len(timeline)} 条"

        children.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": trend_text}}]
            }
        })

    # 5. TOP QUOTES（推文列表 - 两列布局）
    if timeline:
        children.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": f"💬 TOP QUOTES ({len(timeline)} 条推文)"}}]
            }
        })

        # 取前6条推文（按评分排序，调整为6条以适配3组两列）
        top_tweets = sorted(timeline, key=lambda x: x.get("score", 0), reverse=True)[:6]

        # 创建推文信息函数
        def create_tweet_column(tweet, index):
            user_name = tweet.get("user_name", "Unknown")
            timestamp = tweet.get("timestamp", "")
            score = tweet.get("score", 0)
            tweet_url = tweet.get("url", "")

            column_children = [
                # 推文标题
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": f"{index}. {user_name[:20]} | 评分: {score:.0f}"}}]
                    }
                },
                # 推文时间
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": f"⏰ {timestamp[:16]}"}}]
                    }
                }
            ]

            # 嵌入推文
            if tweet_url:
                column_children.append({
                    "object": "block",
                    "type": "embed",
                    "embed": {
                        "url": tweet_url
                    }
                })

            return column_children

        # 分组：2+2+2（每组两列）
        for group_idx in range(0, len(top_tweets), 2):
            group_tweets = top_tweets[group_idx:group_idx+2]

            # 创建两列
            columns = []
            for idx, tweet in enumerate(group_tweets, group_idx + 1):
                column_children = create_tweet_column(tweet, idx)
                columns.append({
                    "object": "block",
                    "type": "column",
                    "column": {
                        "children": column_children
                    }
                })

            # 如果这一组有2条推文，创建column_list
            if len(columns) == 2:
                children.append({
                    "object": "block",
                    "type": "column_list",
                    "column_list": {
                        "children": columns
                    }
                })
            # 如果这一组只有1条推文（最后剩余的情况），直接添加
            elif len(columns) == 1:
                children.extend(columns[0]["column"]["children"])

            # 添加组间分隔（除了最后一组）
            if group_idx + 2 < len(top_tweets):
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "---"}}]
                    }
                })

    # 6. 相关作者
    if authors:
        children.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": f"👥 相关作者 ({len(authors)} 位)"}}]
            }
        })

        top_authors = authors[:10]

        for author in top_authors:
            user_name = author.get("user_name", "Unknown")
            screen_name = author.get("user_screen_name", "")
            heat = author.get("heat_percentage", 0)
            blue_verified = author.get("blue_verified", False)

            verified = " ✓" if blue_verified else ""
            author_text = f"• {user_name}{verified} (@{screen_name}) - 热度: {heat}%"

            children.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": author_text}}]
                }
            })

    # 创建页面
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": parent_page_id
        },
        "properties": {
            "title": {
                "title": [{
                    "text": {"content": keyword[:100]}
                }]
            }
        },
        "children": children
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        page_data = response.json()
        page_id = page_data["id"]
        page_url = page_data["url"]
        log_success(f"  页面创建成功")
        return page_id
    except Exception as e:
        log_error(f"  创建页面失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            log_error(f"  错误详情: {e.response.text[:200]}")
        return ""

def add_database_entry(story: Dict, page_id: str, lang: str,
                        tweet_count: int = 0, translated_summary: str = "") -> bool:
    """在数据库中添加条目，链接到详细页面"""
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    story_id = story.get("id", "")
    keyword = story.get("keyword", "")
    summary = story.get("summary", "")

    # 摘要处理
    if lang == "zh":
        # 中文话题：直接显示原文
        summary_short = summary[:100] + "..." if len(summary) > 100 else summary
    else:
        # 英文话题：组合原文和译文
        if translated_summary:
            summary_short = f"【原文】\n{summary[:100]}...\n\n【译文】\n{translated_summary[:100]}..."
        else:
            summary_short = summary[:100] + "..." if len(summary) > 100 else summary

    payload = {
        "parent": {
            "type": "database_id",
            "database_id": NOTION_DATABASE_ID
        },
        "properties": {
            "Name": {
                "title": [{
                    "text": {"content": keyword[:100]}
                }]
            },
            "语言": {
                "select": {"name": "中文" if lang == "zh" else "英文"}
            },
            "摘要": {
                "rich_text": [{
                    "text": {"content": summary_short}
                }]
            },
            "话题ID": {
                "rich_text": [{
                    "text": {"content": story_id}
                }]
            },
            "状态": {
                "select": {"name": "🔥 热门"}
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        log_error(f"  添加数据库条目失败: {e}")
        return False

# ============ 主函数 ============

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🚀 Chainbase TOPS → Notion 增强版同步")
    print("   (创建详细页面 + 推文数据)")
    print("=" * 70)

    # 检查配置
    if not NOTION_DATABASE_ID:
        log_error("NOTION_DATABASE_ID 未设置！")
        return

    # 1. 获取中文热门话题
    print("\n🇨🇳 获取中文热门话题")
    print("-" * 70)
    zh_stories = get_chainbase_stories("zh")
    if not zh_stories:
        log_error("没有获取到数据")
        return

    # 2. 为每个话题创建详细页面
    print(f"\n📄 为前 {min(len(zh_stories), SYNC_ZH_COUNT)} 个话题创建详细页面")
    print("-" * 70)

    for i, story in enumerate(zh_stories[:SYNC_ZH_COUNT], 1):
        keyword = story.get("keyword", "")
        story_id = story.get("id", "")

        print(f"\n[{i}/{min(len(zh_stories), SYNC_ZH_COUNT)}] 处理: {keyword[:40]}... ")

        # 获取详细数据
        timeline = get_story_timeline(story_id)
        authors = get_story_authors(story_id)

        # 创建详细页面（在父页面下）
        page_id = create_story_page(NOTION_PARENT_PAGE_ID, story, "zh",
                                     timeline, authors)

        if page_id:
            # 在数据库中创建条目
            if add_database_entry(story, page_id, "zh", len(timeline)):
                log_success(f"✅ 完成: {keyword[:30]}")
        else:
            print("❌")

        time.sleep(2)  # 避免API限流

    # 3. 获取英文热门话题
    print("\n🇺🇸 获取英文热门话题")
    print("-" * 70)
    en_stories = get_chainbase_stories("en")
    if not en_stories:
        log_warning("没有获取到英文数据")
        en_stories = []

    # 4. 为每个英文话题创建详细页面（带翻译）
    if en_stories:
        print(f"\n📄 为前 {min(len(en_stories), SYNC_EN_COUNT)} 个英文话题创建详细页面")
        print("-" * 70)

        for i, story in enumerate(en_stories[:SYNC_EN_COUNT], 1):
            keyword = story.get("keyword", "")
            story_id = story.get("id", "")
            summary = story.get("summary", "")

            print(f"\n[{i}/{min(len(en_stories), SYNC_EN_COUNT)}] 处理: {keyword[:40]}... ")

            # 翻译摘要
            translated_summary = ""
            if TRANSLATOR_ENABLED and summary:
                print("  🌐 翻译中...", end="", flush=True)
                translated_summary = translate_text_to_chinese(summary)
                print(" ✅")

            # 获取详细数据
            timeline = get_story_timeline(story_id)
            authors = get_story_authors(story_id)

            # 创建详细页面（在父页面下）
            page_id = create_story_page(NOTION_PARENT_PAGE_ID, story, "en",
                                         timeline, authors, translated_summary)

            if page_id:
                # 在数据库中创建条目
                if add_database_entry(story, page_id, "en", len(timeline), translated_summary):
                    log_success(f"✅ 完成: {keyword[:30]}")
            else:
                print("❌")

            time.sleep(3)  # 英文话题需要翻译，延迟更长

    # 5. 统计
    print("\n" + "=" * 70)
    print("📈 同步统计")
    print("=" * 70)
    log_success(f"中文话题: {min(len(zh_stories), SYNC_ZH_COUNT)} 个")
    if en_stories:
        log_success(f"英文话题: {min(len(en_stories), SYNC_EN_COUNT)} 个（含免费翻译）")
    log_info(f"每个话题包含:")
    log_info(f"  - 详细页面（元数据、摘要、推文、作者）")
    log_info(f"  - 数据库条目（快速访问）")

    print("\n" + "=" * 70)
    print("🎉 增强版同步完成！")
    print("=" * 70)
    print(f"\n💡 查看数据库: https://www.notion.so/{NOTION_DATABASE_ID.replace('-', '')}")
    print(f"   每个话题都有详细页面，包含推文和作者信息")
    if en_stories and TRANSLATOR_ENABLED:
        print(f"   ✅ 英文话题已使用Google免费翻译\n")
    else:
        print()

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
