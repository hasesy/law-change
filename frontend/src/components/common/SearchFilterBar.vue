<template>
  <n-card
    class="filter-card"
    :bordered="true"
    :content-style="{ padding: '14px 14px' }"
  >
    <div class="filter-row">
      <!-- 검색어 -->
      <n-input
        v-model:value="keywordModel"
        class="filter-search"
        size="large"
        :placeholder="keywordPlaceholder"
        clearable
        @keyup.enter="onSearch"
      >
        <template #prefix>
          <n-icon :component="Search" />
        </template>
      </n-input>

      <!-- 기준일자 (옵션은 부모에서 받기) -->
      <n-select
        v-model:value="dateBasisModel"
        :options="dateBasisOptions"
        size="large"
        class="filter-basis"
      />

      <!-- 시작일 ~ 종료일 -->
      <div class="filter-dates">
        <n-date-picker
          v-model:value="startDateModel"
          class="date-picker"
          type="date"
          size="large"
          clearable
          placeholder="시작일"
        />
        <span class="date-separator">-</span>
        <n-date-picker
          v-model:value="endDateModel"
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
        @click="onSearch"
      >
        검색
      </n-button>
    </div>

    <!-- ⬇️ 카테고리 칩 + 오른쪽 추가 필터 -->
    <div class="category-row">
      <!-- 왼쪽: 카테고리 칩 -->
      <div class="category-chip-group">
        <n-tag
          v-for="opt in categoryOptions"
          :key="opt.value"
          class="category-chip"
          checkable
          round
          :checked="categoriesModel.includes(opt.value)"
          :type="categoriesModel.includes(opt.value) ? 'primary' : 'default'"
          @click="toggleCategory(opt.value as AdminRuleCategory)"
        >
          {{ opt.label }}
        </n-tag>
      </div>
      <!-- 오른쪽: 외부에서 받은 추가 필터들 -->
      <div
        v-if="extraFilters && extraFilters.length"
        class="extra-filter-inline"
      >
        <div v-for="f in extraFilters" :key="f.key" class="extra-filter-item">
          <n-select
            class="extra-filter-select"
            :style="{ width: calcSelectWidth(f.label) }"
            size="small"
            :options="f.options"
            :value="extraValuesComputed[f.key] ?? null"
            :placeholder="f.label"
            clearable
            @update:value="(val: string) => onExtraFilterChange(f.key, val)"
          />
        </div>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Search } from "@vicons/tabler";
import type { AdminRuleCategory } from "@/types/adminRule";

type DateBasis = string; // 각 화면에서 다른 union 타입을 쓰므로 여기서는 string으로 통일

interface ExtraFilterOption {
  label: string;
  value: string | null;
}

export interface ExtraFilterConfig {
  key: string; // ex) "importance", "current_hist_cd"
  label: string; // ex) "중요도"
  options: ExtraFilterOption[];
}

const props = defineProps<{
  keyword: string;
  categories: AdminRuleCategory[];
  dateBasis: DateBasis;
  startDate: number | null;
  endDate: number | null;
  dateBasisOptions: { label: string; value: DateBasis }[];
  keywordPlaceholder?: string;
  extraFilters?: ExtraFilterConfig[];
  extraFilterValues?: Record<string, string | null>;
}>();

const emit = defineEmits<{
  (e: "update:keyword", value: string): void;
  (e: "update:categories", value: AdminRuleCategory[]): void;
  (e: "update:dateBasis", value: DateBasis): void;
  (e: "update:startDate", value: number | null): void;
  (e: "update:endDate", value: number | null): void;
  (e: "update:extraFilterValues", value: Record<string, string | null>): void;
  (e: "search"): void;
}>();

// 공통 카테고리 옵션은 컴포넌트 내부에서 정의
const categoryOptions: { label: string; value: AdminRuleCategory }[] = [
  { label: "화학물질", value: "CHEMICAL" },
  { label: "설비·공정 안전(PSM)", value: "PSM" },
  { label: "위험물", value: "DANGER" },
  { label: "환경", value: "ENV" },
  { label: "보건·작업환경", value: "HEALTH" },
  { label: "소방·비상대응", value: "FIRE" },
  { label: "기타", value: "ETC" },
];

