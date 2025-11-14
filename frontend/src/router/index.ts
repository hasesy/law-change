// src/router/index.ts
import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import LawChangeList from "../views/LawChangeList.vue";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    redirect: "/dashboard", // 기본 진입은 대시보드로
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
  },
  {
    path: "/law-changes",
    name: "LawChangeList",
    component: LawChangeList,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
