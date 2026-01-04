"""
小红书服务层 - 旅游博主笔记订阅（增强版）
"""

import httpx
import asyncio
import re
import urllib.parse
import feedparser
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.config import get_settings

settings = get_settings()

# ============================================================
# 旅游博主列表
# ============================================================
# 如何获取博主 ID：
#   1. 打开小红书 App 或网页版 (xiaohongshu.com)
#   2. 进入博主主页，查看 URL：xiaohongshu.com/user/profile/XXXXXX
#   3. URL 中 profile/ 后面的 24 位字符串即为博主 ID
#   4. 例如：https://www.xiaohongshu.com/user/profile/593032945e87e77791e03696
#      博主 ID 为：593032945e87e77791e03696
# ============================================================
TRAVEL_BLOGGERS = [
    # 已验证有效的博主
    {"id": "593032945e87e77791e03696", "name": "小宇菇菇", "tags": ["旅游", "攻略"]},
     # 嬉游: 全网最顶的机酒卡攻略，非常专业
    {"id": "5aec57f04eacab43557f7b77", "name": "嬉游小助理", "tags": ["机酒攻略", "专业"]},
    # 小墨与阿猴: 摄影与攻略结合，适合情侣/年轻人群体
    {"id": "52f59215b4c4d66b2eafa21d", "name": "小墨与阿猴", "tags": ["摄影", "情侣游"]},
    # 这里是新疆: 专注新疆旅游，非常垂直
    {"id": "5acf498411be105586e79b4c", "name": "这里是新疆", "tags": ["新疆", "垂直攻略"]},
    # --- 小众秘境 (避开人流) ---
    # 房琪kiki: 治愈系文案，推荐的地方有格调
    {"id": "5bf9ff7e999837000189d106", "name": "房琪kiki", "tags": ["治愈", "文案", "小众"]},
     # 小🐑爱溜达～: 北京本地吃喝玩乐专家
    {"id": "616cdf5a000000001f03a074", "name": "小🐑爱溜达～", "tags": ["北京", "本地生活"]},
    # 小鹿Lawrence: 导演/摄影师，高质量环球旅行影像
    {"id": "5af05c664eacab116931c0d0", "name": "小鹿Lawrence", "tags": ["环球旅行", "影像", "摄影"]},
    # Linksphotograph: 顶级风光摄影，探索世界极境
    {"id": "5f0a7dfb0000000001007eaa", "name": "Linksphotograph", "tags": ["风光摄影", "极限探索"]},
    # 贝贝贝贝贝 (攻略版): 专注旅游攻略分享
    {"id": "6613e7610000000003033ddc", "name": "贝贝贝贝贝 (攻略版)", "tags": ["攻略", "打卡"]},
    # 旅行搭子小爱酱: 江浙沪周边游，主打高性价比和省钱攻略
    {"id": "64239daf00000000120120dd", "name": "旅行搭子小爱酱", "tags": ["江浙沪", "省钱攻略"]},
    # Eden的环球旅行：29岁花33万环球旅行，已去过七大洲40+国家
    {"id": "5ffd4e370000000001008dbc", "name": "Eden的环球旅行", "tags": ["环球旅行", "攻略", "生活方式"]},

    # 添加更多博主时，请先验证 ID 有效性，格式：
    # {"id": "24位用户ID", "name": "昵称", "tags": ["标签1", "标签2"]},
]


def _fix_localhost_url(url: str) -> str:
    """将 localhost 替换为 127.0.0.1，避免 IPv6 解析问题"""
    return url.replace("localhost", "127.0.0.1")


