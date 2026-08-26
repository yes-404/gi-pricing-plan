<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";

import AuthControl from "./components/AuthControl.vue";
import WorkspaceSelector from "./components/WorkspaceSelector.vue";
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
          to="/models"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Models
        </RouterLink>
        <RouterLink
          to="/objectives"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Objectives
        </RouterLink>
        <RouterLink
          to="/metrics"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Metrics
        </RouterLink>
        <RouterLink
          to="/peril-structures"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Peril structures
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
        <WorkspaceSelector />
        <AuthControl class="ml-auto" />
      </nav>
    </header>
    <main class="mx-auto max-w-6xl px-6 py-8">
      <RouterView />
    </main>
  </div>
</template>
