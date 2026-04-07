#flex_templates.py
from linebot.v3.messaging import FlexMessage
from linebot.v3.messaging.models import (
    FlexBubble,
    FlexBox,
    FlexText,
    FlexSeparator,
    FlexButton,
    FlexCarousel,
    URIAction,
    MessageAction,
    FlexImage,
    FlexFiller
)


def create_status_flex(student_id, student_name, student_major,
                       current_status, company='-', gpa='-',
                       hours='-', doc_status='-'):

    status_color = "#34C759" if current_status == "ผ่านการพิจารณา" else "#FF9500" if current_status == "อยู่ระหว่างพิจารณา" else "#FF3B30"
    consider_emoji = "🟢" if current_status == "ผ่านการพิจารณา" else "🟠" if current_status == "อยู่ระหว่างพิจารณา" else "🔴"

    doc_emoji = "✅" if doc_status == "1" else "⏳"
    doc_text = "เอกสารครบถ้วน" if doc_status == "1" else "รอการตรวจสอบ/ไม่ครบ"

    bubble = FlexBubble(
        header=FlexBox(
            layout="vertical",
            contents=[
                FlexText(text="สถานะการฝึกงานปัจจุบัน", weight="bold", size="lg", color="#1DB446")
            ]
        ),
        body=FlexBox(
            layout="vertical",
            contents=[
                FlexBox(layout="horizontal", margin="md", contents=[
                    FlexText(text="🧑🏻 ชื่อ:", size="sm", color="#AAAAAA"),
                    FlexText(text=student_name, size="sm", weight="bold", align="end")
                ]),
                FlexBox(layout="horizontal", margin="sm", contents=[
                    FlexText(text="รหัส:", size="sm", color="#AAAAAA"),
                    FlexText(text=student_id, size="sm", align="end")
                ]),
                FlexBox(layout="horizontal", margin="sm", contents=[
                    FlexText(text="สาขา:", size="sm", color="#AAAAAA"),
                    FlexText(text=student_major, size="sm", align="end")
                ]),
                FlexSeparator(margin="lg"),
                FlexBox(layout="horizontal", margin="lg", contents=[
                    FlexText(text=consider_emoji),
                    FlexText(text="ผลการพิจารณา:", weight="bold"),
                    FlexText(text=current_status, color=status_color, align="end", weight="bold")
                ]),
                FlexSeparator(margin="lg"),
                FlexBox(layout="vertical", margin="lg", spacing="sm", contents=[
                    FlexBox(layout="horizontal", contents=[
                        FlexText(text="📈 GPA:", size="sm", color="#AAAAAA"),
                        FlexText(text=str(gpa), size="sm", align="end", weight="bold")
                    ]),
                    FlexBox(layout="horizontal", contents=[
                        FlexText(text="⏰ ชม.กิจกรรม:", size="sm", color="#AAAAAA"),
                        FlexText(text=f"{hours} ชม.", size="sm", align="end", weight="bold")
                    ]),
                    FlexBox(layout="horizontal", contents=[
                        FlexText(text="📍 ที่ฝึกงาน:", size="sm", color="#AAAAAA"),
                        FlexText(text=company, size="sm", align="end", weight="bold", wrap=True)
                    ]),
                    FlexBox(layout="horizontal", contents=[
                        FlexText(text=f"{doc_emoji} เอกสาร:", size="sm"),
                        FlexText(text=doc_text, size="sm", align="end", weight="bold")
                    ]),
                ])
            ]
        ),
        footer=FlexBox(
            layout="vertical",
            contents=[
                FlexButton(
                    style="link",
                    action=URIAction(
                        label="ดูรายละเอียดใน Google Sheet",
                        uri="https://docs.google.com/spreadsheets/d/1nd4irLEihU61e03Rr2x7_n0QGeN389H15THM0jb10NY/edit"
                    )
                )
            ]
        )
    )

    return FlexMessage(
        alt_text=f"สถานะของ {student_name}",
        contents=bubble
    )
