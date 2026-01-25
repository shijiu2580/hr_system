<template>
  <RouterView v-slot="{ Component, route }">
    <LayoutShell v-if="!route.meta?.plain">
      <component :is="Component" />
    </LayoutShell>
    <component v-else :is="Component" />
  </RouterView>
</template>
<script setup>
import LayoutShell from './components/LayoutShell.vue';
</script>
