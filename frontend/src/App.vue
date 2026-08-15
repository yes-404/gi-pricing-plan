<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header class="border-b border-slate-200 bg-white">
      <nav class="mx-auto flex max-w-6xl items-center gap-6 px-6 py-4">
        <RouterLink
          to="/data"
          class="text-sm font-semibold tracking-tight"
        >
          GI Pricing Platform
        </RouterLink>
        <RouterLink
          to="/data"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Data
        </RouterLink>
        <RouterLink
          to="/demo"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Demo
        </RouterLink>
        <RouterLink
          to="/reference"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Reference
        </RouterLink>
      </nav>
    </header>
    <main class="mx-auto max-w-6xl px-6 py-8">
      <RouterView />
    </main>
  </div>
</template>
