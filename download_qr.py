import paramiko

def download_qr():
    host = "45.55.92.211"
    user = "root"
    password = "36C&5U_Z&SH4rq"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password, timeout=10)
        sftp = ssh.open_sftp()
        sftp.get("/root/GanoiTouch/qr_login_1.png", "C:\\GanoiTouch\\qr_login_1.png")
        print("QR descargado exitosamente.")
        sftp.close()
    except Exception as e:
        print(f"Error descargando QR: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    download_qr()
