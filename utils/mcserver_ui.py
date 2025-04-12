import discord
from discord.ui import Button, View
import requests
import time
import urllib3
urllib3.disable_warnings()

class Mcserver(View):
    def __init__(self, bot=None, message=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.message = message
        self.emoji = self.bot.emoji

        start_button = Button(
            label="開機",
            style=discord.ButtonStyle.success,
            emoji=self.emoji.get('green_fire'),
            custom_id="start_mcserver"
        )
        start_button.callback = self.start_callback

        stop_button = Button(
            label="關機",
            style=discord.ButtonStyle.danger,
            emoji=self.emoji.get('red_fire'),
            custom_id="stop_mcserver"
        )
        stop_button.callback = self.stop_callback

        self.add_item(start_button)
        self.add_item(stop_button)

    async def update_panel(self):
        ticket, _ = self.get_proxmox_ticket()
        status = self.get_vm_status("pve", 100, ticket)
        status_str = {
            "running": f"🟢 **運行中**",
            "stopped": f"🔴 **已關機**"
        }.get(status, f"❓ 狀態未知：`{status}`")

        embed = discord.Embed(
            title=f"{self.emoji.get('minecraft')} 麥塊伺服器控制面板",
            description=(
                f"按下 {self.emoji.get('green_fire')} **開機**\n"
                f"按下 {self.emoji.get('red_fire')} **關機**\n\n"
                f"🖥️ 伺服器狀態：{status_str}"
            ),
            color=discord.Color.blue()
        )
        await self.message.edit(embed=embed, view=self)

    async def start_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        msg = await interaction.followup.send("🟢 正在開機中...", ephemeral=True)

        ticket, csrf = self.get_proxmox_ticket()
        status = self.get_vm_status("pve", 100, ticket)

        if status == "running":
            await msg.edit(content="✅ 伺服器已經在運行中！")
        elif status == "stopped":
            self.start_vm("pve", 100, ticket, csrf)
            self.wait_for_vm_status("pve", 100, ticket, "running")
            await msg.edit(content="✅ 開機完成！")

        await self.update_panel()

    async def stop_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        msg = await interaction.followup.send("🔴 正在關機中...", ephemeral=True)

        ticket, csrf = self.get_proxmox_ticket()
        status = self.get_vm_status("pve", 100, ticket)

        if status == "stopped":
            await msg.edit(content="✅ 伺服器已經關機了！")
        elif status == "running":
            self.shutdown_vm("pve", 100, ticket, csrf)
            self.wait_for_vm_status("pve", 100, ticket, "stopped")
            await msg.edit(content="✅ 關機完成！")

        await self.update_panel()

    def get_proxmox_ticket(self):
        url = 'https://pve.fearnot.tw/api2/json/access/ticket'
        data = {
            'username': 'mcserver@pve',
            'password': 'mcserver'
        }
        response = requests.post(url, data=data, verify=False)
        response.raise_for_status()
        result = response.json()['data']
        return result['ticket'], result['CSRFPreventionToken']

    def get_vm_status(self, node: str, vmid: int, ticket: str):
        url = f'https://pve.fearnot.tw/api2/json/nodes/{node}/qemu/{vmid}/status/current'
        headers = {
            'Cookie': f'PVEAuthCookie={ticket}'
        }
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()['data']['status']

    def start_vm(self, node: str, vmid: int, ticket: str, csrf: str):
        url = f'https://pve.fearnot.tw/api2/json/nodes/{node}/qemu/{vmid}/status/start'
        headers = {
            'CSRFPreventionToken': csrf,
            'Cookie': f'PVEAuthCookie={ticket}'
        }
        response = requests.post(url, headers=headers, verify=False)
        response.raise_for_status()

    def shutdown_vm(self, node: str, vmid: int, ticket: str, csrf: str):
        url = f'https://pve.fearnot.tw/api2/json/nodes/{node}/qemu/{vmid}/status/shutdown'
        headers = {
            'CSRFPreventionToken': csrf,
            'Cookie': f'PVEAuthCookie={ticket}'
        }
        response = requests.post(url, headers=headers, verify=False)
        response.raise_for_status()

    def wait_for_vm_status(self, node: str, vmid: int, ticket: str, target_status: str, timeout: int = 60):
        url = f'https://pve.fearnot.tw/api2/json/nodes/{node}/qemu/{vmid}/status/current'
        headers = {
            'Cookie': f'PVEAuthCookie={ticket}'
        }
        for _ in range(timeout):
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            status = response.json()['data']['status']
            if status == target_status:
                return True
            time.sleep(2)
        return False

def setup_persistent_views_mcserver(bot):
    try:
        bot.add_view(Mcserver(bot=bot))
        return True
    except Exception as e:
        print(f"設定持久化視圖時發生錯誤: {e}")
        return False
