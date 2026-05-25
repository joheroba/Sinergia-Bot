import paramiko

def setup_vnc():
    host = "45.55.92.211"
    user = "root"
    password = "36C&5U_Z&SH4rq"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password, timeout=10)
        
        commands = [
            "apt-get update",
            "apt-get install -y x11vnc novnc websockify xvfb",
            "pkill x11vnc || true",
            "pkill websockify || true",
            "nohup x11vnc -display :99 -nopw -listen localhost -xkb -ncache 10 -ncache_cr -forever > /root/x11vnc.log 2>&1 &",
            "nohup websockify --web /usr/share/novnc/ 6080 localhost:5900 > /root/websockify.log 2>&1 &",
            "ufw allow 6080"
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())
            
        print("VNC Setup Complete.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    setup_vnc()
