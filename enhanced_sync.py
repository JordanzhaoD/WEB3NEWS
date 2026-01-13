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
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Set
import time

# 免费翻译服务
from deep_translator import GoogleTranslator

# ============ 配置区 ============

# Notion配置（从环境变量读取）
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "2e67c8ad0dbb8128add1fad9be96c1f6")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "2e67c8ad0dbb8173bbfed146339168cc")

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
SYNC_ZH_COUNT = 30  # 中文话题数量
SYNC_EN_COUNT = 30  # 英文话题数量

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

def create_story_page(database_id: str, story: Dict, lang: str,
                       timeline: List[Dict], authors: List[Dict],
                       translated_summary: str = "") -> str:
    """
    为故事创建详细的Notion页面(直接在数据库中创建)

    页面结构:
    1. 标题(heading_2)
    2. 元数据区
    3. 摘要区
    4. TOP QUOTES(推文列表)
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

    # 创建页面(在数据库中创建,避免被删除)
    payload = {
        "parent": {
            "type": "database_id",
            "database_id": database_id
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
            "话题ID": {
                "rich_text": [{
                    "text": {"content": story_id}
                }]
            },
            "状态": {
                "select": {"name": "🔥 热门"}
            }
        },
        "children": children
    }

    # 调试：打印parent_page_id

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

def create_news_column_notion_standard(stories: List[Dict], title: str, lang_emoji: str) -> List[Dict]:
    """
    创建符合Notion标准的单列新闻内容

    Notion标准最佳实践：
    - 使用heading_1突出TOP 3（大号标题）
    - 使用heading_3显示4-30（中号标题，统一格式）
    - 使用callout突出重要信息
    - 使用divider分隔不同区域
    - 使用emoji增强视觉识别

    参数：
        stories: 该语言的新闻列表
        title: 列标题（如"中文热点"）
        lang_emoji: 语言emoji（如"🇨🇳"）
    """
    column_children = []

    # 列标题 - 使用heading_2（中等大小）
    column_children.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [
                {"type": "text", "text": {"content": f"{lang_emoji} {title} ({len(stories)}条)"}}
            ]
        }
    })

    # 分隔线
    column_children.append({
        "object": "block",
        "type": "divider",
        "divider": {}
    })

    # 添加TOP 3新闻 - 使用heading_3（中号显示，简约整齐）
    for i, item in enumerate(stories[:3], 1):
        story = item["story"]
        page_id = item["page_id"]
        keyword = story.get("keyword", "")
        attention_score = story.get("attention_score", 0)
        page_url = f"https://www.notion.so/{page_id.replace('-', '')}"

        # 根据排名使用奖牌emoji
        rank_emojis = ["🥇", "🥈", "🥉"]
        rank_emoji = rank_emojis[i-1]

        # TOP 3 使用heading_3（中号标题，与4-30统一风格）
        column_children.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [
                    {"type": "text", "text": {"content": f"{rank_emoji} "}},
                    {
                        "type": "text",
                        "text": {"content": keyword, "link": {"url": page_url}}
                    },
                    {"type": "text", "text": {"content": f" · {attention_score:,}"}}
                ]
            }
        })

    # 4-30 区域 - 使用bulleted_list_item（正常项目列表，简约整齐）
    if len(stories) > 3:
        # 分隔线
        column_children.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })

        # 4-30 统一使用bulleted_list_item（正常列表项）
        # 使用enumerate获取正确的序号（4-20），而不是全局rank
        for idx, item in enumerate(stories[3:30], start=4):
            story = item["story"]
            page_id = item["page_id"]
            keyword = story.get("keyword", "")
            attention_score = story.get("attention_score", 0)
            page_url = f"https://www.notion.so/{page_id.replace('-', '')}"

            # 使用bulleted_list_item（正常项目列表）
            column_children.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"{idx}. "}},
                        {
                            "type": "text",
                            "text": {"content": keyword, "link": {"url": page_url}}
                        },
                        {"type": "text", "text": {"content": f" · {attention_score:,}"}}
                    ]
                }
            })

    return column_children

def update_parent_page_with_news_list(stories_with_pages: List[Dict]):
    """
    更新父页面，创建符合Notion标准的左右两列新闻列表

    Notion标准布局：
    - 使用column_list创建左右两列
    - 左列：中文30条
    - 右列：英文30条（含翻译）
    - TOP 3: heading_1（大号标题）
    - 4-20: heading_3（中号标题）
    - 21-30: bulleted_list（简洁列表）
    - 使用callout、divider、emoji增强可读性

    参数：
        stories_with_pages: 包含story和page_id的字典列表
    """
    log_info("更新父页面新闻列表（Notion标准左右两列）...")

    url = f"https://api.notion.com/v1/blocks/{NOTION_PARENT_PAGE_ID}/children"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # 1. 先获取并删除父页面的所有现有内容
    try:
        get_url = f"https://api.notion.com/v1/blocks/{NOTION_PARENT_PAGE_ID}/children"
        response = requests.get(get_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 删除所有现有block
        for block in data.get("results", []):
            block_id = block.get("id")
            if block_id:
                delete_url = f"https://api.notion.com/v1/blocks/{block_id}"
                try:
                    requests.delete(delete_url, headers=headers, timeout=5)
                except:
                    pass  # 忽略删除失败

        log_info("  清空父页面旧内容")
    except Exception as e:
        log_warning(f"  清空父页面失败: {e}")

    # 2. 分离中英文新闻
    zh_stories = [s for s in stories_with_pages if s.get("lang") == "zh"]
    en_stories = [s for s in stories_with_pages if s.get("lang") == "en"]

    log_info(f"  中文新闻: {len(zh_stories)} 条")
    log_info(f"  英文新闻: {len(en_stories)} 条")

    # 3. 准备新的页面内容（遵循Notion标准）
    children = []

    # 主标题区 - 使用heading_1
    beijing_tz = timezone(timedelta(hours=8))
    current_time = datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M:%S")

    children.append({
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": "🌐 WEB3 新闻热点 (中英双语)"}}]
        }
    })

    # 更新信息 - 使用callout突出显示
    children.append({
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [
                {"type": "text", "text": {"content": f"⏰ 最后更新: "}},
                {"type": "text", "text": {"content": f"{current_time} (北京时间) | "}},
                {"type": "text", "text": {"content": f"共{len(stories_with_pages)}条新闻"}}
            ]
        }
    })

    # 分隔线
    children.append({
        "object": "block",
        "type": "divider",
        "divider": {}
    })

    # 创建符合Notion标准的左右两列
    left_column_children = create_news_column_notion_standard(zh_stories, "中文热点", "🇨🇳")
    right_column_children = create_news_column_notion_standard(en_stories, "英文热点", "🇺🇸")

    # 构建column_list结构（Notion标准两列布局）
    children.append({
        "object": "block",
        "type": "column_list",
        "column_list": {
            "children": [
                {
                    "object": "block",
                    "type": "column",
                    "column": {
                        "children": left_column_children
                    }
                },
                {
                    "object": "block",
                    "type": "column",
                    "column": {
                        "children": right_column_children
                    }
                }
            ]
        }
    })

    # 4. 批量添加到父页面
    batch_size = 100
    for i in range(0, len(children), batch_size):
        batch = children[i:i+batch_size]
        payload = {"children": batch}

        try:
            response = requests.patch(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
        except Exception as e:
            log_error(f"  添加内容到父页面失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    log_error(f"  错误详情: {error_detail}")
                except:
                    log_error(f"  响应内容: {e.response.text[:500]}")
            return False

    log_success("父页面新闻列表已更新（Notion标准左右两列）")
    return True

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🚀 Chainbase TOPS → Notion 增强版同步")
    print("   (创建详细页面 + 推文数据 + 父页面新闻列表)")
    print("=" * 70)

    print(f"   NOTION_PARENT_PAGE_ID: {NOTION_PARENT_PAGE_ID[:8]}...{NOTION_PARENT_PAGE_ID[-8:]} (长度: {len(NOTION_PARENT_PAGE_ID)})")

    # 检查配置
    if not NOTION_DATABASE_ID:
        log_error("NOTION_DATABASE_ID 未设置！")
        return

    if not NOTION_PARENT_PAGE_ID:
        log_error("NOTION_PARENT_PAGE_ID 未设置！")
        return

    # 存储所有同步的故事和page_id
    stories_with_pages = []

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

        # 创建详细页面(直接在数据库中创建,避免被删除)
        page_id = create_story_page(NOTION_DATABASE_ID, story, "zh",
                                     timeline, authors)

        if page_id:
            # 不再需要单独创建数据库条目,页面已经在数据库中
            # 收集故事数据,用于更新父页面
            stories_with_pages.append({
                "story": story,
                "page_id": page_id,
                "rank": len(stories_with_pages) + 1,
                "lang": "zh"
            })
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

            # 创建详细页面(直接在数据库中创建,避免被删除)
            page_id = create_story_page(NOTION_DATABASE_ID, story, "en",
                                         timeline, authors, translated_summary)

            if page_id:
                # 不再需要单独创建数据库条目,页面已经在数据库中
                # 收集故事数据,用于更新父页面
                stories_with_pages.append({
                    "story": story,
                    "page_id": page_id,
                    "rank": len(stories_with_pages) + 1,
                    "lang": "en"
                })
                log_success(f"✅ 完成: {keyword[:30]}")
            else:
                print("❌")

            time.sleep(3)  # 英文话题需要翻译，延迟更长

    # 5. 更新父页面新闻列表
    if stories_with_pages:
        print("\n📰 更新父页面新闻列表")
        print("-" * 70)
        update_parent_page_with_news_list(stories_with_pages)

    # 6. 统计
    print("\n" + "=" * 70)
    print("📈 同步统计")
    print("=" * 70)
    log_success(f"中文话题: {min(len(zh_stories), SYNC_ZH_COUNT)} 个")
    if en_stories:
        log_success(f"英文话题: {min(len(en_stories), SYNC_EN_COUNT)} 个（含免费翻译）")
    log_info(f"每个话题包含:")
    log_info(f"  - 详细页面（元数据、摘要、推文、作者）")
    log_info(f"  - 数据库条目（快速访问）")
    log_info(f"  - 父页面新闻列表（TOP 20排行）")

    print("\n" + "=" * 70)
    print("🎉 增强版同步完成！")
    print("=" * 70)
    print(f"\n💡 查看数据库: https://www.notion.so/{NOTION_DATABASE_ID.replace('-', '')}")
    print(f"   每个话题都有详细页面，包含推文和作者信息")
    print(f"   ✅ 父页面已更新：新闻列表TOP {len(stories_with_pages)}")
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
