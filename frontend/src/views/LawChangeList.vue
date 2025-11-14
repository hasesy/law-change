<!-- src/views/LawChangeList.vue -->
<template>
  <div class="page">
    <!-- 타이틀 -->
    <div class="page-header">
      <h1 class="page-title">변경이력 목록</h1>
    </div>

    <!-- 🔍 검색 바 영역 -->
    <n-card
      class="filter-card"
      :bordered="true"
      :content-style="{ padding: '14px 14px' }"
    >
      <div class="filter-row">
        <!-- 검색어 -->
        <n-input
          v-model:value="filter.keyword"
          class="filter-search"
          placeholder="법령명을 입력하세요."
          clearable
          @keyup.enter="handleSearch"
        />

        <!-- 기준일자 -->
        <n-select
          v-model:value="filter.date_basis"
          :options="dateBasisOptions"
          class="filter-basis"
        />

        <!-- 시작일 ~ 종료일 -->
        <div class="filter-dates">
          <n-date-picker
            v-model:value="filter.start_date"
            class="date-picker"
            type="date"
            clearable
            placeholder="시작일"
          />
          <span class="date-separator">-</span>
          <n-date-picker
            v-model:value="filter.end_date"
            class="date-picker"
            type="date"
            clearable
            placeholder="종료일"
          />
        </div>

        <!-- 검색 버튼 -->
        <n-button
          type="primary"
          size="large"
          class="filter-button"
          @click="handleSearch"
        >
          검색
        </n-button>
      </div>
    </n-card>

    <!-- 📋 변경이력 카드 리스트 -->
    <div class="list-section">
      <n-spin :show="loading">
        <div v-if="items.length" class="card-grid">
          <n-card
            v-for="item in items"
            :key="item.change_id"
            class="law-card"
            :bordered="false"
            hoverable
            @click="handleCardClick(item)"
          >
            <div class="law-card-main">
              <!-- 왼쪽: 법령 기본정보 -->
              <div class="law-card-left">
                <!-- 제목 + 뱃지 -->
                <div class="law-card-header">
                  <div class="law-title">
                    {{ item.law_name }}
                  </div>
                  <div class="badge-row">
                    <n-tag
                      v-if="item.current_hist_cd"
                      size="small"
                      type="info"
                      round
                    >
                      {{ item.current_hist_cd }}
                    </n-tag>
                    <n-tag
                      v-if="item.change_type"
                      size="small"
                      :type="changeTypeTagType(item.change_type)"
                      round
                    >
                      {{ item.change_type }}
                    </n-tag>
                  </div>
                </div>

                <!-- 공포번호 / 공포일자 -->
                <div class="meta-row">
                  <span class="meta-label">공포번호</span>
                  <span class="meta-value">
                    {{ item.proclamation_no || "-" }}
                  </span>
                </div>
                <div class="meta-row">
                  <span class="meta-label">공포일자</span>
                  <span class="meta-value">
                    {{
                      item.proclamation_date
                        ? formatYmd(item.proclamation_date)
                        : "-"
                    }}
                  </span>
                </div>
              </div>

              <!-- 오른쪽: 내용요약 -->
              <div class="law-card-right">
                <div class="summary-label">변경내용 요약</div>
                <div v-if="item.change_summary" class="summary-text">
                  {{ item.change_summary }}
                </div>
                <div v-else class="summary-text summary-text--empty">
                  변경 내역 요약이 없습니다.
                </div>
              </div>
            </div>
          </n-card>
        </div>

        <!-- 결과 없음 -->
        <div v-else class="empty-wrap">
          <n-empty description="검색 결과가 없습니다." :show-icon="false" />
        </div>
      </n-spin>
    </div>

    <!-- 페이지네이션 -->
    <div v-if="total > 0" class="pagination-row">
      <div class="pagination-info">
        Showing {{ startIndex }}-{{ endIndex }} of {{ total }}
      </div>
      <n-pagination
        v-model:page="page"
        :page-size="pageSize"
        :item-count="total"
        @update:page="onPageChange"
      />
    </div>
  </div>
  <!-- 상세 모달 -->
  <LawChangeDetailModal
    v-model:show="detailVisible"
    :change-id="selectedChangeId"
    :initial-law="selected"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import dayjs from "dayjs";
import type { LawChangeEvent } from "@/types/law";
import { fetchLawChanges } from "@/api/lawChange";
import LawChangeDetailModal from "@/components/law/LawChangeDetailModal.vue";