#============================================================
# ♦️11. ฟังก์ชัน [การแสดง FAQ] -> คำถามที่พบบ่อยจาก GSheet      |
#============================================================
def create_faq_flex(faq_list):
    bubbles = []

    for faq in faq_list[:10]:
        faq_id = faq.get('id', 'N/A')
        question = faq.get('question', 'ไม่มีคำถาม')
        answer = faq.get('answer', 'ไม่มีคำตอบ')

        bubble = FlexBubble(
            header=FlexBox(
                layout="vertical",
                contents=[
                    FlexText(text=f"❓ Q{faq_id}: {question}", weight="bold", size="md", wrap=True)
                ]
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    FlexText(text=answer, size="sm", wrap=True)
                ]
            ),
            footer=FlexBox(
                layout="vertical",
                contents=[
                    FlexButton(
                        style="link",
                        action=MessageAction(label="👍 เข้าใจแล้ว", text="ขอบคุณ")
                    )
                ]
            )
        )

        bubbles.append(bubble)

    return FlexMessage(
        alt_text="รายการคำถามที่พบบ่อย (FAQ)",
        contents=FlexCarousel(contents=bubbles)
    )

#============================================================
# ♦️10. ฟังก์ชัน [เมนูหลัก] -> ตรวจสอบข้อมูล นศ. และหัวข้อย่อยต่างๆ  |
#============================================================
def create_basic_menu_flex(student_id, name, major):

    bubble = FlexBubble(
        header=FlexBox(
            layout="vertical",
            contents=[
                FlexText(text="ยืนยันข้อมูลนักศึกษา", weight="bold", size="lg", color="#1DB446")
            ]
        ),
        body=FlexBox(
            layout="vertical",
            contents=[
                FlexText(text=f"รหัส: {student_id}", size="sm", color="#555555"),
                FlexText(text=f"ชื่อ: {name}", size="md", weight="bold"),
                FlexText(text=f"สาขา: {major}", size="sm", color="#555555"),
                FlexSeparator(margin="lg"),
                FlexText(text="กรุณาเลือกหัวข้อที่ต้องการทราบ:", size="xs", color="#837E7E"),
                FlexBox(layout="vertical", margin="md", spacing="sm", contents=[
                    FlexButton(
                        action=MessageAction(label="📊 ตรวจสอบก่อนฝึกงาน", text=f"ตรวจสอบก่อนฝึกงาน:{student_id}"),
                        style="primary",
                        color="#369A52"
                    ),
                    FlexButton(
                        action=MessageAction(label="📝 สถานะฝึกงาน & เอกสาร", text=f"สถานะการฝึกงานและเอกสาร:{student_id}"),
                        style="primary",
                        color="#369A52"
                    ),
                    FlexButton(
                        action=MessageAction(label="📄 ฝึกงานไหนดี?/ฝึกไหนได้บ้าง", text=f"ฝึกงานไหนดี?/ฝึกไหนได้บ้าง:{student_id}"),
                        style="primary",
                        color="#007AFF"
                    ),

                ])
            ]
        )
    )

    return FlexMessage(
        alt_text=f"ข้อมูลของ {name}",
        contents=bubble
    )
