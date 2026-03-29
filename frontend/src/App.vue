<template>
  <RouterView v-slot="{ Component, route }">
    <LayoutShell v-if="!route.meta?.plain">
      <component :is="Component" :key="getRouteViewKey(route)" />
    </LayoutShell>
    <component v-else :is="Component" :key="getRouteViewKey(route)" />
  </RouterView>
</template>
<script setup>
import LayoutShell from './components/LayoutShell.vue';
import { routeRefreshState } from './utils/routeRefresh';

function getRouteViewKey(route) {
  const routeKey = route?.fullPath || route?.path || 'unknown-route';
  const version = routeRefreshState[routeKey] || 0;
  return `${routeKey}:${version}`;
}
</script>
