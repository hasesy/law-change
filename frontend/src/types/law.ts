export interface LawChangeEvent {
  change_id: string;
  law_id: string;
  law_name: string;
  law_type_name?: string | null;
  ministry_names?: string | null;
  change_type?: string | null;
  proclamation_no?: string | null;
  proclamation_date?: string | null;
  enforce_date?: string | null;
  current_hist_cd?: string | null;
  collected_date: string;
  change_summary?: string | null;
  action_recommendation?: string | null;
  ai_importance?: string | null;
}

export interface ArticleDiffItem {
  diff_id: string;
  old_no?: string | null;
  old_content?: string | null;
  new_no?: string | null;
  new_content?: string | null;
}

export interface LawChangeDetailResponse {
  change: LawChangeEvent;
  has_old_new: "Y" | "N";
  old_basic?: Record<string, any> | null;
  new_basic?: Record<string, any> | null;
  articles: ArticleDiffItem[];
}
