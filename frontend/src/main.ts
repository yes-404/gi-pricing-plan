import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import { bootstrap } from "./auth/bootstrap";
import "./assets/main.css";
import { router } from "./router";

// The session is memory-only (FR-PLAT-2): every hard reload boots anonymous and the
// provider check inside initSession restores the sign-in — a provider act, not storage,
// and exactly why the token must never reach localStorage.
await bootstrap();

createApp(App).use(createPinia()).use(router).mount("#app");
