<!-- src/views/AdminRuleList.vue -->
<template>
  <div class="page">
    <!-- 타이틀 -->
    <div class="page-header">
      <h1 class="page-title">행정규칙 목록</h1>
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
          size="large"
          placeholder="행정규칙명을 입력하세요."
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <n-icon :component="Search" />
          </template>
        </n-input>

        <!-- 카테고리 -->
        <n-select
          v-model:value="filter.category"
          class="filter-category"
          size="large"
          :options="categoryOptions"
          placeholder="카테고리 전체"
          clearable
        />

        <!-- 기준일자 -->
        <n-select
          v-model:value="filter.date_basis"
          :options="dateBasisOptions"
          size="large"
          class="filter-basis"
        />

        <!-- 시작일 ~ 종료일 -->
        <div class="filter-dates">
          <n-date-picker
            v-model:value="filter.start_date"
            class="date-picker"
            type="date"
            size="large"
            clearable
            placeholder="시작일"
          />
          <span class="date-separator">-</span>
          <n-date-picker
            v-model:value="filter.end_date"
            class="date-picker"
            type="date"
            size="large"
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

    <div class="page-body">
      <!-- 📋 행정규칙 카드 리스트 -->
      <div class="list-section">
        <n-spin :show="loading">
          <div v-if="items.length" class="card-grid">
            <n-card
              v-for="item in items"
              :key="item.admrul_sn"
              class="rule-card"
              :bordered="true"
              hoverable
            >
              <!-- 🔹 상단 헤더: 종류 뱃지 + 번호 -->
              <div class="rule-header">
                <div class="rule-type-wrap" v-if="item.admrul_type_name">
                  <n-tag class="type-tag" size="small" type="info" round>
                    {{ item.admrul_type_name }}
                  </n-tag>
                </div>

                <!-- 제2024-123호 처럼 오른쪽 상단 번호 -->
                <div class="rule-no" v-if="item.issue_number">
                  제{{ item.issue_number }}호
                </div>
              </div>

              <!-- 제목 -->
              <div class="rule-title">
                {{ item.admrul_name }}
              </div>

              <!-- 카테고리 태그 -->
              <div class="rule-tags-row">
                <n-tag
                  v-if="item.category"
                  size="small"
                  :type="categoryTagType(item.category)"
                >
                  {{ categoryLabel(item.category) }}
                </n-tag>
              </div>

              <!-- 👇 중간 구분선 추가 -->
              <div class="rule-divider"></div>

              <!-- 메타 정보 -->
              <div class="rule-meta">
                <div class="rule-meta-row">
                  <span class="rule-meta-label">소관부처:</span>
                  <span class="rule-meta-value">
                    {{ item.ministry_names ? item.ministry_names : "-" }}
                  </span>
                </div>
                <div class="rule-meta-row">
                  <span class="rule-meta-label">발령일자:</span>
                  <span class="rule-meta-value">
                    {{ item.issue_date ? formatYmd(item.issue_date) : "-" }}
                  </span>
                </div>
                <div class="rule-meta-row">
                  <span class="rule-meta-label">시행일자:</span>
                  <span class="rule-meta-value">
                    {{ item.enforce_date ? formatYmd(item.enforce_date) : "-" }}
                  </span>
                </div>
              </div>

              <!-- 하단 버튼 -->
              <div class="rule-footer">
                <n-button
                  size="small"
                  type="primary"
                  block
                  class="rule-detail-btn"
                  @click.stop="handleCardClick(item)"
                >
                  <template #icon>
                    <span class="material-symbols-outlined open-icon">
                      open_in_new
                    </span>
                  </template>
                  본문 보기
                </n-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import dayjs from "dayjs";

import { Search } from "@vicons/tabler";
import type { AdminRuleListItem, AdminRuleCategory } from "@/types/adminRule";
import { fetchAdminRules } from "@/api/adminRule";

