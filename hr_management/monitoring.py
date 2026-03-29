"""
系统监控和指标收集

提供系统性能指标、数据库状态、缓存状态等监控信息
"""
import time
import psutil
import threading
from datetime import datetime, timedelta
from collections import deque, defaultdict
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
        self.slow_requests = deque(maxlen=300)

        # APM：接口维度聚合（每个接口保留最近200次）
        self.endpoint_stats = defaultdict(lambda: {
            'durations': deque(maxlen=200),
            'total': 0,
            'errors': 0,
            'last_seen': None,
        })

        # 数据库查询统计
        self.db_query_counts = deque(maxlen=60)
        self.db_query_times = deque(maxlen=1000)

        # 缓存统计
        self.cache_hits = 0
        self.cache_misses = 0

        # 启动时间
        self.start_time = datetime.now()

        self._initialized = True

    def _percentile(self, values, p):
        """计算百分位（不依赖外部库）。"""
        if not values:
            return 0
        sorted_vals = sorted(values)
        idx = int((len(sorted_vals) - 1) * p)
        return sorted_vals[idx]

    def record_request(self, duration_ms, is_error=False, path='/', method='GET', status_code=200, user='anonymous'):
        """记录请求"""
        self.request_times.append(duration_ms)
        key = f'{method} {path}'
        item = self.endpoint_stats[key]
        item['durations'].append(duration_ms)
        item['total'] += 1
        item['last_seen'] = datetime.now().isoformat()

        if is_error:
            item['errors'] += 1

        # 记录慢请求样本，便于快速排查
        if duration_ms >= 800:
            self.slow_requests.appendleft({
                'path': path,
                'method': method,
                'status_code': status_code,
                'duration_ms': round(duration_ms, 2),
                'user': user,
                'timestamp': datetime.now().isoformat(),
            })

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

        p95 = self._percentile(request_times, 0.95)
        p99 = self._percentile(request_times, 0.99)

        return {
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'requests': {
                'count': len(request_times),
                'avg_response_ms': round(avg_response_time, 2),
                'max_response_ms': round(max_response_time, 2),
                'p95_response_ms': round(p95, 2),
                'p99_response_ms': round(p99, 2),
                'slow_sample_count': len(self.slow_requests),
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


def get_apm_snapshot(top_n=10):
    """获取 APM 快照：慢接口排行 + 近期慢请求样本。"""
    ranking = []
    for endpoint, stats in metrics.endpoint_stats.items():
        durations = list(stats['durations'])
        if not durations:
            continue
        avg_ms = sum(durations) / len(durations)
        p95_ms = metrics._percentile(durations, 0.95)
        max_ms = max(durations)
        total = stats['total']
        errors = stats['errors']
        ranking.append({
            'endpoint': endpoint,
            'count': total,
            'error_rate': round((errors / total * 100) if total else 0, 2),
            'avg_ms': round(avg_ms, 2),
            'p95_ms': round(p95_ms, 2),
            'max_ms': round(max_ms, 2),
            'last_seen': stats['last_seen'],
        })

    ranking.sort(key=lambda x: (x['p95_ms'], x['avg_ms'], x['count']), reverse=True)

    return {
        'generated_at': datetime.now().isoformat(),
        'top_slow_endpoints': ranking[:top_n],
        'recent_slow_requests': list(metrics.slow_requests)[:top_n * 2],
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
