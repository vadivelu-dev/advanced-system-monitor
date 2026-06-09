"""System statistics"""
import platform
import os
import psutil
import datetime
import json
from core.logger import setup_logger

logger = setup_logger(__name__)

class SystemStats:
    # Store history for charts
    _history = {
        'cpu': [],
        'memory': [],
        'disk': [],
        'network': []
    }
    
    @staticmethod
    def get_system_info():
        """Get system information"""
        info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_version': platform.python_version()
        }
        logger.info(f"System Info: {info['platform']} {info['platform_version']}")
        return info
    
    @staticmethod
    def get_uptime_info():
        """Get system uptime and user info"""
        try:
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            uptime_str = str(uptime).split('.')[0]
            
            # Get logged-in users
            users = []
            try:
                for user in psutil.users():
                    users.append(user.name)
            except:
                users = ['N/A']
            
            uptime_info = {
                'uptime': uptime_str,
                'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                'current_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'hostname': platform.node(),
                'logged_in_users': ', '.join(set(users)) if users else 'N/A'
            }
            logger.info("Uptime info retrieved")
            return uptime_info
        except Exception as e:
            logger.error(f"Error getting uptime info: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_cpu_info():
        """Get detailed CPU information"""
        try:
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'cpu_percent': round(psutil.cpu_percent(interval=1), 2),
                'cpu_freq': round(psutil.cpu_freq().current, 2) if psutil.cpu_freq() else 'N/A',
                'per_core_percent': [round(x, 2) for x in psutil.cpu_percent(interval=0.5, percpu=True)],
                'load_average': [round(x, 2) for x in os.getloadavg()] if hasattr(os, 'getloadavg') else 'N/A'
            }
            
            # Store history (keep only last 20 entries to save memory)
            SystemStats._history['cpu'].append({
                'timestamp': datetime.datetime.now().isoformat(),
                'percent': cpu_info['cpu_percent']
            })
            if len(SystemStats._history['cpu']) > 20:
                SystemStats._history['cpu'].pop(0)
            
            logger.info("CPU info retrieved")
            return cpu_info
        except Exception as e:
            logger.error(f"Error getting CPU info: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_memory_info():
        """Get detailed memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            memory_info = {
                'total': f"{memory.total / (1024**3):.2f}",
                'available': f"{memory.available / (1024**3):.2f}",
                'used': f"{memory.used / (1024**3):.2f}",
                'percent': round(memory.percent, 2),
                'swap_total': f"{swap.total / (1024**3):.2f}",
                'swap_used': f"{swap.used / (1024**3):.2f}",
                'swap_percent': round(swap.percent, 2),
                'unit': 'GB'
            }
            
            # Store history (keep only last 20 entries to save memory)
            SystemStats._history['memory'].append({
                'timestamp': datetime.datetime.now().isoformat(),
                'percent': memory_info['percent']
            })
            if len(SystemStats._history['memory']) > 20:
                SystemStats._history['memory'].pop(0)
            
            logger.info("Memory info retrieved")
            return memory_info
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_disk_info():
        """Get detailed disk information"""
        try:
            disk_info = {}
            # Get all disk partitions
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'total': f"{usage.total / (1024**3):.2f}",
                        'used': f"{usage.used / (1024**3):.2f}",
                        'free': f"{usage.free / (1024**3):.2f}",
                        'percent': round(usage.percent, 2),
                        'unit': 'GB',
                        'fstype': partition.fstype
                    }
                except PermissionError:
                    continue
            
            logger.info("Disk info retrieved")
            return disk_info
        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_network_info():
        """Get detailed network card information"""
        try:
            network_info = {}
            if_addrs = psutil.net_if_addrs()
            if_stats = psutil.net_if_stats()
            
            # Get network I/O counters
            net_io = psutil.net_io_counters()
            
            for interface, addrs in if_addrs.items():
                if interface not in if_stats:
                    continue
                    
                network_info[interface] = {
                    'status': 'Up' if if_stats[interface].isup else 'Down',
                    'speed': if_stats[interface].speed,
                    'mtu': if_stats[interface].mtu,
                    'addresses': []
                }
                for addr in addrs:
                    network_info[interface]['addresses'].append({
                        'family': addr.family.name,
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
            
            # Add network statistics
            network_stats = {
                'total_bytes_sent': f"{net_io.bytes_sent / (1024**3):.2f} GB",
                'total_bytes_recv': f"{net_io.bytes_recv / (1024**3):.2f} GB",
                'total_packets_sent': net_io.packets_sent,
                'total_packets_recv': net_io.packets_recv,
                'unit': 'GB'
            }
            
            logger.info("Network info retrieved")
            return {
                'interfaces': network_info,
                'statistics': network_stats
            }
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_temperature_info():
        """Get temperature information"""
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return {'info': 'Temperature sensors not available on this system'}
            
            temp_info = {}
            for device, readings in temps.items():
                temp_info[device] = []
                for reading in readings:
                    temp_info[device].append({
                        'name': reading.label or device,
                        'current': round(reading.current, 2),
                        'high': round(reading.high, 2) if reading.high else 'N/A',
                        'critical': round(reading.critical, 2) if reading.critical else 'N/A',
                        'unit': '°C'
                    })
            
            logger.info("Temperature info retrieved")
            return temp_info if temp_info else {'info': 'No temperature data available'}
        except Exception as e:
            logger.error(f"Error getting temperature info: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_battery_info():
        """Get battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return {'info': 'No battery detected (desktop system)'}
            
            battery_info = {
                'percent': round(battery.percent, 2),
                'is_charging': battery.power_plugged,
                'status': 'Charging' if battery.power_plugged else 'Discharging',
                'time_left': str(datetime.timedelta(seconds=battery.secsleft)) if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 'Calculating...'
            }
            
            logger.info("Battery info retrieved")
            return battery_info
        except Exception as e:
            logger.error(f"Error getting battery info: {e}")
            return {'info': 'Battery information not available'}
    
    @staticmethod
    def get_top_processes(sort_by='cpu', limit=10):
        """Get top processes by CPU, memory, disk, or network"""
        try:
            processes = []
            # Use ignore_running_procs for better performance
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'], ignore_running_procs=True):
                try:
                    pid = proc.info['pid']
                    name = proc.info['name']
                    if not pid or not name:
                        continue
                    cpu = proc.info['cpu_percent']
                    mem = proc.info['memory_percent']
                    # Skip processes with 0 values to reduce memory
                    if cpu is None or mem is None:
                        continue
                    processes.append({
                        'pid': pid,
                        'name': name[:40],  # Limit name length
                        'cpu_percent': round(cpu, 2),
                        'memory_percent': round(mem, 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    continue
            
            # Sort based on the parameter
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            else:
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            logger.info(f"Top processes retrieved (sorted by {sort_by})")
            return processes[:limit]
        except Exception as e:
            logger.error(f"Error getting top processes: {e}")
            return []
    
    @staticmethod
    def get_gpu_info():
        """Get GPU information"""
        try:
            import GPUtil
            # Get GPU info only once per request (not repeatedly)
            gpus = GPUtil.getGPUs()
            
            if not gpus:
                return {'info': 'No NVIDIA GPU detected'}
            
            gpu_info = {}
            for gpu in gpus:
                # Only get essential GPU data
                gpu_info[f'GPU {gpu.id}'] = {
                    'name': gpu.name,
                    'load': round(gpu.load * 100, 2),
                    'memory_used': f"{gpu.memoryUsed:.0f} MB",
                    'memory_total': f"{gpu.memoryTotal:.0f} MB",
                    'memory_percent': round((gpu.memoryUsed / gpu.memoryTotal) * 100, 2),
                    'temperature': f"{gpu.temperature}°C" if gpu.temperature else 'N/A',
                    'unit': '%'
                }
            
            logger.info("GPU info retrieved")
            return gpu_info
        except ImportError:
            return {'info': 'GPUtil not available'}
        except Exception as e:
            logger.error(f"Error getting GPU info: {e}")
            return {'info': 'GPU information not available'}
    
    @staticmethod
    def get_system_alerts():
        """Get system alerts based on thresholds"""
        alerts = []
        
        try:
            # CPU alert
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                alerts.append({
                    'type': 'warning',
                    'message': f'High CPU usage: {cpu_percent}%'
                })
            
            # Memory alert
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                alerts.append({
                    'type': 'warning',
                    'message': f'High memory usage: {memory.percent}%'
                })
            
            # Disk alert
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    if usage.percent > 90:
                        alerts.append({
                            'type': 'danger',
                            'message': f'Low disk space on {partition.device}: {usage.percent}% used'
                        })
                except PermissionError:
                    continue
            
            # Temperature alert (if available)
            temps = psutil.sensors_temperatures()
            if temps:
                for device, readings in temps.items():
                    for reading in readings:
                        if reading.high and reading.current > reading.high:
                            alerts.append({
                                'type': 'danger',
                                'message': f'High temperature on {reading.label or device}: {reading.current}°C'
                            })
        
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
        
        return alerts
    
    @staticmethod
    def get_chart_data(metric='cpu'):
        """Get historical data for charts"""
        if metric in SystemStats._history:
            return SystemStats._history[metric]
        return []
    
    @staticmethod
    def get_disk_usage():
        """Get disk usage stats"""
        try:
            total, used, free = os.statvfs('/').f_blocks, os.statvfs('/').f_bavail, 0
            logger.info("Disk usage retrieved")
            return {"total_blocks": total, "free_blocks": free}
        except:
            logger.warning("Could not retrieve disk usage")
            return None
