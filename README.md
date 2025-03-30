# Discord 身份驗證與申請系統

test

這是一個 Discord 機器人，提供身份驗證和身份組申請功能，並支持管理員進行高效的用戶管理。

## 功能

1. **身份驗證**

   - 使用者可以通過點擊驗證按鈕來獲取身份組。
   - 系統會自動檢查用戶 ID 是否在 JSON 文件中。
   - 管理員可以將批准的用戶添加到驗證列表，支持單個或批量操作。

2. **身份組申請**

   - 使用者可以申請特定身份組（例如 115 特選生或特選老人）。
   - 系統會自動創建一個專屬申請頻道。
   - 申請表單包含必要的個人信息，且只能填寫一次。
   - 管理員可以批准或拒絕申請，並提供審核意見。
   - 批准申請後，用戶需要點擊驗證按鈕以獲取身份組。

3. **表情管理**
   - 管理員可以添加、移除或列出伺服器的自訂表情。
   - 支持將表情與功能按鈕綁定，提升用戶體驗。

## 安裝

1. 克隆此項目：
   ```
   git clone <repository_url>
   ```
2. 安裝依賴：
   ```
   pip install -r requirements.txt
   ```
3. 在 `.env` 文件中設置你的 Discord 機器人 Token 和其他必要配置：
   ```
   DISCORD_TOKEN=你的機器人Token
   ```

## 使用方法

### 管理員指令

- `/setup` - 創建身份驗證和申請按鈕。
- `/set_category [category]` - 設置申請頻道的類別（可選）。
- `/add_verification <user_id> <role>` - 添加單個用戶 ID 到驗證列表。
- `/bulk_add_verification <role> <file>` - 從文件批量添加用戶 ID 到驗證列表。
- `/manage_application <user> <action>` - 管理用戶申請 (action: close/approve/reject)。
- `/add_emoji <name> <emoji>` - 添加表情到配置中。
- `/remove_emoji <name>` - 從配置中移除表情。
- `/list_emojis` - 列出所有已配置的表情。

### 使用者操作

1. **驗證身份**

   - 點擊「驗證身份」按鈕。
   - 系統會自動檢查您的用戶 ID 是否已獲授權。
   - 如已獲授權，自動授予相應身份組。

2. **申請身份組**
   - 點擊「申請身份組」按鈕。
   - 選擇要申請的身份組類型（例如 115 特選生或特選老人）。
   - 填寫申請表格（只能填寫一次）。
   - 等待管理員審核。
   - 申請批准後，點擊「驗證身份」按鈕來獲取身份組。

## 文件結構

```
project/
├── data/
│   ├── config/         # 存放 JSON 配置文件
│   └── database/       # 存放資料庫文件
├── cogs/
│   ├── role_management.py  # 身份管理功能
│   └── emoji_management.py # 表情管理功能
├── database/
│   └── db_manager.py      # 數據庫管理
├── utils/
│   ├── ui_components.py   # UI 組件
│   └── helpers.py         # 輔助函數
├── main.py               # 主程序
├── requirements.txt      # 依賴包列表
└── README.md            # 說明文件
```

## JSON 驗證文件範例

當用戶申請被批准後，系統會將用戶 ID 添加到 JSON 驗證文件中。文件路徑格式為 `data/config/verification_伺服器名稱_伺服器ID.json`，例如 `data/config/verification_My_Discord_Server_123456789012345678.json`。

JSON 文件包含兩個主要區塊：

1. **roles** - 存儲角色名稱到角色 ID 的映射。
2. **users** - 存儲角色名稱到用戶 ID 列表的映射。

檔案內容格式如下：

```json
{
  "roles": {
    "test1": 987654321098765432,
    "test2": 876543210987654321
  },
  "users": {
    "test1": ["123456789012345678", "234567890123456789"],
    "test2": ["345678901234567890", "456789012345678901"]
  }
}
```

## Emoji 配置文件

系統使用 JSON 文件來儲存伺服器表情的配置。文件路徑格式為 `data/config/emoji_伺服器名稱_伺服器ID.json`，例如 `data/config/emoji_My_Discord_Server_123456789012345678.json`。

檔案內容格式如下：

```json
{
  "emojis": {
    "emoji_name": 123456789012345678,
    "another_emoji": 987654321098765432
  }
}
```

## 注意事項

- 確保機器人有管理身份組和頻道的權限。
- 申請頻道可以選擇性地放在特定類別中，由管理員通過 `/set_category` 設置。
- 建議設置一個名為「管理員」的身份組，以便正確管理申請頻道。
