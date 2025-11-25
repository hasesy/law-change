<!-- src/views/Dashboard.vue -->
<template>
  <div class="page dashboard-page">
    <!-- 헤더 영역 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">대시보드</h1>
      </div>

      <!-- 기간 선택 Tabs (segment) -->
      <n-tabs
        class="range-tabs"
        v-model:value="range"
        type="segment"
        animated
        size="small"
        @update:value="onRangeChange"
      >
        <n-tab-pane :name="7" tab="최근 7일" />
        <n-tab-pane :name="15" tab="15일" />
        <n-tab-pane :name="30" tab="한 달" />
      </n-tabs>
    </div>

    <n-spin :show="loading" size="large">
      <template v-if="data">
        <!-- 상단 통계 카드들 -->
        <div class="dashboard-content">
          <n-grid
            cols="1 768:2 1024:3 1400:5"
            :x-gap="16"
            :y-gap="16"
            class="top-cards"
          >
            <!-- 1. 최근 변경 이력 -->
            <n-gi>
              <n-card class="stat-card" :bordered="false">
                <div class="stat-card-body">
                  <div class="stat-card-left">
                    <div class="stat-card-title">최근 변경 이력</div>
                    <n-statistic :value="data.overview.total_changes">
                      <template #suffix>건</template>
                    </n-statistic>
                  </div>
                  <div class="stat-card-right">
                    <n-progress
                      type="circle"
                      :percentage="100"
                      :stroke-width="10"
                      :show-indicator="false"
                    />
                  </div>
                </div>
              </n-card>
            </n-gi>

            <!-- 2. 검토 필요 -->
            <n-gi>
              <n-card class="stat-card" :bordered="false">
                <div class="stat-card-body">
                  <div class="stat-card-left">
                    <div class="stat-card-title">검토 필요</div>
                    <n-statistic :value="data.overview.need_review_count">
                      <template #suffix>건</template>
                    </n-statistic>
                  </div>
                  <div class="stat-card-right">
                    <n-progress
                      type="circle"
                      :percentage="reviewRatio"
                      :stroke-width="10"
                      :show-indicator="false"
                      status="warning"
                    />
                  </div>
                </div>
              </n-card>
            </n-gi>

            <!-- 3. 안전 관련 -->
            <n-gi>
              <n-card class="stat-card" :bordered="false">
                <div class="stat-card-body">
                  <div class="stat-card-left">
                    <div class="stat-card-title">안전 관련</div>
                    <n-statistic :value="data.overview.safety_changes">
                      <template #suffix>건</template>
                    </n-statistic>
                  </div>
                  <div class="stat-card-right">
                    <n-progress
                      type="circle"
                      :percentage="safetyRatio"
                      :stroke-width="10"
                      :show-indicator="false"
                      status="success"
                    />
                  </div>
                </div>
              </n-card>
            </n-gi>

            <!-- 4. 화학 관련 -->
            <n-gi>
              <n-card class="stat-card" :bordered="false">
                <div class="stat-card-body">
                  <div class="stat-card-left">
                    <div class="stat-card-title">화학 관련</div>
                    <n-statistic :value="data.overview.chemical_changes">
                      <template #suffix>건</template>
                    </n-statistic>
                  </div>
                  <div class="stat-card-right">
                    <n-progress
                      type="circle"
                      :percentage="chemicalRatio"
                      :stroke-width="10"
                      :show-indicator="false"
                      status="info"
                    />
                  </div>
                </div>
              </n-card>
            </n-gi>

            <!-- 5. 환경 관련 -->
            <n-gi>
              <n-card class="stat-card" :bordered="false">
                <div class="stat-card-body">
                  <div class="stat-card-left">
                    <div class="stat-card-title">환경 관련</div>
                    <n-statistic :value="data.overview.environment_changes">
                      <template #suffix>건</template>
                    </n-statistic>
                  </div>
                  <div class="stat-card-right">
                    <n-progress
                      type="circle"
                      :percentage="environmentRatio"
                      :stroke-width="10"
                      :show-indicator="false"
                      status="error"
                    />
                  </div>
                </div>
              </n-card>
            </n-gi>
          </n-grid>

          <!-- 도메인별 카드 -->
          <n-grid cols="1 1024:3" :x-gap="16" :y-gap="16" class="domain-cards">
            <n-gi
              v-for="domain in data.domain_summary.domains"
              :key="domain.domain"
            >
              <n-card class="domain-card" :bordered="false">
                <div class="domain-card-header">
                  <span style="font-size: 15px"
                    >{{ domain.domain_name }} 관련 법령</span
                  >
                  <span class="domain-total">
                    {{ domain.total_changes }}건
                  </span>
                </div>
                <ul class="domain-law-list">
                  <li
                    v-for="law in domain.laws"
                    :key="law.law_id"
                    class="domain-law-item"
                  >
                    <span class="law-name">{{ law.law_name }}</span>
                    <span class="law-count">{{ law.change_count }}건</span>
                  </li>
                </ul>
              </n-card>
            </n-gi>
          </n-grid>

          <!-- 하단: 최근 개정된 법령 & 주요 조치사항 -->
          <n-grid
            cols="1 1024:3"
            :x-gap="16"
            :y-gap="16"
            class="bottom-section"
          >
            <!-- 최근 개정된 법령 -->
            <n-gi :span="2">
              <n-card class="recent-card" :bordered="false">
                <template #header>
                  <div class="card-header-with-link">
                    <span>최근 개정된 법령 (중요도 MEDIUM 이상)</span>
                    <n-button
                      text
                      type="primary"
                      size="tiny"
                      @click="goToChangeList"
                    >
                      전체 보기
                    </n-button>
                  </div>
                </template>

                <template v-if="data.recent_important_changes.items.length">
                  <div
                    v-for="item in data.recent_important_changes.items"
                    :key="item.change_id"
                    class="recent-item"
                  >
                    <div class="recent-title-row">
                      <span class="recent-law-name">
                        {{ item.law_name }}
                      </span>
                      <n-tag size="small" round>
                        {{ item.change_date }}
                      </n-tag>
                    </div>
                    <div class="recent-meta">
                      <n-tag
                        size="tiny"
                        :type="importanceTagType(item.importance)"
                        round
                      >
                        {{ item.importance }}
                      </n-tag>
                      <span v-if="item.change_type" class="recent-change-type">
                        · {{ item.change_type }}
                      </span>
                    </div>
                    <p class="recent-summary">
                      {{ item.summary || "변경 요약 정보가 없습니다." }}
                    </p>
                  </div>
                </template>
                <template v-else>
                  <n-empty description="표시할 변경 이력이 없습니다." />
                </template>
              </n-card>
            </n-gi>

            <!-- 주요 조치사항 -->
            <n-gi>
              <n-card class="action-card" :bordered="false">
                <template #header>
                  <span>주요 조치사항</span>
                </template>

                <template v-if="data.action_items.items.length">
                  <div
                    v-for="item in data.action_items.items"
                    :key="item.change_id + item.action_title"
                    class="action-item"
                  >
                    <div class="action-header">
                      <n-tag
                        size="small"
                        :type="importanceTagType(item.importance)"
                        round
                      >
                        {{ item.importance }}
                      </n-tag>
                      <span class="action-law-name">{{ item.law_name }}</span>
                    </div>
                    <div class="action-title">
                      {{ item.action_title }}
                    </div>
                    <p class="action-detail">
                      {{ item.action_detail }}
                    </p>
                  </div>
                </template>
                <template v-else>
                  <n-empty description="표시할 조치사항이 없습니다." />
                </template>
              </n-card>
            </n-gi>
          </n-grid>
        </div>
      </template>

      <template v-else>
        <n-empty description="대시보드 데이터를 불러오지 못했습니다." />
      </template>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { fetchDashboard } from "@/api/dashboard";
