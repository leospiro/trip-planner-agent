<template>
  <div v-if="tripPlan" class="result-view">
    <!-- 页面头部：标题和总体建议 -->
    <a-page-header
      :title="`${tripPlan.city} 旅行计划`"
      :sub-title="`${tripPlan.start_date} 至 ${tripPlan.end_date}`"
      @back="() => router.push('/')"
    >
      <template #extra>
        <a-button v-if="!editMode" @click="startEdit">编辑行程</a-button>
        <template v-else>
          <a-button :disabled="!historyStack.length" @click="undoEdit">撤销</a-button>
          <a-button @click="resetEdit">重置</a-button>
          <a-button @click="cancelEdit">取消</a-button>
          <a-button type="primary" @click="saveEdit">保存</a-button>
        </template>
        <a-dropdown>
          <a-button>导出 <DownOutlined /></a-button>
          <template #overlay>
            <a-menu @click="handleExport">
              <a-menu-item key="image">导出图片</a-menu-item>
              <a-menu-item key="pdf">导出 PDF</a-menu-item>
              <a-menu-item key="json">导出 JSON</a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </template>
      <a-descriptions size="small" :column="3">
        <a-descriptions-item label="总体建议">{{ tripPlan.overall_suggestions }}</a-descriptions-item>
      </a-descriptions>
    </a-page-header>

    <!-- 地图区域 -->
    <a-card title="景点地图" size="small" class="map-card glass-effect" v-show="!exporting">
      <div v-if="mapError" class="map-placeholder">
        <p>🗺️ {{ mapError }}</p>
        <p style="font-size: 12px; color: #999;">请在首页 API 设置中配置高德地图 JS Key</p>
      </div>
      <div v-else id="amap-container" style="height: 400px; width: 100%;"></div>
    </a-card>

    <!-- 可导出内容区域 -->
    <div id="trip-plan-content">
      <!-- 预算和天气信息 -->
      <div class="info-section">
        <a-card title="预算概览" v-if="tripPlan.budget" size="small" class="glass-effect">
          <a-descriptions :column="2" size="small">
            <a-descriptions-item label="门票总计">¥{{ tripPlan.budget.total_attractions }}</a-descriptions-item>
            <a-descriptions-item label="酒店总计">¥{{ tripPlan.budget.total_hotels }}</a-descriptions-item>
            <a-descriptions-item label="餐饮总计">¥{{ tripPlan.budget.total_meals }}</a-descriptions-item>
            <a-descriptions-item label="交通总计">¥{{ tripPlan.budget.total_transportation }}</a-descriptions-item>
            <a-descriptions-item label="总计">
              <a-typography-title :level="5" style="color: #88C0D0">¥{{ tripPlan.budget.total }}</a-typography-title>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
        <a-card title="天气预报" v-if="tripPlan.weather_info.length" size="small" class="glass-effect">
          <a-carousel arrows>
            <template #prevArrow>
              <div class="custom-slick-arrow" style="left: 10px; z-index: 1">
                <left-circle-outlined />
              </div>
            </template>
            <template #nextArrow>
              <div class="custom-slick-arrow" style="right: 10px">
                <right-circle-outlined />
              </div>
            </template>
            <div v-for="weather in tripPlan.weather_info" :key="weather.date">
              <div class="weather-card">
                <p>{{ weather.date }}</p>
                <p>{{ weather.day_weather }} / {{ weather.night_weather }}</p>
                <p>{{ weather.day_temp }}°C / {{ weather.night_temp }}°C</p>
                <p>{{ weather.wind_direction }}风 {{ weather.wind_power }}级</p>
              </div>
            </div>
          </a-carousel>
        </a-card>
      </div>

      <!-- 每日行程 Tabs -->
        <a-tabs v-model:activeKey="activeKey" type="card" v-if="!exporting">
          <a-tab-pane v-for="(day, dayIndex) in localDays" :key="`day-${dayIndex}-${day.date}`" :tab="`第 ${dayIndex + 1} 天`">
          <div class="day-plan">
            <p><strong>日期:</strong> {{ day.date }}</p>
            <p><strong>行程:</strong> {{ day.description }}</p>
            <p><strong>交通:</strong> {{ day.transportation }}</p>
            <p><strong>住宿:</strong> {{ day.accommodation }}</p>
            <a-button v-if="editMode" type="dashed" block style="margin: 16px 0" @click="addAttraction(dayIndex)">+ 添加景点</a-button>
            <a-timeline>
              <!-- 酒店信息 -->
              <a-timeline-item v-if="day.hotel">
                <a-card :title="`住宿: ${day.hotel.name}`" size="small" class="glass-effect hotel-card">
                  <p class="hotel-info">📍 地址: {{ day.hotel.address }}</p>
                  <p class="hotel-info">💰 价格: {{ day.hotel.price_range }}</p>
                  <p class="hotel-info">⭐ 评分: {{ day.hotel.rating }}</p>
                </a-card>
              </a-timeline-item>

              <!-- 景点 -->
              <a-timeline-item v-for="(attraction, index) in day.attractions" :key="attraction._uid">
                <a-card :title="`景点: ${attraction.name}`" size="small" class="glass-effect attraction-card">
                  <template #extra>
                    <a-tag>{{ attraction.category }}</a-tag>
                    <template v-if="editMode">
                      <a-button size="small" :disabled="index === 0" @click="moveAttraction(dayIndex, index, 'up')">上移</a-button>
                      <a-button size="small" :disabled="index === day.attractions.length - 1" @click="moveAttraction(dayIndex, index, 'down')">下移</a-button>
                      <a-button size="small" danger @click="deleteAttraction(dayIndex, index)">删除</a-button>
                    </template>
                  </template>
                  <div class="attraction-content">
                    <div class="attraction-image">
                      <a-carousel v-if="attraction.image_urls?.length" autoplay>
                        <div v-for="(imgUrl, imgIdx) in attraction.image_urls" :key="imgIdx" class="carousel-slide">
                          <img :src="imgUrl" :alt="attraction.name" @click="openImage(imgUrl)" @error="(e: Event) => (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=400&auto=format&fit=crop'" />
                        </div>
                      </a-carousel>
                      <img v-else src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=400&auto=format&fit=crop" :alt="attraction.name" @click="openImage('https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2000&auto=format&fit=crop')" />
                    </div>
                    <div class="attraction-details">
                      <p class="attraction-desc">{{ attraction.description }}</p>
                      <p v-if="attraction.address" class="attraction-info">📍 {{ attraction.address }}</p>
                      <p class="attraction-info">⏱️ 建议游玩: {{ attraction.visit_duration }} 分钟</p>
                      <p class="attraction-info">🎫 门票: ¥{{ attraction.ticket_price }}</p>
                    </div>
                  </div>
                </a-card>
              </a-timeline-item>

              <!-- 餐饮 -->
              <a-timeline-item v-for="(meal, index) in day.meals" :key="'m-' + index">
                <a-card :title="`餐饮: ${meal.name}`" size="small" class="glass-effect">
                  <template #extra>
                    <a-tag color="orange">{{ meal.type }}</a-tag>
                  </template>
                  <div class="card-details">
                    <p>{{ meal.description }}</p>
                    <p v-if="meal.address">地址: {{ meal.address }}</p>
                    <p>预估费用: ¥{{ meal.estimated_cost }}</p>
                  </div>
                </a-card>
              </a-timeline-item>
            </a-timeline>
          </div>
        </a-tab-pane>
      </a-tabs>

      <!-- 导出时显示所有天数 -->
      <div v-if="exporting" class="export-all-days">
        <div v-for="(day, dayIndex) in localDays" :key="'export-' + dayIndex" class="export-day-section">
          <h3 class="export-day-title">第 {{ dayIndex + 1 }} 天 - {{ day.date }}</h3>
          <div class="day-plan">
            <p><strong>行程:</strong> {{ day.description }}</p>
            <p><strong>交通:</strong> {{ day.transportation }}</p>
            <p><strong>住宿:</strong> {{ day.accommodation }}</p>
            <div class="export-timeline">
              <div v-if="day.hotel" class="export-item">
                <a-card :title="`住宿: ${day.hotel.name}`" size="small" class="glass-effect hotel-card">
                  <p class="hotel-info">📍 地址: {{ day.hotel.address }}</p>
                  <p class="hotel-info">💰 价格: {{ day.hotel.price_range }}</p>
                  <p class="hotel-info">⭐ 评分: {{ day.hotel.rating }}</p>
                </a-card>
              </div>
              <div v-for="(attraction, index) in day.attractions" :key="'ea-' + index" class="export-item">
                <a-card :title="`景点: ${attraction.name}`" size="small" class="glass-effect attraction-card">
                  <a-tag>{{ attraction.category }}</a-tag>
                  <div class="attraction-content">
                    <div class="attraction-image" v-if="attraction.image_urls?.length">
                      <img :src="attraction.image_urls[0]" :alt="attraction.name" />
                    </div>
                    <div class="attraction-details">
                      <p class="attraction-desc">{{ attraction.description }}</p>
                      <p v-if="attraction.address" class="attraction-info">📍 {{ attraction.address }}</p>
                      <p class="attraction-info">⏱️ 建议游玩: {{ attraction.visit_duration }} 分钟</p>
                      <p class="attraction-info">🎫 门票: ¥{{ attraction.ticket_price }}</p>
                    </div>
                  </div>
                </a-card>
              </div>
              <div v-for="(meal, index) in day.meals" :key="'em-' + index" class="export-item">
                <a-card :title="`餐饮: ${meal.name}`" size="small" class="glass-effect">
                  <a-tag color="orange">{{ meal.type }}</a-tag>
                  <div class="card-details">
                    <p>{{ meal.description }}</p>
                    <p v-if="meal.address">地址: {{ meal.address }}</p>
                    <p>预估费用: ¥{{ meal.estimated_cost }}</p>
                  </div>
                </a-card>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 相关攻略搜索（页面底部） -->
    <XHSPreview :keywords="tripPlan.search_keywords || [`${tripPlan.city}旅游攻略`]" />

    <!-- 图片预览弹窗 -->
    <div v-if="previewVisible" class="image-preview-overlay" @click="closePreview">
      <div class="preview-close" @click.stop="closePreview">✕</div>
      <img :src="previewUrl" class="preview-image" @click.stop />
    </div>
  </div>
  <div v-else>
    <a-empty description="没有可用的旅行计划。请返回主页生成一个新的计划。" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue';
