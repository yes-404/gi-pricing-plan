<script setup lang="ts">
import { computed } from "vue";

import { signIn, signOut, useSessionUser } from "../auth/session";

const user = useSessionUser();
const name = computed(() => user.value?.profile.name ?? "Signed in");
</script>

<template>
  <button
    v-if="!user"
    type="button"
    class="text-sm text-slate-600 hover:text-slate-900"
    @click="signIn"
  >
    Sign in
  </button>
  <span
    v-else
    class="flex items-center gap-4"
  >
    <span class="text-sm text-slate-600">{{ name }}</span>
    <button
      type="button"
      class="text-sm text-slate-600 hover:text-slate-900"
      @click="signOut"
    >
      Sign out
    </button>
  </span>
</template>
