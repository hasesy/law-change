<!-- src/views/AdminRuleList.vue -->
<template>
  <div class="page">
    <!-- 타이틀 -->
    <div class="page-header">
      <h1 class="page-title">행정규칙 목록</h1>
    </div>

    <!-- 🔍 검색 바 영역 -->
    <SearchFilterBar
      v-model:keyword="filter.keyword"
      v-model:categories="filter.categories"
      v-model:date-basis="filter.date_basis"
      v-model:start-date="filter.start_date"
      v-model:end-date="filter.end_date"
      :date-basis-options="dateBasisOptions"
      keyword-placeholder="행정규칙명을 입력하세요."
      @search="handleSearch"
    />

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
              @click="handleCardClick(item)"
            >
              <!-- ✅ 카드 오른쪽 상단 중요도 -->
              <div
                class="importance-wrap"
                v-if="item.ai_importance && item.ai_importance !== 'NONE'"
              >
                <div
                  class="importance-chip"
                  :class="`importance-${item.ai_importance.toLowerCase()}`"
                >
                  <span class="importance-dot" />
                  <span class="importance-text">
                    {{ item.ai_importance }}
                  </span>
                </div>
              </div>

              <div class="rule-card-main">
                <!-- 왼쪽: 기본 정보 (제목 + 뱃지 + 메타) -->
                <div class="rule-card-left">
                  <div class="rule-card-header">
                    <div class="rule-title">
                      {{ item.admrul_name }}
                    </div>
                    <div class="badge-row">
                      <n-tag
                        v-if="item.current_history_type"
                        size="small"
                        :type="currentHistTagType(item.current_history_type)"
                      >
                        {{ item.current_history_type }}
                      </n-tag>
                      <n-tag
                        v-if="item.change_type_name"
                        size="small"
                        :type="changeTypeTagType(item.change_type_name)"
                      >
                        {{ item.change_type_name }}
                      </n-tag>
                    </div>
                  </div>

                  <!-- 발령번호 / 발령일자 -->
                  <div class="law-card-meta">
                    <div class="meta-row">
                      <span class="meta-label">발령번호</span>
                      <span class="meta-value">
                        {{
                          item.issue_number ? `제${item.issue_number}호` : "-"
                        }}
                      </span>
                    </div>
                    <div class="meta-row">
                      <span class="meta-label">발령일자</span>
                      <span class="meta-value">
                        {{ item.issue_date ? formatYmd(item.issue_date) : "-" }}
                      </span>
                    </div>
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
  </div>

  <!-- 상세 모달 -->
  <AdminRuleDetailModal
    v-model:show="detailVisible"
    :detail-data="detailData"
    :initial-law="selected"
  />

  <!-- ✅ 신·구법 비교 없음 안내 모달 (커스텀 스타일) -->
  <n-modal
    v-model:show="noOldNewVisible"
    preset="card"
    class="no-oldnew-modal"
    :mask-closable="false"
    :closable="false"
    :style="{ width: '420px', maxWidth: '90vw' }"
  >
    <div class="no-oldnew-inner">
      <!-- 동그란 아이콘 -->
      <div class="no-oldnew-icon-wrap">
        <div class="no-oldnew-icon">i</div>
      </div>

      <!-- 제목 -->
      <div class="no-oldnew-title">비교 정보 없음</div>

      <!-- 설명 문구 -->
      <div class="no-oldnew-desc">
        해당 변경 건에 대한 신·구법 조문 비교 내역이 없습니다.
      </div>

      <!-- 확인 버튼 -->
      <n-button
        type="primary"
        size="large"
        block
        class="no-oldnew-button"
        @click="noOldNewVisible = false"
      >
        확인
      </n-button>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import dayjs from "dayjs";

import type {
  AdminRuleListItem,
  AdminRuleCategory,
  AdminRuleChangeDetailResponse,
} from "@/types/adminRule";
import { fetchAdminRules, fetchAdminRuleDetail } from "@/api/adminRule";
import SearchFilterBar from "@/components/common/SearchFilterBar.vue";
import AdminRuleDetailModal from "@/components/AdminRuleDetailModal.vue";