import { useRouter } from 'vue-router';
import type { TripPlan, DayPlan } from '@/types';
import { LeftCircleOutlined, RightCircleOutlined, DownOutlined } from '@ant-design/icons-vue';
import XHSPreview from '@/components/XHSPreview.vue';
import { getAmapJsKey } from '@/services/api';
import AMapLoader from '@amap/amap-jsapi-loader';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const props = defineProps<{
  tripPlan: TripPlan;
}>();

const router = useRouter();
const activeKey = ref(0);
const editMode = ref(false);
const originalPlan = ref<TripPlan | null>(null);
const historyStack = ref<string[]>([]);
const exporting = ref(false);
const mapError = ref('');

// 本地响应式数据副本
const localDays = ref<DayPlan[]>([]);

// 唯一ID生成器
let uidCounter = 0;
const genUid = () => `uid-${Date.now()}-${++uidCounter}`;

// 初始化本地数据，为每个景点注入唯一 _uid
const initLocalDays = () => {
  if (props.tripPlan?.days) {
    const days = JSON.parse(JSON.stringify(props.tripPlan.days)) as DayPlan[];
    days.forEach(day => {
      day.attractions?.forEach(attr => {
        (attr as any)._uid = genUid();
      });
    });
    localDays.value = days;
  }
};

