import paramiko
import time

def deploy():
    host = "45.55.92.211"
    user = "root"
    password = "36C&5U_Z&SH4rq"

    print(f"Conectando a {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password, timeout=10)
        print("Conexión exitosa. Ejecutando actualización (git pull)...")
        
        commands = [
            "cd /root/GanoiTouch && git fetch origin && git reset --hard origin/main && git clean -fd",
            "cd /root/GanoiTouch && pip install -r requirements.txt --break-system-packages",
            "cd /root/GanoiTouch && bash restart_ninja.sh"
        ]
        
        for cmd in commands:
            print(f"Ejecutando: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            # Imprimir salida
            for line in stdout:
                print(line.strip('\n'))
            for line in stderr:
                print("ERROR: ", line.strip('\n'))
                
        print("¡Despliegue finalizado exitosamente!")
    except Exception as e:
        print(f"Error en el despliegue: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
