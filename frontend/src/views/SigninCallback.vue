<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";

import { completeRedirectIfPresent } from "../auth/session";

const router = useRouter();

onMounted(async () => {
  await completeRedirectIfPresent();
  await router.push({ name: "datasets" });
});
</script>

<template>
  <p class="text-sm text-slate-600">
    Signing in…
  </p>
</template>
