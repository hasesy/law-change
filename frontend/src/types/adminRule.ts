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
  category: AdminRuleCategory;
  issue_date?: string | null;
  enforce_date?: string | null;
  nlic_registered_date?: string | null;
  issue_number?: string | null;
  detail_link_path?: string | null;
}

export interface AdminRuleListResponse {
  total: number;
  items: AdminRuleListItem[];
}
