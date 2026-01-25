"""
系统监控和指标收集

提供系统性能指标、数据库状态、缓存状态等监控信息
"""
import time
import psutil
import threading
from datetime import datetime, timedelta
from collections import deque
from django.core.cache import cache
from django.db import connection
from django.conf import settings


class SystemMetrics:
    """系统指标收集器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 请求统计（最近1小时）
        self.request_counts = deque(maxlen=60)  # 每分钟一个数据点
        self.request_times = deque(maxlen=1000)  # 最近1000个请求的响应时间
        self.error_counts = deque(maxlen=60)
        
        # 数据库查询统计
        self.db_query_counts = deque(maxlen=60)
        self.db_query_times = deque(maxlen=1000)
        
        # 缓存统计
        self.cache_hits = 0
        self.cache_misses = 0
        
        # 启动时间
        self.start_time = datetime.now()
        
        self._initialized = True
    
    def record_request(self, duration_ms, is_error=False):
        """记录请求"""
        self.request_times.append(duration_ms)
        if is_error:
            pass  # 可以记录错误详情
    
    def record_db_query(self, duration_ms):
        """记录数据库查询"""
        self.db_query_times.append(duration_ms)
    
    def record_cache_hit(self):
        """记录缓存命中"""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """记录缓存未命中"""
        self.cache_misses += 1
    
    def get_metrics(self):
        """获取当前指标"""
        # 计算请求统计
        request_times = list(self.request_times)
        avg_response_time = sum(request_times) / len(request_times) if request_times else 0
        max_response_time = max(request_times) if request_times else 0
        
        # 计算数据库查询统计
        db_times = list(self.db_query_times)
        avg_db_time = sum(db_times) / len(db_times) if db_times else 0
        
        # 缓存命中率
        total_cache = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache * 100) if total_cache > 0 else 0
        
        # 系统资源
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
        except Exception:
            cpu_percent = 0
            memory = type('obj', (object,), {'percent': 0, 'used': 0, 'total': 0})()
            disk = type('obj', (object,), {'percent': 0, 'used': 0, 'total': 0})()
        
        return {
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'requests': {
                'count': len(request_times),
                'avg_response_ms': round(avg_response_time, 2),
                'max_response_ms': round(max_response_time, 2),
            },
            'database': {
                'query_count': len(db_times),
                'avg_query_ms': round(avg_db_time, 2),
            },
            'cache': {
                'hits': self.cache_hits,
                'misses': self.cache_misses,
                'hit_rate': round(cache_hit_rate, 2),
            },
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': round(memory.used / 1024 / 1024, 2),
                'memory_total_mb': round(memory.total / 1024 / 1024, 2),
                'disk_percent': disk.percent,
                'disk_used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
                'disk_total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
            }
        }


# 全局指标收集器实例
metrics = SystemMetrics()


def check_database_health():
    """检查数据库健康状态"""
    start = time.time()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        duration_ms = (time.time() - start) * 1000
        return {
            'status': 'healthy',
            'response_time_ms': round(duration_ms, 2)
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def check_cache_health():
    """检查缓存健康状态"""
    test_key = '_health_check_'
    test_value = 'ok'
    
    try:
        cache.set(test_key, test_value, 10)
        result = cache.get(test_key)
        cache.delete(test_key)
        
        if result == test_value:
            return {'status': 'healthy'}
        return {'status': 'degraded', 'error': 'Cache read/write mismatch'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def get_health_report():
    """获取完整健康报告"""
    db_health = check_database_health()
    cache_health = check_cache_health()
    system_metrics = metrics.get_metrics()
    
    # 整体状态判断
    overall_status = 'healthy'
    if db_health['status'] != 'healthy':
        overall_status = 'unhealthy'
    elif cache_health['status'] != 'healthy':
        overall_status = 'degraded'
    elif system_metrics['system']['cpu_percent'] > 90:
        overall_status = 'degraded'
    elif system_metrics['system']['memory_percent'] > 90:
        overall_status = 'degraded'
    
    return {
        'status': overall_status,
        'timestamp': datetime.now().isoformat(),
        'database': db_health,
        'cache': cache_health,
        'metrics': system_metrics,
    }
