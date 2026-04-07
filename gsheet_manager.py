# gsheet_manager.py

import gspread, datetime
from google.oauth2.service_account import Credentials
import os,re
# เพิ่ม get_internship_progress_66 เข้าไปในรายการ import

FAQ_SHEET_NAME = "FAQ"
CREDENTIAL_FILE_NAME = "google_key.json"
_cached_client = None

def connect_to_sheets():
    global _cached_client
    
    try:
        if _cached_client is not None:
            return _cached_client
        
        _cached_client = gspread.service_account(filename=CREDENTIAL_FILE_NAME)
        print("🟢 Google Sheets Connected (New Session).")
        return _cached_client    
    except Exception as e:
            print(f"❌ Connection Error: {e}")
            return None
# ----------------------------------------------------
# 3. ฟังก์ชันสำหรับค้นหาข้อมูลนักศึกษา
# ----------------------------------------------------
# gsheet_manager.py (แก้ไข get_student_info)
def get_student_info(student_id, client): # 💡 เพิ่ม client
    try:
        # 💡 ใช้ client ที่รับมาเปิด Sheet
        sheet = client.open("Chatbot_DB").worksheet('Student_Data')
        data = sheet.get_all_values()
        
        for row in data:
            if row[1] == str(student_id): # สมมติรหัสอยู่คอลัมน์ B (Index 1)
                return row
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
        # ค้นหา StudentID (สมมติว่าอยู่ในคอลัมน์ B)
        
# ----------------------------------------------------
# 4. ฟังก์ชันสำหรับค้นหาสถานะฝึกงาน
# ----------------------------------------------------
# gsheet_manager.py (แก้ไข get_internship_status)
def get_internship_status(student_id, client): # 💡 เพิ่ม client
    """ค้นหาสถานะฝึกงานตาม StudentID ใน Internship_Status Sheet"""
    try:
        # 💡 ใช้ client ที่รับมาเปิด Sheet
        spreadsheet = client.open("Chatbot_DB") 
        status_sheet = spreadsheet.worksheet('Internship_Status')
        
        # ค้นหา StudentID (สมมติว่าอยู่ในคอลัมน์ A)
        cell = status_sheet.find(str(student_id))
        
        if cell:
            row_data = status_sheet.row_values(cell.row)
            status = row_data[4] 
            return status
        else:
            return "ไม่พบสถานะฝึกงาน"
    except Exception as e:
        print(f"Error reading Internship_Status: {e}")
        return "เกิดข้อผิดพลาดในการดึงข้อมูลสถานะ"
    
# gsheet_manager.py (เพิ่มโค้ดนี้)

# 💡 สมมติว่าตัวแปร client และฟังก์ชัน connect_to_sheets พร้อมใช้งานแล้ว
# ----------------------------------------------------
# 5. ฟังก์ชันสำหรับคำถามการฝึกงาน
# ----------------------------------------------------

def get_faq_list(client):
    """ดึงรายการคำถาม-คำตอบ (FAQ) ทั้งหมดจาก Google Sheet"""
    try:
        sheet = client.open("Chatbot_DB").worksheet(FAQ_SHEET_NAME)
        faq_data = sheet.get_all_values()
        
        faq_list = []
        if len(faq_data) > 1:
            # ใช้ for loop ดึงข้อมูลแบบเดิม
            current_id = 1
            for row in faq_data[1:]: 
                if len(row) >= 2 and row[0].strip() != '': 
                    faq_list.append({
                        "id": str(current_id), 
                        "question": row[0].strip(),
                        "answer": row[1].strip()
                    })
                    current_id += 1
        return faq_list
        
    except Exception as e:
        print(f"Error fetching FAQ data from {FAQ_SHEET_NAME}: {e}")
        return None
