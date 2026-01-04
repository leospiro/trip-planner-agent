<template>
  <div class="xhs-preview">
    <h3 class="xhs-title">🔍 相关攻略搜索</h3>
    
    <div v-if="keywords.length === 0" class="no-keywords">
      暂无推荐关键词
    </div>
    
    <div v-else class="search-section">
      <div v-for="keyword in keywords" :key="keyword" class="keyword-row">
        <span class="keyword-text">{{ keyword }}</span>
        <div class="search-buttons">
          <a :href="getXHSUrl(keyword)" target="_blank" class="search-btn xhs">
            📱 小红书
          </a>
          <a :href="getGoogleUrl(keyword)" target="_blank" class="search-btn google">
            🔍 Google
          </a>
          <a :href="getBaiduUrl(keyword)" target="_blank" class="search-btn baidu">
            🔎 百度
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  keywords: string[]
}

const props = withDefaults(defineProps<Props>(), {
  keywords: () => []
})

const getXHSUrl = (keyword: string) => {
  return `https://www.xiaohongshu.com/search_result?keyword=${encodeURIComponent(keyword)}`
}

const getGoogleUrl = (keyword: string) => {
  return `https://www.google.com/search?q=${encodeURIComponent(keyword + ' 旅游攻略')}`
}

const getBaiduUrl = (keyword: string) => {
  return `https://www.baidu.com/s?wd=${encodeURIComponent(keyword)}`
}
</script>

<style scoped>
.xhs-preview {
  margin: 20px 0;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.xhs-title {
  color: #333;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.no-keywords {
  text-align: center;
  color: #999;
  padding: 20px;
}

.search-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.keyword-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-text {
  font-weight: 500;
  color: #333;
  flex: 1;
  min-width: 150px;
}

.search-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.search-btn {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
  text-decoration: none;
  transition: transform 0.2s, opacity 0.2s;
  white-space: nowrap;
}

.search-btn:hover {
  transform: scale(1.05);
  opacity: 0.9;
}

.search-btn.xhs {
  background: linear-gradient(135deg, #fe2c55, #ff6b6b);
  color: white;
}

.search-btn.google {
  background: linear-gradient(135deg, #4285f4, #34a853);
  color: white;
}

.search-btn.baidu {
  background: linear-gradient(135deg, #2932e1, #4e6ef2);
  color: white;
}

@media (max-width: 768px) {
  .keyword-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .keyword-text {
    margin-bottom: 8px;
  }
  
  .xhs-preview {
    margin: 16px 0;
    padding: 16px;
  }
}
</style>
