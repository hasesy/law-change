// src/main.ts
import { createApp } from "vue";
import App from "./App.vue";
import { createRouter, createWebHistory } from "vue-router";
import routes from "./router";
import { createNaiveUi } from "./naive-ui";
import "./style.css";

const app = createApp(App);
const router = createRouter({
  history: createWebHistory(),
  routes,
});

app.use(router);
app.use(createNaiveUi());
app.mount("#app");
