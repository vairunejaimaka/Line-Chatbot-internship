# app.py
import os ,time,json
from dotenv import load_dotenv
import google.generativeai as genai
from flask import Flask, request, abort
from linebot.exceptions import InvalidSignatureError

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    ShowLoadingAnimationRequest,
    TextMessage,
    BroadcastRequest
    ) 
from linebot.v3.webhooks import MessageEvent, TextMessageContent


from gsheet_manager import get_internship_companies, get_student_info, get_internship_status, get_faq_list, connect_to_sheets, find_faq_answer, get_internship_progress_66
from flex_templates import create_status_flex, create_faq_flex ,create_basic_menu_flex

# 1. ตั้งค่า LINE API Keys (แทนที่ด้วยค่าจริงของคุณ)
# ดึงค่าเหล่านี้จาก LINE Developers Console -> Messaging API
load_dotenv()  # โหลดตัวแปรสภาพแวดล้อมจากไฟล์ .env

CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')    

model = genai.GenerativeModel('gemini-2.5-flash')
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])

def callback():
    # รับ X-Line-Signature header จาก LINE
    signature = request.headers['X-Line-Signature']
    if signature is None:
        abort(400)

    # รับ Request body ทั้งหมดเป็นข้อความ
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # จัดการ Webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. ตรวจสอบ Channel Secret และ Access Token อีกครั้ง")
        abort(400)

    return 'OK'

@app.route("/broadcast-news", methods=['GET'])
def broadcast_news():
    """ยิงประกาศหาทุกคน (KFC Style)"""
    try:
        from gsheet_manager import connect_to_sheets, get_active_news
        from flex_templates import create_news_flex
        client = connect_to_sheets()
        news_data = get_active_news(client)
        if not news_data: return "❌ ไม่มีข่าวสารที่เปิดใช้งาน", 200
        
        flex_news = create_news_flex(news_data)
        line_bot_api.broadcast(BroadcastRequest(messages=[flex_news]))
        return f"✅ ประกาศเรื่อง '{news_data['title']}' สำเร็จ!", 200
    except Exception as e:
        return f"❌ Error: {e}", 500



# ===============================
# 🔷 ฟังก์ชั่นจับคู่การคำถามกับคำตอบ   |
# ===============================
def semantic_faq_match(user_message, faq_list):
    faq_text = ""
    for item in faq_list:
        faq_text += f"{item['id']}. {item['question']}\n"

    prompt = f"""
        คุณคือระบบจับคู่คำถามนักศึกษา

        ด้านล่างคือรายการคำถาม FAQ:
        {faq_text}

        คำถามของนักศึกษา:
        {user_message}

        ให้ตอบเฉพาะหมายเลขข้อที่ใกล้เคียงที่สุด
        ถ้าไม่เกี่ยวข้องเลย ให้ตอบว่า 0
        ตอบเป็นตัวเลขเท่านั้น
        """

    response = model.generate_content(prompt)
    result = response.text.strip()

    return result

# ===============================
# 🔹 ฟังก์ชันกรอง ก่อนค้นหา         |
# ===============================
def is_likely_name(text):
    text = text.strip()
    if any(c in text for c in ["นาย", "นางสาว", "นาง"]):
        return True
    
    # มีตัวเลข → ไม่ใช่ชื่อ 
    if any(char.isdigit() for char in text):
        return False

    # คำถาม → ตัดทิ้ง
    question_words = ["อะไร", "ยังไง", "ไหม", "มั้ย", "หรือ", "ต้อง", "ทำไง", "ยัง", "ได้", "กี่"]
    if any(word in text for word in question_words):
        return False

    # ต้องมีอย่างน้อย 2 คำ (สำคัญมาก)
    if len(text.split()) < 2:
        return False

    # ยาวเกิน → ไม่ใช่ชื่อ
    if len(text.split()) > 3:
        return False

    # มีสัญลักษณ์ → ไม่ใช่ชื่อ
    if any(c in text for c in [":", "?", "!", ".", ","]):
        return False

    return True




