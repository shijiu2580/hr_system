<template>
  <div class="map-picker">
    <!-- 错误提示 -->
    <div v-if="mapError" class="map-error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 8v4M12 16h.01"/>
      </svg>
      <div class="error-content">
        <strong>地图加载失败</strong>
        <p>{{ mapError }}</p>
        <p class="hint" v-if="mapError.includes('VITE_AMAP')">
          请在 <code>frontend/.env</code> 文件中添加：<br>
          <code>VITE_AMAP_KEY=你的高德Key</code><br>
          <code>VITE_AMAP_SECURITY_JS_CODE=你的安全密钥</code><br>
          然后重启前端服务。
        </p>
        <p class="hint" v-else>
          请检查网络连接或高德地图 Key 是否正确。
        </p>
      </div>
    </div>

    <template v-else>
      <div class="search-box">
        <input 
          v-model="searchText" 
          type="text" 
          class="search-input" 
          placeholder="搜索地址或地点名称..."
          @keyup.enter="searchPlace"
        />
        <button class="btn-search" @click="searchPlace" :disabled="searching">
          {{ searching ? '搜索中...' : '搜索' }}
        </button>
        
        <!-- 搜索结果列表 -->
        <div v-if="searchResults.length > 0" class="search-results">
          <div 
            v-for="(item, index) in searchResults" 
            :key="index" 
            class="search-item"
            @click="selectSearchResult(item)"
          >
            <span class="item-name">{{ item.name }}</span>
            <span class="item-address">{{ item.address }}</span>
          </div>
        </div>
      </div>
      
      <div ref="mapContainer" class="map-container">
        <div v-if="mapLoading" class="map-loading">
          <div class="spinner"></div>
          <span>地图加载中...</span>
        </div>
      </div>
      
      <div class="selected-info" v-if="selectedLocation">
        <div class="info-row">
          <span class="label">已选地点：</span>
          <span class="value">{{ selectedLocation.name || '未命名' }}</span>
        </div>
        <div class="info-row">
          <span class="label">详细地址：</span>
          <span class="value">{{ selectedLocation.address || '未知' }}</span>
        </div>
        <div class="info-row">
          <span class="label">经度：</span>
          <span class="value">{{ selectedLocation.longitude }}</span>
        </div>
        <div class="info-row">
          <span class="label">纬度：</span>
          <span class="value">{{ selectedLocation.latitude }}</span>
        </div>
      </div>
      
      <div class="tip-text">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 16v-4M12 8h.01"/>
        </svg>
        点击地图选择签到地点，或输入地址搜索
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: null
  },
  radius: {
    type: Number,
    default: 1000
  }
})

const emit = defineEmits(['update:modelValue'])

const mapContainer = ref(null)
const searchText = ref('')
const searchResults = ref([])
const searching = ref(false)
const selectedLocation = ref(null)
const mapError = ref('')
const mapLoading = ref(true)

let map = null
let marker = null
let circle = null
let geocoder = null
let placeSearch = null

// 高德地图 Key（建议在 .env 中配置：VITE_AMAP_KEY / VITE_AMAP_SECURITY_JS_CODE）
const AMAP_KEY = import.meta.env.VITE_AMAP_KEY
const AMAP_SECURITY_CODE = import.meta.env.VITE_AMAP_SECURITY_JS_CODE