#----------------------------------------------------
# 6. ฟังก์ชันเชื่อมต่อ Google Sheets  
#----------------------------------------------------
def connect_to_sheets():
    'เชื่อมต่อกับ Google Sheets โดยใช้ Credential ที่ตั้งค่าไว้'
    global _cached_client
    try:
        if _cached_client is not None:
            return _cached_client
        
        # ใช้ชื่อไฟล์ที่คุณยืนยันมา
        _cached_client = gspread.service_account(filename=CREDENTIAL_FILE_NAME) 
        print("🟢 Google Sheets Connected.")
        return _cached_client
    
    except Exception as e:
        # ถ้ามีปัญหาในการเชื่อมต่อ ให้แสดงชื่อไฟล์ที่คาดหวังด้วย
        print(f"❌ Error connecting to Google Sheets. Check if '{CREDENTIAL_FILE_NAME}' exists and is valid: {e}")
        return None


#----------------------------------------------------
# 7. ฟังก์ชันค้นหาคำตอบ FAQ โดยใช้ข้อความคำถาม
#----------------------------------------------------
def find_faq_answer(question_text, client):
    """ค้นหาคำตอบ FAQ โดยใช้ข้อความคำถามที่ผู้ใช้พิมพ์ (ยืดหยุ่นขึ้น)"""
    try:
        sheet = client.open("Chatbot_DB").worksheet(FAQ_SHEET_NAME)
        faq_data = sheet.get_all_values()
        
        normalized_query = question_text.strip().lower() 
        
        if len(faq_data) > 1:
            for row in faq_data[1:]: 
                if len(row) >= 2:
                    question_in_db = row[0].strip().lower() 
                    
                    if normalized_query == question_in_db:
                        return row[1].strip()
        
        return None
        
    except Exception as e:
        print(f"Error finding FAQ answer: {e}")
        return None
    
# ====================================================
# 🔷8. ฟังก์ชันดึงข้อมูลจาก รายงานความก้าวหน้าฝึกงาน รหัส 66  |
# ====================================================
# gsheet_manager.py (เพิ่มส่วนนี้เข้าไป)

def get_internship_progress_66(student_id, client):
    """ดึงข้อมูลความก้าวหน้าการฝึกงานจาก Sheet รายงานความก้าวหน้า รหัส 66"""
    try:
        # 1. เปิดไฟล์ Sheet ใหม่ (ใช้ชื่อไฟล์ให้ตรงกับใน Google Drive ของคุณ)
        # อย่าลืมกด Share ไฟล์นี้ให้ Email ของ Service Account ด้วยนะครับ
        spreadsheet = client.open("รายงานความก้าวหน้าฝึกงาน รหัส 66 (1)") 
        sheet = spreadsheet.worksheet(0) # เปิดหน้าแรก
        data = sheet.get_all_values()
                
        for row in data:
            if len(row) > 1 and row[1] == str(student_id): # สมมติรหัสอยู่คอลัมน์ B
                
                DEBUG = False
                if DEBUG:
                    print("ROW:", row)
                    print("ROW[18]:", repr(row[18]))
                
                raw_result = row[18].strip()
                print("RAW:", repr(raw_result))
                
                clean_result = raw_result
                clean_result = re.sub(r'[○•◦●]', '', clean_result)
                clean_result = clean_result.replace('\n', ' ').replace('\r', ' ').strip()                
                
                print("CLEAN:", repr(clean_result))
                
                return {
                    "student_id": row[1], # B
                    "name": row[2],       # C
                    "gpa": row[3],        # D
                    "hours": row[5],      # F
                    "ict": row[6],        # G
                    "intern": row[7],     # H
                    "coop": row[8],       # I
                    "result": clean_result,      # J (สถานที่ฝึกงานที่แจ้ง/ผลการตรวจสอบ)
                    "company": row[20] if row[20] != "" else "ยังไม่แจ้งที่ฝึกงาน" , # เพิ่มข้อมูลบริษัทจากคอลัมน์ J  
                    "doc_status": row[11] # L 
              }
                
        return None            
    except Exception as e:
        print(f"Error reading Progress Sheet: {e}")
        return None
    
