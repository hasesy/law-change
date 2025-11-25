export type Importance = "HIGH" | "MEDIUM" | "LOW" | "NONE";

export interface DashboardResponse {
  overview: {
    period: {
      start_date: string;
      end_date: string;
    };
    total_changes: number;
    need_review_count: number;
    safety_changes: number;
    chemical_changes: number;
    environment_changes: number;
  };
  domain_summary: {
    domains: {
      domain: string;
      domain_name: string;
      total_changes: number;
      laws: {
        law_id: string;
        law_name: string;
        change_count: number;
      }[];
    }[];
  };
  recent_important_changes: {
    items: {
      change_id: string;
      law_id: string;
      law_name: string;
      importance: Importance;
      change_date: string;
      summary: string | null;
      change_type: string | null;
    }[];
  };
  action_items: {
    items: {
      change_id: string;
      law_name: string;
      importance: Importance;
      action_title: string;
      action_detail: string;
    }[];
  };
}
