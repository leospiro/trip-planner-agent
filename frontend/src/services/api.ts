import axios from 'axios';
import type { TripPlan, TripPlanRequest, XHSResponse, ApiKeys } from '@/types';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:18080/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

const API_KEYS_STORAGE_KEY = 'trip_planner_api_keys';

// API Key 管理
export const saveApiKeys = (keys: ApiKeys): void => {
  localStorage.setItem(API_KEYS_STORAGE_KEY, JSON.stringify(keys));
};

export const loadApiKeys = (): ApiKeys => {
  const stored = localStorage.getItem(API_KEYS_STORAGE_KEY);
  return stored ? JSON.parse(stored) : {};
};

export const clearApiKeys = (): void => {
  localStorage.removeItem(API_KEYS_STORAGE_KEY);
};

// 获取高德地图 JS Key
export const getAmapJsKey = (): string => {
  const keys = loadApiKeys();
  return keys.amap_js_key || '';
};

// 遮蔽 Key 显示
export const maskKey = (key: string | undefined): string => {
  if (!key || key.length < 8) return key ? '****' : '';
  return `${key.slice(0, 4)}****${key.slice(-4)}`;
};

export const generateTripPlan = async (request: TripPlanRequest): Promise<TripPlan> => {
  try {
    const storedKeys = loadApiKeys();
    const hasKeys = Object.values(storedKeys).some(v => v);
    const requestWithKeys = hasKeys ? { ...request, api_keys: storedKeys } : request;
    
    const response = await apiClient.post('/trip/plan', requestWithKeys);
    return response.data;
  } catch (error) {
    console.error('Error generating trip plan:', error);
    throw error;
  }
};

export interface StreamProgress {
  step: number;
  status: string;
  progress: number;
  data?: TripPlan;
  error?: string;
}

export const generateTripPlanStream = async (
  request: TripPlanRequest,
  onProgress: (progress: StreamProgress) => void
): Promise<TripPlan> => {
  const storedKeys = loadApiKeys();
  const hasKeys = Object.values(storedKeys).some(v => v);
  const requestWithKeys = hasKeys ? { ...request, api_keys: storedKeys } : request;

  const response = await fetch('http://127.0.0.1:18080/api/trip/plan/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestWithKeys),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let tripPlan: TripPlan | null = null;
  let buffer = '';

  if (!reader) throw new Error('Stream not available');

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const messages = buffer.split('\n\n');
    buffer = messages.pop() || '';

    for (const message of messages) {
      const line = message.trim();
      if (!line.startsWith('data: ')) continue;
      
      try {
        const progress: StreamProgress = JSON.parse(line.slice(6));
        onProgress(progress);
        if (progress.data) tripPlan = progress.data as TripPlan;
        if (progress.error) throw new Error(progress.error);
      } catch (e) {
        if (e instanceof SyntaxError) continue;
        throw e;
      }
    }
  }

  if (!tripPlan) throw new Error('No trip plan received');
  return tripPlan;
};

export const getXHSPreviews = async (keyword: string): Promise<XHSResponse> => {
  try {
    const response = await apiClient.get(`/xhs/previews?keyword=${encodeURIComponent(keyword)}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching XHS previews:', error);
    throw error;
  }
};
