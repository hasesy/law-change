import http from "./http";
import type { DashboardResponse } from "@/types/dashboard";

export async function fetchDashboard(days: number = 7) {
  const { data } = await http.get<DashboardResponse>("/dashboard", {
    params: { days },
  });
  return data;
}
