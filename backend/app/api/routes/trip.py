from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import TripPlanRequest, TripPlan
from app.agents.trip_planner_agent import TripPlannerAgent
from app.services.unsplash_service import UnsplashService
from app.config import get_settings, get_effective_keys
import json
import asyncio

router = APIRouter()

@router.post("/plan", response_model=TripPlan)
async def create_trip_plan(request: TripPlanRequest) -> TripPlan:
    print(f"[DEBUG] 收到旅行计划请求: {request.city}")
    try:
        effective_keys = get_effective_keys(request.api_keys)
        agent = TripPlannerAgent(
            amap_api_key=effective_keys["amap_api_key"],
            llm_api_key=effective_keys["llm_api_key"],
            llm_model_id=effective_keys["llm_model_id"],
            llm_base_url=effective_keys["llm_base_url"]
        )
        unsplash_service = UnsplashService(effective_keys["unsplash_access_key"])
        
        trip_plan = await asyncio.to_thread(agent.plan_trip, request)

        for day in trip_plan.days:
            for attraction in day.attractions:
                if not attraction.image_urls:
                    attraction.image_urls = unsplash_service.get_photo_urls(
                        f"{attraction.name} {trip_plan.city}", count=5
                    )
        
        return trip_plan
    except Exception as e:
        print(f"[DEBUG] 发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plan/stream")
async def create_trip_plan_stream(request: TripPlanRequest):
    """流式返回旅行计划生成进度"""
    async def event_generator():
        try:
            effective_keys = get_effective_keys(request.api_keys)
            agent = TripPlannerAgent(
                amap_api_key=effective_keys["amap_api_key"],
                llm_api_key=effective_keys["llm_api_key"],
                llm_model_id=effective_keys["llm_model_id"],
                llm_base_url=effective_keys["llm_base_url"]
            )
            unsplash_service = UnsplashService(effective_keys["unsplash_access_key"])
            
            # 定义步骤
            steps = [
                {"step": 1, "status": "🔍 正在搜索景点...", "progress": 15},
                {"step": 2, "status": "🌤️ 正在查询天气...", "progress": 35},
                {"step": 3, "status": "🏨 正在搜索酒店...", "progress": 55},
                {"step": 4, "status": "📋 正在生成行程计划...", "progress": 75},
                {"step": 5, "status": "🖼️ 正在获取图片...", "progress": 90},
            ]
            
            # 步骤1: 搜索景点
            yield f"data: {json.dumps(steps[0], ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)  # 让出控制权确保数据发送
            attraction_response = await asyncio.to_thread(
                agent.attraction_agent.run,
                f"请搜索{request.city}的{request.preferences}景点"
            )
            
            # 步骤2: 查询天气
            yield f"data: {json.dumps(steps[1], ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)
            weather_response = await asyncio.to_thread(
                agent.weather_agent.run,
                f"请查询{request.city}的天气"
            )
            
            # 步骤3: 搜索酒店
            yield f"data: {json.dumps(steps[2], ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)
            hotel_response = await asyncio.to_thread(
                agent.hotel_agent.run,
                f"请搜索{request.city}的{request.accommodation}酒店"
            )
            
            # 步骤4: 生成计划
            yield f"data: {json.dumps(steps[3], ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)
            planner_query = agent._build_planner_query(
                request, attraction_response, weather_response, hotel_response
            )
            planner_response = await asyncio.to_thread(
                agent.planner_agent.run,
                planner_query
            )
            trip_plan = agent._parse_trip_plan(planner_response)
            
            # 步骤5: 获取图片
            yield f"data: {json.dumps(steps[4], ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)
            for day in trip_plan.days:
                for attraction in day.attractions:
                    if not attraction.image_urls:
                        attraction.image_urls = unsplash_service.get_photo_urls(
                            f"{attraction.name} {trip_plan.city}", count=5
                        )
            
            # 完成
            result = {"step": 6, "status": "✅ 完成！", "progress": 100, "data": trip_plan.model_dump()}
            yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error = {"error": str(e), "status": "❌ 发生错误"}
            yield f"data: {json.dumps(error, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )
