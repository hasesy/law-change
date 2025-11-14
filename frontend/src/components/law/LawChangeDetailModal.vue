<template>
  <n-modal
    v-model:show="innerShow"
    preset="card"
    to="body"
    :mask-closable="false"
    :auto-focus="false"
    :style="{ width: '1280px', maxWidth: '1280px', maxHeight: '90vh' }"
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
        <!-- 오른쪽 액션 영역 제거 (다운로드 / 커스텀 닫기 버튼 삭제) -->
      </div>
    </template>

    <n-spin :show="loading" stroke-width="14">
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
    </n-spin>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, watch, ref } from "vue";
import dayjs from "dayjs";
import { fetchLawChangeDetail } from "@/api/lawChange";
import type { LawChangeEvent, LawChangeDetailResponse } from "@/types/law";

// 부모에서 내려오는 props
const props = defineProps<{
  show: boolean;
  changeId: string | null;
  initialLaw?: LawChangeEvent | null; // ✅ 리스트에서 클릭한 row
}>();

const emit = defineEmits<{
  (e: "update:show", v: boolean): void;
}>();

// v-model:show 래핑
const innerShow = computed({
  get: () => props.show,
  set: (v: boolean) => emit("update:show", v),
});

// ✅ 상세 응답 타입: LawChangeDetailResponse 사용
const detail = ref<LawChangeDetailResponse | null>(null);
const loading = ref(false);

function formatYmd(value?: string | null) {
  if (!value) return "";
  return dayjs(value).format("YYYY.MM.DD");
}

function basicValue(
  basic: Record<string, any> | null | undefined,
  key: string
): string | null {
  if (!basic) return null;
  const v = basic[key];
  return v == null ? null : String(v);
}

async function loadDetail() {
  if (!props.changeId) {
    detail.value = null;
    return;
  }
  loading.value = true;
  try {
    // ✅ 이 함수의 반환 타입도 LawChangeDetailResponse 이어야 함
    const resp = await fetchLawChangeDetail(props.changeId);
    detail.value = resp;
  } catch (e) {
    console.error(e);
    detail.value = null;
  } finally {
    loading.value = false;
  }
}

// 모달이 열릴 때마다 상세 재조회
watch(
  () => props.show,
  (show) => {
    if (show && props.changeId) {
      loadDetail();
    }
  }
);
</script>

<style scoped>
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
  background: rgba(15, 23, 42, 0.6);
  min-height: 140px; /* 🔹 기본 세로 길이 확보 */
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
  font-size: 15px; /* 🔹 글씨 조금 키움 */
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
  justify-content: space-between; /* 🔹 좌/우 균등 분배 */
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

/* 스크롤 컨테이너 */
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

/* 🔴 개정 전: <p>만 빨간색 */
.article-col--old :deep(p) {
  display: inline;
  margin: 0;
  color: #ef4444;
  font-weight: 500;
}

/* 🔵 개정 후: <p>만 파란색 */
.article-col--new :deep(p) {
  display: inline;
  margin: 0;
  color: #3b82f6;
  font-weight: 500;
}

/* mark 강조 유지 */
.article-body :deep(mark) {
  padding: 0 2px;
  border-radius: 3px;
}

@media (max-width: 1024px) {
  .article-row {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