import type { DashboardResponse, Importance } from "@/types/dashboard";

const range = ref<7 | 15 | 30>(7);
const loading = ref(false);
const data = ref<DashboardResponse | null>(null);

const router = useRouter();

async function loadDashboard() {
  loading.value = true;
  try {
    data.value = await fetchDashboard(range.value);
  } finally {
    loading.value = false;
  }
}

function onRangeChange(value: 7 | 15 | 30) {
  range.value = value;
  loadDashboard();
}

const totalChanges = computed(() => data.value?.overview.total_changes ?? 0);

const reviewRatio = computed(() => {
  if (!totalChanges.value) return 0;
  return Math.round(
    ((data.value?.overview.need_review_count ?? 0) / totalChanges.value) * 100
  );
});

const safetyRatio = computed(() => {
  if (!totalChanges.value) return 0;
  return Math.round(
    ((data.value?.overview.safety_changes ?? 0) / totalChanges.value) * 100
  );
});

const chemicalRatio = computed(() => {
  if (!totalChanges.value) return 0;
  return Math.round(
    ((data.value?.overview.chemical_changes ?? 0) / totalChanges.value) * 100
  );
});

const environmentRatio = computed(() => {
  if (!totalChanges.value) return 0;
  return Math.round(
    ((data.value?.overview.environment_changes ?? 0) / totalChanges.value) * 100
  );
});