// 图片预览状态
const previewVisible = ref(false);
const previewUrl = ref('');

let map: any = null;

// 地图初始化
const initMap = async () => {
  if (!props.tripPlan) return;
  
  const amapJsKey = getAmapJsKey();
  if (!amapJsKey) {
    mapError.value = '未配置高德地图 JS Key，地图功能不可用';
    return;
  }
  mapError.value = '';
  
  try {
    const AMap = await AMapLoader.load({
      key: amapJsKey,
      version: '2.0'
    });
    
    map = new AMap.Map('amap-container', {
      zoom: 12,
      viewMode: '2D'
    });

    const markers: any[] = [];
    let markerIndex = 1;

    // 遍历所有天的景点
    props.tripPlan.days.forEach((day) => {
      day.attractions.forEach((attraction) => {
        if (attraction.location?.latitude && attraction.location?.longitude) {
          const marker = new AMap.Marker({
            position: [attraction.location.longitude, attraction.location.latitude],
            title: attraction.name,
            label: {
              content: `<div class="marker-label">${markerIndex}</div>`,
              direction: 'top'
            }
          });
          markers.push(marker);
          markerIndex++;
        }
      });
    });

    if (markers.length > 0) {
      map.add(markers);
      map.setFitView(markers);
    }
  } catch (e) {
    console.error('地图加载失败:', e);
    mapError.value = '地图加载失败，请检查 Key 是否正确';
  }
};