#============================================================
# 🔷 ฟังก์ชั่น"การตรวจสอบ" -> ตรวจสอบก่อนฝึกงาน                   |
#============================================================
def create_pre_internship_flex(data):
    
    #🔹Flex Message สำหรับหัวข้อที่ 1: 📊ตรวจสอบก่อนฝึกงาน
    bubble = FlexBubble(
        header=FlexBox(
            layout="vertical",
            contents=[
                FlexText(text="📊 ผลการตรวจสอบข้อมูล", weight="bold", size="lg", color="#1DB446")
            ]
        ),
        body=FlexBox(
            layout="vertical",
            spacing="md",
            contents=[
                # ข้อมูลพื้นฐาน
                FlexBox(layout="horizontal", contents=[
                    FlexText(text="รหัส:", size="sm", color="#AAAAAA", flex=1),
                    FlexText(text=data['student_id'], size="sm", align="end", flex=4)
                ]),
                FlexBox(layout="horizontal", contents=[
                    FlexText(text="ชื่อ:", size="sm", color="#AAAAAA", flex=1),
                    FlexText(text=data['name'], size="sm", align="end", flex=4, wrap=True)
                ]),
                FlexSeparator(margin="md"),
                
                # ส่วนข้อมูลเกณฑ์การตรวจสอบ
                FlexBox(layout="vertical", spacing="sm", margin="md", contents=[
                    FlexBox(layout="horizontal", contents=[
                        FlexText(text=" GPA:", size="sm", flex=2), #📈
                        FlexText(text=data['gpa'], size="sm", align="end", weight="bold", flex=2)
                    ]),
                    FlexBox(layout="horizontal", contents=[
                        FlexText(text=" ชม.กิจกรรม:", size="sm", flex=2), #⏰
                        FlexText(text=data['hours'], size="sm", align="end", weight="bold", flex=2)
                    ]),
                    FlexBox(layout="horizontal", contents=[
                        FlexText(text=" ICT:", size="sm", flex=2), #💻
                        FlexText(text=data['ict'], size="sm", align="end", weight="bold", flex=2)
                    ]),
                ]),
                FlexSeparator(margin="md"),
                
                # ส่วนสถานะผ่าน/ไม่ผ่าน
                FlexBox(layout="vertical", spacing="sm", contents=[
                    FlexBox(layout="horizontal", contents=[
                        FlexText(text="✅ ตรวจสอบฝึกงาน:", size="sm", flex=3),
                        FlexText(text=data['intern_pass'], size="sm", align="end", weight="bold", flex=2)
                    ]),
                    FlexBox(layout="horizontal", contents=[
                        FlexText(text="💼 ตรวจสอบสหกิจ:", size="sm", flex=3),
                        FlexText(text=data['coop_pass'], size="sm", align="end", weight="bold", flex=2)
                    ]),
                ]),
                FlexSeparator(margin="md"),
                 
                # ส่วนสรุปจาก Column T (แก้ปัญหาจุดไข่ปลา)
                FlexBox(layout="vertical", spacing="xs", contents=[
                    FlexText(text=" ผลการตรวจสอบ / สิ่งที่ต้องทำ:", size="xs", color="#AAAAAA", weight="bold"),
                    FlexText(
                        text=data['result'], 
                        size="md", 
                        color=data['res_color'], 
                        wrap=True,     
                        margin="sm",
                        weight="bold"
                    )
                ]) ,
                FlexSeparator(margin="md"),
                
                # 📁 ไฟล์สนับสนุนก่อนฝึกงาน
                FlexBox(
                    layout="vertical",
                    margin="lg",
                    paddingAll="md",
                    backgroundColor="#F0F8FF", 
                    cornerRadius="md",
                    contents=[
                        FlexText(text="📁 ไฟล์สนับสนุนก่อนฝึกงาน", weight="bold", size="sm", color="#007AFF", margin="xs"),
                        
                        # 1.1 ปฏิทินการศึกษา
                        FlexText(
                            text=" 1.1 ปฏิทินการศึกษา",
                            size="sm",
                            color="#325377",
                            align="start",
                            action=URIAction(
                                label="1.1 ปฏิทินการศึกษา",
                                uri="https://reg.mju.ac.th/registrar/calendar.asp?schedulegroupid=1001&acadyear=2568&semester=1"
                            ),
                            margin="sm"
                        ),
                        # 1.2 ระเบียบสหกิจ มจ.
                        FlexText(
                            text=" 1.2 ระเบียบสหกิจศึกษา มจ.",
                            size="sm",
                            color="#325377",
                            align="start",
                            action=URIAction(
                                label="1.2 ระเบียบสหกิจศึกษา มจ.",
                                uri="https://drive.google.com/file/d/1FGOpMPJ1zFD-2wDVVDX2zkL5OMdKnvid/view"
                            ),
                            margin="sm"
                        ),
                        # 1.3 คำอธิบายและแผนการฝึกงาน (CS)
                        FlexText(
                            text=" 1.3 แผนการฝึกงาน CS",
                            size="sm",
                            color="#325377",  
                            align="start",
                            action=URIAction(
                                label=" 1.3 แผนการฝึกงาน CS", #💻
                                uri="https://drive.google.com/file/d/1FGOpMPJ1zFD-2wDVVDX2zkL5OMdKnvid/view"
                            ),
                            margin="sm"
                        ),
                        # 1.4 คำอธิบายสหกิจ รหัส 65
                        FlexText(
                            text=" 1.4 คำอธิบายสหกิจ รหัส 65",
                            size="sm",
                            color="#325377",
                            align="start",
                            action=URIAction(
                                label=" 1.4 คำอธิบายสหกิจ รหัส 65", #📘
                                uri="https://drive.google.com/file/d/1auB6t6NxJYSGn3Fsobmw058MT7xOGp1o/view"
                            ),
                            margin="sm"
                        ),     
                    ]   
                ),
                
                # 📄 สิ่งที่ต้องเตรียมก่อนฝึกงาน
                FlexBox(
                    layout="vertical",
                    margin="lg",
                    paddingAll="md",
                    backgroundColor="#2E523C", 
                    cornerRadius="md",
                    
                    borderColor="#1DB446",
                    borderWidth="2px",
                    contents=[
                        FlexText(text="📄❗เอกสารที่ต้องเตรียมก่อนฝึกงาน", weight="bold", size="sm", color="#FFFFFF", margin="xs"),
                        
                        # 🔹2.1 สำเนา transcript 5 ภาคเรียน
                        FlexText(
                            text=" 2.1 สำเนา transcript 5 ภาคเรียน ",
                            size="sm",
                            color="#DFDFDF",
                            align="start",
                            action=URIAction(
                                label="2.1 สำเนา transcript 5 ภาคเรียน",
                                uri="https://maps.app.goo.gl/VUHJjJfnS2dvHRL79"
                            ),  
                            margin="sm"
                        ),
                        FlexBox(
                            layout="horizontal",
                            margin="xs",
                            paddingStart="lg",
                            contents=[
                                FlexText(
                                    text="🔗 ดูตย.ใบ transcript 5 ภาคเรียน",
                                    size="xs",
                                    color="#68B1FF",
                                    action=URIAction(
                                        label="ตัวอย่าง", 
                                        uri="https://drive.google.com/file/d/12BjG8GeFR976dNXvia_i0gGJIs65RMjn/view?usp=sharing"
                                    )
                                )
                            ]
                        ),
                        # 🔹2.2 ประกาศนียบัตรการอบรม สัมมนา ฯลฯ (ถ้ามี)
                        FlexText(
                            text=" 2.2 ใบรับรองการอบรม สัมมนา ฯลฯ(ถ้ามี)",
                            size="sm",
                            color="#DFDFDF",
                            align="start",
                            margin="sm"
                        ),
                        
                        # 🔹2.3 ความสำคัญของการเขียนประวัติย่อ(CV)
                        FlexText(
                            text=" 2.3 ความสำคัญของการเขียนประวัติย่อ (CV)",
                            size="sm",
                            color="#DFDFDF",
                            align="start",
                            action=URIAction(
                                label="2.3 ความสำคัญของการเขียนประวัติย่อ (CV)",
                                uri="https://www.airkhaek.com/%E0%B8%95%E0%B8%B1%E0%B8%A7%E0%B8%AD%E0%B8%A2%E0%B9%88%E0%B8%B2%E0%B8%87-cv/"
                            ),
                            margin="sm"
                        ),
                        FlexBox(
                            layout="vertical",
                            margin="xs",
                            paddingStart="lg",
                            contents=[
                                #FlexText(
                                #    text="🔗 ดูตัวอย่างใบ transcript 5 ภาค",
                                #    size="xs",
                                #    color="#007AFF",
                                #    action=URIAction(
                                #        label="ตัวอย่าง", 
                                #        uri="https://drive.google.com/file/d/12BjG8GeFR976dNXvia_i0gGJIs65RMjn/view?usp=sharing"
                                #    )
                                #),
                                 
                                FlexText(
                                    text="🔗 ดูตย.ใบประวัติย่อ(1 คน 1 ไฟล์ pdf เท่านั้น)",
                                    size="xs",
                                    color="#68B1FF",
                                    action=URIAction(
                                        label="ตัวอย่างใบประวัติย่อ", 
                                        uri="https://drive.google.com/file/d/12QyWIr-XrWnCsu0QrKkuWYYzguhiEMl4/view?usp=sharing"
                                    )
                                )
                            ]
                        ),

                        # 🔹 คำอธิบายและแผนการฝึกงาน (CS)
                        FlexText(
                            text="📒คู่มือ การสมัครเป็นนศ.ฝึกงาน",
                            size="sm",
                            color="#DFDFDF",  
                            align="start",
                            action=URIAction(
                                label=" 2.4 คู่มือ การสมัครเป็นนศ.ฝึกงาน", #💻
                                uri="https://drive.google.com/file/d/1N42uM1VYJypH-NyIH1xFI8wBuQGOy1xM/view?fbclid=IwZXh0bgNhZW0CMTEAYnJpZBExUGpaRk9FNE5nZmZyZWhaQ3NydGMGYXBwX2lkDDI1NjI4MTA0MDU1OAABHsEvISJgydG9r1R59vyzrCvXdis8LhEXwSmlajwfGbiFDwNOJXeafitTXMMM_aem_4tzl6XemfofaXMN5RcDl2A"
                            ),
                            margin="sm"
                        ),
                        # 🔹 ลิงก์อ้างอิงที่มา
                        #
                        FlexText(
                            text="ลิงก์อ้างอิงที่มา",
                            size="xs",
                            color="#007AFF",
                            align="end",
                            action=URIAction(
                                label="ลิงก์อ้างอิงที่มา",
                                uri="https://web.facebook.com/legacy/notes/801476346610710/"
                            ),
                            margin="sm"
                        ),                             
                    ]   
                )        
            ]
        ),
        footer=FlexBox(
            layout="vertical",
            contents=[
                FlexText(text="*ตรวจสอบข้อมูลให้ถูกต้องก่อนดำเนินการ", size="xxs", color="#BCBCBC", align="center")
            ]
        )
    )

    return FlexMessage(
        alt_text=f"ผลการตรวจสอบของ {data['name']}",
        contents=bubble
    )
