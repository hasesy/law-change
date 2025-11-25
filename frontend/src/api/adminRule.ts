import http from "./http";
import type {
  AdminRuleListResponse,
  AdminRuleCategory,
} from "@/types/adminRule";

export interface AdminRuleListParams {
  page: number;
  page_size: number;
  keyword?: string | null;
  category?: AdminRuleCategory | null;
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
