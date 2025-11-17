<template>
  <n-modal
    v-model:show="innerShow"
    preset="card"
    to="body"
    :mask-closable="false"
    :auto-focus="false"
    :style="{ width: '1280px', maxWidth: '1280px' }"
    class="law-change-detail-modal"
  >
    <!-- 헤더 영역 -->
    <template #header>
      <div class="modal-header">
        <div class="modal-title-wrap">
          <h2 class="modal-title">
            {{
              detail?.change.law_name || initialLaw?.law_name || "변경이력 상세"
            }}
          </h2>
          <n-tag
            v-if="detail?.change.law_type_name"
            size="small"
            type="info"
            round
          >
            {{ detail.change.law_type_name }}
          </n-tag>
        </div>
      </div>
    </template>

    <template v-if="detail">
      <!-- 상단 요약 영역 -->
      <div class="summary-section">
        <div class="summary-card">
          <div class="summary-card-title">변경 내역에 대한 요약</div>
          <div class="summary-card-body">
            <p v-if="detail.change.change_summary">
              {{ detail.change.change_summary }}
            </p>
            <p v-else class="summary-empty">
              변경 내역 요약이 등록되어 있지 않습니다.
            </p>
          </div>
        </div>

        <div class="summary-card">
          <div class="summary-card-title">조치사항</div>
          <div class="summary-card-body">
            <p v-if="detail.change.action_recommendation">
              {{ detail.change.action_recommendation }}
            </p>
            <p v-else class="summary-empty">
              조치사항이 아직 등록되지 않았습니다.
            </p>
          </div>
        </div>
      </div>

      <!-- 개정 전 / 개정 후 기본 정보 -->
      <div class="basic-section">
        <!-- 개정 전 -->
        <div class="basic-col">
          <div class="basic-title">개정 전</div>
          <div class="basic-meta-grid">
            <div class="basic-row">
              <div class="basic-field">
                <span class="meta-label">시행일자</span>
                <span class="meta-value">
                  {{ basicValue(detail.old_basic, "시행일자") || "-" }}
                </span>
              </div>
              <div class="basic-field">
                <span class="meta-label">공포번호</span>
                <span class="meta-value">
                  {{
                    basicValue(detail.old_basic, "공포번호") ||
                    detail.change.proclamation_no ||
                    "-"
                  }}
                </span>
              </div>
            </div>
            <div class="basic-row">
              <div class="basic-field">
                <span class="meta-label">공포일자</span>
                <span class="meta-value">
                  {{ basicValue(detail.old_basic, "공포일자") || "-" }}
                </span>
              </div>
              <div class="basic-field">
                <span class="meta-label">제개정구분</span>
                <span class="meta-value">
                  {{
                    basicValue(detail.old_basic, "제개정구분") ||
                    detail.change.change_type ||
                    "-"
                  }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 개정 후 -->
        <div class="basic-col">
          <div class="basic-title">개정 후</div>
          <div class="basic-meta-grid">
            <div class="basic-row">
              <div class="basic-field">
                <span class="meta-label">시행일자</span>
                <span class="meta-value">
                  {{
                    detail.change.enforce_date
                      ? formatYmd(detail.change.enforce_date)
                      : "-"
                  }}
                </span>
              </div>
              <div class="basic-field">
                <span class="meta-label">공포번호</span>
                <span class="meta-value">
                  {{ detail.change.proclamation_no || "-" }}
                </span>
              </div>
            </div>
            <div class="basic-row">
              <div class="basic-field">
                <span class="meta-label">공포일자</span>
                <span class="meta-value">
                  {{
                    detail.change.proclamation_date
                      ? formatYmd(detail.change.proclamation_date)
                      : "-"
                  }}
                </span>
              </div>
              <div class="basic-field">
                <span class="meta-label">제개정구분</span>
                <span class="meta-value">
                  {{ detail.change.change_type || "-" }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 조문 비교 영역 -->
      <n-scrollbar
        class="article-scroll"
        style="max-height: 420px"
        :x-scrollable="false"
      >
        <div class="article-section">
          <div
            v-for="article in detail.articles"
            :key="article.diff_id"
            class="article-row"
          >
            <!-- 개정 전 -->
            <div class="article-col article-col--old">
              <div
                v-if="article.old_content"
                class="article-body"
                v-html="article.old_content"
              />
              <div v-else class="article-body article-body-empty">
                개정 전 조문 정보가 없습니다.
              </div>
            </div>

            <!-- 개정 후 -->
            <div class="article-col article-col--new">
              <div
                v-if="article.new_content"
                class="article-body"
                v-html="article.new_content"
              />
              <div v-else class="article-body article-body-empty">
                개정 후 조문 정보가 없습니다.
              </div>
            </div>
          </div>

          <div v-if="!detail.articles.length" class="article-empty-wrap">
            <n-empty
              description="조문 비교 내역이 없습니다."
              :show-icon="false"
            />
          </div>
        </div>
      </n-scrollbar>
    </template>

    <template v-else>
      <div class="article-empty-wrap">
        <n-empty
          description="상세 정보를 불러오지 못했습니다."
          :show-icon="false"
        />
      </div>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed } from "vue";
import dayjs from "dayjs";
import type { LawChangeDetailResponse, LawChangeEvent } from "@/types/law";

// 부모에서 내려오는 props
const props = defineProps<{
  show: boolean;
  detailData: LawChangeDetailResponse | null;
  initialLaw?: LawChangeEvent | null;
}>();

const emit = defineEmits<{ (e: "update:show", v: boolean): void }>();

// v-model:show 래핑
const innerShow = computed({
  get: () => props.show,
  set: (v: boolean) => emit("update:show", v),
});

// detailData 바로 사용
const detail = computed(() => props.detailData);

function formatYmd(value?: string | null) {
  if (!value) return "";
  return dayjs(value).format("YYYY.MM.DD");
}

function basicValue(obj: any, key: string) {
  if (!obj) return "-";
  return obj[key] || "-";
}
</script>

<style scoped>
/* ───────────────────────────
  공통 레이아웃 / 폰트 (테마 무관)
─────────────────────────── */

/* 헤더 */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.modal-title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 상단 요약 두 카드 */
.summary-section {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card {
  border-radius: 12px;
  padding: 16px 18px;
  transition: background-color 0.2s ease, border-color 0.2s ease;
  min-height: 140px;
}

.summary-card-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
}

.summary-card-body {
  font-size: 13px;
  line-height: 1.6;
}

.summary-empty {
  opacity: 0.7;
}

/* 개정 전/후 기본 정보 */
.basic-section {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 32px;
  margin-bottom: 6px;
}

.basic-col {
  padding: 4px 2px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.35);
  padding-bottom: 10px;
}