#============================================================
#🔹ฟังก์ชั่น[การตรวจสอบ] ->สถานะฝึกงาน & เอกสาร ````````````                 |
#============================================================
def create_combined_internship_flex(data):
    """ฟังก์ชันใหม่: รวมสถานที่ฝึกงานและเอกสารไว้ในแผ่นเดียว"""
    bubble = FlexBubble(
        header=FlexBox(layout="vertical", contents=[
            FlexText(text="🏢 สถานะการฝึกงาน & เอกสาร", weight="bold", size="lg", color="#007AFF")
        ]),
        body=FlexBox(layout="vertical", spacing="md", contents=[
            # ข้อมูล นศ.
            FlexBox(layout="horizontal", contents=[
                FlexText(text="รหัส:", size="sm", color="#AAAAAA", flex=1),
                FlexText(text=data['student_id'], size="sm", align="start", flex=3)
            ]),
            FlexBox(layout="horizontal", contents=[
                FlexText(text="ชื่อ:", size="sm", color="#AAAAAA", flex=1),
                FlexText(text=data['name'], size="sm", align="start", flex=3, wrap=True)
            ]),
            FlexSeparator(margin="md"),
            
            # --- ส่วนที่ 1: สถานที่ฝึกงาน ---
            FlexBox(layout="vertical", margin="md", spacing="xs", contents=[
                FlexText(text=" สถานที่ฝึกงาน:", size="xs", color="#AAAAAA", weight="bold"), #📍
                FlexText(text=data['company'], size="sm", weight="bold", color=data['comp_color'], wrap=True),
                FlexText(text=f"จังหวัด: {data['province']} | ประเภท: {data['type']}", size="xxs", color="#8E8E93")
            ]),
            
            FlexSeparator(margin="md"),
            
            # --- ส่วนที่ 2: เอกสาร & สิ่งที่ต้องทำ ---
            FlexBox(layout="vertical", margin="md", spacing="xs", contents=[
                FlexText(text="📄 เอกสารล่าสุด:", size="xs", color="#AAAAAA", weight="bold"),
                FlexText(text=data['latest_doc'], size="sm", weight="bold"),
                FlexBox(layout="vertical", margin="md", paddingAll="sm", cornerRadius="sm", backgroundColor="#F8F8F8", contents=[
                    FlexText(text="💡 สิ่งที่ต้องทำถัดไป:", size="xxs", color="#888888", weight="bold"),
                    FlexText(text=data['todo_text'], size="sm", weight="bold", color=data['todo_color'], wrap=True)
                ])
            ])
        ])
    )
    return FlexMessage(alt_text=f"สรุปสถานะของ {data['name']}", contents=bubble)

