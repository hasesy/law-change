export type AdminRuleCategory =
  | "CHEMICAL"
  | "PSM"
  | "DANGER"
  | "ENV"
  | "HEALTH"
  | "FIRE"
  | "ETC";

export interface AdminRuleListItem {
  admrul_sn: string;
  admrul_id: number;
  admrul_name: string;
  admrul_type_name?: string | null;
  ministry_names?: string | null;
  category?: AdminRuleCategory | null;
  issue_date?: string | null;
  enforce_date?: string | null;
  nlic_registered_date?: string | null;
  issue_number?: string | null;
  current_history_type?: string | null;
  change_type_name?: string | null;
  detail_link_path?: string | null;
  change_summary?: string | null;
  action_recommendation?: string | null;
  ai_importance?: string | null;
}

export interface AdminRuleListResponse {
  total: number;
  items: AdminRuleListItem[];
}

export interface AdminRuleSummary {
  admrul_sn: string;
  admrul_id: string;
  admrul_name: string;
  admrul_type_name?: string | null;
  ministry_names?: string | null;
  category?: AdminRuleCategory | null;
  change_type_name?: string | null;
  current_history_type?: string | null;
  issue_number?: string | null;
  issue_date?: string | null;
  enforce_date?: string | null;
  change_summary?: string | null;
  action_recommendation?: string | null;
  ai_importance?: string | null;
}

export interface AdminRuleArticleDiffItem {
  diff_id: string;
  old_no?: string | null;
  old_content?: string | null;
  new_no?: string | null;
  new_content?: string | null;
}

export interface AdminRuleChangeDetailResponse {
  rule: AdminRuleSummary;
  has_old_new: "Y" | "N";
  old_basic?: Record<string, any> | null;
  new_basic?: Record<string, any> | null;
  articles: AdminRuleArticleDiffItem[];
}
