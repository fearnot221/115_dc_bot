import discord
from discord.ui import Button, View
import requests
import time
import urllib3
urllib3.disable_warnings()  # 關閉 SSL 警告


class Mcserver(View):
    def __init__(self, bot=None):
        super().__init__(timeout=None)
        self.bot = bot
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

    async def start_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        node = 'pve'
        vmid = 100

        try:
            ticket, csrf = self.get_proxmox_ticket()
            status = self.get_vm_status(node, vmid, ticket)

            if status == "running":
                msg = discord.Embed(
                    title="✅ 伺服器已啟動",
                    description="Minecraft 伺服器目前已經在執行中。",
                    color=discord.Color.green()
                )
            elif status == "stopped":
                self.start_vm(node, vmid, ticket, csrf)
                msg = discord.Embed(
                    title="🟢 開機中...",
                    description="Minecraft 伺服器正在啟動，請稍候...",
                    color=discord.Color.blue()
                )
                await interaction.followup.send(embed=msg, ephemeral=True)

                if self.wait_for_vm_status(node, vmid, ticket, "running"):
                    msg = discord.Embed(
                        title="🎉 開機完成",
                        description="伺服器已啟動，可以進入遊戲了！",
                        color=discord.Color.green()
                    )
                else:
                    msg = discord.Embed(
                        title="⚠️ 開機失敗",
                        description="伺服器未在預期時間內啟動。",
                        color=discord.Color.red()
                    )
            else:
                msg = discord.Embed(
                    title="⚠️ 狀態錯誤",
                    description=f"目前無法處理的 VM 狀態：`{status}`",
                    color=discord.Color.red()
                )

        except Exception as e:
            msg = discord.Embed(
                title="❌ 錯誤",
                description=f"開機失敗：{str(e)}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=msg, ephemeral=True)

    async def stop_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        node = 'pve'
        vmid = 100

        try:
            ticket, csrf = self.get_proxmox_ticket()
            status = self.get_vm_status(node, vmid, ticket)

            if status == "stopped":
                msg = discord.Embed(
                    title="📴 伺服器尚未開機",
                    description="目前伺服器已關閉，無需關機。",
                    color=discord.Color.yellow()
                )
            elif status == "running":
                self.shutdown_vm(node, vmid, ticket, csrf)
                msg = discord.Embed(
                    title="🛑 關機中...",
                    description="伺服器正在關機中，請稍候...",
                    color=discord.Color.yellow()
                )
                await interaction.followup.send(embed=msg, ephemeral=True)

                if self.wait_for_vm_status(node, vmid, ticket, "stopped"):
                    msg = discord.Embed(
                        title="✅ 關機完成",
                        description="伺服器已成功關閉。",
                        color=discord.Color.green()
                    )
                else:
                    msg = discord.Embed(
                        title="⚠️ 關機失敗",
                        description="伺服器未在預期時間內關機。",
                        color=discord.Color.red()
                    )
            else:
                msg = discord.Embed(
                    title="⚠️ 狀態錯誤",
                    description=f"目前無法處理的 VM 狀態：`{status}`",
                    color=discord.Color.red()
                )

        except Exception as e:
            msg = discord.Embed(
                title="❌ 錯誤",
                description=f"關機失敗：{str(e)}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=msg, ephemeral=True)

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
