"""
Data models and dataclasses for the TTS system.

This module contains all the dataclass definitions used throughout the TTS system.
Layer 1 - Foundation: No dependencies on other modules.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class PreloadMessage:
    """Represents a preloadable message with metadata"""
    text: str
    voice: str = "af_bella"
    speed: float = 1.0
    format_type: str = "wav"
    generated_at: Optional[float] = None
    audio_data: Optional[bytes] = None


@dataclass
class ThreadInfo:
    """Thread information from server debug endpoint"""
    name: str
    id: int
    alive: bool
    daemon: bool


@dataclass
class StorageInfo:
    """Storage information from server debug endpoint"""
    device: str
    mountpoint: str
    fstype: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float


@dataclass
class CPUInfo:
    """CPU information from server debug endpoint"""
    cpu_count: int
    cpu_percent: float
    per_cpu_percent: List[float]
    load_avg: List[float]


@dataclass
class MemoryInfo:
    """Memory information from server debug endpoint"""
    total_gb: float
    available_gb: float
    used_gb: float
    percent: float


@dataclass
class ProcessInfo:
    """Process information from server debug endpoint"""
    pid: int
    status: str
    create_time: str
    cpu_percent: float
    memory_percent: float


@dataclass
class NetworkInfo:
    """Network information from server debug endpoint"""
    connections: int
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int


@dataclass
class ServerDebugInfo:
    """Complete server debug information"""
    timestamp: float
    threads: Optional[Dict[str, Any]] = None
    storage: Optional[List[StorageInfo]] = None
    system: Optional[Dict[str, Any]] = None
    session_pools: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    
    def is_healthy(self) -> bool:
        """Assess overall server health"""
        if self.errors:
            return False
        
        # Check CPU usage
        if self.system and 'cpu' in self.system:
            cpu_percent = self.system['cpu'].get('cpu_percent', 0)
            if cpu_percent > 90:
                return False
        
        # Check memory usage
        if self.system and 'memory' in self.system:
            memory = self.system['memory'].get('virtual', {})
            memory_percent = memory.get('percent', 0)
            if memory_percent > 95:
                return False
        
        # Check storage usage
        if self.storage:
            for storage in self.storage:
                if storage.percent_used > 95:
                    return False
        
        return True
    
    def get_health_summary(self) -> str:
        """Get a summary of server health"""
        if not self.is_healthy():
            return "🔴 UNHEALTHY"
        
        issues = []
        
        # Check for moderate resource usage
        if self.system and 'cpu' in self.system:
            cpu_percent = self.system['cpu'].get('cpu_percent', 0)
            if cpu_percent > 70:
                issues.append(f"High CPU: {cpu_percent:.1f}%")
        
        if self.system and 'memory' in self.system:
            memory = self.system['memory'].get('virtual', {})
            memory_percent = memory.get('percent', 0)
            if memory_percent > 80:
                issues.append(f"High Memory: {memory_percent:.1f}%")
        
        if self.storage:
            for storage in self.storage:
                if storage.percent_used > 80:
                    issues.append(f"Storage {storage.device}: {storage.percent_used:.1f}%")
        
        if issues:
            return f"🟡 WARNING: {'; '.join(issues)}"
        
        return "🟢 HEALTHY"