#======================================================
# ♦️9.1. ฟังก์ชัน [ตรวจสอบข้อมูล] -> ก่อนฝึกงาน               |            
#======================================================
def get_pre_internship_info(student_id, client):
    """หัวข้อที่ 1: ตรวจสอบก่อนฝึกงาน (Index 1, 3, 4, 5, 6, 7, 8, 9)"""
    try:
        spreadsheet = client.open("รายงานความก้าวหน้าฝึกงาน รหัส 66 (1)") 
        sheet = spreadsheet.worksheet("Sheet1")
        data = sheet.get_all_values()
        
        for row in data:
            if len(row) > 1 and row[1].strip() == str(student_id):
                
                DEBUG = False
                if DEBUG:
                    print("ROW:", row)
                    print("ROW[18]:", repr(row[18]))
                
                # Logic เช็คสี/ความผิดปกติ
                gpa_val = row[3].strip()  # D
                hours_val = row[5].strip() # F
                ict_val = row[6].strip() # G
                intern_val = row[7].strip() # H
                coop_val = row[17].strip() # R (แก้จาก 8 เป็น 17 เพราะข้อมูลฝึกงาน/สหกิจย้ายไปคอลัมน์ R)
                result_val = row[19].strip() # J (สถานที่ฝึกงานที่แจ้ง/ผลการตรวจสอบ)
                # --- 2. Logic เช็คเงื่อนไขตามสั่ง ---
                clean_result = result_val
                clean_result = re.sub(r'[○•◦●]', '', clean_result)
                clean_result = clean_result.replace('\n', ' ').replace('\r', ' ').strip()
                # GPA: ต่ำกว่า 2.00 หรือมีเครื่องหมาย < ให้สีแดง
                gpa_status = "🔴" if "<2.00" in gpa_val or (gpa_val.replace('.','',1).isdigit() and float(gpa_val) < 2.0) else "🟢"
                
                # ชม.กิจกรรม: ต่ำกว่า 25 ให้สีแดง
                hours_num = ''.join(filter(str.isdigit, hours_val))
                hours_status = "🔴" if hours_num == "" or int(hours_num) < 25 else "🟢"
                
                # ICT: F ให้แดง นอกนั้นเขียว
                ict_status = "🔴" if ict_val.upper() == "F" else "🟢"
                
                # ฝึกงาน/สหกิจ: "ได้" เขียว, "ไม่ได้" แดง
                intern_status = "🟢" if "ได้" in intern_val and "ไม่ได้" not in intern_val else "🔴"
                coop_status = "🟢" if "ได้" in coop_val and "ไม่ได้" not in coop_val else "🔴"
                
                # ผลการตรวจสอบ (Column T): เช็คคำขึ้นต้น
                if "แจ้งที่ฝึกงาน" in clean_result:
                    res_emoji = "⚠️"
                    res_color = "#CFA704"
                elif "แนะนำให้ฝึกงานในปีถัดไป" in clean_result:
                    res_emoji = "❌"
                    res_color = "#FF3B30"
                elif clean_result.strip() in ["", "-"]:
                    res_emoji = "⚪"
                    res_color = "#8E8E93"
                else:
                    res_emoji = "✅" # กรณีเป็นชื่อบริษัทหรืออื่นๆ
                    res_color = "#34C759"
                    
                print("FINAL RESULT:", repr(clean_result))
                print("CLEAN RESULT:", repr(clean_result))
                
                return {
                    "student_id": row[1],
                    "name": row[2],
                    "gpa": f"{gpa_val} {gpa_status}",
                    "hours": f"{hours_val} {hours_status}",
                    "ict": f"{ict_val} {ict_status}",
                    "intern_pass": f"{intern_val} {intern_status}",
                    "coop_pass": f"{coop_val} {coop_status}",
                    "result": f"   {res_emoji} {clean_result}",
                    "res_color": res_color
                }
        return None
    except Exception as e:
        print(f"❌ Error in Pre-Internship Check: {e}")
        return None
    
