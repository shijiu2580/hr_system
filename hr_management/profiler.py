"""
性能分析工具 - 用于调试和优化

提供:
1. 数据库查询分析
2. 内存使用分析
3. 函数执行时间分析
4. 请求性能报告
"""
import time
import functools
import traceback
import logging
from typing import Callable, Any, Dict, List, Optional
from contextlib import contextmanager
from collections import defaultdict
from django.db import connection, reset_queries
from django.conf import settings


logger = logging.getLogger('hr_management.profiler')


class QueryProfiler:
    """
    数据库查询分析器
    
    用于分析视图或函数中的数据库查询，帮助发现 N+1 问题
    
    Example:
        with QueryProfiler() as profiler:
            # 执行一些数据库操作
            users = list(User.objects.all())
        
        print(profiler.get_report())
    """
    
    def __init__(self, name: str = None):
        self.name = name or 'QueryProfiler'
        self.queries: List[Dict] = []
        self.start_time: float = 0
        self.end_time: float = 0
    
    def __enter__(self):
        reset_queries()
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.queries = list(connection.queries)
        return False
    
    @property
    def total_time(self) -> float:
        """总执行时间（秒）"""
        return self.end_time - self.start_time
    
    @property
    def query_count(self) -> int:
        """查询次数"""
        return len(self.queries)
    
    @property
    def total_query_time(self) -> float:
        """数据库查询总时间（秒）"""
        return sum(float(q.get('time', 0)) for q in self.queries)
    
    def get_duplicate_queries(self) -> Dict[str, int]:
        """获取重复查询"""
        sql_counts = defaultdict(int)
        for q in self.queries:
            sql_counts[q['sql']] += 1
        return {sql: count for sql, count in sql_counts.items() if count > 1}
    
    def get_slow_queries(self, threshold_ms: float = 100) -> List[Dict]:
        """获取慢查询"""
        threshold_sec = threshold_ms / 1000
        return [q for q in self.queries if float(q.get('time', 0)) > threshold_sec]
    
    def get_report(self) -> Dict[str, Any]:
        """获取完整报告"""
        duplicates = self.get_duplicate_queries()
        slow = self.get_slow_queries()
        
        return {
            'name': self.name,
            'total_time_ms': self.total_time * 1000,
            'query_count': self.query_count,
            'query_time_ms': self.total_query_time * 1000,
            'python_time_ms': (self.total_time - self.total_query_time) * 1000,
            'duplicate_queries': len(duplicates),
            'slow_queries': len(slow),
            'potential_n_plus_1': len(duplicates) > 0,
            'details': {
                'duplicates': duplicates,
                'slow': slow,
            }
        }
    
    def print_report(self):
        """打印报告到日志"""
        report = self.get_report()
        logger.info(f"""
=== Query Profile: {report['name']} ===
Total Time: {report['total_time_ms']:.2f}ms
Query Count: {report['query_count']}
Query Time: {report['query_time_ms']:.2f}ms
Python Time: {report['python_time_ms']:.2f}ms
Duplicate Queries: {report['duplicate_queries']}
Slow Queries: {report['slow_queries']}
Potential N+1: {report['potential_n_plus_1']}
""")
        
        if report['details']['duplicates']:
            logger.warning("Duplicate queries detected:")
            for sql, count in list(report['details']['duplicates'].items())[:5]:
                logger.warning(f"  [{count}x] {sql[:100]}...")


def profile_queries(name: str = None):
    """
    查询分析装饰器
    
    Example:
        @profile_queries('get_employees')
        def get_employees():
            return Employee.objects.all()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not settings.DEBUG:
                return func(*args, **kwargs)
            
            with QueryProfiler(name or func.__name__) as profiler:
                result = func(*args, **kwargs)
            
            profiler.print_report()
            return result
        
        return wrapper
    return decorator


class FunctionProfiler:
    """
    函数执行时间分析器
    
    Example:
        profiler = FunctionProfiler()
        
        @profiler.track
        def my_function():
            ...
        
        # 执行多次后
        print(profiler.get_stats())
    """
    
    def __init__(self):
        self.stats: Dict[str, Dict] = defaultdict(lambda: {
            'calls': 0,
            'total_time': 0,
            'min_time': float('inf'),
            'max_time': 0,
        })
    
    def track(self, func: Callable) -> Callable:
        """装饰器：追踪函数执行时间"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.time() - start
                stats = self.stats[func.__name__]
                stats['calls'] += 1
                stats['total_time'] += elapsed
                stats['min_time'] = min(stats['min_time'], elapsed)
                stats['max_time'] = max(stats['max_time'], elapsed)
        
        return wrapper
    
    def get_stats(self) -> Dict[str, Dict]:
        """获取所有函数的统计信息"""
        result = {}
        for name, stats in self.stats.items():
            if stats['calls'] > 0:
                result[name] = {
                    'calls': stats['calls'],
                    'total_ms': stats['total_time'] * 1000,
                    'avg_ms': (stats['total_time'] / stats['calls']) * 1000,
                    'min_ms': stats['min_time'] * 1000,
                    'max_ms': stats['max_time'] * 1000,
                }
        return result
    
    def reset(self):
        """重置统计"""
        self.stats.clear()