// 动态加载高德地图 JS API
function loadAMapScript() {
  return new Promise((resolve, reject) => {
    if (window.AMap) {
      resolve(window.AMap)
      return
    }

    if (!AMAP_KEY || !AMAP_SECURITY_CODE) {
      reject(new Error('缺少高德地图配置：请在 frontend/.env 中设置 VITE_AMAP_KEY 与 VITE_AMAP_SECURITY_JS_CODE'))
      return
    }
    
    // 设置安全密钥
    window._AMapSecurityConfig = {
      securityJsCode: AMAP_SECURITY_CODE
    }
    
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}&plugin=AMap.Geocoder,AMap.PlaceSearch,AMap.Geolocation`
    script.async = true
    script.onload = () => resolve(window.AMap)
    script.onerror = reject
    document.head.appendChild(script)
  })
}

// 初始化地图
async function initMap() {
  mapLoading.value = true
  mapError.value = ''
  try {
    const AMap = await loadAMapScript()
    
    // 默认中心点（北京）
    let center = [116.397428, 39.90923]
    
    // 如果有传入的值，使用传入的坐标
    if (props.modelValue?.longitude && props.modelValue?.latitude) {
      center = [props.modelValue.longitude, props.modelValue.latitude]
      selectedLocation.value = { ...props.modelValue }
    }
    
    map = new AMap.Map(mapContainer.value, {
      zoom: 15,
      center: center,
      resizeEnable: true
    })
    
    // 初始化地理编码器
    geocoder = new AMap.Geocoder({
      city: '全国',
      radius: 1000
    })
    
    // 初始化地点搜索
    placeSearch = new AMap.PlaceSearch({
      city: '全国',
      pageSize: 10
    })
    
    // 如果有初始值，添加标记
    if (props.modelValue?.longitude && props.modelValue?.latitude) {
      addMarker(center, props.modelValue.name || '', props.modelValue.address || '')
    }
    
    // 点击地图选点
    map.on('click', (e) => {
      const lnglat = e.lnglat
      reverseGeocode(lnglat)
    })
    
    // 尝试获取当前位置
    tryGetCurrentLocation()
    
    mapLoading.value = false
  } catch (error) {
    console.error('地图加载失败:', error)
    mapError.value = error.message || '地图加载失败'
    mapLoading.value = false
  }
}

// 尝试获取当前位置
function tryGetCurrentLocation() {
  if (!props.modelValue?.longitude && navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { longitude, latitude } = position.coords
        if (map) {
          map.setCenter([longitude, latitude])
        }
      },
      (error) => {
        console.log('获取位置失败:', error.message)
      },
      { enableHighAccuracy: true, timeout: 5000 }
    )
  }
}

// 添加标记和范围圈
function addMarker(lnglat, name, address) {
  // 移除旧标记
  if (marker) {
    map.remove(marker)
  }
  if (circle) {
    map.remove(circle)
  }
  
  // 添加新标记
  marker = new AMap.Marker({
    position: lnglat,
    draggable: true,
    title: name || '签到地点'
  })
  marker.setMap(map)
  
  // 标记拖动事件
  marker.on('dragend', (e) => {
    const pos = marker.getPosition()
    reverseGeocode(pos)
  })
  
  // 添加范围圈
  circle = new AMap.Circle({
    center: lnglat,
    radius: props.radius,
    strokeColor: '#3b82f6',
    strokeWeight: 2,
    strokeOpacity: 0.8,
    fillColor: '#3b82f6',
    fillOpacity: 0.2
  })
  circle.setMap(map)
}

// 逆地理编码（坐标转地址）
function reverseGeocode(lnglat) {
  if (!geocoder) return
  
  geocoder.getAddress([lnglat.lng, lnglat.lat], (status, result) => {
    if (status === 'complete' && result.info === 'OK') {
      const regeocode = result.regeocode
      const address = regeocode.formattedAddress
      const poi = regeocode.pois?.[0]?.name || ''
      
      updateSelectedLocation({
        name: poi || address.split('').slice(-10).join(''),
        address: address,
        longitude: lnglat.lng,
        latitude: lnglat.lat
      })
      
      addMarker([lnglat.lng, lnglat.lat], poi, address)
    }
  })
}

// 搜索地点
function searchPlace() {
  console.log('searchPlace called, searchText:', searchText.value, 'placeSearch:', !!placeSearch)
  
  if (!searchText.value.trim()) {
    console.log('搜索词为空')
    return
  }
  
  if (!placeSearch) {
    console.log('placeSearch 未初始化')
    return
  }
  
  searching.value = true
  searchResults.value = []
  
  placeSearch.search(searchText.value, (status, result) => {
    console.log('搜索结果:', status, result)
    searching.value = false
    if (status === 'complete' && result.info === 'OK') {
      searchResults.value = result.poiList.pois.map(poi => {
        // 处理地址为空或NaN的情况
        let addr = poi.address
        if (!addr || addr === 'NaN' || addr === 'undefined') {
          addr = [poi.pname, poi.cityname, poi.adname].filter(Boolean).join('')
        }
        return {
          name: poi.name,
          address: addr || '暂无详细地址',
          location: poi.location
        }
      })
      console.log('处理后的结果:', searchResults.value)
    } else {
      console.log('搜索失败或无结果:', status, result?.info)
    }
  })
}

// 选择搜索结果
function selectSearchResult(item) {
  const lnglat = [item.location.lng, item.location.lat]
  
  updateSelectedLocation({
    name: item.name,
    address: item.address,
    longitude: item.location.lng,
    latitude: item.location.lat
  })
  
  addMarker(lnglat, item.name, item.address)
  map.setCenter(lnglat)
  map.setZoom(16)
  
  searchResults.value = []
  searchText.value = ''
}

// 更新选中的位置
function updateSelectedLocation(location) {
  selectedLocation.value = location
  emit('update:modelValue', location)
}

// 监听 radius 变化，更新范围圈
watch(() => props.radius, (newRadius) => {
  if (circle) {
    circle.setRadius(newRadius)
  }
})

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  if (newVal?.longitude && newVal?.latitude && map) {
    const center = [newVal.longitude, newVal.latitude]
    map.setCenter(center)
    addMarker(center, newVal.name || '', newVal.address || '')
    selectedLocation.value = { ...newVal }
  }
}, { deep: true })

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  if (map) {
    map.destroy()
    map = null
  }
})
</script>

<style scoped>
.map-picker {
  width: 100%;
  position: relative;
}

.search-box {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1001;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: none;
}

.btn-search {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-search:hover {
  background: #2563eb;
}

.btn-search:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 68px;
  z-index: 1000;
  max-height: 240px;
  overflow-y: auto;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  margin-top: 4px;
}

.search-item {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s;
}

.search-item:hover {
  background: #f3f4f6;
}

.search-item:last-child {
  border-bottom: none;
}

.item-name {
  display: block;
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.item-address {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.map-container {
  width: 100%;
  height: 350px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  position: relative;
}

.map-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: #f8fafc;
  color: #64748b;
  font-size: 13px;
}

.spinner {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.map-error {
  padding: 24px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.map-error svg {
  color: #dc2626;
  flex-shrink: 0;
  margin-top: 2px;
}

.error-content {
  flex: 1;
}

.error-content strong {
  color: #991b1b;
  font-size: 14px;
}

.error-content p {
  margin: 6px 0 0;
  color: #b91c1c;
  font-size: 13px;
}

.error-content .hint {
  margin-top: 12px;
  padding: 10px 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #fecaca;
  color: #374151;
  font-size: 12px;
  line-height: 1.6;
}

.error-content code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 11px;
  color: #1f2937;
}

.selected-info {
  margin-top: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.info-row {
  display: flex;
  margin-bottom: 6px;
  font-size: 13px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  color: #64748b;
  width: 80px;
  flex-shrink: 0;
}

.info-row .value {
  color: #1e293b;
  word-break: break-all;
}

.tip-text {
  margin-top: 10px;
  font-size: 12px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tip-text svg {
  color: #9ca3af;
}
</style>
