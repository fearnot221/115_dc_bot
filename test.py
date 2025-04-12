import requests
import time

def get_proxmox_ticket():
    url = 'https://pve.fearnot.tw/api2/json/access/ticket'
    data = {
        'username': 'mcserver@pve',
        'password': 'mcserver'
    }

    response = requests.post(url, data=data, verify=False)
    response.raise_for_status()

    result = response.json()['data']
    return result['ticket'], result['CSRFPreventionToken']

def start_vm(node: str, vmid: int, ticket: str, csrf: str):
    url = f'https://pve.fearnot.tw/api2/json/nodes/{node}/qemu/{vmid}/status/start'
    headers = {
        'CSRFPreventionToken': csrf,
        'Cookie': f'PVEAuthCookie={ticket}'
    }

    response = requests.post(url, headers=headers, verify=False)
    response.raise_for_status()
    print(f"🚀 啟動請求已送出")

    # 等待開機完成
    wait_for_vm_status(node, vmid, ticket, 'running')

def shutdown_vm(node: str, vmid: int, ticket: str, csrf: str):
    url = f'https://pve.fearnot.tw/api2/json/nodes/{node}/qemu/{vmid}/status/shutdown'
    headers = {
        'CSRFPreventionToken': csrf,
        'Cookie': f'PVEAuthCookie={ticket}'
    }

    response = requests.post(url, headers=headers, verify=False)
    response.raise_for_status()
    print(f"📴 關機請求已送出")

    # 等待關機完成
    wait_for_vm_status(node, vmid, ticket, 'stopped')

    
def get_vm_status(node: str, vmid: int, ticket: str):
    url = f'https://pve.fearnot.tw/api2/json/nodes/{node}/qemu/{vmid}/status/current'
    headers = {
        'Cookie': f'PVEAuthCookie={ticket}'
    }

    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    status = response.json()['data']['status']
    return status

def wait_for_vm_status(node: str, vmid: int, ticket: str, target_status: str, timeout: int = 60):
    url = f'https://pve.fearnot.tw/api2/json/nodes/{node}/qemu/{vmid}/status/current'
    headers = {
        'Cookie': f'PVEAuthCookie={ticket}'
    }

    print(f"⏳ 等待 VM {vmid} 進入狀態：{target_status} ...")
    for i in range(timeout):
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        status = response.json()['data']['status']
        if status == target_status:
            print(f"✅ VM {vmid} 已完成狀態轉換：{target_status}")
            return True
        time.sleep(2)

    print(f"⚠️ 等待超時，VM 狀態仍為 {status}")
    return False

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()  # 關閉 SSL 警告

    node = 'pve'       # 你的 Proxmox 節點名稱
    vmid = 100         # 要操作的 VM ID

    ticket, csrf = get_proxmox_ticket()

    # 啟動 VM
    # start_vm(node, vmid, ticket, csrf)

    # 關機 VM（如果要測試）
    shutdown_vm(node, vmid, ticket, csrf)
