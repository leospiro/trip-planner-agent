from hello_agents import HelloAgentsLLM, SimpleAgent
# from hello_agents.tools import MCPTool
from hello_agents.tools.builtin.protocol_tools import MCPTool
from app.config import get_settings
from app.models.schemas import TripPlanRequest, TripPlan
from .prompts import ATTRACTION_AGENT_PROMPT, WEATHER_AGENT_PROMPT, HOTEL_AGENT_PROMPT, PLANNER_AGENT_PROMPT
import json
import logging

logger = logging.getLogger(__name__)

class TripPlannerAgent:
    def __init__(self, amap_api_key: str = None, llm_api_key: str = None, llm_model_id: str = None, llm_base_url: str = None):
        settings = get_settings()
        
        # 构建 LLM 配置
        llm_kwargs = {}
        if llm_api_key:
            llm_kwargs["api_key"] = llm_api_key
        if llm_model_id:
            llm_kwargs["model"] = llm_model_id
        if llm_base_url:
            llm_kwargs["base_url"] = llm_base_url
        
        self.llm = HelloAgentsLLM(**llm_kwargs) if llm_kwargs else HelloAgentsLLM()
        
        # 使用传入的 key 或默认配置
        effective_amap_key = amap_api_key or settings.amap_api_key

        self.mcp_tool = MCPTool(
            name="amap_mcp",
            server_command=["npx", "-y", "@sugarforever/amap-mcp-server"],
            env={"AMAP_API_KEY": effective_amap_key}
        )

        self.attraction_agent = SimpleAgent(name="AttractionSearchAgent", llm=self.llm, system_prompt=ATTRACTION_AGENT_PROMPT)
        self.attraction_agent.add_tool(self.mcp_tool)

        self.weather_agent = SimpleAgent(name="WeatherQueryAgent", llm=self.llm, system_prompt=WEATHER_AGENT_PROMPT)
        self.weather_agent.add_tool(self.mcp_tool)

        self.hotel_agent = SimpleAgent(name="HotelAgent", llm=self.llm, system_prompt=HOTEL_AGENT_PROMPT)
        self.hotel_agent.add_tool(self.mcp_tool)
        
        self.planner_agent = SimpleAgent(name="PlannerAgent", llm=self.llm, system_prompt=PLANNER_AGENT_PROMPT)

    def _build_planner_query(self, request: TripPlanRequest, attraction_response: str, weather_response: str, hotel_response: str) -> str:
        return f"""
请根据以下信息生成{request.city}的{request.days}日旅行计划:

**用户需求:**
- 目的地: {request.city}
- 日期: {request.start_date} 至 {request.end_date}
- 天数: {request.days}天
- 偏好: {request.preferences}
- 预算: {request.budget}
- 交通方式: {request.transportation}
- 住宿类型: {request.accommodation}

**景点信息:**
{attraction_response}

**天气信息:**
{weather_response}

**酒店信息:**
{hotel_response}

请生成详细的旅行计划,包括每天的景点安排、餐饮推荐、住宿信息和预算明细。
"""

    def _parse_trip_plan(self, planner_response: str) -> TripPlan:
        try:
            # Clean the response by finding the JSON object
            start_index = planner_response.find('{')
            end_index = planner_response.rfind('}') + 1
            if start_index == -1 or end_index == 0:
                raise ValueError("No JSON object found in the response")
            
            json_str = planner_response[start_index:end_index]
            plan_dict = json.loads(json_str)
            try:
                return TripPlan.model_validate(plan_dict)
            except Exception as ve:
                logger.error(f"Pydantic validation error: {ve}")
                raise ve
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse trip plan JSON: {e}")
            logger.error(f"Raw planner response: {planner_response}")
            # Fallback or error handling
            raise ValueError(f"Could not generate a valid trip plan: {str(e)}")

    def plan_trip(self, request: TripPlanRequest) -> TripPlan:
        print(f"[AGENT DEBUG] 开始处理旅行计划请求: {request.city}")
        
        # Step 1: Attraction Search
        print("[AGENT DEBUG] 步骤1: 搜索景点")
        attraction_response = self.attraction_agent.run(
            f"请搜索{request.city}的{request.preferences}景点"
        )
        print(f"[AGENT DEBUG] 景点搜索完成: {len(attraction_response)} 字符")

        # Step 2: Weather Query
        print("[AGENT DEBUG] 步骤2: 查询天气")
        weather_response = self.weather_agent.run(
            f"请查询{request.city}的天气"
        )
        print(f"[AGENT DEBUG] 天气查询完成: {len(weather_response)} 字符")

        # Step 3: Hotel Recommendation
        print("[AGENT DEBUG] 步骤3: 搜索酒店")
        hotel_response = self.hotel_agent.run(
            f"请搜索{request.city}的{request.accommodation}酒店"
        )
        print(f"[AGENT DEBUG] 酒店搜索完成: {len(hotel_response)} 字符")

        # Step 4: Consolidate and Generate Plan
        print("[AGENT DEBUG] 步骤4: 生成旅行计划")
        planner_query = self._build_planner_query(
            request, attraction_response, weather_response, hotel_response
        )
        planner_response = self.planner_agent.run(planner_query)
        print(f"[AGENT DEBUG] 计划生成完成: {len(planner_response)} 字符")

        # Step 5: Parse JSON and validate with Pydantic
        print("[AGENT DEBUG] 步骤5: 解析JSON")
        trip_plan = self._parse_trip_plan(planner_response)
        print("[AGENT DEBUG] 旅行计划处理完成")
        return trip_plan
