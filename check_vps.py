import paramiko

def check_vps():
    host = "45.55.92.211"
    user = "root"
    password = "36C&5U_Z&SH4rq"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password, timeout=10)
        
        stdin, stdout, stderr = ssh.exec_command("python3 /root/GanoiTouch/whatsapp_bot.py")
        print("STDOUT:")
        print(stdout.read().decode())
        print("STDERR:")
        print(stderr.read().decode())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_vps()
