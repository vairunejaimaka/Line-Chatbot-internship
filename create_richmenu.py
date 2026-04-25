# create_richmenu.py

import os
import requests
import json
from linebot import LineBotApi

# 1. ตั้งค่า LINE API Keys (ใช้ค่าเดียวกับใน app.py)
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")  # <--- แทนที่ด้วยค่า Access Token จริงของคุณ

LINE_API_URL = "https://api.line.me/v2/bot"
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# 2. ตั้งค่าไฟล์รูปภาพ (แทนที่ด้วยชื่อไฟล์จริงของคุณ)
IMAGE_FILE_NAME = "qa_icon_182956_2500x1686.png"  # <--- แทนที่ชื่อไฟล์รูปภาพของคุณ
IMAGE_MIME_TYPE = "image/png" # หรือ image/jpeg

# 3. กำหนดโครงสร้าง Rich Menu
# ขนาด 2500x1686 (สำหรับ Full Menu)
# การแบ่งโซน: สมมติว่าแบ่งเป็น 3 ปุ่มแนวนอน
RICHMENU_OBJECT = {
    "size": {"width": 2500, "height": 1686},
    "selected": True,  # ให้แสดงเป็นค่าเริ่มต้น
    "name": "Internship Main Menu",
    "chatBarText": "เมนูหลัก", # ข้อความที่แสดงตรงปุ่มเปิด-ปิดเมนู
    "areas": [
        # โซน 1: ตรวจสอบสถานะ (ซ้าย)
        {
            "bounds": {"x": 0, "y": 0, "width": 833, "height": 1686},
            "action": {
                "type": "message", # หรือ postback
                "text": "สถานะ" # ข้อความที่ Bot จะได้รับเมื่อกด
            }
        },
        # โซน 2: คำถามที่พบบ่อย (กลาง)
        {
            "bounds": {"x": 833, "y": 0, "width": 834, "height": 1686},
            "action": {
                "type": "message",
                "text": "เมนู" # ข้อความที่ Bot จะได้รับเมื่อกด
            }
        },
        # โซน 3: ติดต่อ/ลิงก์ (ขวา)
        {
            "bounds": {"x": 1667, "y": 0, "width": 833, "height": 1686},
            "action": {
                "type": "uri",
                "uri": "https://www.facebook.com/share/g/16KmFaGUQz/" # <--- แทนที่ URL จริง
            }
        }
    ]
}

def create_and_set_rich_menu():
    print("--- 1. Creating Rich Menu Object ---")
    
    # 1.1 สร้าง Rich Menu Object
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    richmenu_response = requests.post(
        f"{LINE_API_URL}/richmenu", 
        headers=headers, 
        data=json.dumps(RICHMENU_OBJECT)
    )
    richmenu_id = richmenu_response.json().get("richMenuId")
    
    if richmenu_response.status_code != 200 or not richmenu_id:
        print(f"❌ Failed to create Rich Menu Object. Response: {richmenu_response.text}")
        return

    print(f"🟢 Rich Menu Object Created. ID: {richmenu_id}")

    # 2. อัปโหลดรูปภาพ
    print("\n--- 2. Uploading Rich Menu Image ---")
    
    if not os.path.exists(IMAGE_FILE_NAME):
        print(f"❌ Error: Image file '{IMAGE_FILE_NAME}' not found. Please place it in the same folder.")
        return

    image_headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": IMAGE_MIME_TYPE
    }
    
    with open(IMAGE_FILE_NAME, 'rb') as f:
        image_response = requests.post(
            f"{LINE_API_URL}/richmenu/{richmenu_id}/content",
            headers=image_headers,
            data=f
        )

    if image_response.status_code != 200:
        print(f"❌ Failed to upload image. Response: {image_response.text}")
        return

    print("🟢 Rich Menu Image Uploaded Successfully.")

    # 3. ตั้งค่าเป็น Rich Menu หลัก (Default)
    print("\n--- 3. Setting Rich Menu as Default ---")
    
    default_response = requests.put(
        f"{LINE_API_URL}/user/all/richmenu/{richmenu_id}",
        headers={"Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    )

    if default_response.status_code != 200:
        print(f"❌ Failed to set default Rich Menu. Response: {default_response.text}")
        return

    print("✅ Rich Menu Set as Default for all users!")
    print("\nFinish: Refresh your LINE chat to see the new Rich Menu.")

if __name__ == "__main__":
    create_and_set_rich_menu()