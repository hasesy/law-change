// src/main.ts
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createNaiveUi } from "./naive-ui";
import "./style.css";

const app = createApp(App);

app.use(router);
app.use(createNaiveUi());
app.mount("#app");