.basic-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 10px;
  opacity: 0.9;
}

.basic-meta-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.basic-row {
  display: flex;
  justify-content: space-between;
  gap: 48px;
}

.basic-field {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.meta-label {
  opacity: 0.7;
  min-width: 70px;
}

.meta-value {
  font-weight: 500;
}

/* 조문 비교 영역 */
.article-scroll {
  margin-top: 4px;
  border-top: 1px solid rgba(148, 163, 184, 0.3);
  padding-top: 12px;
}

.article-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  padding: 12px 0;
}

.article-row + .article-row {
  border-top: 1px dashed rgba(148, 163, 184, 0.35);
}

.article-col {
  font-size: 13px;
  border-radius: 12px;
  padding: 6px 12px;
}

.article-body {
  line-height: 1.6;
  word-break: keep-all;
}

.article-body-empty {
  opacity: 0.6;
}

.article-empty-wrap {
  padding: 40px 0 20px;
  text-align: center;
}

/* mark 강조 유지 */
.article-body :deep(mark) {
  padding: 0 2px;
  border-radius: 3px;
}

/* 반응형: 좁은 화면에서는 1열 */
@media (max-width: 1024px) {
  .summary-section {
    grid-template-columns: minmax(0, 1fr);
  }
  .basic-section {
    grid-template-columns: minmax(0, 1fr);
  }
  .article-row {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>

<style>
/* ───────────────────────────
  모달 카드 배경 / 스크롤
─────────────────────────── */

/* 공통 높이 제한 */
.law-change-detail-modal {
  max-height: 88vh;
  overflow: hidden;
}

/* 실제 내용 영역만 스크롤 */
.law-change-detail-modal .n-card__content {
  max-height: calc(88vh - 80px); /* 헤더/패딩 제외 */
  overflow-y: auto;
}

/* 다크 테마 모달 배경 */
.theme-dark .law-change-detail-modal {
  background: #0f172a;
  border: 1px solid rgba(148, 163, 184, 0.35);
}

/* 라이트 테마 모달 배경 */
.theme-light .law-change-detail-modal {
  background: #f3f4f6; /* 너무 새하얀 느낌 방지용 회색 */
  border: 1px solid #e5e7eb;
}

/* ───────────────────────────
  요약 카드 배경 (테마별)
─────────────────────────── */

/* 다크 테마 요약 카드 */
.theme-dark .law-change-detail-modal .summary-card {
  background: rgba(33, 41, 58, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.4);
}

/* 라이트 테마 요약 카드 */
.theme-light .law-change-detail-modal .summary-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

/* ───────────────────────────
  조문 하이라이트 색상
─────────────────────────── */

/* 다크 테마 - 개정 전(빨강) */
.theme-dark .law-change-detail-modal .article-col--old p,
.theme-dark .law-change-detail-modal .article-col--old span,
.theme-dark .law-change-detail-modal .article-col--old mark,
.theme-dark .law-change-detail-modal .article-col--old strong,
.theme-dark .law-change-detail-modal .article-col--old font {
  display: inline;
  margin: 0;
  color: #fecaca;
  font-weight: 500;
  background: rgba(239, 68, 68, 0.3);
  padding: 2px 4px;
  border-radius: 4px;
}

/* 다크 테마 - 개정 후(파랑) */
.theme-dark .law-change-detail-modal .article-col--new p,
.theme-dark .law-change-detail-modal .article-col--new span,
.theme-dark .law-change-detail-modal .article-col--new mark,
.theme-dark .law-change-detail-modal .article-col--new strong,
.theme-dark .law-change-detail-modal .article-col--new font {
  display: inline;
  margin: 0;
  color: #bfdbfe;
  font-weight: 500;
  background: rgba(59, 130, 246, 0.25);
  padding: 2px 4px;
  border-radius: 4px;
}

/* 라이트 테마 - 개정 전(진한 빨강) */
.theme-light .law-change-detail-modal .article-col--old p,
.theme-light .law-change-detail-modal .article-col--old span,
.theme-light .law-change-detail-modal .article-col--old mark,
.theme-light .law-change-detail-modal .article-col--old strong,
.theme-light .law-change-detail-modal .article-col--old font {
  display: inline;
  margin: 0;
  color: #d63232 !important;
  font-weight: 600;
  background: rgba(248, 113, 113, 0.18);
  padding: 2px 4px;
  border-radius: 4px;
}

/* 라이트 테마 - 개정 후(진한 파랑) */
.theme-light .law-change-detail-modal .article-col--new p,
.theme-light .law-change-detail-modal .article-col--new span,
.theme-light .law-change-detail-modal .article-col--new mark,
.theme-light .law-change-detail-modal .article-col--new strong,
.theme-light .law-change-detail-modal .article-col--new font {
  display: inline;
  margin: 0;
  color: #1d4ed8 !important;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.16);
  padding: 2px 4px;
  border-radius: 4px;
}
</style>
