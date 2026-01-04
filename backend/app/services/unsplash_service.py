import requests
from typing import Optional, List, Dict
import logging
from hello_agents import HelloAgentsLLM, SimpleAgent

logger = logging.getLogger(__name__)

class UnsplashService:
    def __init__(self, access_key: str):
        self.access_key = access_key
        self.base_url = "https://api.unsplash.com"
        self.llm = HelloAgentsLLM()
        self.translator = SimpleAgent(
            name="UnsplashTranslator",
            llm=self.llm,
            system_prompt="You are a translator for Chinese tourist attractions. Translate the attraction name to its official English name. Return ONLY the English name, nothing else."
        )

    def _translate_to_english(self, text: str, city: str = "") -> str:
        """使用 LLM 将景点名称翻译为英文"""
        try:
            prompt = f"Translate this Chinese attraction name to English: {text}"
            response = self.translator.run(prompt)
            translated = response.strip()
            # 添加 China Landmark 后缀提高搜索准确性
            search_query = f"{translated} China Landmark"
            logger.info(f"关键词翻译: {text} -> {search_query}")
            return search_query, translated, city
        except Exception as e:
            logger.error(f"翻译关键词失败: {e}")
            return f"{text} China Landmark", text, city

    def _do_search(self, query: str, per_page: int) -> List[Dict]:
        """执行实际的 Unsplash API 搜索"""
        url = f"{self.base_url}/search/photos"
        params = {
            "query": query,
            "per_page": per_page,
            "client_id": self.access_key,
            "order_by": "relevant",
            "content_filter": "high"
        }
        logger.info(f"正在请求 Unsplash API: query={query}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])

    def search_photos(self, query: str, per_page: int = 10, city: str = "") -> List[Dict]:
        try:
            # 翻译并构建搜索关键词
            search_query, translated, city_name = self._translate_to_english(query, city)
            
            # 第一次搜索
            results = self._do_search(search_query, per_page)
            
            # 回退搜索：如果无结果，使用城市+Architecture
            if not results and city_name:
                fallback_query = f"{city_name} Architecture"
                logger.info(f"回退搜索: {fallback_query}")
                results = self._do_search(fallback_query, per_page)
            
            # 再次回退：仅使用翻译后的名称
            if not results:
                logger.info(f"再次回退搜索: {translated}")
                results = self._do_search(translated, per_page)
            
            logger.info(f"Unsplash 搜索结果数量: {len(results)}")
            
            photos = []
            for result in results:
                photos.append({
                    "url": result["urls"]["regular"],
                    "description": result.get("description", ""),
                    "photographer": result["user"]["name"]
                })
            return photos
        except Exception as e:
            logger.error(f"搜索图片失败: {e}")
            return []

    def get_photo_url(self, query: str, city: str = "") -> Optional[str]:
        photos = self.search_photos(query, per_page=1, city=city)
        return photos[0].get("url") if photos else None

    def get_photo_urls(self, query: str, count: int = 5, city: str = "") -> List[str]:
        """获取多张图片URL，返回实际搜索到的数量（最多count张）"""
        photos = self.search_photos(query, per_page=count, city=city)
        return [p.get("url") for p in photos if p.get("url")]