#============================================================
#🔹ฟังก์ชั่นปุ่ม[ฝึกงานไหนดี?/ฝึกไหนได้บ้าง] -> สร้าง Flex             |
#============================================================
def create_internship_list_flex(bkk_data, north_data):
    # ฟังก์ชันสร้าง Bubble ย่อยสำหรับแต่ละโซน
    def create_bubble(title, subtitle, data_list, note=""):
        contents = [
            FlexText(text=title, weight="bold", size="lg", color="#007AFF"),
            FlexText(text=subtitle, size="xxs", color="#FF3B30", wrap=True, margin="xs") if subtitle else FlexFiller(size="xs"),
            FlexSeparator(margin="md")
        ]
        
        # ใส่รายชื่อบริษัท
        list_text = "\n".join(data_list) if data_list else "ไม่มีข้อมูล"
        contents.append(FlexText(text=list_text, size="xxs", wrap=True, margin="md", color="#333333"))
        
        if note:
            contents.append(FlexSeparator(margin="md"))
            contents.append(FlexText(text=note, size="xxs", color="#AAAAAA", wrap=True, margin="md", style="italic"))
            
        return FlexBubble(
            body=FlexBox(layout="vertical", contents=contents),
            footer=FlexBox(layout="vertical", spacing="sm", contents=[
                FlexButton(style="link", height="sm", color="#007AFF", action=URIAction(label="🔗 ตรวจสอบบริษัททั้งหมด", uri="https://docs.google.com/spreadsheets/d/11Zff0QuQ5QDD5Zv7U25wd7JeqfD1KbjQ/edit?usp=share_link&ouid=111522346972593692384&rtpof=true&sd=true&fbclid=IwZXh0bgNhZW0CMTEAYnJpZBExRXB5T0txTDlGM0FkSUVBR3NydGMGYXBwX2lkDDI1NjI4MTA0MDU1OAABHh7lvWysQuhvfC_gjNXV-qUzAk0JMfvomVywbC-0qSV0P7RI1p5MFGcjR3mv_aem_9O5gz3pCsZJyD-h5eevKqQ")),
                FlexButton(style="link", height="md", color="#007AFF", action=URIAction(label="🔗 ตรวจสอบบริษัทพี่ๆ ศิษย์เก่า", uri="https://docs.google.com/spreadsheets/d/1B7Jwjd5AtQyFAVvd6RyPppOG6fdfJd4QeiYYghjTqs4/edit?usp=sharing"))
            ])
        )

    # รวมเป็น Carousel
    carousel = FlexCarousel(contents=[
        create_bubble("📍 กรุงเทพและปริมณฑล", "(กรุงเทพและปริมณฑลส่วนใหญ่จะรับเข้าฝึกงาน 2 เดือน และต่อด้วยสหกิจ 4 เดือน ไม่รับฝึกงานอย่างเดียว)", bkk_data),
        create_bubble("📍 เชียงใหม่ ลำพูน", "", north_data, "สามารถหาบริษัทได้ด้วยตนเอง แต่ต้องเป็นสายซอฟต์แวร์/ไอที และปรึกษาพี่ฝนก่อนทุกครั้ง")
    ])
    
    return FlexMessage(alt_text="รายชื่อสถานที่ฝึกงาน", contents=carousel)