async def check_rsshub_health() -> Dict[str, Any]:
    """检查 RSSHub 服务健康状态"""
    results = {}
    
    for url in [settings.xhs_rsshub_base_url, settings.xhs_rsshub_fallback_url]:
        fixed_url = _fix_localhost_url(url)
        try:
            async with httpx.AsyncClient(timeout=5.0, trust_env=False) as client:
                health_url = f"{fixed_url}/healthz"
                print(f"[DEBUG] 健康检查: {health_url}")
                resp = await client.get(health_url)
                print(f"[DEBUG] 响应: {resp.status_code}")
                results[url] = {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
        except Exception as e:
            print(f"[DEBUG] 健康检查异常: {type(e).__name__}: {e}")
            results[url] = {"status": "error", "error": str(e)}
    
    return results


async def get_xhs_notes(keyword: str) -> Dict[str, Any]:
    """
    获取小红书笔记数据
    策略：先尝试本地 RSSHub，失败后切换到公共实例
    """
    rsshub_urls = [settings.xhs_rsshub_base_url, settings.xhs_rsshub_fallback_url]
    
    print(f"[XHS] 开始获取笔记，关键词: {keyword}")
    
    for base_url in rsshub_urls:
        print(f"[XHS] 尝试 RSSHub: {base_url}")
        result = await _try_get_notes(base_url, keyword)
        
        if result["status"] == "success" and result["data"]:
            print(f"[XHS] 成功从 {base_url} 获取 {len(result['data'])} 条笔记")
            return result
        
        print(f"[XHS] {base_url} 失败，尝试下一个...")
    
    print("[XHS] 所有 RSSHub 实例失败，返回降级响应")
    return {
        "status": "fallback",
        "data": [],
        "search_url": _build_search_url(keyword),
        "message": "小红书数据暂时无法获取，请点击链接直接搜索"
    }


async def _try_get_notes(base_url: str, keyword: str) -> Dict[str, Any]:
    """尝试从指定 RSSHub 实例获取笔记 - 搜索所有博主，严格匹配关键词"""
    matched_notes = []  # 只存储匹配关键词的笔记
    fixed_base_url = _fix_localhost_url(base_url)
    success_count = 0
    
    print(f"[DEBUG] _try_get_notes: 原始URL={base_url}, 修正后={fixed_base_url}")
    print(f"[DEBUG] 开始搜索全部 {len(TRAVEL_BLOGGERS)} 个博主...")
    
    # 并发请求所有博主，提高效率
    async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
        for i, blogger in enumerate(TRAVEL_BLOGGERS):
            if i > 0:
                await asyncio.sleep(0.5)  # 减少间隔，加快搜索
            
            url = f"{fixed_base_url}/xiaohongshu/user/{blogger['id']}/notes"
            
            try:
                print(f"[DEBUG] [{i+1}/{len(TRAVEL_BLOGGERS)}] 请求: {blogger['name']}")
                response = await client.get(url)
                print(f"[DEBUG] {blogger['name']}: status={response.status_code}, len={len(response.text)}")
                
                if response.status_code != 200:
                    print(f"[DEBUG] 响应内容: {response.text[:200]}")
                    continue
                
                success_count += 1
                notes = _parse_rss(response.text, blogger["name"], blogger.get("tags", []))
                
                if notes:
                    # 严格匹配：只添加匹配关键词的笔记
                    filtered = _filter_by_keyword(notes, keyword)
                    if filtered:
                        matched_notes.extend(filtered)
                        print(f"[DEBUG] {blogger['name']}: 匹配 {len(filtered)} 条")
                            
            except httpx.TimeoutException:
                print(f"[DEBUG] 超时: {blogger['name']}")
            except Exception as e:
                print(f"[DEBUG] 异常 {blogger['name']}: {type(e).__name__}: {e}")
    
    print(f"[DEBUG] 搜索完成: 成功请求 {success_count}/{len(TRAVEL_BLOGGERS)} 个博主, 匹配 {len(matched_notes)} 条笔记")
    
    # 严格匹配：有匹配结果才返回 success，否则返回 fallback
    if matched_notes:
        matched_notes.sort(key=lambda x: x.get("liked_count", 0), reverse=True)
        return {
            "status": "success",
            "data": matched_notes[:6],
            "search_url": _build_search_url(keyword)
        }
    
    # 无匹配时直接降级，不返回不相关的帖文
    return {"status": "fallback", "data": [], "search_url": _build_search_url(keyword)}


def _parse_rss(xml_content: str, author_name: str, author_tags: List[str]) -> List[Dict]:
    """解析 RSS XML，提取完整笔记信息"""
    notes = []
    
    try:
        feed = feedparser.parse(xml_content)
        
        for i, entry in enumerate(feed.entries[:10]):
            cover_image = _extract_cover_image(entry)
            liked_count = _extract_liked_count(entry)
            published = _extract_published(entry)
            description = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            
            link = getattr(entry, 'link', '')
            note_id = _extract_note_id(link, i)
            title = getattr(entry, 'title', '无标题')
            
            print(f"[DEBUG] 笔记: {title[:30]}... | 图片: {cover_image[:80] if cover_image else '无'}")
            
            notes.append({
                "id": note_id,
                "title": title,
                "note_url": link,
                "cover_image": cover_image,
                "description": description,
                "author": author_name,
                "author_tags": author_tags,
                "liked_count": liked_count,
                "published": published,
            })
            
    except Exception as e:
        print(f"[XHS] RSS 解析错误: {e}")
    
    return notes


def _extract_note_id(link: str, index: int) -> str:
    """从链接提取笔记 ID"""
    if '/discovery/item/' in link:
        return link.split('/discovery/item/')[-1].split('?')[0]
    elif '/explore/' in link:
        return link.split('/explore/')[-1].split('?')[0]
    return f"note_{index}"


def _extract_cover_image(entry) -> str:
    """提取封面图片"""
    content = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
    
    if not content:
        return ""
    
    # 视频封面
    video_match = re.search(r'poster=["\']([^"\']+)["\']', content)
    if video_match:
        return _proxy_image(video_match.group(1))
    
    # 图片
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    if img_match:
        return _proxy_image(img_match.group(1))
    
    return ""


def _extract_liked_count(entry) -> int:
    """提取点赞数"""
    # RSSHub 可能在 upvotes 字段返回点赞数
    if hasattr(entry, 'upvotes'):
        try:
            return int(entry.upvotes)
        except (ValueError, TypeError):
            pass
    
    # 尝试从描述中提取
    content = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
    match = re.search(r'(\d+)\s*(?:赞|点赞|likes?)', content, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    return 0


def _extract_published(entry) -> Optional[str]:
    """提取发布时间"""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6])
            return dt.strftime("%Y-%m-%d")
        except Exception:
            pass
    
    if hasattr(entry, 'published'):
        return entry.published[:10] if len(entry.published) >= 10 else entry.published
    
    return None


def _proxy_image(img_url: str) -> str:
    """代理图片 URL，解决防盗链"""
    if not img_url:
        return ""
    encoded = urllib.parse.quote(img_url, safe='')
    return f"https://wsrv.nl/?url={encoded}"


def _filter_by_keyword(notes: List[Dict], keyword: str) -> List[Dict]:
    """根据关键词筛选笔记（搜索标题和描述）"""
    if not keyword:
        return notes
    
    keywords = keyword.lower().split()
    
    def match_note(note):
        title = note.get("title", "").lower()
        desc = note.get("description", "").lower()
        return any(kw in title or kw in desc for kw in keywords)
    
    matched = [note for note in notes if match_note(note)]
    print(f"[DEBUG] 关键词筛选: {keyword} -> 匹配 {len(matched)}/{len(notes)} 条")
    return matched


def _build_search_url(keyword: str) -> str:
    """构建小红书搜索 URL"""
    encoded = urllib.parse.quote(keyword)
    return f"https://www.xiaohongshu.com/search_result?keyword={encoded}"
