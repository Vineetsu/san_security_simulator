from datetime import datetime
import json

class SANMonitor:
    def __init__(self, san_fabric):
        self.san_fabric = san_fabric
        self.performance_metrics = []
    
    def log_performance_metric(self, initiator, target, response_time, success):
        """Log performance metrics for analysis"""
        metric = {
            'timestamp': datetime.now(),
            'initiator': initiator,
            'target': target,
            'response_time_ms': response_time,
            'success': success
        }
        self.performance_metrics.append(metric)
    
    def get_performance_report(self):
        """Generate performance analysis report"""
        if not self.performance_metrics:
            return "No performance data available"
        
        df = pd.DataFrame(self.performance_metrics)
        avg_response_time = df['response_time_ms'].mean()
        success_rate = (df['success'].sum() / len(df)) * 100
        
        report = f"""
PERFORMANCE REPORT
==================
Generated: {datetime.now()}

Overall Metrics:
- Average Response Time: {avg_response_time:.2f} ms
- Success Rate: {success_rate:.1f}%
- Total Operations: {len(self.performance_metrics)}

Top Slowest Operations:
"""
        # Get top 5 slowest operations
        slow_ops = df.nlargest(5, 'response_time_ms')
        for _, op in slow_ops.iterrows():
            report += f"- {op['initiator']} -> {op['target']}: {op['response_time_ms']} ms\n"
        
        return report