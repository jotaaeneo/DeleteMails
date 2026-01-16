import paramiko

hostname = ''
port = ''
username = ''
password = ''

remote_command = ''

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    
    client.connect(hostname, port=port, username=username, password=password)
    print(f"Connected to {hostname} on port {port} as {username}")
    stdin, stdout, stderr = client.exec_command(remote_command)
    print(f"Executing command: {remote_command}")
    output = stdout.read().decode()
    print("stdout.read().decode()")

    client.close()
    print("CONNECTIOJ CLOSED")
except Exception as e:
    print(f"An ocurred Error: {e}")
