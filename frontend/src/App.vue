<!-- src/App.vue -->
<template>
  <n-config-provider :theme="currentTheme" :theme-overrides="themeOverrides">
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
        <div
          style="display: flex; align-items: center; gap: 8px; cursor: pointer"
          @click="router.push('/dashboard')"
        >
          <!-- 로고 -->
          <img
            src="@/assets/logo.png"
            alt="logo"
            style="
              width: 28px;
              height: 28px;
              border-radius: 6px;
              object-fit: cover;
            "
          />
          <div style="display: flex; flex-direction: column">
            <span style="font-weight: 600; font-size: 16px">
              LegalTracker
            </span>
          </div>
        </div>

        <!-- 🔥 다크모드 버튼 -->
        <n-button tertiary @click="toggleTheme">
          {{ isDark ? "🌞 라이트 모드" : "🌙 다크 모드" }}
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
          <div
            style="
              padding: 12px 12px 8px;
              font-size: 11px;
              color: rgba(148, 163, 184, 0.9);
            "
          >
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
          <n-scrollbar style="height: 100%">
            <div>
              <router-view />
            </div>
          </n-scrollbar>
        </n-layout-content>
      </n-layout>
    </n-layout>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { darkTheme, type GlobalThemeOverrides } from "naive-ui";

const router = useRouter();
const route = useRoute();

// 라우터 경로 기준으로 메뉴 활성화
const activeKey = computed(() => route.path);

const menuOptions = [
  {
    label: "대시보드",
    key: "/dashboard",
  },
  {
    label: "법령 변경이력",
    key: "/law-changes",
  },
];

const isDark = ref(true);

// 🔹 실제 Naive UI theme 객체
const currentTheme = computed(() => (isDark.value ? darkTheme : null));

// 🔹 공통 색상 토큰 살짝 커스텀
const themeOverrides = computed<GlobalThemeOverrides>(() => {
  if (isDark.value) {
    // 🌙 세미 다크 테마
    return {
      common: {
        // 배경 / 카드 / 텍스트
        bodyColor: "#020617", // slate-950 느낌
        cardColor: "#0f172a",
        modalColor: "#0f172a",
        popoverColor: "#0f172a",
        inputColor: "#0f172a",
        textColorBase: "#f9fafb", // 거의 흰색
        textColor1: "#f9fafb", // 제목/주요 텍스트
        textColor2: "#e5e7eb", // 일반 텍스트
        textColor3: "#9ca3af", // 서브/보조 텍스트
        borderColor: "rgba(148, 163, 184, 0.35)",

        // 포커스 / 프라이머리
        primaryColor: "#60a5fa",
        primaryColorHover: "#3b82f6",
        primaryColorPressed: "#1d4ed8",
        primaryColorSuppl: "#60a5fa",

        // 레이아웃 헤더/사이더 살짝 밝게
        invertedColor: "#0b1120",
      },
      Card: {
        // 카드 배경은 body보다 확실히 밝게
        color: "#0f172a",
        borderColor: "rgba(148, 163, 184, 0.28)",
        boxShadow: "0 16px 40px rgba(15, 23, 42, 0.75)",
        borderRadius: "16px",
      },
      Layout: {
        // 헤더/사이더는 배경과 맞춰주고
        headerColor: "#020617",
        siderColor: "#020617",
        footerColor: "#020617",
      },
    };
  }

  // 🌞 소프트 라이트 테마
  return {
    common: {
      bodyColor: "#f3f4f6", // 아주 밝은 회색
      cardColor: "#ffffff",
      modalColor: "#ffffff",
      popoverColor: "#ffffff",
      inputColor: "#ffffff",
      textColorBase: "#111827", // 기본 텍스트
      textColor1: "#111827", // 제목/주요 텍스트
      textColor2: "#374151", // 일반 텍스트 (조금 진한 회색)
      textColor3: "#6b7280", // 보조 텍스트
      borderColor: "#d1d5db",

      primaryColor: "#2563eb",
      primaryColorHover: "#1d4ed8",
      primaryColorPressed: "#1d4ed8",
      primaryColorSuppl: "#2563eb",
    },
    Card: {
      borderRadius: "16px",
    },
  };
});

// 🔹 body 클래스 토글해서 바깥 배경까지 맞추기
function applyBodyTheme(dark: boolean) {
  if (dark) {
    document.body.classList.add("theme-dark");
    document.body.classList.remove("theme-light");
  } else {
    document.body.classList.add("theme-light");
    document.body.classList.remove("theme-dark");
  }
}

onMounted(() => {
  applyBodyTheme(isDark.value);
});

watch(isDark, (val) => {
  applyBodyTheme(val);
});

function handleMenuSelect(key: string) {
  if (key !== route.path) {
    router.push(key);
  }
}

const toggleTheme = () => {
  isDark.value = !isDark.value;
};
</script>
