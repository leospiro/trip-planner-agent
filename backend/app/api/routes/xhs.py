from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import XHSResponse, XHSNote
from app.services.xhs_service import get_xhs_notes, check_rsshub_health

router = APIRouter()


@router.get("/health")
async def rsshub_health_check():
    """检查 RSSHub 服务健康状态"""
    return await check_rsshub_health()


@router.get("/previews", response_model=XHSResponse)
async def get_xhs_previews(keyword: str = Query(..., description="搜索关键词")) -> XHSResponse:
    """
    获取小红书笔记预览
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        XHSResponse: 包含笔记数据或fallback链接的响应
    """
    try:
        # 调用小红书服务获取笔记数据
        result = await get_xhs_notes(keyword)
        
        # 将字典数据转换为 XHSNote 对象
        notes = [XHSNote(**note) for note in result.get("data", [])]
        
        return XHSResponse(
            status=result.get("status", "fallback"),
            data=notes,
            search_url=result.get("search_url", f"https://www.xiaohongshu.com/search_result?keyword={keyword}")
        )
            
    except Exception as e:
        # 异常情况，返回fallback
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
        return XHSResponse(
            status="fallback",
            data=[],
            search_url=search_url
        )