#======================================================
# ♦️9.2. ฟังก์ชันรวมร่าง [สถานะฝึกงาน + เอกสาร + สิ่งที่ต้องทำ] |
#======================================================
def get_combined_internship_data(student_id, client):
    """รวมหัวข้อที่ 2 และ 3: สถานะฝึกงานและเอกสาร (Index 19-27)"""
    try:
        spreadsheet = client.open("รายงานความก้าวหน้าฝึกงาน รหัส 66 (1)") 
        sheet = spreadsheet.get_worksheet(0)
        data = sheet.get_all_values()
        
        for row in data:
            if len(row) > 1 and row[1].strip() == str(student_id):
                # --- 1. ส่วนสถานที่ฝึกงาน (เดิมคือหัวข้อ 10) ---
                company_val = row[19].strip()
                if "แนะนำให้ฝึกงานในปีถัดไป" in company_val:
                    comp_color, comp_emoji = "#FF3B30", "❌"
                elif "แจ้งที่ฝึกงาน" in company_val:
                    comp_color, comp_emoji = "#E2B80C", "⚠️"
                elif company_val in ["", "-"]:
                    comp_color, comp_emoji, company_val = "#8E8E93", "⚪", "ยังไม่ได้แจ้งที่ฝึกงาน"
                else:
                    comp_color, comp_emoji = "#34C759", "🏢"

                # --- 2. ส่วนสถานะเอกสารล่าสุด (เดิมคือหัวข้อ 11, 12) ---
                doc_indices = [22, 23, 24, 25, 26]
                latest_doc = "ยังไม่มีการส่งเอกสาร"
                for idx in reversed(doc_indices):
                    if len(row) > idx and row[idx].strip() != "":
                        doc_num = idx - 21 
                        latest_doc = f"ใบที่ {doc_num}: {row[idx].strip()}"
                        break
                
                # --- 3. ส่วนสิ่งที่ นศ. ต้องทำ (Index 27) ---
                todo_val = row[27].strip() if len(row) > 27 else "-"
                if "เตรียมตัวฝึกงาน" in todo_val:
                    todo_color, todo_emoji = "#34C759", "✅"
                elif "แจ้งที่ฝึกงาน" in todo_val:
                    todo_color, todo_emoji = "#FFCC00", "⚠️"
                elif any(word in todo_val for word in ["วางแผนฝึกงานปีถัดไป", "นักศึกษาแจ้งขอฝึกงานในปีถัดไป"]):
                    todo_color, todo_emoji = "#FF3B30", "🚫"
                else:
                    todo_color, todo_emoji = "#8E8E93", "ℹ️"

                return {
                    "student_id": row[1],
                    "name": row[2],
                    "company": f"{comp_emoji} {company_val}",
                    "type": row[20].strip() if row[20].strip() != "" else "-",
                    "province": row[21].strip() if row[21].strip() != "" else "-",
                    "comp_color": comp_color,
                    "latest_doc": latest_doc,
                    "todo_text": f"{todo_emoji} {todo_val}",
                    "todo_color": todo_color
                }
        return None
    except Exception as e:
        print(f"❌ Error in Combined Internship Data: {e}")
        return None

#=======================================================
# ♦️9.3. ฟังก์ชันแสดงที่ฝึกงาน[ฝึกงาน/สหกิจ] พร้อมสถานะเอกสาร  |
#=======================================================
def get_internship_companies(client):   
    """ดึงรายชื่อบริษัทแบ่งตามโซน"""
    try:
        sheet = client.open("รายชื่อบริษัท สำหรับนักศึกษา รหัส 63").worksheet("Sheet1")
        all_values = sheet.get_all_values()
        
        bkk_list = []
        north_list = []

        for row in all_values[3:19]:  # ข้ามหัวตาราง

            # สมมติมีคอลัมน์ 'Zone' เพื่อแยกพื้นที่
            if len(row[3]) > 1 and row[1]:
                item = f"{row[0]}.{row[1]} ({row[2]})"
                bkk_list.append(item)
                
        for row in all_values[21:58]:
            if len(row[3]) > 1 and row[1]:
                item = f"{row[0]}.{row[1]} ({row[2]})"
                north_list.append(item)
                
        return bkk_list[:15], north_list[:15] # เอาแค่ 15 อันดับแรกตามที่พี่ชายต้องการ
    except Exception as e:
        print(f"Error fetching companies: {e}")
        return [], []                                               
    
