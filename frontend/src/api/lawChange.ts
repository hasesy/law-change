// src/api/lawChange.ts
import http from "./http";
import type { LawChangeEvent, LawChangeDetailResponse } from "../types/law";

export interface LawChangeQuery {
  start_date?: string | null;
  end_date?: string | null;
  keyword?: string | null;
  change_type?: string | null;
  date_basis?: "promulgation" | "enforcement" | "collected" | null;
  page?: number;
  page_size?: number;
}

export interface LawChangeListResponse {
  items: LawChangeEvent[];
  total: number;
}

export async function fetchLawChanges(
  params: LawChangeQuery
): Promise<LawChangeListResponse> {
  // http 인스턴스 baseURL이 보통 "/api/v1" 일 거라고 가정
  const { data } = await http.get<LawChangeListResponse>("/changes", {
    params,
  });
  return data;
}

export async function fetchLawChangeDetail(
  id: string
): Promise<LawChangeDetailResponse> {
  const { data } = await http.get<LawChangeDetailResponse>(`/changes/${id}`);
  return data;
}
