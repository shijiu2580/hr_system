"""
数据库查询监控模块
用于开发环境下检测 N+1 查询问题和慢查询
"""
import time
import logging
import functools
from collections import defaultdict
from typing import Optional, Callable, Any
from contextlib import contextmanager
from django.db import connection, reset_queries
from django.conf import settings


logger = logging.getLogger('hr_system.db')


class QueryMonitor:
    """
    数据库查询监控器
    
    用于追踪和分析 SQL 查询：
    - 查询数量统计
    - 慢查询检测
    - N+1 查询问题检测
    - 重复查询检测
    """
    
    # 慢查询阈值（秒）
    SLOW_QUERY_THRESHOLD = 0.1
    
    # 警告查询数量阈值
    QUERY_COUNT_WARNING = 10
    
    def __init__(self):
        self.enabled = settings.DEBUG
        self._query_stats = defaultdict(int)
    
    @contextmanager
    def monitor(self, label: str = 'request'):
        """
        监控代码块的数据库查询
        
        Usage:
            with QueryMonitor().monitor('my_view'):
                # Your code here
                pass
        """
        if not self.enabled:
            yield
            return
        
        reset_queries()
        start_time = time.time()
        
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            queries = connection.queries
            
            self._analyze_queries(label, queries, elapsed)
    
    def _analyze_queries(self, label: str, queries: list, elapsed: float):
        """分析查询并记录问题"""
        query_count = len(queries)
        
        # 基本统计
        stats = {
            'label': label,
            'query_count': query_count,
            'total_time': elapsed,
            'slow_queries': [],
            'duplicate_queries': [],
        }
        
        # 检测慢查询和重复查询
        query_hash_count = defaultdict(int)
        
        for query in queries:
            sql = query.get('sql', '')
            query_time = float(query.get('time', 0))
            
            # 慢查询检测
            if query_time > self.SLOW_QUERY_THRESHOLD:
                stats['slow_queries'].append({
                    'sql': sql[:500],  # 截断长SQL
                    'time': query_time,
                })
            
            # 重复查询检测（简化SQL进行比较）
            normalized = self._normalize_sql(sql)
            query_hash_count[normalized] += 1
        
        # 找出重复查询
        for sql_pattern, count in query_hash_count.items():
            if count > 1:
                stats['duplicate_queries'].append({
                    'pattern': sql_pattern[:200],
                    'count': count,
                })
        
        # 记录日志
        self._log_stats(stats)
    
    def _normalize_sql(self, sql: str) -> str:
        """
        标准化 SQL 用于比较
        移除具体的值，只保留模式
        """
        import re
        
        # 移除具体的数字值
        sql = re.sub(r'\b\d+\b', '?', sql)
        # 移除字符串值
        sql = re.sub(r"'[^']*'", '?', sql)
        # 移除 IN 子句中的多个值
        sql = re.sub(r'\(\?(?:, \?)+\)', '(?...)', sql)
        
        return sql
    
    def _log_stats(self, stats: dict):
        """记录统计信息"""
        label = stats['label']
        query_count = stats['query_count']
        total_time = stats['total_time']
        
        # 基本信息
        if query_count > self.QUERY_COUNT_WARNING:
            logger.warning(
                f'[{label}] 查询数量过多: {query_count} queries in {total_time:.3f}s'
            )
        else:
            logger.debug(
                f'[{label}] {query_count} queries in {total_time:.3f}s'
            )
        
        # 慢查询警告
        for slow in stats['slow_queries']:
            logger.warning(
                f'[{label}] 慢查询 ({slow["time"]:.3f}s): {slow["sql"]}'
            )
        
        # 重复查询警告（可能是 N+1 问题）
        for dup in stats['duplicate_queries']:
            if dup['count'] > 2:
                logger.warning(
                    f'[{label}] 可能的 N+1 问题: 查询执行 {dup["count"]} 次: {dup["pattern"]}'
                )


