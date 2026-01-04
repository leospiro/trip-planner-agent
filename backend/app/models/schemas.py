from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

class Location(BaseModel):
    longitude: float = Field(..., description="经度", ge=-180, le=180)
    latitude: float = Field(..., description="纬度", ge=-90, le=90)

class Attraction(BaseModel):
    name: str = Field(..., description="景点名称")
    address: str = Field(default="未知地址", description="地址")
    location: Optional[Location] = Field(default=None, description="经纬度坐标")
    visit_duration: int = Field(default=120, description="建议游览时间(分钟)", gt=0)
    description: str = Field(default="暂无描述", description="景点描述")
    category: Optional[str] = Field(default="景点", description="景点类别")
    rating: Optional[float] = Field(default=None, ge=0, le=5, description="评分")
    image_urls: List[str] = Field(default_factory=list, description="图片URL列表")
    ticket_price: int = Field(default=0, ge=0, description="门票价格(元)")

class Meal(BaseModel):
    type: str = Field(..., description="餐饮类型：breakfast/lunch/dinner/snack")
    name: str = Field(..., description="餐饮名称")
    address: Optional[str] = Field(default=None, description="地址")
    location: Optional[Location] = Field(default=None, description="经纬度坐标")
    description: Optional[str] = Field(default=None, description="描述")
    estimated_cost: int = Field(default=0, description="预估费用(元)")

class Hotel(BaseModel):
    name: str = Field(..., description="酒店名称")
    address: str = Field(default="", description="酒店地址")
    location: Optional[Location] = Field(default=None, description="酒店位置")
    price_range: str = Field(default="", description="价格范围")
    rating: str = Field(default="", description="评分")
    distance: str = Field(default="", description="距离景点距离")
    type: str = Field(default="", description="酒店类型")
    estimated_cost: int = Field(default=0, description="预估费用(元/晚)")

class Budget(BaseModel):
    total_attractions: int = Field(default=0, description="景点门票总费用")
    total_hotels: int = Field(default=0, description="酒店总费用")
    total_meals: int = Field(default=0, description="餐饮总费用")
    total_transportation: int = Field(default=0, description="交通总费用")
    total: int = Field(default=0, description="总费用")

class DayPlan(BaseModel):
    date: str = Field(..., description="日期")
    day_index: int = Field(..., description="第几天(从0开始)")
    description: str = Field(default="今日行程安排", description="当日行程描述")
    transportation: str = Field(default="建议打车或公共交通", description="交通方式")
    accommodation: str = Field(default="入住酒店", description="住宿安排")
    hotel: Optional[Hotel] = Field(default=None, description="酒店信息")
    attractions: List[Attraction] = Field(default_factory=list, description="景点列表")
    meals: List[Meal] = Field(default_factory=list, description="餐饮安排")

# class WeatherInfo(BaseModel):
#     date: str = Field(..., description="日期")
#     day_weather: str = Field(..., description="白天天气")
#     night_weather: str = Field(..., description="夜间天气")
#     day_temp: int = Field(..., description="白天温度(摄氏度)")
#     night_temp: int = Field(..., description="夜间温度(摄氏度)")
#     wind_direction: str = Field(..., description="风向")
#     wind_power: str = Field(..., description="风力")
    
#     @field_validator('day_temp', 'night_temp', mode='before')
#     def parse_temperature(cls, v):
#         if isinstance(v, str):
#             v = v.replace('°C', '').replace('℃', '').replace('°', '').strip()
#             try:
#                 return int(v)
#             except ValueError:
#                 return 0
#         return v

class WeatherInfo(BaseModel):
    date: str = Field(..., description="日期")
    day_weather: str = Field(..., description="白天天气")
    night_weather: str = Field(..., description="夜间天气")
    day_temp: int = Field(..., description="白天温度(摄氏度)")
    night_temp: int = Field(..., description="夜间温度(摄氏度)")
    wind_direction: str = Field(..., description="风向")
    wind_power: str = Field(..., description="风力")
    
    @field_validator('day_temp', 'night_temp', mode='before')
    @classmethod
    def parse_temperature(cls, v):
        if isinstance(v, str):
            v = v.replace('°C', '').replace('℃', '').replace('°', '').strip()
            try:
                return int(v)
            except ValueError:
                return 0
        return v
    
    # 新增：确保 wind_power 始终是字符串
    @field_validator('wind_power', mode='before')
    @classmethod
    def parse_wind_power(cls, v):
        """把任何类型的输入都转成字符串"""
        if v is None:
            return "未知"
        return str(v)


class TripPlan(BaseModel):
    city: str = Field(..., description="目的地城市")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    days: List[DayPlan] = Field(default_factory=list, description="每日行程")
    weather_info: List[WeatherInfo] = Field(default_factory=list, description="天气信息")
    overall_suggestions: str = Field(default="祝您旅途愉快！", description="总体建议")
    budget: Optional[Budget] = Field(default=None, description="预算信息")
    search_keywords: List[str] = Field(default_factory=list, description="推荐搜索关键词")

class ApiKeys(BaseModel):
    """用户自定义 API Keys"""
    llm_api_key: Optional[str] = None
    llm_model_id: Optional[str] = None
    llm_base_url: Optional[str] = None
    amap_api_key: Optional[str] = None
    unsplash_access_key: Optional[str] = None

class TripPlanRequest(BaseModel):
    city: str
    start_date: str
    end_date: str
    days: int
    preferences: str
    budget: str
    transportation: str
    accommodation: str
    api_keys: Optional[ApiKeys] = None

# 小红书相关模型
class XHSNote(BaseModel):
    """小红书笔记模型"""
    id: str = Field(..., description="笔记ID")
    title: str = Field(..., description="笔记标题")
    note_url: str = Field(..., description="笔记链接")
    cover_image: str = Field(..., description="封面图片URL")
    author: str = Field(..., description="作者名称")
    liked_count: int = Field(default=0, description="点赞数")
    published: Optional[str] = Field(default=None, description="发布时间")
    author_tags: List[str] = Field(default_factory=list, description="作者标签")

class XHSResponse(BaseModel):
    """小红书API响应模型"""
    status: str = Field(..., description="响应状态：success/fallback")
    data: List[XHSNote] = Field(default_factory=list, description="笔记数据列表")
    search_url: str = Field(..., description="搜索页面URL")
