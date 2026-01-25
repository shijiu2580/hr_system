<template>
  <svg aria-hidden="true" :class="svgClass" :style="customStyle">
    <use :href="symbolId" :fill="color" />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  prefix: {
    type: String,
    default: 'icon',
  },
  name: {
    type: String,
    required: true,
  },
  color: {
    type: String,
    default: '#333',
  },
  size: {
    type: [Number, String],
    default: '1em',
  },
  className: {
    type: String,
    default: '',
  },
})

const symbolId = computed(() => `#${props.prefix}-${props.name}`)

const svgClass = computed(() => {
  if (props.className) {
    return 'svg-icon ' + props.className
  }
  return 'svg-icon'
})

const customStyle = computed(() => {
  const s = props.size
  const sizeValue = typeof s === 'number' ? `${s}px` : s
  return {
    fontSize: sizeValue,
    width: sizeValue,
    height: sizeValue
  }
})
</script>

<style scoped>
.svg-icon {
  width: 1em;
  height: 1em;
  vertical-align: -0.15em;
  fill: currentColor;
  overflow: hidden;
  display: inline-block;
}
</style>
