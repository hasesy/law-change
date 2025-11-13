<!-- src/App.vue -->
<template>
  <n-config-provider>
    <n-layout style="min-height: 100vh">
      <n-layout-header bordered style="padding: 0 24px; display: flex; align-items: center;">
        <h2 style="margin: 0; font-size: 18px;">
          법령 변경이력 모니터링
        </h2>
      </n-layout-header>

      <n-layout-content style="padding: 16px 24px 24px;">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-config-provider>
</template>

<script setup lang="ts"></script>