#============================================================
#🔹ฟังก์ชั่น[การแสดงข่าวสาร] -> สร้าง Flex สำหรับประกาศข่าวสาร      |
#============================================================
def create_news_flex(news_data):
    """สร้างหน้าตาประกาศข่าวสาร (เหมือนโฆษณา KFC)"""
    bubble = FlexBubble(
        size="mega",
        header=FlexBox(
            layout="vertical",
            paddingAll="0px",
            contents=[
                FlexImage(
                    url=news_data['image'],
                    size="full",
                    aspect_mode="cover",
                    aspect_ratio="1.1:1" # สัดส่วนรูปภาพ
                )
            ]
        ),
        body=FlexBox(
            layout="vertical",
            spacing="md",
            contents=[
                FlexText(text=news_data['title'], weight="bold", size="xl", color="#007AFF"),
                FlexText(text=news_data['desc'], size="sm", wrap=True),
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(text="📅 Deadline:", size="xs", color="#AAAAAA", flex=1),
                        FlexText(text=news_data['deadline'], size="xs", color="#FF3B30", flex=3, weight="bold")
                    ]
                )
            ]
        ),
        footer=FlexBox(
            layout="vertical",
            contents=[
                FlexButton(
                    style="primary",
                    color="#007AFF",
                    action=URIAction(label="อ่านรายละเอียด", uri="https://cs.mju.ac.th")
                )
            ]
        )
    )
    # ต้องครอบด้วย FlexMessage เพื่อให้ส่งออกไปได้
    return FlexMessage(alt_text="📢 มีข่าวสารใหม่จากภาควิชา!", contents=bubble)