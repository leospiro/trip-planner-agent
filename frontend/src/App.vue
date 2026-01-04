<template>
  <a-layout class="layout">
    <a-layout-header>
      <div class="header-left">
        <span class="title">智能旅行助手</span>
        <span class="logo-text">leospiro</span>
      </div>
    </a-layout-header>
    <a-layout-content style="padding: 0 50px">
      <div :style="{ background: '#fff', padding: '24px', minHeight: 'calc(100vh - 158px)' }">
        <RouterView />
      </div>
    </a-layout-content>
    <a-layout-footer style="text-align: center">
      <div>HelloAgents Trip Planner ©2024</div>
      <div class="footer-info">
        Made by leospiro |
        <a href="https://github.com/datawhalechina/Hello-Agents" target="_blank" rel="noopener">Datawhale</a>
      </div>
    </a-layout-footer>
  </a-layout>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<style scoped>
.header-left {
  display: flex;
  align-items: center;
  height: 64px;
}
.title {
  color: #fff;
  font-size: 18px;
  font-weight: 500;
}
.logo-text {
  color: #fff;
  font-family: 'Cambria Math', Cambria, serif;
  font-size: 16px;
  margin-left: 12px;
}
.footer-info {
  margin-top: 4px;
  font-size: 13px;
}
.footer-info a {
  color: #1890ff;
}
</style>
