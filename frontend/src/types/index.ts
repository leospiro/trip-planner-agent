// 根据 schemas.py 生成的 TypeScript 类型

export interface Location {
  longitude: number;
  latitude: number;
}

export interface Attraction {
  name: string;
  address: string;
  location: Location;
  visit_duration: number;
  description: string;
  category?: string;
  rating?: number;
  image_urls: string[];
  ticket_price: number;
}

export interface Meal {
  type: string;
  name: string;
  address?: string;
  location?: Location;
  description?: string;
  estimated_cost: number;
}

export interface Hotel {
  name: string;
  address: string;
  location?: Location;
  price_range: string;
  rating: string;
  distance: string;
  type: string;
  estimated_cost: number;
}

export interface Budget {
  total_attractions: number;
  total_hotels: number;
  total_meals: number;
  total_transportation: number;
  total: number;
}

export interface DayPlan {
  date: string;
  day_index: number;
  description: string;
  transportation: string;
  accommodation: string;
  hotel?: Hotel;
  attractions: Attraction[];
  meals: Meal[];
}

export interface WeatherInfo {
  date: string;
  day_weather: string;
  night_weather: string;
  day_temp: number;
  night_temp: number;
  wind_direction: string;
  wind_power: string;
}

export interface TripPlan {
  city: string;
  start_date: string;
  end_date: string;
  days: DayPlan[];
  weather_info: WeatherInfo[];
  overall_suggestions: string;
  budget?: Budget;
  search_keywords?: string[];
}

export interface ApiKeys {
  llm_api_key?: string;
  llm_model_id?: string;
  llm_base_url?: string;
  amap_api_key?: string;
  amap_js_key?: string;
  unsplash_access_key?: string;
}

export interface TripPlanRequest {
  city: string;
  start_date: string;
  end_date: string;
  days: number;
  preferences: string;
  budget: string;
  transportation: string;
  accommodation: string;
  api_keys?: ApiKeys;
}

// 小红书相关接口
export interface XHSNote {
  id: string;
  title: string;
  note_url: string;
  cover_image: string;
  author: string;
  author_tags?: string[];
  liked_count?: number;
  published?: string;
}

export interface XHSResponse {
  status: string;
  data: XHSNote[];
  search_url: string;
  message?: string;
}