// v-model 브리지용 computed
const keywordModel = computed({
  get: () => props.keyword,
  set: (val: string) => emit("update:keyword", val),
});

// 카테고리 멀티 v-model
const categoriesModel = computed<AdminRuleCategory[]>({
  get: () => props.categories ?? [],
  set: (val) => emit("update:categories", val),
});

const dateBasisModel = computed({
  get: () => props.dateBasis,
  set: (val: DateBasis) => emit("update:dateBasis", val),
});

const startDateModel = computed({
  get: () => props.startDate,
  set: (val: number | null) => emit("update:startDate", val),
});

const endDateModel = computed({
  get: () => props.endDate,
  set: (val: number | null) => emit("update:endDate", val),
});

const keywordPlaceholder = computed(
  () => props.keywordPlaceholder || "검색어를 입력하세요."
);

const extraValuesComputed = computed<Record<string, string | null>>({
  get: () => props.extraFilterValues ?? {},
  set: (val) => emit("update:extraFilterValues", val),
});

const extraFilters = computed(() => props.extraFilters ?? []);

function onSearch() {
  emit("search");
}

// 🔥 카테고리 뱃지 토글 (멀티 선택)
function toggleCategory(value: AdminRuleCategory) {
  const current = [...categoriesModel.value];
  const idx = current.indexOf(value);
  if (idx >= 0) {
    current.splice(idx, 1); // 이미 있으면 제거
  } else {
    current.push(value); // 없으면 추가
  }
  categoriesModel.value = current;
  emit("search"); // 선택 즉시 검색
}

// 🔥 추가 필터는 선택하는 순간 바로 검색 실행
function onExtraFilterChange(key: string, value: string | null) {
  const next = { ...extraValuesComputed.value, [key]: value };
  extraValuesComputed.value = next;
  emit("search");
}

// 🔢 글자 수 기반 width 계산 (placeholder 기준)
// 대략 글자당 12px + 좌우 패딩 40px, 최소 60px 정도로 잡자
function calcSelectWidth(label: string): string {
  const len = label ? label.length : 0;
  const px = Math.max(60, len * 16 + 60);
  return `${px}px`;
}
</script>

<style scoped>
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

.filter-row :deep(.n-input),
.filter-row :deep(.n-base-selection) {
  border-radius: 6px;
}

.filter-card :deep(.n-card__content) {
  border-radius: 10px;
}

/* 🔹 카테고리 뱃지 영역 */
.category-row {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap; /* 좁아지면 자동 줄바꿈 */
}

/* 왼쪽 칩 그룹 */
.category-chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1; /* 나머지 공간 차지해서 오른쪽 필터를 끝으로 밀어냄 */
}

.category-chip {
  cursor: pointer;
  font-size: 12px;
  padding: 0 10px;
}

/* 오른쪽 추가 필터 그룹 */
.extra-filter-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
  flex-shrink: 0; /* 너무 줄어들지 않도록 */
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

/* 🔽 아래 필터 영역 */
.extra-filter-row {
  margin-top: 10px;
}

.extra-filter-inner {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.extra-filter-item :deep(.n-base-selection-label),
.extra-filter-item :deep(.n-base-selection) {
  border-radius: 8px;
}

/* 반응형: 좁을 때는 줄바꿈 */
@media (max-width: 900px) {
  .filter-row {
    grid-template-columns: minmax(0, 1fr);
  }

  .extra-filter-inner {
    border-radius: 16px;
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
  border-radius: 6px;
}

.theme-light .category-chip {
  border: 1px solid rgb(194, 194, 194, 0.5);
}

.theme-dark .category-chip {
  border: 1px solid #1f2937;
}

.theme-light .n-base-selection-placeholder__inner {
  color: #505458;
}

.theme-dark .n-base-selection-placeholder__inner {
  color: rgb(229, 231, 235, 0.8);
}
</style>
