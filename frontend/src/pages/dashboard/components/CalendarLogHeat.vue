<template>
  <div class="log-calendar" v-if="days && days.length">
    <div class="calendar-grid">
  <div v-for="cell in calendarCells" :key="cell.date" class="day-cell" :class="{ today: cell.isToday, empty: !cell.hasData }" :style="cellStyle(cell)" @mouseenter="showTip(cell, $event)" @mouseleave="hideTip">
  <span class="day-num">{{ cell.day }}</span>
  <span v-if="cell.lunar && props.showLunar" class="lunar">{{ cell.lunar }}</span>
    <span v-if="props.showCount && cell.total>0" class="count">{{ cell.total }}</span>
      </div>
    </div>
    <div v-if="tooltip.visible" class="tooltip" :style="tooltipStyle">
      <div class="tip-date">{{ formatDate(tooltip.cell.date) }}</div>
    </div>
  </div>
  <div v-else class="empty-box">当月暂无日志数据。</div>
</template>
<script setup>
import { computed, ref } from 'vue'
import solarlunar from 'solarlunar'
// props: year, month, today, days: [{day,date,total,levels:{...}}]
const props = defineProps({
  year: { type: Number, required: true },
  month: { type: Number, required: true },
  today: { type: String, required: true },
  days: { type: Array, required: true },
  showLunar: { type: Boolean, default: true },
  showCount: { type: Boolean, default: false }
})
// 可提取级别列表
const levelKeys = computed(() => {
  if(!props.days || props.days.length===0) return []
  const first = props.days.find(d=>d.levels) || { levels: {} }
  return Object.keys(first.levels)
})
const maxTotal = computed(()=> props.days.reduce((m,d)=> d.total>m?d.total:m,0))
// 构造日历（按星期填充前置空格）
function buildCells(){
  if(!props.days || props.days.length===0) return []
  const year = props.year, month = props.month
  const firstDate = new Date(`${year}-${String(month).padStart(2,'0')}-01T00:00:00`)
  const firstWeekday = firstDate.getDay() // 0=周日
  const daysInMonth = props.days.length // 已按当月天数给出
  const cells = []
  for(let i=0;i<firstWeekday;i++){ // 前置占位
    cells.push({ day: '', date: `blank-${i}`, total:0, levels:{}, isToday:false, hasData:false, blank:true })
  }
  const todayStr = props.today
  for(const d of props.days){
    // 生成农历：d.date 格式 YYYY-MM-DD
    let lunarStr = ''
    try {
      const [Y,M,D] = d.date.split('-').map(n=>parseInt(n,10))
      const lunar = solarlunar.solar2lunar(Y,M,D)
      if(lunar.dayCn === '初一') {
        let mcn = lunar.monthCn
        if(!/月$/.test(mcn)) mcn += '月'
        lunarStr = mcn
      } else {
        lunarStr = lunar.dayCn
      }
    } catch(_) {}
    cells.push({ ...d, isToday: d.date===todayStr, hasData: d.total>0, blank:false, lunar: lunarStr })
  }
  return cells
}
const calendarCells = computed(buildCells)
// 颜色比例
function colorScale(ratio){
  // ratio 0..1 -> 从 #e0f2fe 到 #0369a1 (浅到深蓝)
  const start = [224,242,254];
  const end = [3,105,161];
  const rgb = start.map((s,i)=> Math.round(s + (end[i]-s)*ratio))
  return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`
}
function cellStyle(cell){
  if(cell.blank) return {}
  // 仅高亮今天，其余全部统一灰底
  if(cell.isToday){
    return { background:'#87CEEB' }
  }
  return { background:'var(--cal-empty,#f3f4f6)' }
}
// tooltip
const tooltip = ref({ visible:false, cell:null, x:0, y:0 })
function showTip(cell, evt){ if(cell.blank) return; tooltip.value = { visible:true, cell, x:evt.clientX, y:evt.clientY } }
function hideTip(){ tooltip.value.visible=false }
function formatDate(iso){
  try { const [y,m,d] = iso.split('-'); return `${y}年${m}月${d}日`; } catch(_) { return iso; }
}
const tooltipStyle = computed(()=> ({ left: tooltip.value.x + 12 + 'px', top: tooltip.value.y + 12 + 'px' }))
</script>
<style scoped>
.log-calendar {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: var(--cal-cell-gap, 2px);
}

.day-cell {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: flex-start;
  padding: 2px 3px 1px;
  min-height: var(--cal-cell-height, 34px);
  border-radius: 4px;
  font-size: 9px;
  line-height: 1.05;
  border: 1px solid rgba(148, 163, 184, 0.3);
  transition: background 0.25s, border-color 0.25s;
}

.day-cell.today {
  background: #87CEEB !important;
  outline: 2px solid #1e3a8a;
  outline-offset: 1px;
  color: #0f172a;
}

.day-cell.empty {
  color: #9ca3af;
}

.day-cell:hover {
  border-color: rgba(148, 163, 184, 0.6);
}

.day-num {
  font-weight: 600;
  color: #1f2937;
  font-size: 10px;
  align-self: flex-start;
}

.lunar {
  font-size: 9px;
  color: #475569;
  align-self: flex-start;
  line-height: 1;
  margin-top: 1px;
}

.count {
  font-size: 8px;
  margin-top: auto;
  color: #1e3a8a;
  font-weight: 500;
}

.empty-box {
  background: #f8fafc;
  color: #64748b;
  padding: 0.6rem 0.75rem;
  border: 1px dashed rgba(148, 163, 184, 0.5);
  border-radius: 6px;
  font-size: 12px;
}

.tooltip {
  position: fixed;
  z-index: 3000;
  background: #1e293b;
  color: #fff;
  padding: 0.35rem 0.55rem;
  border-radius: 6px;
  font-size: 11px;
  box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.25);
  white-space: nowrap;
}

.tip-date {
  font-weight: 600;
  margin-bottom: 4px;
}

.tip-total {
  font-size: 11px;
  margin-bottom: 4px;
}

.tip-row {
  display: flex;
  justify-content: space-between;
}

.tip-row .lvl {
  opacity: 0.8;
}
</style>
