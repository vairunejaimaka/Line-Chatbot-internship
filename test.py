#import time
#import google.generativeai as genai
#genai.configure(api_key="AIzaSyA7nsWn9loBJEGvuYz-B8_frbuvoCFqWyM")
#for m in genai.list_models():
#  if 'generateContent' in m.supported_generation_methods:
#    print(m.name)
#    
#model = genai.GenerativeModel("gemini-flash-latest")
#
#prompt = "ตอบสั้นๆ 1 บรรทัด ใส่ 1 emoji: สวัสดี"
#
#t = time.time()
#response = model.generate_content(prompt)
#print("TIME:", time.time() - t)
#print(response.text)

from urllib.parse import quote

url = "https://www.airkhaek.com/ตัวอย่าง-cv/"
safe_url = quote(url, safe=':/?=&')

print(safe_url)