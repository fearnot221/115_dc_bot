import aiosqlite
import json
import os
import re
from typing import Dict, List, Any

class DatabaseManager:
    def __init__(self, guild_id: int, guild_name: str = None):
        self.guild_id = guild_id
        
        # 處理伺服器名稱，移除不適合作為檔案名的字元
        if guild_name:
            safe_guild_name = re.sub(r'[^\w\-]', '_', guild_name)
            if len(safe_guild_name) > 30:
                safe_guild_name = safe_guild_name[:30]
            self.db_name = f'data/database/database_{safe_guild_name}_{guild_id}.db'
            self.verification_json = f'data/config/verification_{safe_guild_name}_{guild_id}.json'
            self.config_json = f'data/config/config_{safe_guild_name}_{guild_id}.json'
        else:
            self.db_name = f'data/database/database_{guild_id}.db'
            self.verification_json = f'data/config/verification_{guild_id}.json'
            self.config_json = f'data/config/config_{guild_id}.json'
        
        self.emoji_json = 'data/config/emoji.json'
        
        # 建立必要的資料夾與檔案
        os.makedirs('data/config', exist_ok=True)
        os.makedirs('data/database', exist_ok=True)
        
        if not os.path.exists(self.verification_json):
            with open(self.verification_json, 'w', encoding='utf-8') as f:
                json.dump({"roles": {}, "users": {}}, f, ensure_ascii=False, indent=4)
        
        if not os.path.exists(self.config_json):
            with open(self.config_json, 'w', encoding='utf-8') as f:
                json.dump({"application_category_id": None, "bot_created_channels": []}, f, ensure_ascii=False, indent=4)

        if not os.path.exists(self.emoji_json):
            with open(self.emoji_json, 'w', encoding='utf-8') as f:
                json.dump({"emojis": {}}, f, ensure_ascii=False, indent=4)

    async def init_db(self):
        """初始化資料庫表格"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS application_channels (
                    user_id INTEGER PRIMARY KEY,
                    channel_id INTEGER,
                    status TEXT
                )
            ''')
            await db.commit()

    async def save_verification_role(self, user_id: str, role_id: int, role_name: str = None):
        """儲存驗證角色資訊"""
        try:
            with open(self.verification_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"roles": {}, "users": {}}
        
        if role_name is None:
            for name, rid in data.get("roles", {}).items():
                if rid == role_id:
                    role_name = name
                    break
            
            if role_name is None:
                role_name = f"role_{role_id}"
                data.setdefault("roles", {})[role_name] = role_id
        else:
            data.setdefault("roles", {})[role_name] = role_id
        
        if "users" not in data:
            data["users"] = {}
        
        if role_name not in data["users"]:
            data["users"][role_name] = []
        
        if user_id not in data["users"][role_name]:
            data["users"][role_name].append(user_id)
        
        with open(self.verification_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        return True
    
    async def get_role_id(self, role_name: str) -> int:
        """取得角色 ID"""
        try:
            with open(self.verification_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("roles", {}).get(role_name)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        
    async def get_channel_id(self, channel_name: str) -> int:
        """取得頻道 ID"""
        try:
            with open(self.config_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("channels", {}).get(channel_name)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    async def get_verification_role(self, user_id: str) -> int:
        """取得使用者的驗證角色"""
        try:
            with open(self.verification_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for role_name, users in data.get("users", {}).items():
                    if user_id in users:
                        return data.get("roles", {}).get(role_name)
                
                return None
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    async def get_all_user_roles(self, user_id: str) -> list:
        """取得使用者所有角色"""
        try:
            with open(self.verification_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                roles = []
                
                for role_name, users in data.get("users", {}).items():
                    if user_id in users:
                        role_id = data.get("roles", {}).get(role_name)
                        if role_id:
                            roles.append({
                                "name": role_name,
                                "id": role_id
                            })
                
                return roles
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    async def save_application_channel(self, user_id: int, channel_id: int, status: str = "pending"):
        """儲存申請頻道資訊"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'INSERT OR REPLACE INTO application_channels (user_id, channel_id, status) VALUES (?, ?, ?)',
                (user_id, channel_id, status)
            )
            await db.commit()

    async def update_application_status(self, user_id: int, status: str):
        """更新申請狀態"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE application_channels SET status = ? WHERE user_id = ?',
                (status, user_id)
            )
            await db.commit()

    async def get_application_channel(self, user_id: int) -> Dict:
        """取得使用者的申請頻道資訊"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                'SELECT channel_id, status FROM application_channels WHERE user_id = ?', 
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {"channel_id": row[0], "status": row[1]}
                return None 

    async def save_application_category(self, category_id: int) -> bool:
        """儲存申請分類頻道 ID"""
        try:
            with open(self.config_json, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {"application_category_id": None, "bot_created_channels": []}
        
        config["application_category_id"] = category_id
        
        with open(self.config_json, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
            
        return True

    async def get_application_category(self) -> int:
        """取得申請分類頻道 ID"""
        try:
            with open(self.config_json, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("application_category_id")
        except (FileNotFoundError, json.JSONDecodeError):
            return None
            
    async def register_bot_created_channel(self, channel_id: int) -> bool:
        """註冊機器人建立的頻道"""
        try:
            with open(self.config_json, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {"application_category_id": None, "bot_created_channels": []}
        
        if "bot_created_channels" not in config:
            config["bot_created_channels"] = []
            
        if channel_id not in config["bot_created_channels"]:
            config["bot_created_channels"].append(channel_id)
        
        with open(self.config_json, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
            
        return True
        
    async def is_bot_created_channel(self, channel_id: int) -> bool:
        """檢查頻道是否由機器人建立"""
        try:
            with open(self.config_json, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return channel_id in config.get("bot_created_channels", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return False
            
    async def remove_bot_created_channel(self, channel_id: int) -> bool:
        """移除機器人建立的頻道"""
        try:
            with open(self.config_json, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {"application_category_id": None, "bot_created_channels": []}
        
        if "bot_created_channels" in config and channel_id in config["bot_created_channels"]:
            config["bot_created_channels"].remove(channel_id)
        
        with open(self.config_json, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
            
        return True

    async def get_available_roles(self) -> List[Dict[str, Any]]:
        """取得所有可用的角色"""
        try:
            with open(self.verification_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                roles = []
                
                for role_name, role_id in data.get("roles", {}).items():
                    roles.append({
                        "name": role_name,
                        "id": role_id
                    })
                
                return roles
        except (FileNotFoundError, json.JSONDecodeError):
            return [] 

    async def save_emoji(self, emoji_name: str, emoji_id: int, emoji_format: str) -> bool:
        """儲存表情符號到全域設定"""
        try:
            with open(self.emoji_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"emojis": {}}
            
        if "emojis" not in data:
            data["emojis"] = {}
            
        data["emojis"][emoji_name] = {
            "id": emoji_id,
            "format": emoji_format
        }
        
        with open(self.emoji_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        return True

    async def get_emoji(self, emoji_name: str) -> Dict:
        """取得指定的表情符號"""
        try:
            with open(self.emoji_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("emojis", {}).get(emoji_name)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    async def get_all_emojis(self) -> Dict:
        """取得所有表情符號"""
        try:
            with open(self.emoji_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("emojis", {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    async def remove_emoji(self, emoji_name: str) -> bool:
        """移除指定的表情符號"""
        try:
            with open(self.emoji_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False
            
        if "emojis" in data and emoji_name in data["emojis"]:
            del data["emojis"][emoji_name]
            with open(self.emoji_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
            
        return False