const items = ref<AdminRuleListItem[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 6;

const loading = ref(false);

// 🔹 기본 날짜: 오늘 ~ 7일 전 (발령일자 기준)
const today = dayjs();
const defaultStart = today.subtract(7, "day").valueOf();
const defaultEnd = today.valueOf();

// 검색 필터 상태
const filter = ref({
  keyword: "",
  category: null as AdminRuleCategory | null,
  date_basis: "issue" as "issue" | "enforce" | "created",
  start_date: defaultStart as number | null,
  end_date: defaultEnd as number | null,
});

const categoryOptions = [
  { label: "전체", value: null },
  { label: "화학물질", value: "CHEMICAL" },
  { label: "설비·공정 안전(PSM)", value: "PSM" },
  { label: "위험물", value: "DANGER" },
  { label: "환경(대기·수질·폐기물)", value: "ENV" },
  { label: "보건·작업환경", value: "HEALTH" },
  { label: "소방·비상대응", value: "FIRE" },
  { label: "기타", value: "ETC" },
];

const dateBasisOptions = [
  { label: "발령일자 기준", value: "issue" },
  { label: "시행일자 기준", value: "enforce" },
  { label: "생성일자 기준", value: "created" },
];

const startIndex = computed(() =>
  total.value === 0 ? 0 : (page.value - 1) * pageSize + 1
);
const endIndex = computed(() => Math.min(page.value * pageSize, total.value));

function formatYmd(value?: string | number | Date | null) {
  if (!value) return "-";
  return dayjs(value).format("YYYY.MM.DD");
}

function categoryLabel(cat: AdminRuleCategory): string {
  switch (cat) {
    case "CHEMICAL":
      return "#화학물질";
    case "PSM":
      return "#설비·공정 안전";
    case "DANGER":
      return "#위험물";
    case "ENV":
      return "#환경";
    case "HEALTH":
      return "#보건·작업환경";
    case "FIRE":
      return "#소방·비상대응";
    case "ETC":
    default:
      return "#기타";
  }
}

function categoryTagType(cat: AdminRuleCategory) {
  switch (cat) {
    case "CHEMICAL":
      return "success";
    case "PSM":
      return "warning";
    case "DANGER":
      return "error";
    case "ENV":
      return "info";
    case "HEALTH":
      return "primary";
    case "FIRE":
      return "error";
    case "ETC":
    default:
      return "default";
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
      category: filter.value.category || null,
      date_basis: filter.value.date_basis,
      start_date: filter.value.start_date
        ? dayjs(filter.value.start_date).format("YYYY-MM-DD")
        : null,
      end_date: filter.value.end_date
        ? dayjs(filter.value.end_date).format("YYYY-MM-DD")
        : null,
    };

    const resp = await fetchAdminRules(params);
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

function handleCardClick(row: AdminRuleListItem) {
  if (!row.detail_link_path) return;

  const baseUrl = import.meta.env.VITE_API_BASE_URL;
  const url = `${baseUrl}${row.detail_link_path}`;
  window.open(url, "_blank");
}

onMounted(loadData);
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: calc(100vh - 110px);
}

.page-header {
  margin-bottom: 4px;
}

.page-body {
  flex: 1;
  display: flex;
  flex-direction: column;
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
  grid-template-columns:
    minmax(0, 2.5fr) minmax(0, 1.5fr) minmax(0, 1.5fr)
    minmax(0, 2.2fr) auto;
  gap: 12px;
  align-items: center;
}

.filter-search,
.filter-basis,
.filter-category {
  width: 100%;
}

.filter-row :deep(.n-input),
.filter-row :deep(.n-base-selection) {
  border-radius: 6px;
}

.filter-card :deep(.n-card__content) {
  border-radius: 10px;
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
  flex: 1;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

/* 카드 스타일 (이미지 스타일 반영) */
.rule-card {
  border-radius: 12px;
  cursor: default;
}

/* Naive UI 카드 content padding 조정 */
.rule-card :deep(.n-card__content) {
  padding: 18px 18px 16px;
}

/* 🔹 상단 헤더 (종류 + 번호) */
.rule-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

/* 제목 */
.rule-title {
  font-size: 15px;
  font-weight: 700;
  line-height: 1.4;
  margin-bottom: 14px;
}

/* 카테고리 태그 */
.rule-tags-row {
  display: flex;
  gap: 6px;
}

/* 🔹 중간 구분선 */
.rule-divider {
  border-top: 1px solid rgba(148, 163, 184, 0.35);
  margin: 16px 0;
}

/* 메타 정보 */
.rule-meta {
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 14px;
}

.rule-meta-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.rule-meta-label {
  opacity: 0.7;
  min-width: 72px;
}

.rule-meta-value {
  font-weight: 500;
  text-align: right;
}

/* 하단 버튼 */
.rule-footer {
  margin-top: 4px;
}

.rule-detail-btn {
  border-radius: 8px;
  padding: 20px 0px;
}

/* 결과 없음 */
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

.open-icon {
  font-size: 16px;
  margin-right: 4px;
  vertical-align: middle;
}

.type-tag {
  padding: 10px;
}

/* 반응형 */
@media (max-width: 1200px) {
  .card-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .filter-row {
    grid-template-columns: minmax(0, 1fr);
  }

  .card-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>

<style>
/* 🌙 다크 모드용 */
.theme-dark .filter-card .n-card__content {
  background-color: #020617 !important;
  border: 0.5px solid #1f2937;
}

/* ☀️ 라이트 모드용 */
.theme-light .filter-card .n-card__content {
  background-color: #ffffff !important;
}

/* ☀️ 라이트 모드용 */
.theme-light .n-input-wrapper,
.theme-light .n-base-selection-label {
  background-color: #f3f4f6 !important;
}
</style>
