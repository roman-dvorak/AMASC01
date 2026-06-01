"""
Unix socket server for IPC
"""
import socket
import threading
import json
import os
import logging

from . import config

logger = logging.getLogger(__name__)

class SocketServer:
    """Unix domain socket server for IPC"""
    
    def __init__(self, controller, socket_path=config.SOCKET_PATH):
        self.controller = controller
        self.socket_path = socket_path
        self.running = False
        self.server_socket = None
        self.thread = None
        
    def start(self):
        """Start socket server in background thread"""
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        logger.info(f"Socket server started on {self.socket_path}")
        
    def stop(self):
        """Stop socket server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        logger.info("Socket server stopped")
    
    def _run_server(self):
        """Main server loop"""
        # Remove old socket if exists
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        # Create socket
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        os.chmod(self.socket_path, 0o666)  # Allow all users to connect
        self.server_socket.listen(5)
        self.server_socket.settimeout(1.0)  # Timeout for clean shutdown
        
        while self.running:
            try:
                client, _ = self.server_socket.accept()
                self._handle_client(client)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Socket server error: {e}")
    
    def _handle_client(self, client):
        """Handle client connection"""
        try:
            # Receive command
            data = client.recv(4096).decode('utf-8')
            if not data:
                return
            
            command = json.loads(data)
            response = self._process_command(command)
            
            # Send response
            client.send(json.dumps(response).encode('utf-8'))
        except Exception as e:
            error_response = {"error": str(e)}
            try:
                client.send(json.dumps(error_response).encode('utf-8'))
            except:
                pass
        finally:
            client.close()
    
    def _process_command(self, command):
        """Process command and return response"""
        cmd_type = command.get('command')
        
        if cmd_type == 'status':
            return self.controller.get_status()
        
        elif cmd_type == 'set-target':
            temp = command.get('temperature')
            if temp is None or temp > 60.0 or temp < 0:
                return {"error": "Invalid temperature (must be 0-60°C)"}
            self.controller.set_target_temperature(temp)
            return {"success": True, "target_temp": temp}
        
        elif cmd_type == 'set-cooling':
            min_temp = command.get('min')
            max_temp = command.get('max')
            if min_temp is not None:
                self.controller.set_cooling_min(min_temp)
            if max_temp is not None:
                self.controller.set_cooling_max(max_temp)
            return {"success": True, "cooling_min": config.COOLING_TEMP_MIN, "cooling_max": config.COOLING_TEMP_MAX}
        
        elif cmd_type == 'fan-override':
            percent = command.get('percent')
            if percent is None or percent < 0 or percent > 100:
                return {"error": "Invalid fan percent (0-100)"}
            self.controller.fan_override = percent
            return {"success": True, "fan_override": percent}
        
        elif cmd_type == 'heater-override':
            percent = command.get('percent')
            if percent is None or percent < 0 or percent > 100:
                return {"error": "Invalid heater percent (0-100)"}
            self.controller.heater_override = percent
            return {"success": True, "heater_override": percent}
        
        elif cmd_type == 'heater-auto':
            self.controller.heater_override = None
            return {"success": True, "heater_mode": "auto"}

        elif cmd_type == 'fan-auto':
            self.controller.fan_override = None
            return {"success": True, "fan_mode": "auto"}
        
        elif cmd_type == 'set-pid':
            kp = command.get('kp')
            ki = command.get('ki')
            kd = command.get('kd')
            if kp is not None:
                self.controller.pid.kp = kp
            if ki is not None:
                self.controller.pid.ki = ki
            if kd is not None:
                self.controller.pid.kd = kd
            return {"success": True, "kp": self.controller.pid.kp, "ki": self.controller.pid.ki, "kd": self.controller.pid.kd}
        
        else:
            return {"error": f"Unknown command: {cmd_type}"}
