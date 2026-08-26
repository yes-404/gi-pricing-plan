<script setup lang="ts">
import { onMounted } from "vue";

import { completeSilentRenew } from "../auth/session";

onMounted(async () => {
  await completeSilentRenew();
});
</script>

<template>
  <div />
</template>
