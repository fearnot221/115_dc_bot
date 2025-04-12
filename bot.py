import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import json
from datetime import datetime
import logging
from dotenv import load_dotenv
from utils.role_ui import setup_persistent_views_role
from utils.exchange_ui import setup_persistent_views_exchange
from utils.role_button_ui import setup_persistent_views_role_button
from utils.mcserver.ui import setup_persistent_views_mcserver

# 設定 log
logging.basicConfig(level=logging.INFO)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# 檢查是否具有 admin 權限
def is_admin():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

# 載入特定資料夾中的所有 JSON 檔案
def load_json_folder(folder_path: str) -> dict:
    data = {}
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                name = filename.replace('.json', '')
                try:
                    with open(f"{folder_path}/{filename}", 'r', encoding='utf-8') as f:
                        data[name] = json.load(f)
                    logging.info(f"已載入 JSON 檔案: {filename}")
                except Exception as e:
                    logging.error(f"載入 JSON 檔案 {filename} 時發生錯誤: {str(e)}")
    else:
        logging.warning(f"資料夾 {folder_path} 不存在")
    return data

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='/',
            intents=intents
        )

        # Discord API 請求監控
        self.system_status = "normal"
        self.request_count = 0
        self.last_reset = datetime.now()
        self.rate_limit_hits = 0
        self.activity_index = 0

        # 建立資料目錄（若不存在）
        os.makedirs('data/config', exist_ok=True)
        os.makedirs('data/database', exist_ok=True)

        # 初始化 JSON 資料
        self.config_data = {}  # 用於存儲所有伺服器的配置
        self.verification_data = {}  # 用於存儲所有伺服器的驗證資料
        self.emoji_data = {}  # 用於存儲所有表情符號資料

        # 簡化的 emoji 字典，可直接通過 emoji 名稱取得格式
        self.emoji = {}  # 用於直接通過名稱取得 emoji 格式

        # 載入 JSON 資料
        self.load_all_json_data()

        # 載入所有 cogs 的清單
        self.loadcogs = []
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                self.loadcogs.append(f'cogs.{filename[:-3]}')

    def load_all_json_data(self):
        """載入所有 JSON 檔案"""
        try:
            # 載入 config
            config_files = [f for f in os.listdir('data/config') if f.startswith('config_')]
            for config_file in config_files:
                guild_id = config_file.split('_')[-1].replace('.json', '')
                try:
                    with open(f'data/config/{config_file}', 'r', encoding='utf-8') as f:
                        self.config_data[guild_id] = json.load(f)
                except Exception as e:
                    logging.error(f"載入 {config_file} 時發生錯誤: {str(e)}")

            # 載入 verification
            verification_files = [f for f in os.listdir('data/config') if f.startswith('verification_') and not f.endswith('example.json')]
            for verification_file in verification_files:
                guild_id = verification_file.split('_')[-1].replace('.json', '')
                try:
                    with open(f'data/config/{verification_file}', 'r', encoding='utf-8') as f:
                        self.verification_data[guild_id] = json.load(f)
                except Exception as e:
                    logging.error(f"載入 {verification_file} 時發生錯誤: {str(e)}")

            # 載入 emoji
            emoji_file = 'data/config/emoji.json'
            if os.path.exists(emoji_file):
                try:
                    with open(emoji_file, 'r', encoding='utf-8') as f:
                        emoji_data = json.load(f)
                        self.emoji_data = emoji_data

                        if 'emojis' in emoji_data:
                            for emoji_name, emoji_info in emoji_data['emojis'].items():
                                if 'format' in emoji_info:
                                    self.emoji[emoji_name] = emoji_info['format']
                except Exception as e:
                    logging.error(f"載入 {emoji_file} 時發生錯誤: {str(e)}")
            else:
                # 如果全局表情文件不存在，創建一個空的
                with open(emoji_file, 'w', encoding='utf-8') as f:
                    json.dump({"emojis": {}}, f, ensure_ascii=False, indent=4)

            logging.info("JSON 資料載入完成")
        except Exception as e:
            logging.error(f"載入 JSON 資料時發生錯誤: {str(e)}")

    def get_emoji(self, name):
        return self.emoji.get(name, f":{name}:")

    @tasks.loop(seconds=30)
    async def status_monitor(self):
        """定期更新機器人狀態"""
        try:
            activities = [
                discord.Game(name=f"| 燒雞中..."),
                discord.Game(name=f"| 還沒上岸嗚嗚嗚 T_T"),
            ]
            self.activity_index = (self.activity_index + 1) % len(activities)
            await self.change_presence(
                activity=activities[self.activity_index],
                status=discord.Status.online
            )
        except Exception as e:
            logging.error(f"Status monitor error: {e}")

    @status_monitor.before_loop
    async def before_status_monitor(self):
        await self.wait_until_ready()

    @tasks.loop(count=1)
    async def setup_bot(self):
        """初始化伺服器數據庫"""
        for guild in self.guilds:
            try:
                identity_cog = self.get_cog('IdentityManagement')
                if identity_cog:
                    await identity_cog.cogs_load(guild.id)
            except Exception as e:
                logging.error(f"初始化伺服器 {guild.name} ({guild.id}) 的數據庫時出錯: {e}")

    @setup_bot.before_loop
    async def before_setup_bot(self):
        await self.wait_until_ready()

    async def setup_hook(self):
        """設置機器人啟動時的初始化邏輯"""
        setup_successful = setup_persistent_views_role(self) and setup_persistent_views_exchange(self) and setup_persistent_views_role_button(self) and setup_persistent_views_mcserver(self)
        if not setup_successful:
            logging.warning("持久化視圖設置可能不完整")
        else:
            logging.info("持久化視圖設置完成")

        for ext in self.loadcogs:
            try:
                await self.load_extension(ext)
            except Exception as e:
                logging.error(f"載入 {ext} 時發生錯誤: {str(e)}")

        try:
            synced = await self.tree.sync()
            logging.info(f'已同步 {len(synced)} 個指令')
        except Exception as e:
            logging.error(f'指令同步失敗: {e}')

        self.status_monitor.start()
        self.setup_bot.start()

        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            embed = discord.Embed(title="錯誤", color=discord.Color.red())
            if isinstance(error, discord.app_commands.errors.CheckFailure):
                embed.description = "此指令限管理員使用。"
            else:
                embed.description = f"發生未知錯誤: {error}"
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(embed=embed, ephemeral=True)

    async def on_ready(self):
        logging.info(f'{self.user} 已上線！')

    async def on_guild_join(self, guild):
        """處理新加入的伺服器"""
        try:
            identity_cog = self.get_cog('IdentityManagement')
            if identity_cog:
                await identity_cog.setup_db(guild.id)
        except Exception as e:
            logging.error(f"初始化伺服器 {guild.name} ({guild.id}) 的數據庫時出錯: {e}")

async def main():
    bot = Bot()
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logging.error("未設定 DISCORD_TOKEN 環境變數")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
