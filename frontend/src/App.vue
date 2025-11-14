<!-- src/App.vue -->
<template>
  <n-config-provider :theme="theme">
    <n-layout style="min-height: 100vh">
      <!-- 🔹 상단 헤더 -->
      <n-layout-header
        bordered
        style="
          height: 56px;
          padding: 0 20px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        "
      >
        <div style="display: flex; align-items: center; gap: 8px">
          <!-- 로고 영역 (원하면 이미지로 교체) -->
          <div
            style="
              width: 28px;
              height: 28px;
              border-radius: 8px;
              background: #2563eb;
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-weight: 700;
              font-size: 16px;
            "
          >
            L
          </div>
          <div style="display: flex; flex-direction: column">
            <span style="font-weight: 600; font-size: 16px">
              법령 변경이력 모니터링
            </span>
          </div>
        </div>

        <!-- 🔥 다크모드 버튼 -->
        <n-button tertiary @click="toggleTheme">
          {{ isDark ? "🌞 라이트모드" : "🌙 다크모드" }}
        </n-button>
      </n-layout-header>

      <!-- 🔹 헤더 아래: 좌측 메뉴 + 우측 본문 -->
      <n-layout has-sider style="height: calc(100vh - 56px)">
        <!-- 왼쪽 사이드 메뉴 -->
        <n-layout-sider
          bordered
          :width="220"
          collapse-mode="width"
          show-trigger="bar"
        >
          <div style="padding: 12px 12px 8px; font-size: 11px; color: #9ca3af">
            메인 메뉴
          </div>
          <n-menu
            :options="menuOptions"
            :value="activeKey"
            @update:value="handleMenuSelect"
          />
        </n-layout-sider>
        <!-- 오른쪽 본문 -->
        <n-layout-content style="padding: 16px 24px 24px; overflow: auto">
          <router-view />
        </n-layout-content>
      </n-layout>
    </n-layout>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { darkTheme } from "naive-ui";

const router = useRouter();
const route = useRoute();

// 라우터 경로 기준으로 메뉴 활성화
const activeKey = computed(() => route.path);

// 메뉴 항목 정의 (지금은 하나지만 나중에 추가 가능)
const menuOptions = [
  {
    label: "대시보드",
    key: "/dashboard",
  },
  {
    label: "법령 변경이력",
    key: "/law-changes",
  },
  // 나중에 이런 식으로 추가 가능
  // { label: '신·구조문 비교', key: '/diff' },
];

const isDark = ref(true);

const theme = computed(() => (isDark.value ? darkTheme : null));

function handleMenuSelect(key: string) {
  if (key !== route.path) {
    router.push(key);
  }
}

const toggleTheme = () => (isDark.value = !isDark.value);
</script>
