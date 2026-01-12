#!/usr/bin/env python3
"""
测试Notion embed方案 - 完整流程
只同步1个话题，验证Twitter embed效果
"""

import sys
sys.path.append('/Users/ziwind/my-vibe-project/WEB3NEWS')

from enhanced_sync import (
    get_chainbase_stories,
    get_story_timeline,
    get_story_authors,
    create_story_page,
    add_database_entry,
    NOTION_PARENT_PAGE_ID,
    NOTION_DATABASE_ID,
    log_info, log_success, log_error
)

def test_one_topic():
    """测试同步1个话题"""
    print("\n" + "=" * 70)
    print("🧪 Notion Embed方案测试 - 完整流程")
    print("=" * 70)

    # 获取中文话题
    print("\n📡 获取中文热门话题...")
    stories = get_chainbase_stories("zh")

    if not stories:
        log_error("没有获取到数据")
        return False

    # 只测试第一个话题
    story = stories[0]
    keyword = story.get("keyword", "")
    story_id = story.get("id", "")

    print(f"\n🎯 测试话题: {keyword}")
    print(f"   话题ID: {story_id}")
    print("-" * 70)

    # 获取详细数据
    print("\n📊 获取推文时间线...")
    timeline = get_story_timeline(story_id)

    print("👥 获取相关作者...")
    authors = get_story_authors(story_id)

    # 创建详细页面（包含embed推文）
    print("\n📄 创建详细页面（含Twitter embed）...")
    page_id = create_story_page(
        NOTION_PARENT_PAGE_ID,
        story,
        "zh",
        timeline,
        authors
    )

    if not page_id:
        log_error("页面创建失败")
        return False

    # 添加数据库条目
    print("\n💾 添加数据库条目...")
    if add_database_entry(story, page_id, "zh", len(timeline)):
        log_success("✅ 数据库条目添加成功")
    else:
        log_warning("数据库条目添加失败（页面已创建）")

    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)
    print(f"\n📝 请访问以下页面查看Twitter embed效果:")
    print(f"   详细页面: https://www.notion.so/{page_id.replace('-', '')}")
    print(f"   数据库视图: https://www.notion.so/{NOTION_DATABASE_ID.replace('-', '')}")
    print(f"\n💡 每条推文都使用Notion embed显示，包含:")
    print(f"   - 用户信息和认证标识")
    print(f"   - 完整推文内容")
    print(f"   - 图片/视频")
    print(f"   - 互动数据（点赞、回复）")
    print(f"   - 可点击跳转到Twitter")
    print()

    return True

if __name__ == "__main__":
    try:
        success = test_one_topic()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        log_error(f"程序异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