@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    start_time = time.time() #⏱️ เริ่มจับเวลาเมื่อได้รับข้อความ
    try:
        line_bot_api.show_loading_animation(
            ShowLoadingAnimationRequest(
                chat_id=event.source.user_id,
                loading_seconds=5 # แสดงไว้นานสูงสุด 5 วินาที (จะหายไปเองเมื่อบอท reply)
            )
        )
    except Exception as e:
        print("Loading Animation Error:", e)
    user_id = event.source.user_id
    user_message = event.message.text.strip()
    lower_message = user_message.lower()
    
    if any(k in lower_message for k in ['คุณ','ติดต่อ','เตรียมตัว','พี่','พี่คับ','ดีคับพี่', 'ดีคับ','สวัสดี', 'หวัดดี', 'หวัดดีคับ', 'ดีพี่']):
        reply_text = ('😊พี่ชื่อเอ็ม ออนิวครับผม\n'
        'พิมพ์ "รหัสนศ. 10 หลัก" หรือ "ชื่อ-นามสกุล"'
        'เพื่อตรวจสอบข้อมูล เเละเมนูต่างๆครับ\n') 
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )
        return
    #______________________________________________
    print("/ BEFORE CONNECT ===")                   
    t = time.time()
    client = connect_to_sheets()
    duration = time.time() - t
    print(f"\_ CONNECT TIME === {duration:.5f} s")
    #______________________________________________
    
    if not client:
        return
    print("📩 USER MESSAGE:", user_message)

    
    #==================================================
    # 🔹 คำสั่งแบบ command:student_id (ชุดที่สมบูรณ์ที่สุด)   |
    #==================================================
    if ":" in user_message:
        try:
            command, std_id = user_message.split(":",1)
            command = command.strip()
            std_id = std_id.strip()

            # 1. หัวข้อ: ตรวจสอบก่อนฝึกงาน (ใช้ Flex Message)
            student_data = get_student_info(std_id, client)
            if not student_data:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=f"❌ ไม่พบรหัสนักศึกษา {std_id}")]
                    )
                )
                return
            
            if command == "ตรวจสอบก่อนฝึกงาน":
                from gsheet_manager import get_pre_internship_info
                from flex_templates import create_pre_internship_flex
                
                data = get_pre_internship_info(std_id, client)
                if data:
                    flex_msg = create_pre_internship_flex(data)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[flex_msg]
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=f"❌ ไม่พบข้อมูลการตรวจสอบของรหัส {std_id}")]
                        )
                    )
                return # ✅ จบงานทันที

            elif command in ["สถานะฝึกงานนศ.", "เอกสาร/นศ.ต้องทำอะไร", "สถานะการฝึกงานและเอกสาร"]:
                from gsheet_manager import get_combined_internship_data
                from flex_templates import create_combined_internship_flex
                
                # ดึงข้อมูลชุดรวม
                data = get_combined_internship_data(std_id, client)
                if data:
                    # ใช้ Flex ตัวใหม่ที่รวมข้อมูลทุกอย่างไว้ด้วยกัน
                    flex_msg = create_combined_internship_flex(data)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(reply_token=event.reply_token, messages=[flex_msg])
                    )
                else:
                    line_bot_api.reply_message(
                        ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text="❌ ไม่พบข้อมูลรายละเอียดการฝึกงานและเอกสาร")])
                    )
                return
            
            elif command in ["ฝึกงานไหนดี?/ฝึกไหนได้บ้าง","หาที่ฝึกงาน","ฝึกงานไหนดี","ฝึกงานที่ไหนได้บ้าง"]:
                from gsheet_manager import get_internship_companies
                from flex_templates import create_internship_list_flex
                
                bkk, north = get_internship_companies(client)
                flex_msg = create_internship_list_flex(bkk, north)
                
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[flex_msg])
                )
                reply_text_for_log = "แสดงรายชื่อบริษัทฝึกงาน"
                
            else:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="❌ ไม่พบหัวข้อที่ระบุ กรุณาเลือกจากเมนูครับ")]
                    )
                ) 
                return
             
        except Exception as e:
            print("Command Error:", e)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="❌ รูปแบบคำสั่งไม่ถูกต้องหรือระบบขัดข้อง")]
                )
            )
            return
    
    
    # ==============================================
    # 🔹 กรณีเป็นรหัสนักศึกษา 10 หลัก ชื่อ-นามสกุล        |
    # ==============================================
    if user_message.isdigit() and len(user_message) == 10:
        
        student_data = get_student_info(user_message, client)
        if student_data:
            student_name = student_data[2].strip()
            student_major = student_data[4]

            flex_message = create_basic_menu_flex(user_message, student_name, student_major)

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_message] # ส่งตัวแปร flex_message ได้เลยเพราะข้างในเป็น FlexSendMessage แล้ว
                )
            )
            #duration = time.time() - start_time
            #print(f"⏱️ RESPONSE TIME: {duration:.2f} seconds")
            return
        else:
            reply_text = f"❌ ไม่พบรหัสนักศึกษา {user_message} ในระบบ"
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
            return
    elif is_likely_name(user_message) and len(user_message.split()) >= 2:
        from gsheet_manager import search_students_by_name
        matches = search_students_by_name(user_message, client)
        
        if not matches:
            # ถ้าหาชื่อไม่เจอ และไม่ใช่รหัส 10 หลักด้วย
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="🔎 ไม่พบรายชื่อหรือรหัสที่ตรงกับคำค้นหาครับ\n(กรุณาพิมพ์รหัส 10 หลัก หรือชื่อจริงเพื่อค้นหา)")]
                )
            )
            return
        elif len(matches) == 1:
            # เจอคนเดียว
            match_name = matches[0]['name']
            match_id = matches[0]['id']
            
            
            def clean(text): return text.replace(" ","").replace("นาย","").replace("นางสาว","").replace("นาง","")
            
            if clean(user_message) == clean(match_name):
                # 🟢 ถ้าพิมพ์มาครบถ้วนเป๊ะ ให้เข้าสู่เมนูยืนยันข้อมูลทันที
                student_data = get_student_info(match_id, client)
                if student_data:
                    student_major = student_data[4]
                    flex_message = create_basic_menu_flex(match_id, match_name, student_major)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(reply_token=event.reply_token, messages=[flex_message])
                    )
                    return
            else:
                res_text = f"✅ พบข้อมูลครับ:\n{matches[0]['name']}\nรหัส: `{matches[0]['id']}`\n\n(💡Copy-paste 'ชื่อ-สกุล'หรือ'รหัสนศ.'เพื่อเข้าดูเมนูครับ)"
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=res_text)])
                )
                return
        else:
            res_text = f"🔎 พบรายชื่อที่ใกล้เคียง {len(matches)} คนครับ:\n\n"
            for m in matches[:10]:
                res_text += f"👤 {m['name']}\n🆔 `{m['id']}`\n"
                res_text += "------------------\n"
            res_text += "\n💡Copy-paste \n'ชื่อ-สกุล'หรือ'รหัสนศ.'เพื่อเข้าดูเมนูครับ"
            
            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=res_text)])
            )
            return
        
    # -------------------------------
    # 🔹 เมนู FAQ
    # -------------------------------
    
    if any(k in lower_message for k in ['เมนู', 'ถาม', 'faq', 'คำถาม']):
        faq_list = get_faq_list(client)

        if faq_list:
            flex_message = create_faq_flex(faq_list)
            line_bot_api.reply_message( 
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_message] 
                )
            )
        else:
            reply_text = "❌ ยังไม่มีรายการ FAQ ในระบบ"
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        return

    # ===============================
    # 🔹 NLP (ยิง LLM แค่ครั้งเดียว)
    # ===============================
    try:
        faq_list = get_faq_list(client)

        faq_text = ""
        if faq_list:
            for item in faq_list:
                faq_text += f"{item['question']} -> {item['answer']}\n"

        prompt = f"""
    คุณคือผู้ช่วยดูแลนักศึกษาฝึกงาน
    - ถ้าคำถามตรงกับ FAQ ให้ใช้คำตอบจาก FAQ
    - ถ้าเป็นเรื่องฝึกงานทั่วไป ให้ตอบสั้น ไม่เกิน 3 บรรทัด
    - ถ้าเป็นข้อความเชิงอารมณ์ ให้กำลังใจสั้น ๆ
    - ถ้าไม่เกี่ยวกับฝึกงาน ให้ปฏิเสธสุภาพ
    - ใช้ emoji ได้ 1 อัน

    FAQ:
    {faq_text}

    ข้อความ:
    {user_message}
    """
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.3}
        )
        reply_text = response.text.strip()

    except Exception as e:
        print("LLM ERROR:", e)
        reply_text = "LLM error"
        #reply_text = "ไม่สามารถประมวลผลได้ กรุณาลองใหม่อีกครั้งครับ"

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
    )
    

    # ==============================================
    # 📊 [AI Analytics] ใช้ Gemini ช่วยจำแนกข้อมูล
    # ==============================================
    if client:
        try:
            import json
            from gsheet_manager import save_to_analytics
            
            # ถาม Gemini ให้วิเคราะห์หมวดหมู่และอารมณ์
            analise_prompt = f"""
            วิเคราะห์ข้อความ: "{user_message}"
            
            เลือก category ได้เพียง 1 ค่า:
            GREETING | DOCUMENT | PRE_CHECK | INTERN_STATUS | CONSULT | OTHER

            เลือก sentiment ได้เพียง 1 ค่า:
            POSITIVE | NEUTRAL | NEGATIVE
            
            ตอบเป็น JSON เท่านั้น ห้ามมีข้อความอื่น:
            {{
                "category": "...",
                "sentiment": "..."
            }}
            """
            analise_res = model.generate_content(analise_prompt)
            
            # ✨ Logic การแกะ JSON (ป้องกัน AI ตอบติดเศษข้อความ)
            raw_json = analise_res.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(raw_json)
            
            # ดึงค่าออกมา
            category = data.get("category", "OTHER")
            sentiment = data.get("sentiment", "NEUTRAL")
            
            # สั่งบันทึก (แอบทำหลังตอบเสร็จแล้ว)
            save_to_analytics(
                student_id=user_message if user_message.isdigit() and len(user_message) == 10 else "N/A",
                message=user_message,
                category=category, 
                sentiment=sentiment, # 👈 เพิ่มช่องนี้ใน gsheet_manager ด้วยนะคับ
                reply=reply_text,
                client=client
            )
            print(f"📊 Logged: {category} | {sentiment}")

        except Exception as e:
            print(f"📊 Analytics Error: {e}")
    return

def log_time(start_time):
    duration = time.time() - start_time
    print(f"⏱️ RESPONSE TIME: {duration:.2f} seconds")

if __name__ == "__main__":
    app.run(port=8000, debug=True) 
