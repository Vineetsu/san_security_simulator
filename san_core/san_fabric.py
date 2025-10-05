import networkx as nx
import matplotlib.pyplot as plt
import json
from datetime import datetime, time

class SANFabric:
    def __init__(self, config_file="config/default_config.json"):
        self.load_config(config_file)
        self.initialize_fabric()
        self.access_log = []
        self.emergency_mode = False
        self.threat_alerts = []
        
    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
    def initialize_fabric(self):
        self.G = nx.Graph()
        
        # Add storage units
        for storage_id, storage_info in self.config['storage_units'].items():
            # Create a copy of storage_info without 'type' if it exists
            node_attrs = storage_info.copy()
            node_attrs['node_type'] = 'storage'  # Use 'node_type' instead of 'type'
            self.G.add_node(storage_id, **node_attrs)
        
        # Add zones and members
        for zone_name, zone_info in self.config['zones'].items():
            for member in zone_info['members']:
                if member not in self.G:
                    # Determine node type
                    node_type = 'server' if any(x in member for x in ['Server', 'Workstation']) else 'storage'
                    self.G.add_node(member, node_type=node_type, zone=zone_name)
        
        # Create connections within zones
        for zone_name, zone_info in self.config['zones'].items():
            members = zone_info['members']
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    if members[i] in self.G and members[j] in self.G:
                        self.G.add_edge(members[i], members[j], zone=zone_name, bandwidth=8, latency=5)
    
    def is_within_business_hours(self):
        current_time = datetime.now().time()
        business_start = time(9, 0)  # 9 AM
        business_end = time(17, 0)   # 5 PM
        return business_start <= current_time <= business_end
    
    def check_zone_access(self, initiator, target):
        """Check if initiator and target share any zones"""
        common_zones = []
        for zone_name, zone_info in self.config['zones'].items():
            if initiator in zone_info['members'] and target in zone_info['members']:
                common_zones.append(zone_name)
        return common_zones
    
    def detect_anomalous_behavior(self, initiator):
        """Simple anomaly detection based on access patterns"""
        recent_attempts = [log for log in self.access_log[-20:] 
                          if log['initiator'] == initiator]
        
        if len(recent_attempts) > 15:  # Too many recent attempts
            return True, "Excessive access attempts"
        
        # Check for unusual access patterns
        unique_targets = len(set(log['target'] for log in recent_attempts))
        if unique_targets > 8:  # Accessing too many different targets
            return True, "Accessing unusual number of targets"
            
        return False, "Normal behavior"
    
    def request_access(self, initiator, target, access_type="read"):
        """Main access control function"""
        access_time = datetime.now()
        
        # Log the attempt
        attempt = {
            'timestamp': access_time,
            'initiator': initiator,
            'target': target,
            'access_type': access_type,
            'granted': False,
            'reason': '',
            'emergency_mode': self.emergency_mode
        }
        
        # Emergency mode override
        if self.emergency_mode and initiator == "Admin_Workstation":
            attempt['granted'] = True
            attempt['reason'] = 'Emergency access granted'
            self.access_log.append(attempt)
            return True, "Emergency access granted"
        
        # Check if nodes exist
        if initiator not in self.G or target not in self.G:
            attempt['reason'] = 'Invalid initiator or target'
            self.access_log.append(attempt)
            return False, "Invalid initiator or target"
        
        # Check zone access
        common_zones = self.check_zone_access(initiator, target)
        if not common_zones:
            attempt['reason'] = 'No common zones'
            self.access_log.append(attempt)
            return False, "Access denied: No common zones"
        
        # Check time-based restrictions
        for zone in common_zones:
            zone_schedule = self.config['zones'][zone]['work_schedule']
            
            if zone_schedule == 'business_hours' and not self.is_within_business_hours():
                continue
            if zone_schedule == 'off_hours' and self.is_within_business_hours():
                continue
            if zone_schedule == 'emergency_only' and not self.emergency_mode:
                continue
            
            # Check for anomalous behavior
            is_anomalous, anomaly_reason = self.detect_anomalous_behavior(initiator)
            if is_anomalous:
                attempt['reason'] = f'Suspicious behavior: {anomaly_reason}'
                self.threat_alerts.append({
                    'timestamp': access_time,
                    'initiator': initiator,
                    'threat': anomaly_reason,
                    'severity': 'high'
                })
                self.access_log.append(attempt)
                return False, f"Access denied: {anomaly_reason}"
            
            # Access granted
            attempt['granted'] = True
            attempt['reason'] = f'Access granted via {zone}'
            self.access_log.append(attempt)
            return True, f"Access granted via {zone}"
        
        attempt['reason'] = 'Time-based restrictions'
        self.access_log.append(attempt)
        return False, "Access denied: Time-based restrictions"
    
    def activate_emergency_mode(self):
        """Activate emergency access mode"""
        self.emergency_mode = True
        return "Emergency mode activated - Admin has full access"
    
    def deactivate_emergency_mode(self):
        """Deactivate emergency access mode"""
        self.emergency_mode = False
        return "Emergency mode deactivated"
    
    def visualize_fabric(self):
        """Create visual representation of SAN fabric"""
        plt.figure(figsize=(15, 10))
        
        # Define node colors based on node_type
        node_colors = []
        for node in self.G.nodes():
            if self.G.nodes[node].get('node_type') == 'storage':
                node_colors.append('red')
            else:
                node_colors.append('lightblue')
        
        pos = nx.spring_layout(self.G, seed=42)  # Consistent layout
        nx.draw(self.G, pos, node_color=node_colors, with_labels=True, 
                node_size=800, font_size=8, font_weight='bold', edge_color='gray')
        
        plt.title("SAN Fabric Topology\nRed=Storage, Blue=Servers/Workstations")
        plt.tight_layout()
        plt.savefig('san_topology.png', dpi=300, bbox_inches='tight')
        print("SAN topology saved as 'san_topology.png'")
        plt.show()
    
    def generate_security_report(self):
        """Generate comprehensive security report"""
        total_attempts = len(self.access_log)
        granted_attempts = len([log for log in self.access_log if log['granted']])
        denied_attempts = total_attempts - granted_attempts
        
        # Analyze reasons for denial
        denial_reasons = {}
        for log in self.access_log:
            if not log['granted']:
                reason = log['reason']
                denial_reasons[reason] = denial_reasons.get(reason, 0) + 1
        
        report = f"""
SAN SECURITY REPORT
===================
Generated: {datetime.now()}

ACCESS STATISTICS:
- Total attempts: {total_attempts}
- Granted: {granted_attempts}
- Denied: {denied_attempts}
- Success rate: {(granted_attempts/total_attempts*100 if total_attempts > 0 else 0):.1f}%

DENIAL ANALYSIS:
{chr(10).join(f'  - {reason}: {count}' for reason, count in denial_reasons.items())}

SECURITY STATUS:
- Emergency Mode: {'ACTIVE' if self.emergency_mode else 'Inactive'}
- Threat Alerts: {len(self.threat_alerts)}
- Active Zones: {len(self.config['zones'])}
- Total Devices: {len(self.G.nodes())}
"""
        return report