class QueryDebugMiddleware:
    """
    数据库查询调试中间件
    
    在开发环境下记录每个请求的数据库查询统计
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.monitor = QueryMonitor()
    
    def __call__(self, request):
        if not settings.DEBUG:
            return self.get_response(request)
        
        label = f'{request.method} {request.path}'
        
        with self.monitor.monitor(label):
            response = self.get_response(request)
        
        # 在响应头中添加查询统计（仅开发环境）
        query_count = len(connection.queries)
        response['X-DB-Query-Count'] = str(query_count)
        
        return response


def monitor_queries(func: Callable = None, label: str = None):
    """
    装饰器：监控函数的数据库查询
    
    Usage:
        @monitor_queries
        def my_view(request):
            ...
        
        @monitor_queries(label='custom_label')
        def another_view(request):
            ...
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            monitor = QueryMonitor()
            func_label = label or f.__name__
            
            with monitor.monitor(func_label):
                return f(*args, **kwargs)
        
        return wrapper
    
    if func is not None:
        return decorator(func)
    
    return decorator


def explain_query(queryset) -> str:
    """
    获取查询的 EXPLAIN 结果
    
    Usage:
        qs = Employee.objects.filter(status='active')
        print(explain_query(qs))
    """
    sql, params = queryset.query.sql_with_params()
    
    with connection.cursor() as cursor:
        cursor.execute(f'EXPLAIN QUERY PLAN {sql}', params)
        results = cursor.fetchall()
    
    return '\n'.join(str(row) for row in results)


def get_query_count() -> int:
    """获取当前请求的查询数量"""
    return len(connection.queries)


def get_recent_queries(limit: int = 10) -> list:
    """获取最近的查询"""
    return connection.queries[-limit:]


def print_queries():
    """打印所有查询（调试用）"""
    for i, query in enumerate(connection.queries):
        print(f'\n--- Query {i + 1} ({query["time"]}s) ---')
        print(query['sql'])


class QueryProfiler:
    """
    查询分析器 - 用于性能分析
    
    Usage:
        profiler = QueryProfiler()
        profiler.start()
        
        # Your code
        
        profiler.stop()
        profiler.report()
    """
    
    def __init__(self):
        self.queries = []
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """开始分析"""
        reset_queries()
        self.queries = []
        self.start_time = time.time()
    
    def stop(self):
        """停止分析"""
        self.end_time = time.time()
        self.queries = list(connection.queries)
    
    def report(self) -> dict:
        """生成分析报告"""
        if not self.queries:
            return {'error': 'No queries captured'}
        
        total_time = self.end_time - self.start_time if self.end_time else 0
        db_time = sum(float(q.get('time', 0)) for q in self.queries)
        
        # 按表分组查询
        table_stats = defaultdict(lambda: {'count': 0, 'time': 0})
        for query in self.queries:
            sql = query.get('sql', '')
            query_time = float(query.get('time', 0))
            
            # 简单的表名提取
            tables = self._extract_tables(sql)
            for table in tables:
                table_stats[table]['count'] += 1
                table_stats[table]['time'] += query_time
        
        return {
            'total_queries': len(self.queries),
            'total_time': total_time,
            'db_time': db_time,
            'app_time': total_time - db_time,
            'db_time_percent': (db_time / total_time * 100) if total_time else 0,
            'table_stats': dict(table_stats),
            'slowest_queries': sorted(
                [{'sql': q['sql'][:200], 'time': float(q['time'])} for q in self.queries],
                key=lambda x: x['time'],
                reverse=True
            )[:5],
        }
    
    def _extract_tables(self, sql: str) -> list:
        """从 SQL 中提取表名"""
        import re
        
        # 简单的表名提取
        patterns = [
            r'FROM\s+[`"]?(\w+)[`"]?',
            r'JOIN\s+[`"]?(\w+)[`"]?',
            r'UPDATE\s+[`"]?(\w+)[`"]?',
            r'INSERT\s+INTO\s+[`"]?(\w+)[`"]?',
        ]
        
        tables = []
        for pattern in patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            tables.extend(matches)
        
        return list(set(tables))


# 开发环境下自动启用查询日志
if settings.DEBUG:
    logging.getLogger('django.db.backends').setLevel(logging.DEBUG)
