<!-- src/views/Dashboard.vue -->
<template>
  <div class="dashboard-page">
    <!-- 상단 타이틀 -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">대시보드</h1>
      <p class="dashboard-subtitle">
        최근 법령 개정 현황 및 요약입니다. ({{ referenceDate }} 기준)
      </p>
    </div>

    <!-- 🔹 요약 카드 2개 (전날 변경 이력 / 검토 필요 건수) -->
    <div class="summary-row">
      <n-card
        v-for="stat in stats"
        :key="stat.key"
        class="summary-card"
        size="small"
        :bordered="true"
      >
        <div class="summary-label">{{ stat.label }}</div>
        <div class="summary-main">
          <span class="summary-value">{{ stat.value }}</span>
          <span class="summary-unit">{{ stat.unit }}</span>
        </div>
      </n-card>
    </div>

    <!-- 🔹 하단 2컬럼 레이아웃 -->
    <div class="bottom-layout">
      <!-- 왼쪽: 최근 개정된 법령 -->
      <div class="left-panel">
        <n-card class="section-card" :bordered="true">
          <template #header>
            <div class="section-header">
              <span class="section-title">최근 개정된 법령</span>
              <n-button text size="tiny">전체 보기</n-button>
            </div>
          </template>

          <div class="recent-list">
            <n-card
              v-for="law in recentLaws"
              :key="law.id"
              class="recent-law-card"
              size="small"
              :bordered="false"
            >
              <div class="recent-law-header">
                <div class="recent-law-title">
                  [{{ law.source }}] {{ law.title }}
                </div>
                <div class="pill pill-date">
                  {{ law.changeDate }}
                </div>
              </div>

              <div class="diff-block">
                <div class="diff-line diff-old">
                  {{ law.oldText }}
                </div>
                <div class="diff-line diff-new">
                  {{ law.newText }}
                </div>
              </div>
            </n-card>
          </div>
        </n-card>
      </div>

      <!-- 오른쪽: 주요 조치사항 -->
      <div class="right-panel">
        <n-card
          class="section-card actions-card"
          :bordered="true"
          title="주요 조치사항"
        >
          <div class="actions-list">
            <div v-for="action in actions" :key="action.id" class="action-item">
              <div class="action-icon" :class="'action-icon-' + action.type">
                <span>{{ action.icon }}</span>
              </div>
              <div class="action-text">
                <div class="action-title">{{ action.title }}</div>
                <div class="action-desc">
                  {{ action.description }}
                </div>
              </div>
            </div>
          </div>
        </n-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import dayjs from "dayjs";

const referenceDate = computed(() => dayjs().format("YYYY-MM-DD"));

// 🔹 요약 카드 2개만
const stats = [
  {
    key: "changes",
    label: "전날 변경된 이력 개수",
    value: 12,
    unit: "건",
  },
  {
    key: "review",
    label: "검토 필요 건수",
    value: 3,
    unit: "건",
  },
];

const recentLaws = [
  {
    id: 1,
    source: "법제처",
    title: "제4조(정의) 일부 개정",
    changeDate: "2025-10-02",
    version: "20251001",
    oldText: '"유해물질"',
    newText: '"특수관리물질"',
  },
  {
    id: 2,
    source: "법제처",
    title: "별표1 개정",
    changeDate: "2025-10-20",
    version: "20251020",
    oldText: "1ppm",
    newText: "0.5ppm",
  },
];

const actions = [
  {
    id: 1,
    type: "danger",
    icon: "!",
    title: "내부 규정 업데이트",
    description:
      "제4조(정의) 개정에 따라 유해물질 관련 내부 가이드를 수정해야 합니다.",
  },
  {
    id: 2,
    type: "warning",
    icon: "⚠",
    title: "임직원 교육 실시",
    description:
      "별표1 개정에 따른 변경 취급기준 사항에 대해 관련 부서 교육이 필요합니다.",
  },
  {
    id: 3,
    type: "info",
    icon: "✓",
    title: "보고 양식 확인",
    description:
      "시행령 제11조2 개정으로 인한 보고 주기 변경사항을 확인하고 시스템에 반영합니다.",
  },
];
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dashboard-header {
  margin-bottom: 4px;
}

.dashboard-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.dashboard-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  opacity: 0.7;
}

/* 🔹 요약 카드 2개 – 가로로 길게 + 반응형 */
.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-top: 4px;
}

.summary-card {
  border-radius: 16px;
  padding: 16px 20px;
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.12);
}

.summary-label {
  font-size: 13px;
  opacity: 0.8;
  margin-bottom: 8px;
}

.summary-main {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.summary-value {
  font-size: 30px;
  font-weight: 700;
  line-height: 1.1;
}

.summary-unit {
  font-size: 14px;
  opacity: 0.8;
}

/* 🔹 하단 2컬럼 */
.bottom-layout {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr)); /* ← 1:1 */
  gap: 16px;
  margin-top: 4px;
}

.section-card {
  border-radius: 16px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.12);
}

/* 최근 개정된 법령 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-weight: 600;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-law-card {
  border-radius: 14px;
}

.recent-law-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 4px;
}

.recent-law-title {
  font-weight: 600;
  font-size: 14px;
}

.pill {
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 11px;
  white-space: nowrap;
}

.pill-date {
  opacity: 0.85;
  border: 1px solid rgba(148, 163, 184, 0.5);
}

.recent-meta {
  font-size: 12px;
  opacity: 0.7;
  margin-bottom: 8px;
}

.diff-block {
  margin-top: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.diff-label {
  font-size: 11px;
  opacity: 0.7;
}

.diff-label-new {
  margin-top: 4px;
}

.diff-line {
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
}

.diff-old {
  background: rgba(248, 113, 113, 0.18);
}

.diff-new {
  background: rgba(74, 222, 128, 0.18);
}

/* 조치사항 */
.actions-card {
  height: 100%;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.action-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.action-icon-danger {
  background: rgba(239, 68, 68, 0.18);
}

.action-icon-warning {
  background: rgba(234, 179, 8, 0.18);
}

.action-icon-info {
  background: rgba(59, 130, 246, 0.18);
}

.action-text {
  flex: 1;
}

.action-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 2px;
}

.action-desc {
  font-size: 12px;
  opacity: 0.8;
}

/* 좁은 화면에서는 아래로 한 줄씩 */
@media (max-width: 1024px) {
  .bottom-layout {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
