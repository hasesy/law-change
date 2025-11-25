import http from "./http";
import type {
  AdminRuleListResponse,
  AdminRuleChangeDetailResponse,
} from "@/types/adminRule";

export interface AdminRuleListParams {
  page: number;
  page_size: number;
  keyword?: string | null;
  categories?: string[] | null;
  date_basis: "issue" | "enforce" | "created";
  start_date?: string | null;
  end_date?: string | null;
}

export async function fetchAdminRules(
  params: AdminRuleListParams
): Promise<AdminRuleListResponse> {
  const { data } = await http.get<AdminRuleListResponse>("/admin-rules", {
    params,
  });
  return data;
}

export async function fetchAdminRuleDetail(
  admrulSn: string
): Promise<AdminRuleChangeDetailResponse> {
  const { data } = await http.get<AdminRuleChangeDetailResponse>(
    `/admin-rules/${admrulSn}`
  );
  return data;
}
