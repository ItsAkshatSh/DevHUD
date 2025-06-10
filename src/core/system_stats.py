import psutil
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

class SystemStats(QObject):
    stats_updated = pyqtSignal(dict)  
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.update_interval = 1.0  
        self.monitor_thread = None
        self.gpu_available = False
        
        try:
            import GPUtil
            self.gpu_available = len(GPUtil.getGPUs()) > 0
        except ImportError:
            self.gpu_available = False
            
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            stats = self._collect_stats()
            self.stats_updated.emit(stats)
            time.sleep(self.update_interval)
            
    def _collect_stats(self):
        """Collect current system statistics"""
        stats = {
            'cpu': self._get_cpu_stats(),
            'memory': self._get_memory_stats(),
            'gpu': self._get_gpu_stats() if self.gpu_available else None
        }
        return stats
        
    def _get_cpu_stats(self):
        """Get CPU usage statistics"""
        cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        
        return {
            'percent_per_core': cpu_percent,
            'total_percent': sum(cpu_percent) / len(cpu_percent),
            'frequency': {
                'current': cpu_freq.current if cpu_freq else None,
                'min': cpu_freq.min if cpu_freq else None,
                'max': cpu_freq.max if cpu_freq else None
            },
            'cores': cpu_count
        }
        
    def _get_memory_stats(self):
        """Get memory usage statistics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
        }
        
    def _get_gpu_stats(self):
        """Get GPU usage statistics if available"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return [{
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': gpu.load * 100,  # Convert to percentage
                    'memory': {
                        'total': gpu.memoryTotal,
                        'used': gpu.memoryUsed,
                        'free': gpu.memoryFree
                    },
                    'temperature': gpu.temperature
                } for gpu in gpus]
        except Exception:
            return None
            
    def set_update_interval(self, interval):
        """Set the update interval in seconds"""
        self.update_interval = max(0.1, interval) 