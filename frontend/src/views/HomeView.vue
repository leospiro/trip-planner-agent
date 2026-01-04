<template>
  <div class="home-container">
    <div class="hero-section">
      <h1 class="hero-title">🌍 开启你的智能旅行</h1>
      <p class="hero-subtitle">AI 驱动的个性化行程规划</p>
    </div>
    
    <!-- 加载进度条 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-card glass-effect">
        <h3 class="loading-status">{{ loadingStatus }}</h3>
        <a-progress
          :percent="loadingProgress"
          status="active"
          :stroke-color="{ '0%': '#88C0D0', '100%': '#8FBCBB' }"
          :show-info="false"
        />
        <div class="progress-text">{{ loadingProgress }}%</div>
        <p class="loading-tip">AI 正在为您规划完美行程...</p>
      </div>
    </div>

    <div class="form-card glass-effect">
      <!-- API 设置折叠面板 -->
      <a-collapse style="margin-bottom: 24px;" ghost>
        <a-collapse-panel key="api">
          <template #header>
            <span class="collapse-header-text">⚙️ API 设置（可选）</span>
          </template>
          <div class="api-settings-grid">
            <div class="api-warning">⚠️ 仅支持 OpenAI 格式的 API（如 OpenAI、DeepSeek、Moonshot 等），请勿填写其他格式的 API</div>
            <a-form layout="vertical" :model="apiKeysState">
              <a-row :gutter="16">
                <a-col :span="8">
                  <a-form-item label="LLM API Key">
                    <a-input-password v-model:value="apiKeysState.llm_api_key" placeholder="DeepSeek/OpenAI" />
                    <span v-if="apiKeysState.llm_api_key" class="key-status">✓ {{ maskKey(apiKeysState.llm_api_key) }}</span>
                  </a-form-item>
                </a-col>
                <a-col :span="8">
                  <a-form-item label="LLM Model ID">
                    <a-input v-model:value="apiKeysState.llm_model_id" placeholder="如 deepseek-chat" />
                  </a-form-item>
                </a-col>
                <a-col :span="8">
                  <a-form-item label="LLM Base URL">
                    <a-input v-model:value="apiKeysState.llm_base_url" placeholder="如 https://api.deepseek.com" />
                  </a-form-item>
                </a-col>
              </a-row>
              <a-row :gutter="16">
                <a-col :span="8">
                  <a-form-item label="高德地图 Web Key">
                    <a-input-password v-model:value="apiKeysState.amap_api_key" placeholder="后端 POI/天气" />
                    <span v-if="apiKeysState.amap_api_key" class="key-status">✓ {{ maskKey(apiKeysState.amap_api_key) }}</span>
                  </a-form-item>
                </a-col>
                <a-col :span="8">
                  <a-form-item label="高德地图 JS Key">
                    <a-input-password v-model:value="apiKeysState.amap_js_key" placeholder="前端地图显示" />
                    <span v-if="apiKeysState.amap_js_key" class="key-status">✓ {{ maskKey(apiKeysState.amap_js_key) }}</span>
                  </a-form-item>
                </a-col>
                <a-col :span="8">
                  <a-form-item label="Unsplash Access Key">
                    <a-input-password v-model:value="apiKeysState.unsplash_access_key" placeholder="图片搜索" />
                    <span v-if="apiKeysState.unsplash_access_key" class="key-status">✓ {{ maskKey(apiKeysState.unsplash_access_key) }}</span>
                  </a-form-item>
                </a-col>
              </a-row>
              <a-space class="api-buttons">
                <a-button type="primary" size="small" @click="saveKeys" class="glass-button">保存配置</a-button>
                <a-button size="small" @click="clearKeys" class="glass-button secondary">清除</a-button>
              </a-space>
            </a-form>
          </div>
        </a-collapse-panel>
      </a-collapse>

      <a-form :model="formState" @finish="onFinish" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="目的地" name="city">
              <a-input v-model:value="formState.city" placeholder="请输入目的地城市" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="日期范围" name="dateRange">
              <a-range-picker v-model:value="formState.dateRange" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="旅行偏好" name="preferences">
          <a-textarea v-model:value="formState.preferences" :rows="3" placeholder="描述您的旅行偏好..." />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="预算" name="budget">
              <a-select v-model:value="formState.budget">
                <a-select-option value="经济">💰 经济</a-select-option>
                <a-select-option value="舒适">💎 舒适</a-select-option>
                <a-select-option value="豪华">👑 豪华</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="交通方式" name="transportation">
              <a-input v-model:value="formState.transportation" placeholder="如：公共交通" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="住宿类型" name="accommodation">
              <a-input v-model:value="formState.accommodation" placeholder="如：四星级酒店" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading" block class="submit-btn">
            🚀 生成旅行计划
          </a-button>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { generateTripPlanStream, loadApiKeys, saveApiKeys, clearApiKeys, maskKey } from '@/services/api';
import type { TripPlanRequest, ApiKeys } from '@/types';
import dayjs from 'dayjs';
import { message } from 'ant-design-vue';

const router = useRouter();
const loading = ref(false);
const loadingProgress = ref(0);
const loadingStatus = ref('');

const apiKeysState = reactive<ApiKeys>({
  llm_api_key: '',
  llm_model_id: '',
  llm_base_url: '',
  amap_api_key: '',
  amap_js_key: '',
  unsplash_access_key: '',
});

const formState = reactive({
  city: '北京',
  dateRange: [dayjs(), dayjs().add(2, 'day')],
  preferences: '喜欢历史古迹和自然风光',
  budget: '舒适',
  transportation: '公共交通',
  accommodation: '四星级酒店',
});