function importanceTagType(importance: Importance) {
  switch (importance) {
    case "HIGH":
      return "error";
    case "MEDIUM":
      return "warning";
    case "LOW":
      return "info";
    default:
      return "default";
  }
}

function goToChangeList() {
  router.push("/law-changes");
}

onMounted(() => {
  loadDashboard();
});
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 헤더 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

.page-subtitle {
  margin: 4px 0 0;
  font-size: 14px;
  opacity: 0.72;
}

/* 상단 카드 */
.top-cards {
  margin-top: 8px;
}

.stat-card {
  display: flex;
  flex-direction: column;
}

.stat-card-title {
  font-size: 16px;
  font-weight: 500;
}

/* 좌우 2컬럼 레이아웃 */
.stat-card-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 왼쪽 컬럼: 제목 + 숫자 세로 */
.stat-card-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 오른쪽 progress 크기 */
.stat-card-right .n-progress {
  width: 80px;
  height: 80px;
}

/* 상단 통계 카드 숫자만 크게 + 두껍게 */
.stat-card :deep(.n-statistic-value__content) {
  font-size: 30px;
  font-weight: 700;
}

.stat-card :deep(.n-statistic-value__suffix) {
  font-size: 20px;
}

/* 도메인 카드 */
.domain-card-header {
  display: flex;
  justify-content: space-between;
  font-weight: 600;
  margin-bottom: 8px;
}

.domain-total {
  font-size: 13px;
  opacity: 0.8;
}

.domain-law-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.domain-law-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 13px;
}

.domain-law-item + .domain-law-item {
  border-top: 1px solid rgba(148, 163, 184, 0.24);
  padding-top: 6px;
  margin-top: 6px;
}

.law-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.law-count {
  font-weight: 600;
}

/* 하단 섹션 */
.bottom-section {
  margin-top: 8px;
}

.card-header-with-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 최근 변경 카드 */
.recent-item {
  padding: 10px 0;
}

.recent-item + .recent-item {
  border-top: 1px solid rgba(148, 163, 184, 0.22);
}

.recent-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-law-name {
  font-weight: 600;
  font-size: 14px;
  margin-right: 8px;
}

.recent-meta {
  margin-top: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0.85;
}

.recent-change-type {
  font-size: 12px;
}

.recent-summary {
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.5;
}

/* 조치사항 카드 */
.action-item {
  padding: 10px 0;
}

.action-item + .action-item {
  border-top: 1px solid rgba(148, 163, 184, 0.22);
}

.action-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.action-law-name {
  font-size: 13px;
  font-weight: 500;
}

.action-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.action-detail {
  font-size: 13px;
  line-height: 1.5;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 16px; /* 세 개의 n-grid 블록 사이 간격 */
}

.range-tabs {
  width: fit-content;
  min-width: 260px;
}

.range-tabs :deep(.n-tabs-nav--segment-type) {
  height: 36px;
}

.range-tabs :deep(.n-tabs-tab) {
  padding: 0 20px;
  font-size: 14px;
}

.range-tabs :deep(.n-tabs-tab--active) {
  height: 30px;
}
</style>