@contextmanager
def timer(name: str = 'Operation'):
    """
    计时上下文管理器
    
    Example:
        with timer('Load data'):
            data = load_large_data()
        # 输出: Load data took 123.45ms
    """
    start = time.time()
    yield
    elapsed = (time.time() - start) * 1000
    logger.debug(f"{name} took {elapsed:.2f}ms")


def timed(func: Callable) -> Callable:
    """
    简单的计时装饰器
    
    Example:
        @timed
        def slow_function():
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = (time.time() - start) * 1000
            logger.debug(f"{func.__name__} took {elapsed:.2f}ms")
    
    return wrapper


class MemoryProfiler:
    """
    内存使用分析器
    
    Example:
        with MemoryProfiler() as mp:
            large_list = [i for i in range(1000000)]
        
        print(f"Memory used: {mp.memory_used_mb:.2f}MB")
    """
    
    def __init__(self):
        self.start_memory: int = 0
        self.end_memory: int = 0
    
    def __enter__(self):
        import psutil
        process = psutil.Process()
        self.start_memory = process.memory_info().rss
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import psutil
        process = psutil.Process()
        self.end_memory = process.memory_info().rss
        return False
    
    @property
    def memory_used(self) -> int:
        """使用的内存（字节）"""
        return self.end_memory - self.start_memory
    
    @property
    def memory_used_mb(self) -> float:
        """使用的内存（MB）"""
        return self.memory_used / (1024 * 1024)


class RequestProfiler:
    """
    请求性能分析器 - 用于分析单个请求的完整性能
    
    Example:
        profiler = RequestProfiler(request)
        profiler.mark('start_processing')
        # ... 一些处理 ...
        profiler.mark('query_done')
        # ... 更多处理 ...
        profiler.mark('response_ready')
        
        print(profiler.get_timeline())
    """
    
    def __init__(self, request=None):
        self.request = request
        self.start_time = time.time()
        self.marks: List[Dict] = []
        self.queries_start = len(connection.queries) if settings.DEBUG else 0
    
    def mark(self, name: str, data: Dict = None):
        """标记时间点"""
        self.marks.append({
            'name': name,
            'time': time.time() - self.start_time,
            'data': data,
        })
    
    def get_timeline(self) -> Dict[str, Any]:
        """获取时间线"""
        query_count = 0
        if settings.DEBUG:
            query_count = len(connection.queries) - self.queries_start
        
        timeline = []
        prev_time = 0
        for mark in self.marks:
            timeline.append({
                'name': mark['name'],
                'elapsed_ms': mark['time'] * 1000,
                'delta_ms': (mark['time'] - prev_time) * 1000,
                'data': mark.get('data'),
            })
            prev_time = mark['time']
        
        return {
            'total_time_ms': (time.time() - self.start_time) * 1000,
            'query_count': query_count,
            'timeline': timeline,
            'path': self.request.path if self.request else None,
            'method': self.request.method if self.request else None,
        }


# 全局函数分析器实例
function_profiler = FunctionProfiler()


def enable_sql_logging():
    """启用 SQL 日志（仅开发环境）"""
    if settings.DEBUG:
        import logging
        sql_logger = logging.getLogger('django.db.backends')
        sql_logger.setLevel(logging.DEBUG)
        sql_logger.addHandler(logging.StreamHandler())


def get_query_count() -> int:
    """获取当前请求的查询数量"""
    if settings.DEBUG:
        return len(connection.queries)
    return 0


def analyze_queryset(qs, name: str = 'QuerySet'):
    """
    分析 QuerySet 的查询性能
    
    Example:
        qs = Employee.objects.select_related('department')
        analyze_queryset(qs, 'employees')
    """
    with QueryProfiler(name) as profiler:
        # 强制执行查询
        list(qs)
    
    report = profiler.get_report()
    
    if report['potential_n_plus_1']:
        logger.warning(f"QuerySet '{name}' has potential N+1 problem!")
        logger.warning(f"Consider using select_related or prefetch_related")
    
    return report