#======================================================
# ♦️13. ฟังก์ชันค้นหานักศึกษาจากชื่อ (Partial Match)         |
#======================================================
def search_students_by_name(search_query, client):
    """ค้นหานักศึกษาจากชื่อ (Partial Match) และส่งกลับเป็น List ของคนที่เจอ"""
    try:
        spreadsheet = client.open("รายงานความก้าวหน้าฝึกงาน รหัส 66 (1)") 
        sheet = spreadsheet.get_worksheet(0)
        data = sheet.get_all_values()
        
        matches = []
        search_query = search_query.strip()
        
        # ข้ามหัวตาราง 2 แถวแรก
        for row in data[2:]:
            if len(row) > 2:
                student_name = row[2] # คอลัมน์ C (ชื่อ-นามสกุล)
                student_id = row[1]   # คอลัมน์ B (รหัส)
                
                # ถ้าคำที่ค้นหา อยู่ในชื่อนักศึกษา
                if search_query in student_name:
                    matches.append({
                        "name": student_name,
                        "id": student_id
                    })
        
        return matches # ส่งกลับเป็น List เช่น [{'name': 'กษิพสิทธิ์...', 'id': '66...'}, ...]
    except Exception as e:
        print(f"❌ Error in Search by Name: {e}")
        return []
    
    
    
#===========================================================
# ♦️14. ฟังก์ชันบันทึกข้อมูลการสนทนาเพื่อการวิเคราะห์ (Analytics)    |
#===========================================================    

def save_to_analytics(student_id, message, category, sentiment, reply, client):
    """
    ฟังก์ชันบันทึกข้อมูลการสนทนาลงใน Google Sheets เพื่อการวิเคราะห์ (Analytics)
    
    Args:
        student_id (str): รหัสนักศึกษา (ถ้ามี)
        message (str): ข้อความที่นักศึกษาพิมพ์มา
        category (str): หมวดหมู่ที่ AI จำแนกได้
        sentiment (str): ความรู้สึกที่ AI วิเคราะห์ได้
        reply (str): ข้อความที่บอทตอบกลับไป
        client: gspread client object
    """
    try:

        spreadsheet = client.open("Chatbot_DB")
        sheet = spreadsheet.worksheet("Chat_Analytics")
        
        # 2. สร้าง Timestamp ปัจจุบัน (เวลาไทย)
        # ถ้า Server เป็น UTC อาจจะต้อง +7 ชั่วโมง แต่เบื้องต้นใช้เวลา Server ก่อนครับ
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 3. จัดเตรียมแถวข้อมูลที่จะบันทึก
        # แนะนำลำดับ Column: [เวลา, รหัสนศ., ข้อความนศ., หมวดหมู่, ความรู้สึก, สิ่งที่บอทตอบ]
        row_data = [
            now, 
            student_id, 
            message, 
            category, 
            sentiment, 
            reply
        ]
        
        # 4. บันทึกข้อมูลต่อท้ายแถวสุดท้าย (Append)
        sheet.append_row(row_data)
        
        # คืนค่า True เมื่อบันทึกสำเร็จ (เอาไว้ debug ใน app.py ได้)
        return True
        
    except Exception as e:
        # พิมพ์ Error ออกทาง Console เพื่อให้เราไล่เช็คได้ง่าย
        print(f"❌ Error in save_to_analytics: {e}")
        return False

#=======================================================
# ♦️15. ฟังก์ชันดึงข่าวสารประกาศล่าสุดจาก Sheet News_Board    |
#=======================================================
def get_active_news(client):
    try:
        # เปิด Sheet ชื่อ News_Board
        sheet = client.open("Chatbot_DB").worksheet("News_Board")
        records = sheet.get_all_records()
        
        for row in records:
            # เช็คว่า Status เป็น TRUE หรือไม่
            print(f"DEBUG ROW DATA: {row}")
            if str(row.get('Status', '')).upper() == 'TRUE':
                return {
                    "image": row.get('Image_URL'),
                    "title": row.get('Title'),
                    "desc": row.get('Description'),
                    "deadline": row.get('Deadline')
                }
        return None
    except Exception as e:
        print(f"Error fetching news: {e}")
        return None