const items = ref<LawChangeEvent[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 8;

const loading = ref(false);

const detailVisible = ref(false);
const selected = ref<LawChangeEvent | null>(null);
const selectedChangeId = ref<string | null>(null);

// 🔹 기본 날짜: 오늘 ~ 7일 전
const today = dayjs();
const defaultStart = today.subtract(7, "day").valueOf(); // 7일 전
const defaultEnd = today.valueOf(); // 오늘

const filter = ref({
  keyword: "",
  date_basis: "promulgation" as "promulgation" | "enforcement" | "collected",
  start_date: defaultStart as number | null,
  end_date: defaultEnd as number | null,
});

const dateBasisOptions = [
  { label: "공포일자 기준", value: "promulgation" },
  { label: "시행일자 기준", value: "enforcement" },
  { label: "변경일자 기준", value: "collected" },
];

const startIndex = computed(() =>
  total.value === 0 ? 0 : (page.value - 1) * pageSize + 1
);
const endIndex = computed(() => Math.min(page.value * pageSize, total.value));

function formatYmd(value: string | number | Date) {
  return dayjs(value).format("YYYY.MM.DD");
}

function changeTypeTagType(changeType: string) {
  switch (changeType) {
    case "전부개정":
      return "primary";
    case "일부개정":
      return "success";
    case "타법개정":
      return "warning";
    case "일부폐지":
      return "error";
    default:
      return "info";
  }
}

/** 실제 API 호출 */
async function loadData() {
  loading.value = true;
  try {
    const params = {
      page: page.value,
      page_size: pageSize,
      keyword: filter.value.keyword || null,
      date_basis: filter.value.date_basis,
      start_date: filter.value.start_date
        ? dayjs(filter.value.start_date).format("YYYY-MM-DD")
        : null,
      end_date: filter.value.end_date
        ? dayjs(filter.value.end_date).format("YYYY-MM-DD")
        : null,
      change_type: null as string | null,
    };

    const resp = await fetchLawChanges(params);
    total.value = resp.total;
    items.value = resp.items;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  page.value = 1;
  loadData();
}

function onPageChange(p: number) {
  page.value = p;
  loadData();
}

function handleCardClick(row: LawChangeEvent) {
  selected.value = row;
  selectedChangeId.value = row.change_id;
  detailVisible.value = true;
}

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  margin-bottom: 4px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

/* 검색바 영역 */
.filter-card {
  border-radius: 10px;
}

.filter-row {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 1.5fr) minmax(0, 2.2fr) auto;
  gap: 12px;
  align-items: center;
}

.filter-search,
.filter-basis {
  width: 100%;
}

.filter-dates {
  display: flex;
  align-items: center;
  gap: 6px;
}

.date-picker {
  flex: 1;
}

.date-separator {
  font-size: 14px;
  opacity: 0.7;
}

.filter-button {
  padding: 0 24px;
}

/* 리스트 영역 */
.list-section {
  margin-top: 4px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.law-card {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
  cursor: pointer;
}

/* 카드 내부 레이아웃 (좌: 기본정보 / 우: 요약) */
.law-card-main {
  display: flex;
  gap: 24px;
}

/* 왼쪽: 법령 기본정보 */
.law-card-left {
  flex: 0 0 55%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.law-card-header {
  display: flex;
  align-items: center; /* 👉 같은 높이로 정렬 */
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  white-space: nowrap; /* 👉 줄바꿈 방지 */
}

.law-title {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap; /* 👉 줄바꿈 방지 */
  flex: 1 1 auto; /* 👉 남은 공간 모두 차지 */
}

.badge-row {
  display: flex;
  flex-direction: row; /* 🔥 기존 column → row */
  align-items: center;
  gap: 6px; /* 뱃지 사이 간격 */
  flex-shrink: 0; /* 👉 작아지지 않음 */
}

/* 공포번호 / 공포일자 */
.meta-row {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.meta-label {
  opacity: 0.7;
  min-width: 60px;
}

.meta-value {
  font-weight: 500;
}

/* 오른쪽: 내용요약 */
.law-card-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

.summary-label {
  font-weight: 600;
  opacity: 0.75;
}

.summary-text {
  line-height: 1.5;
  line-clamp: 3;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.summary-text--empty {
  opacity: 0.5;
}

.empty-wrap {
  padding: 40px 0;
}

/* 페이지네이션 */
.pagination-row {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  opacity: 0.8;
}

/* 반응형 */
@media (max-width: 1100px) {
  .filter-row {
    grid-template-columns: minmax(0, 1fr);
  }

  .card-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .law-card-main {
    flex-direction: column;
  }

  .law-card-left {
    flex: 1;
  }
}
</style>