onMounted(() => {
  const stored = loadApiKeys();
  Object.assign(apiKeysState, stored);
});

const saveKeys = () => {
  const keysToSave: ApiKeys = {};
  if (apiKeysState.llm_api_key) keysToSave.llm_api_key = apiKeysState.llm_api_key;
  if (apiKeysState.llm_model_id) keysToSave.llm_model_id = apiKeysState.llm_model_id;
  if (apiKeysState.llm_base_url) keysToSave.llm_base_url = apiKeysState.llm_base_url;
  if (apiKeysState.amap_api_key) keysToSave.amap_api_key = apiKeysState.amap_api_key;
  if (apiKeysState.amap_js_key) keysToSave.amap_js_key = apiKeysState.amap_js_key;
  if (apiKeysState.unsplash_access_key) keysToSave.unsplash_access_key = apiKeysState.unsplash_access_key;
  saveApiKeys(keysToSave);
  message.success('API Key 已保存');
};

const clearKeys = () => {
  clearApiKeys();
  apiKeysState.llm_api_key = '';
  apiKeysState.llm_model_id = '';
  apiKeysState.llm_base_url = '';
  apiKeysState.amap_api_key = '';
  apiKeysState.amap_js_key = '';
  apiKeysState.unsplash_access_key = '';
  message.info('API Key 已清除');
};

const onFinish = async (values: any) => {
  loading.value = true;
  loadingProgress.value = 0;
  loadingStatus.value = '🚀 准备开始...';
  
  try {
    const request: TripPlanRequest = {
      city: values.city,
      start_date: values.dateRange[0].format('YYYY-MM-DD'),
      end_date: values.dateRange[1].format('YYYY-MM-DD'),
      days: values.dateRange[1].diff(values.dateRange[0], 'day') + 1,
      preferences: values.preferences,
      budget: values.budget,
      transportation: values.transportation,
      accommodation: values.accommodation,
    };

    const tripPlan = await generateTripPlanStream(request, (progress) => {
      if (progress.status) loadingStatus.value = progress.status;
      if (progress.progress) loadingProgress.value = progress.progress;
    });

    loadingProgress.value = 100;
    loadingStatus.value = '✅ 完成！';
    
    setTimeout(() => {
      sessionStorage.setItem('tripPlan', JSON.stringify(tripPlan));
      router.push({ name: 'result' });
    }, 800);
  } catch (error: any) {
    console.error('Failed to generate trip plan:', error);
    message.error(error.message || '生成旅行计划失败');
    loading.value = false;
  }
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background-image:
    linear-gradient(rgba(46, 52, 64, 0.8), rgba(46, 52, 64, 0.8)),
    url('https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2000&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  padding: 60px 20px;
  font-family: "Noto Sans SC", sans-serif;
}

.glass-effect {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

.hero-section {
  text-align: center;
  margin-bottom: 50px;
}

.hero-title {
  font-size: 3rem;
  color: #ECEFF4;
  margin-bottom: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  font-size: 1.2rem;
  color: #D8DEE9;
  opacity: 0.9;
}

.form-card {
  max-width: 900px;
  margin: 0 auto;
  border-radius: 24px;
  padding: 40px;
  color: #E5E9F0;
}

:deep(.ant-form-item-label > label) {
  color: #E5E9F0 !important;
  font-weight: 500;
}

:deep(.ant-input), :deep(.ant-input-password), :deep(.ant-select-selector), :deep(.ant-picker) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: #ECEFF4 !important;
  border-radius: 12px !important;
}

:deep(.ant-input::placeholder), :deep(.ant-select-selection-placeholder) {
  color: rgba(229, 233, 240, 0.5) !important;
}

.key-status {
  color: #8FBCBB;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.api-settings-grid {
  padding: 20px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  margin-top: 10px;
}

.api-warning {
  background: rgba(255, 193, 7, 0.15);
  border: 1px solid rgba(255, 193, 7, 0.4);
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 16px;
  color: #ffc107;
  font-size: 13px;
}

.collapse-header-text {
  color: #88C0D0;
  font-weight: 600;
}

.api-buttons {
  margin-top: 10px;
}

.glass-button {
  background: rgba(136, 192, 208, 0.2) !important;
  border: 1px solid rgba(136, 192, 208, 0.4) !important;
  color: #88C0D0 !important;
  border-radius: 8px !important;
  transition: all 0.3s ease;
}

.glass-button:hover {
  background: rgba(136, 192, 208, 0.4) !important;
  transform: translateY(-1px);
}

.glass-button.secondary {
  background: rgba(216, 222, 233, 0.1) !important;
  border: 1px solid rgba(216, 222, 233, 0.2) !important;
  color: #D8DEE9 !important;
}

.submit-btn {
  height: 56px;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #88C0D0 0%, #5E81AC 100%) !important;
  border: none !important;
  border-radius: 16px !important;
  margin-top: 20px;
  box-shadow: 0 4px 15px rgba(136, 192, 208, 0.3);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(136, 192, 208, 0.4);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(46, 52, 64, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-card {
  padding: 50px 80px;
  text-align: center;
  border-radius: 32px;
  min-width: 450px;
}

.loading-status {
  font-size: 1.5rem;
  color: #88C0D0;
  margin-bottom: 24px;
  font-weight: 600;
}

.progress-text {
  margin-top: 12px;
  color: #D8DEE9;
  font-weight: 600;
  font-size: 1.1rem;
}

.loading-tip {
  margin-top: 24px;
  color: #81A1C1;
  font-size: 15px;
  font-style: italic;
}

:deep(.ant-progress-inner) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}
</style>