// 保存当前状态到历史栈（限制最多10条）
const MAX_HISTORY = 10;
const saveHistory = () => {
  if (historyStack.value.length >= MAX_HISTORY) {
    historyStack.value.shift();
  }
  historyStack.value.push(JSON.stringify(localDays.value));
};

// 行程编辑功能
const startEdit = () => {
  originalPlan.value = JSON.parse(JSON.stringify(props.tripPlan));
  historyStack.value = [];
  editMode.value = true;
};

const cancelEdit = () => {
  if (originalPlan.value) {
    localDays.value = JSON.parse(JSON.stringify(originalPlan.value.days));
  }
  editMode.value = false;
  originalPlan.value = null;
  historyStack.value = [];
  nextTick(() => initMap());
};

const saveEdit = () => {
  // 将本地修改同步回 props（通过 emit 或直接赋值）
  props.tripPlan.days = JSON.parse(JSON.stringify(localDays.value));
  editMode.value = false;
  originalPlan.value = null;
  historyStack.value = [];
  nextTick(() => initMap());
};

const undoEdit = () => {
  if (historyStack.value.length > 0) {
    const prev = historyStack.value.pop();
    if (prev) localDays.value = JSON.parse(prev);
  }
};

const resetEdit = () => {
  if (originalPlan.value) {
    localDays.value = JSON.parse(JSON.stringify(originalPlan.value.days));
    historyStack.value = [];
  }
};

const moveAttraction = (dayIndex: number, index: number, direction: 'up' | 'down') => {
  if (!localDays.value?.[dayIndex]) return;
  const attractions = localDays.value[dayIndex].attractions;
  if (!attractions) return;
  
  const newIndex = direction === 'up' ? index - 1 : index + 1;
  if (newIndex >= 0 && newIndex < attractions.length) {
    saveHistory();
    const [item] = attractions.splice(index, 1);
    if (item) attractions.splice(newIndex, 0, item);
    // 触发响应式更新
    localDays.value = [...localDays.value];
  }
};

const deleteAttraction = (dayIndex: number, index: number) => {
  if (!localDays.value?.[dayIndex]?.attractions) return;
  saveHistory();
  localDays.value[dayIndex].attractions.splice(index, 1);
  localDays.value = [...localDays.value];
};

const addAttraction = (dayIndex: number) => {
  if (!localDays.value?.[dayIndex]) return;
  saveHistory();
  const newAttr = {
    name: '新景点',
    address: '',
    location: { longitude: 0, latitude: 0 },
    description: '请编辑景点描述',
    category: '景点',
    visit_duration: 60,
    ticket_price: 0,
    image_urls: [],
    _uid: genUid()
  };
  localDays.value[dayIndex].attractions.push(newAttr as any);
  localDays.value = [...localDays.value];
};

// 图片预览功能
const openImage = (url: string) => {
  previewUrl.value = url;
  previewVisible.value = true;
};

const closePreview = () => {
  previewVisible.value = false;
  previewUrl.value = '';
};

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && previewVisible.value) closePreview();
};

// 导出功能
const handleExport = async ({ key }: { key: string }) => {
  if (key === 'image') {
    await exportAsImage();
  } else if (key === 'pdf') {
    await exportAsPDF();
  } else if (key === 'json') {
    exportAsJSON();
  }
};