const items = ref<AdminRuleListItem[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 8;

const loading = ref(false);

// 상세 모달 상태
const detailVisible = ref(false);
const detailData = ref<AdminRuleChangeDetailResponse | null>(null);
const selected = ref<AdminRuleListItem | null>(null);

// 신·구 비교 없음 모달
const noOldNewVisible = ref(false);

// 🔹 기본 날짜: 최근 6개월
const today = dayjs();
const defaultStart = today.subtract(6, "month").valueOf();
const defaultEnd = today.valueOf();

// 검색 필터 상태
const filter = ref({
  keyword: "",
  categories: [] as AdminRuleCategory[],
  date_basis: "issue" as "issue" | "enforce" | "created",
  start_date: defaultStart as number | null,
  end_date: defaultEnd as number | null,
});

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

function changeTypeTagType(changeType: string) {
  switch (changeType) {
    case "제정":
      return "primary";
    case "일부개정":
      return "success";
    case "타법개정":
      return "warning";
    case "전부개정":
      return "error";
    default:
      return "info";
  }
}

function currentHistTagType(value: string) {
  switch (value) {
    case "현행":
      return "info";
    case "연혁":
      return "default";
    default:
      return "info";
  }
}

/** 목록 API */
async function loadData() {
  loading.value = true;
  try {
    const params = {
      page: page.value,
      page_size: pageSize,
      keyword: filter.value.keyword || null,
      categories: filter.value.categories.length
        ? filter.value.categories
        : undefined,
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
    console.log(items.value);
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

async function handleCardClick(row: AdminRuleListItem) {
  selected.value = row;
  try {
    const resp = await fetchAdminRuleDetail(row.admrul_sn);

    if (resp.has_old_new === "N") {
      noOldNewVisible.value = true;
      return;
    }

    detailData.value = resp;
    detailVisible.value = true;
  } catch (e) {
    console.error(e);
  }
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

/* 리스트 영역 */
.list-section {
  margin-top: 4px;
  flex: 1;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.rule-card {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
  cursor: pointer;
  position: relative;
}

/* 카드 내부 레이아웃 (좌: 기본정보 / 우: 요약) */
.rule-card-main {
  display: flex;
  gap: 24px;
  min-height: 100px;
  max-height: 190px;
  overflow: hidden;
}

/* 왼쪽: 기본정보 */
.rule-card-left {
  flex: 0 0 55%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.rule-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
}

.rule-title {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.35;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: normal;
  flex: 1 1 auto;
  min-width: 0;
}

.badge-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

/* 카테고리 태그 줄 */
.rule-tags-row {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}

/* 메타 정보 */
.rule-card-meta {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

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

/* 오른쪽: 변경내용 요약 */
.rule-card-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-label {
  font-weight: 600;
  font-size: 14px;
}

.summary-text {
  line-height: 1.5;
  line-clamp: 3;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 13px;
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

/* 중요도 칩 (법령 화면과 동일) */
.importance-wrap {
  position: absolute;
  top: 12px;
  right: 24px;
  z-index: 1;
}

.importance-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
}

.importance-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

/* 반응형 */
@media (max-width: 1100px) {
  .card-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .rule-card-main {
    flex-direction: column;
  }

  .rule-card-left {
    flex: 1;
  }
}
</style>

<style>
/* 신·구 비교 없음 모달 스타일 (법령 화면과 동일) */
.no-oldnew-modal .n-card__content {
  padding: 28px 28px 24px;
}

.no-oldnew-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
}

.no-oldnew-icon-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 4px;
}

.no-oldnew-icon {
  width: 60px;
  height: 60px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 28px;
}

.no-oldnew-title {
  font-size: 18px;
  font-weight: 700;
}

.no-oldnew-desc {
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.9;
  margin-bottom: 4px;
  max-width: 320px;
}

.no-oldnew-button {
  margin-top: 4px;
  border-radius: 8px;
  transition: transform 0.12s ease-out, box-shadow 0.12s ease-out,
    opacity 0.12s ease-out;
}

.theme-dark .no-oldnew-icon {
  background: rgba(37, 99, 235, 0.16);
  color: #60a5fa;
}

.theme-light .no-oldnew-icon {
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
}

.theme-dark .no-oldnew-title {
  color: #e5e7eb;
}

.theme-light .no-oldnew-title {
  color: #111827;
}

.theme-dark .no-oldnew-desc {
  color: #cbd5f5;
}

.theme-light .no-oldnew-desc {
  color: #4b5563;
}
</style>
