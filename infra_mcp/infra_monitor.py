"""
Infrastructure monitoring utilities for collecting system information.
"""

import os
import subprocess
import psutil
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path


logger = logging.getLogger(__name__)


class InfraMonitor:
    """Infrastructure monitoring and data collection utilities."""
    
    def __init__(self):
        self.log_paths = [
            "/var/log/syslog",
            "/var/log/auth.log", 
            "/var/log/kern.log",
            "/var/log/dmesg",
            "/var/log/messages",
            "/var/log/system.log",  # macOS
            "/var/log/boot.log"
        ]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uname = os.uname()
            return {
                "hostname": uname.nodename,
                "platform": uname.sysname,
                "platform_release": uname.release,
                "platform_version": uname.version,
                "architecture": uname.machine,
                "processor": getattr(uname, 'processor', 'unknown'),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used,
                    "free": psutil.virtual_memory().free
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "boot_time": boot_time.isoformat(),
                "uptime": str(datetime.now() - boot_time)
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}
    
    def get_service_status(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get service status using systemctl (Linux) or other system tools."""
        try:
            services = {}
            
            if service_name:
                # Get specific service status
                result = self._get_systemd_service_status(service_name)
                if result:
                    services[service_name] = result
            else:
                # Get common services status
                common_services = [
                    "ssh", "sshd", "nginx", "apache2", "httpd", "docker", 
                    "postgres", "mysql", "redis", "mongodb", "cron", "crond"
                ]
                
                for service in common_services:
                    status = self._get_systemd_service_status(service)
                    if status:
                        services[service] = status
            
            # Add running processes info
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort processes by CPU usage, handling None values
            sorted_processes = sorted(
                processes, 
                key=lambda x: x.get('cpu_percent') or 0, 
                reverse=True
            )[:10]
            
            return {
                "services": services,
                "total_processes": len(processes),
                "top_processes": sorted_processes
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {"error": str(e)}
    
    def _get_systemd_service_status(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get systemd service status."""
        try:
            # Try with .service extension first
            result = subprocess.run(
                ["systemctl", "is-active", f"{service_name}.service"],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                status = result.stdout.strip()
            else:
                # Try without .service extension
                result = subprocess.run(
                    ["systemctl", "is-active", service_name],
                    capture_output=True, text=True, timeout=5
                )
                status = result.stdout.strip() if result.returncode == 0 else "inactive"
            
            # Get enabled status
            enabled_result = subprocess.run(
                ["systemctl", "is-enabled", f"{service_name}.service"],
                capture_output=True, text=True, timeout=5
            )
            enabled = enabled_result.stdout.strip() if enabled_result.returncode == 0 else "unknown"
            
            return {
                "status": status,
                "enabled": enabled,
                "checked_at": datetime.now().isoformat()
            }
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # systemctl not available or service doesn't exist
            return None
        except Exception as e:
            logger.error(f"Error checking service {service_name}: {e}")
            return None
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user information and active sessions."""
        try:
            users = {}
            
            # Get current users
            for user in psutil.users():
                if user.name not in users:
                    users[user.name] = []
                users[user.name].append({
                    "terminal": user.terminal,
                    "host": user.host,
                    "started": datetime.fromtimestamp(user.started).isoformat(),
                    "pid": user.pid if hasattr(user, 'pid') else None
                })
            
            # Try to get additional user info from /etc/passwd
            passwd_users = []
            try:
                with open('/etc/passwd', 'r') as f:
                    for line in f:
                        parts = line.strip().split(':')
                        if len(parts) >= 6:
                            passwd_users.append({
                                "username": parts[0],
                                "uid": parts[2],
                                "gid": parts[3],
                                "home": parts[5],
                                "shell": parts[6] if len(parts) > 6 else ""
                            })
            except (FileNotFoundError, PermissionError):
                pass
            
            return {
                "active_sessions": users,
                "total_active_users": len(users),
                "system_users": passwd_users,
                "current_user": os.getenv('USER', 'unknown'),
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {"error": str(e)}
    
    def get_logs(self, log_type: str = "syslog", lines: int = 100, since: Optional[str] = None) -> Dict[str, Any]:
        """Get system logs."""
        try:
            logs = []
            log_file = None
            
            # Determine log file path
            if log_type == "syslog":
                log_file = "/var/log/syslog"
            elif log_type == "auth":
                log_file = "/var/log/auth.log"
            elif log_type == "kernel":
                log_file = "/var/log/kern.log"
            elif log_type == "dmesg":
                # Use dmesg command for kernel ring buffer
                try:
                    result = subprocess.run(
                        ["dmesg", "--time-format=iso", f"--lines={lines}"],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        logs = result.stdout.strip().split('\n')
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    pass
            else:
                # Try to find the log file in common locations
                for path in self.log_paths:
                    if log_type in path and os.path.exists(path):
                        log_file = path
                        break
            
            # Read from log file if found
            if log_file and os.path.exists(log_file) and not logs:
                try:
                    with open(log_file, 'r') as f:
                        all_lines = f.readlines()
                        logs = [line.strip() for line in all_lines[-lines:]]
                except PermissionError:
                    # Try using tail command
                    try:
                        result = subprocess.run(
                            ["tail", f"-{lines}", log_file],
                            capture_output=True, text=True, timeout=10
                        )
                        if result.returncode == 0:
                            logs = result.stdout.strip().split('\n')
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                        pass
            
            return {
                "log_type": log_type,
                "log_file": log_file,
                "lines_requested": lines,
                "lines_returned": len(logs),
                "logs": logs,
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return {"error": str(e)}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network interface and connection information."""
        try:
            interfaces = {}
            for interface, addresses in psutil.net_if_addrs().items():
                interface_info = {
                    "addresses": [],
                    "stats": None
                }
                
                for addr in addresses:
                    interface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
                
                # Get interface statistics
                try:
                    stats = psutil.net_if_stats()[interface]
                    interface_info["stats"] = {
                        "isup": stats.isup,
                        "duplex": str(stats.duplex),
                        "speed": stats.speed,
                        "mtu": stats.mtu
                    }
                except KeyError:
                    pass
                
                interfaces[interface] = interface_info
            
            # Get network connections
            connections = []
            try:
                for conn in psutil.net_connections():
                    connections.append({
                        "fd": conn.fd,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status,
                        "pid": conn.pid
                    })
            except psutil.AccessDenied:
                connections = ["Access denied - run with elevated privileges for connection details"]
            
            return {
                "interfaces": interfaces,
                "connections": connections[:20],  # Limit to avoid overwhelming output
                "io_counters": dict(psutil.net_io_counters()._asdict()),
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            return {"error": str(e)}

