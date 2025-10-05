import pandas as pd
from datetime import datetime, timedelta

class SecurityEngine:
    def __init__(self, san_fabric):
        self.san_fabric = san_fabric
        self.behavior_profiles = {}
        self.initialize_behavior_profiles()
    
    def initialize_behavior_profiles(self):
        """Initialize normal behavior profiles for all devices"""
        base_profiles = {
            'DB_Server': {'access_rate': 5, 'target_variety': 3, 'normal_hours': True},
            'Web_Server': {'access_rate': 20, 'target_variety': 2, 'normal_hours': True},
            'Backup_Server': {'access_rate': 2, 'target_variety': 10, 'normal_hours': False},
            'Workstation': {'access_rate': 3, 'target_variety': 2, 'normal_hours': True},
            'Admin_Workstation': {'access_rate': 1, 'target_variety': 5, 'normal_hours': True}
        }
        
        for node in self.san_fabric.G.nodes():
            if self.san_fabric.G.nodes[node].get('type') == 'server':
                for pattern, profile in base_profiles.items():
                    if pattern in node:
                        self.behavior_profiles[node] = profile.copy()
                        break
                else:
                    # Default profile
                    self.behavior_profiles[node] = {'access_rate': 5, 'target_variety': 3, 'normal_hours': True}
    
    def analyze_access_patterns(self, hours_back=24):
        """Analyze access patterns for anomalies"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_logs = [log for log in self.san_fabric.access_log 
                      if log['timestamp'] > cutoff_time]
        
        if not recent_logs:
            return "No recent activity to analyze"
        
        analysis = "ACCESS PATTERN ANALYSIS:\n"
        analysis += "=" * 30 + "\n"
        
        # Group by initiator
        df = pd.DataFrame(recent_logs)
        if df.empty:
            return "No data for analysis"
        
        initiator_stats = df.groupby('initiator').agg({
            'timestamp': 'count',
            'target': 'nunique',
            'granted': 'sum'
        }).rename(columns={'timestamp': 'total_attempts', 'target': 'unique_targets'})
        
        for initiator, stats in initiator_stats.iterrows():
            analysis += f"\n{initiator}:\n"
            analysis += f"  - Total attempts: {stats['total_attempts']}\n"
            analysis += f"  - Unique targets: {stats['unique_targets']}\n"
            success_rate = (stats['granted']/stats['total_attempts']*100) if stats['total_attempts'] > 0 else 0
            analysis += f"  - Success rate: {success_rate:.1f}%\n"
            
            # Check against behavior profile
            if initiator in self.behavior_profiles:
                profile = self.behavior_profiles[initiator]
                if stats['total_attempts'] > profile['access_rate'] * 2:
                    analysis += f"  ⚠️  HIGH ACTIVITY: Exceeds normal rate\n"
                if stats['unique_targets'] > profile['target_variety'] * 2:
                    analysis += f"  ⚠️  SUSPICIOUS: Accessing unusual targets\n"
        
        return analysis
    
    def get_threat_level(self):
        """Calculate current threat level"""
        recent_alerts = [alert for alert in self.san_fabric.threat_alerts 
                        if datetime.now() - alert['timestamp'] < timedelta(hours=1)]
        
        if not recent_alerts:
            return "LOW", "No recent threats detected"
        
        high_severity = len([alert for alert in recent_alerts if alert['severity'] == 'high'])
        
        if high_severity >= 3:
            return "CRITICAL", f"{high_severity} high-severity threats in last hour"
        elif high_severity >= 1:
            return "HIGH", f"{high_severity} high-severity threats detected"
        else:
            return "MEDIUM", f"{len(recent_alerts)} security events in last hour"