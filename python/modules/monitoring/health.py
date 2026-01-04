"""
Server health monitoring for the TTS system.

This module provides server health checking and debug information gathering.
Layer 3 - Storage & Processing: Depends on Layers 1-2.
"""

import time
import logging
from typing import Tuple

from modules.types.data_models import ServerDebugInfo, StorageInfo
from modules.types.protocols import ServerMonitorProtocol, ConnectionPoolProtocol

logger = logging.getLogger(__name__)


class ServerHealthMonitor(ServerMonitorProtocol):
    """Server health monitoring and debug information gathering"""
    
    def __init__(self, connection_pool: ConnectionPoolProtocol):
        """
        Initialize server health monitor.
        
        Args:
            connection_pool: HTTP connection pool for API requests
        """
        self.conn_pool = connection_pool
    
    def get_server_health(self) -> Tuple[bool, str]:
        """Get quick server health assessment"""
        try:
            debug_info = self.get_server_debug_info()
            return debug_info.is_healthy(), debug_info.get_health_summary()
        except Exception as e:
            return False, f"🔴 Health check failed: {str(e)}"
    
    def get_server_debug_info(self) -> ServerDebugInfo:
        """Get comprehensive server debug information from all endpoints"""
        debug_info = ServerDebugInfo(timestamp=time.time())
        
        # Get threads information
        try:
            response = self.conn_pool.get("/debug/threads", timeout=5)
            if response.status_code == 200:
                debug_info.threads = response.json()
        except Exception as e:
            debug_info.errors.append(f"Threads endpoint failed: {str(e)}")
        
        # Get storage information
        try:
            response = self.conn_pool.get("/debug/storage", timeout=5)
            if response.status_code == 200:
                storage_data = response.json()
                debug_info.storage = []
                for item in storage_data.get('storage_info', []):
                    debug_info.storage.append(StorageInfo(
                        device=item['device'],
                        mountpoint=item['mountpoint'],
                        fstype=item['fstype'],
                        total_gb=item['total_gb'],
                        used_gb=item['used_gb'],
                        free_gb=item['free_gb'],
                        percent_used=item['percent_used']
                    ))
        except Exception as e:
            debug_info.errors.append(f"Storage endpoint failed: {str(e)}")
        
        # Get system information
        try:
            response = self.conn_pool.get("/debug/system", timeout=5)
            if response.status_code == 200:
                debug_info.system = response.json()
        except Exception as e:
            debug_info.errors.append(f"System endpoint failed: {str(e)}")
        
        # Get session pools information (may fail)
        try:
            response = self.conn_pool.get("/debug/session_pools", timeout=5)
            if response.status_code == 200:
                debug_info.session_pools = response.json()
        except Exception as e:
            # This endpoint commonly fails, so don't treat as critical error
            logger.debug(f"Session pools endpoint failed (not critical): {str(e)}")
        
        return debug_info
    
    def format_server_stats(self, debug_info: ServerDebugInfo) -> str:
        """Format server debug information for display"""
        lines = []
        lines.append(f"🖥️  Server Statistics ({debug_info.get_health_summary()})")
        lines.append("=" * 60)
        
        # Threads information
        if debug_info.threads:
            lines.append(f"🧵 Threads:")
            lines.append(f"   Total: {debug_info.threads.get('total_threads', 'N/A')}")
            lines.append(f"   Active: {debug_info.threads.get('active_threads', 'N/A')}")
            lines.append(f"   Memory: {debug_info.threads.get('memory_mb', 0):.1f}MB")
            
            thread_details = debug_info.threads.get('thread_details', [])
            if thread_details:
                lines.append(f"   Names: {', '.join([t.get('name', 'Unknown') for t in thread_details[:5]])}")
                if len(thread_details) > 5:
                    lines.append(f"          ... and {len(thread_details) - 5} more")
        
        # System information
        if debug_info.system:
            system = debug_info.system
            
            # CPU info
            if 'cpu' in system:
                cpu = system['cpu']
                lines.append(f"💻 CPU:")
                lines.append(f"   Cores: {cpu.get('cpu_count', 'N/A')}")
                lines.append(f"   Usage: {cpu.get('cpu_percent', 0):.1f}%")
                load_avg = cpu.get('load_avg', [])
                if load_avg:
                    lines.append(f"   Load: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
            
            # Memory info
            if 'memory' in system:
                memory = system['memory']
                if 'virtual' in memory:
                    vm = memory['virtual']
                    lines.append(f"🧠 Memory:")
                    lines.append(f"   Total: {vm.get('total_gb', 0):.1f}GB")
                    lines.append(f"   Used: {vm.get('used_gb', 0):.1f}GB ({vm.get('percent', 0):.1f}%)")
                    lines.append(f"   Available: {vm.get('available_gb', 0):.1f}GB")
                
                if 'swap' in memory:
                    swap = memory['swap']
                    if swap.get('total_gb', 0) > 0:
                        lines.append(f"   Swap: {swap.get('used_gb', 0):.1f}GB / {swap.get('total_gb', 0):.1f}GB")
            
            # Process info
            if 'process' in system:
                proc = system['process']
                lines.append(f"⚙️  Process:")
                lines.append(f"   PID: {proc.get('pid', 'N/A')}")
                lines.append(f"   Status: {proc.get('status', 'N/A')}")
                lines.append(f"   CPU: {proc.get('cpu_percent', 0):.1f}%")
                lines.append(f"   Memory: {proc.get('memory_percent', 0):.1f}%")
            
            # Network info
            if 'network' in system:
                net = system['network']
                lines.append(f"🌐 Network:")
                lines.append(f"   Connections: {net.get('connections', 'N/A')}")
                if 'network_io' in net:
                    io = net['network_io']
                    sent_mb = io.get('bytes_sent', 0) / (1024 * 1024)
                    recv_mb = io.get('bytes_recv', 0) / (1024 * 1024)
                    lines.append(f"   Data: {sent_mb:.1f}MB sent, {recv_mb:.1f}MB received")
        
        # Storage information
        if debug_info.storage:
            lines.append(f"💾 Storage:")
            for storage in debug_info.storage[:3]:  # Show first 3 mounts
                lines.append(f"   {storage.device}: {storage.used_gb:.1f}GB / {storage.total_gb:.1f}GB ({storage.percent_used:.1f}%)")
            if len(debug_info.storage) > 3:
                lines.append(f"   ... and {len(debug_info.storage) - 3} more mounts")
        
        # Session pools (if available)
        if debug_info.session_pools:
            lines.append(f"🔧 ONNX Sessions: Available")
        
        # Errors
        if debug_info.errors:
            lines.append(f"⚠️  Warnings:")
            for error in debug_info.errors[:3]:
                lines.append(f"   • {error}")
            if len(debug_info.errors) > 3:
                lines.append(f"   ... and {len(debug_info.errors) - 3} more")
        
        return "\n".join(lines)
    
    def monitor_server_continuous(self, interval: int = 5, duration: int = 60, quiet_mode: bool = False) -> None:
        """
        Monitor server continuously for a specified duration.
        
        Args:
            interval: Update interval in seconds
            duration: Total monitoring duration in seconds
            quiet_mode: Suppress output
        """
        if not quiet_mode:
            print(f"🔍 Monitoring server for {duration}s (interval: {interval}s)")
            print("Press Ctrl+C to stop early")
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                debug_info = self.get_server_debug_info()
                
                # Clear screen (optional)
                if not quiet_mode:
                    print("\\033[H\\033[J", end="")  # ANSI clear screen
                    print(self.format_server_stats(debug_info))
                    print(f"\\nNext update in {interval}s... (Ctrl+C to stop)")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            if not quiet_mode:
                print("\\n🛑 Monitoring stopped by user")