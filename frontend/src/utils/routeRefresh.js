import { reactive } from 'vue';

export const routeRefreshState = reactive({});

export function refreshRouteView(routeKey = '') {
  if (!routeKey) return;
  routeRefreshState[routeKey] = (routeRefreshState[routeKey] || 0) + 1;
}
