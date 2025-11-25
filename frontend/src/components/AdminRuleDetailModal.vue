<!-- src/components/adminRule/AdminRuleDetailModal.vue -->
<template>
  <n-modal
    v-model:show="innerShow"
    preset="card"
    to="body"
    :mask-closable="false"
    :auto-focus="false"
    :style="{ width: '80%', maxWidth: '80%' }"
    class="admin-rule-detail-modal"
  >
    <!-- 헤더 영역 -->
    <template #header>
      <div class="modal-header">
        <div class="modal-title-wrap">
          <h2 class="modal-title">
            {{
              detail?.rule.admrul_name ||
              initialRule?.admrul_name ||
              "행정규칙 상세"
            }}
          </h2>
          <n-tag
            v-if="detail?.rule.admrul_type_name"
            size="small"
            type="info"
            round
          >
            {{ detail.rule.admrul_type_name }}
          </n-tag>

          <!-- ✅ 중요도 표시 (법명 옆, 태그 옆) -->
          <div
            v-if="detail?.rule.ai_importance"
            class="importance-chip header-importance-chip"
            :class="`importance-${detail?.rule.ai_importance.toLowerCase()}`"
          >
            <span class="importance-dot" />
            <span class="importance-text">
              {{ detail?.rule.ai_importance }}
            </span>
          </div>
        </div>
      </div>
    </template>

    <template v-if="detail">
      <!-- 상단 요약 영역 -->
      <div class="summary-section">
        <div class="summary-card">
          <div class="summary-card-title">변경 내역에 대한 요약</div>
          <div class="summary-card-body">
            <n-scrollbar
              v-if="detail.rule.change_summary"
              style="max-height: 140px"
              :x-scrollable="false"
            >
              <p>{{ detail.rule.change_summary }}</p>
            </n-scrollbar>
            <p v-else class="summary-empty">
              변경 내역 요약이 등록되어 있지 않습니다.
            </p>
          </div>
        </div>

        <div class="summary-card">
          <div class="summary-card-title">조치사항</div>
          <div class="summary-card-body">
            <n-scrollbar
              v-if="detail.rule.action_recommendation"
              style="max-height: 140px"
              :x-scrollable="false"
            >
              <div
                class="multiline-text"
                v-html="formatMultiline(detail.rule.action_recommendation!)"
              ></div>
            </n-scrollbar>
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
                <span class="meta-label">발령번호</span>
                <span class="meta-value">
                  {{
                    basicValue(detail.old_basic, "발령번호") ||
                    detail.rule.issue_number ||
                    "-"
                  }}
                </span>
              </div>
            </div>
            <div class="basic-row">
              <div class="basic-field">
                <span class="meta-label">발령일자</span>
                <span class="meta-value">
                  {{ basicValue(detail.old_basic, "발령일자") || "-" }}
                </span>
              </div>
              <div class="basic-field">
                <span class="meta-label">제개정구분</span>
                <span class="meta-value">
                  {{
                    basicValue(detail.old_basic, "제개정구분") ||
                    detail.rule.change_type_name ||
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
                    detail.rule.enforce_date
                      ? formatYmd(detail.rule.enforce_date)
                      : "-"
                  }}
                </span>
              </div>
              <div class="basic-field">
                <span class="meta-label">발령번호</span>
                <span class="meta-value">
                  {{ detail.rule.issue_number || "-" }}
                </span>
              </div>
            </div>
            <div class="basic-row">
              <div class="basic-field">
                <span class="meta-label">발령일자</span>
                <span class="meta-value">
                  {{
                    detail.rule.issue_date
                      ? formatYmd(detail.rule.issue_date)
                      : "-"
                  }}
                </span>
              </div>
              <div class="basic-field">
                <span class="meta-label">제개정구분</span>
                <span class="meta-value">
                  {{ detail.rule.change_type_name || "-" }}
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
import type {
  AdminRuleChangeDetailResponse,
  AdminRuleListItem,
} from "@/types/adminRule";

const props = defineProps<{
  show: boolean;
  detailData: AdminRuleChangeDetailResponse | null;
  initialRule?: AdminRuleListItem | null;
}>();

const emit = defineEmits<{ (e: "update:show", v: boolean): void }>();

const innerShow = computed({
  get: () => props.show,
  set: (v: boolean) => emit("update:show", v),
});

const detail = computed(() => props.detailData);

function formatYmd(value?: string | null) {
  if (!value) return "";
  return dayjs(value).format("YYYY.MM.DD");
}

function basicValue(obj: any, key: string) {
  if (!obj) return "-";
  return obj[key] || "-";
}