const exportAsJSON = () => {
  const dataStr = JSON.stringify(props.tripPlan, null, 2);
  const blob = new Blob([dataStr], { type: 'application/json' });
  const link = document.createElement('a');
  link.download = `${props.tripPlan.city}旅行计划.json`;
  link.href = URL.createObjectURL(blob);
  link.click();
};

// 等待容器内所有图片加载完成
const waitForImages = (container: HTMLElement): Promise<void> => {
  const images = container.querySelectorAll('img');
  const promises = Array.from(images).map(img => {
    if (img.complete) return Promise.resolve();
    return new Promise<void>(resolve => {
      img.onload = () => resolve();
      img.onerror = () => resolve();
    });
  });
  return Promise.all(promises).then(() => {});
};

const exportAsImage = async () => {
  exporting.value = true;
  await nextTick();
  
  const element = document.getElementById('trip-plan-content');
  if (!element) { exporting.value = false; return; }
  
  await waitForImages(element);
  
  const canvas = await html2canvas(element, {
    scale: 3,
    useCORS: true,
    logging: false,
    backgroundColor: '#2E3440'
  });
  const link = document.createElement('a');
  link.download = `${props.tripPlan.city}旅行计划.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
  
  exporting.value = false;
};

const exportAsPDF = async () => {
  exporting.value = true;
  await nextTick();
  
  const element = document.getElementById('trip-plan-content');
  if (!element) { exporting.value = false; return; }
  
  await waitForImages(element);
  
  const canvas = await html2canvas(element, {
    scale: 3,
    useCORS: true,
    logging: false,
    backgroundColor: '#2E3440'
  });
  const imgData = canvas.toDataURL('image/png');
  
  const pdf = new jsPDF('p', 'mm', 'a4');
  const pdfWidth = pdf.internal.pageSize.getWidth();
  const pdfPageHeight = pdf.internal.pageSize.getHeight();
  const imgHeight = (canvas.height * pdfWidth) / canvas.width;
  
  let heightLeft = imgHeight;
  let position = 0;
  
  pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, imgHeight);
  heightLeft -= pdfPageHeight;
  
  while (heightLeft > 0) {
    position = heightLeft - imgHeight;
    pdf.addPage();
    pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, imgHeight);
    heightLeft -= pdfPageHeight;
  }
  
  pdf.save(`${props.tripPlan.city}旅行计划.pdf`);
  exporting.value = false;
};

onMounted(() => {
  initLocalDays();
  initMap();
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});

watch(() => props.tripPlan, () => {
  initLocalDays();
  nextTick(() => initMap());
}, { deep: true });
</script>

<style scoped>
.result-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 100vh;
  background-image:
    linear-gradient(rgba(46, 52, 64, 0.9), rgba(46, 52, 64, 0.9)),
    url('https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2000&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  color: #ECEFF4;
}

.glass-effect {
  background: rgba(255, 255, 255, 0.05) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

.result-view :deep(.ant-page-header) {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 24px;
}

:deep(.ant-page-header-heading-title), :deep(.ant-page-header-heading-sub-title), :deep(.ant-descriptions-item-label), :deep(.ant-descriptions-item-content) {
  color: #ECEFF4 !important;
}

.map-card {
  margin-bottom: 24px;
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.map-card :deep(.ant-card-head) {
  background: rgba(136, 192, 208, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.map-card :deep(.ant-card-head-title) {
  color: #88C0D0;
  font-weight: 600;
}

.map-placeholder {
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
  color: #D8DEE9;
}

.info-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.info-section :deep(.ant-card) {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-section :deep(.ant-card-head) {
  background: rgba(180, 142, 173, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.info-section :deep(.ant-card-head-title) {
  color: #B48EAD;
  font-weight: 600;
}

.weather-card {
  text-align: center;
  padding: 20px;
  background: rgba(129, 161, 193, 0.2);
  border-radius: 16px;
  color: #ECEFF4;
  margin: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.weather-card p {
  margin: 4px 0;
}

:deep(.ant-tabs-card > .ant-tabs-nav .ant-tabs-tab) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px 12px 0 0;
  color: #D8DEE9;
  margin-right: 4px;
}

:deep(.ant-tabs-card > .ant-tabs-nav .ant-tabs-tab-active) {
  background: rgba(136, 192, 208, 0.3) !important;
  border-bottom-color: transparent !important;
}

:deep(.ant-tabs-card > .ant-tabs-nav .ant-tabs-tab-active .ant-tabs-tab-btn) {
  color: #88C0D0 !important;
  font-weight: 600;
}

.day-plan {
  padding: 32px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  border-radius: 0 0 24px 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-top: none;
}

.day-plan > p {
  color: #ECEFF4;
}

.day-plan > p strong {
  color: #88C0D0;
}

.day-plan :deep(.ant-card) {
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.day-plan :deep(.ant-card:hover) {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

.day-plan :deep(.ant-card-head-title) {
  color: #ECEFF4;
}

.card-content {
  display: flex;
  gap: 20px;
}

.card-details {
  flex: 1;
}

.card-details p {
  margin: 8px 0;
  color: #D8DEE9;
}

/* 住宿卡片文字样式 */
.hotel-info {
  color: #A3BE8C !important;
  font-size: 14px;
  margin: 8px 0;
}

/* 景点卡片新布局 */
.attraction-content {
  display: flex;
  flex-direction: column;
}

.attraction-image {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.attraction-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: transform 0.3s ease;
}

.attraction-image img:hover {
  transform: scale(1.05);
}

.attraction-image :deep(.ant-carousel) {
  height: 100%;
}

.attraction-image :deep(.ant-carousel .slick-slide) {
  height: 100%;
}

.attraction-image :deep(.ant-carousel .slick-list) {
  height: 100%;
}

.carousel-slide {
  height: 100%;
  aspect-ratio: 16 / 9;
}

.carousel-slide img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: transform 0.3s ease;
}

.carousel-slide img:hover {
  transform: scale(1.05);
}

.attraction-details {
  padding: 0 4px;
}

.attraction-desc {
  color: #ECEFF4;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
}

.attraction-info {
  color: #88C0D0;
  font-size: 13px;
  margin: 6px 0;
}

:deep(.marker-label) {
  background: #88C0D0;
  color: #2E3440;
  padding: 4px 10px;
  border-radius: 50%;
  font-weight: 800;
  box-shadow: 0 0 15px rgba(136, 192, 208, 0.6);
}

:deep(.ant-timeline-item-content) {
  margin-left: 30px;
}

:deep(.ant-timeline-item-tail) {
  border-left: 2px dashed rgba(136, 192, 208, 0.3);
}

:deep(.ant-timeline-item-head) {
  background: #88C0D0;
  border-color: #88C0D0;
  box-shadow: 0 0 10px rgba(136, 192, 208, 0.4);
}

:deep(.ant-tag) {
  border-radius: 6px;
  background: rgba(136, 192, 208, 0.1);
  border: 1px solid rgba(136, 192, 208, 0.3);
  color: #88C0D0;
}

:deep(.ant-btn) {
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ECEFF4;
}

:deep(.ant-btn-primary) {
  background: #88C0D0 !important;
  border: none !important;
  color: #2E3440 !important;
  font-weight: 600;
}

/* 图片预览弹窗 */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
}

.preview-close {
  position: absolute;
  top: 20px;
  right: 30px;
  font-size: 32px;
  color: #fff;
  cursor: pointer;
  z-index: 10000;
  transition: transform 0.2s;
}

.preview-close:hover {
  transform: scale(1.2);
}

.preview-image {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  cursor: default;
  border-radius: 8px;
}

/* 导出时显示所有天数的样式 */
.export-all-days {
  background: rgba(46, 52, 64, 0.95);
  padding: 20px;
}

.export-day-section {
  margin-bottom: 32px;
  page-break-inside: avoid;
}

.export-day-title {
  color: #88C0D0;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: rgba(136, 192, 208, 0.2);
  border-radius: 12px;
  border-left: 4px solid #88C0D0;
}

.export-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.export-item {
  margin-left: 20px;
  position: relative;
}

.export-item::before {
  content: '';
  position: absolute;
  left: -16px;
  top: 50%;
  width: 8px;
  height: 8px;
  background: #88C0D0;
  border-radius: 50%;
  transform: translateY(-50%);
}
</style>