function formatMultiline(text: string) {
  if (!text) return "";
  return text.replace(/\n/g, "<br>");
}
</script>

<style scoped>
/* ───────────────────────────
  공통 레이아웃 / 폰트 (법령 모달과 동일)
─────────────────────────── */

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-importance-chip {
  margin-left: 4px;
}

.importance-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  line-height: 1;
}

.importance-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 999px;
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
}

.summary-card-body {
  font-size: 13px;
  line-height: 1.6;
}

.summary-empty {
  opacity: 0.7;
}

.multiline-text {
  padding: 12px 0;
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

.article-body :deep(mark) {
  padding: 0 2px;
  border-radius: 3px;
}

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
/* 모달 카드 배경 / 스크롤 */

.admin-rule-detail-modal {
  max-height: 88vh;
}

.admin-rule-detail-modal .n-card__content {
  max-height: none;
  overflow: visible;
}

/* 다크 테마 */
.theme-dark .admin-rule-detail-modal {
  background: #0f172a;
  border: 1px solid rgba(148, 163, 184, 0.35);
}

/* 라이트 테마 */
.theme-light .admin-rule-detail-modal {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
}

/* 요약 카드 배경 */

.theme-dark .admin-rule-detail-modal .summary-card {
  background: rgba(33, 41, 58, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.4);
}

.theme-light .admin-rule-detail-modal .summary-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

/* 조문 하이라이트 색상 - 법령 모달과 동일 */

.theme-dark .admin-rule-detail-modal .article-col--old p,
.theme-dark .admin-rule-detail-modal .article-col--old span,
.theme-dark .admin-rule-detail-modal .article-col--old mark,
.theme-dark .admin-rule-detail-modal .article-col--old strong,
.theme-dark .admin-rule-detail-modal .article-col--old font {
  display: inline;
  margin: 0;
  color: #fecaca;
  font-weight: 500;
  background: rgba(239, 68, 68, 0.3);
  padding: 2px 4px;
  border-radius: 4px;
}

.theme-dark .admin-rule-detail-modal .article-col--new p,
.theme-dark .admin-rule-detail-modal .article-col--new span,
.theme-dark .admin-rule-detail-modal .article-col--new mark,
.theme-dark .admin-rule-detail-modal .article-col--new strong,
.theme-dark .admin-rule-detail-modal .article-col--new font {
  display: inline;
  margin: 0;
  color: #bfdbfe;
  font-weight: 500;
  background: rgba(59, 130, 246, 0.25);
  padding: 2px 4px;
  border-radius: 4px;
}

.theme-light .admin-rule-detail-modal .article-col--old p,
.theme-light .admin-rule-detail-modal .article-col--old span,
.theme-light .admin-rule-detail-modal .article-col--old mark,
.theme-light .admin-rule-detail-modal .article-col--old strong,
.theme-light .admin-rule-detail-modal .article-col--old font {
  display: inline;
  margin: 0;
  color: #d63232 !important;
  font-weight: 600;
  background: rgba(248, 113, 113, 0.18);
  padding: 2px 4px;
  border-radius: 4px;
}

.theme-light .admin-rule-detail-modal .article-col--new p,
.theme-light .admin-rule-detail-modal .article-col--new span,
.theme-light .admin-rule-detail-modal .article-col--new mark,
.theme-light .admin-rule-detail-modal .article-col--new strong,
.theme-light .admin-rule-detail-modal .article-col--new font {
  display: inline;
  margin: 0;
  color: #1d4ed8 !important;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.16);
  padding: 2px 4px;
  border-radius: 4px;
}

/* 중요도 색 */

.theme-light .importance-chip.importance-low .importance-dot {
  background-color: #facc15;
}
.theme-light .importance-chip.importance-medium .importance-dot {
  background-color: #f97316;
}
.theme-light .importance-chip.importance-high .importance-dot {
  background-color: #ef4444;
}

.theme-dark .importance-chip.importance-low .importance-dot {
  background-color: #facc15;
}
.theme-dark .importance-chip.importance-medium .importance-dot {
  background-color: #fb923c;
}
.theme-dark .importance-chip.importance-high .importance-dot {
  background-color: #f87171;
}

.theme-light .importance-chip.importance-low {
  color: #92400e;
}
.theme-light .importance-chip.importance-medium {
  color: #9a3412;
}
.theme-light .importance-chip.importance-high {
  color: #b91c1c;
}

.theme-dark .importance-chip.importance-low {
  color: #facc15;
}
.theme-dark .importance-chip.importance-medium {
  color: #fdba74;
}
.theme-dark .importance-chip.importance-high {
  color: #fecaca;
}
</style>
