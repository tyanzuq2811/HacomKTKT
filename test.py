from google import genai

import os
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Bạn là ai?"
)

print(response.text)

# from pathlib import Path

# old_file = Path("D:\OIP.webp")   # Đường dẫn file gốc
# new_file = old_file.with_suffix(".xlsx") # Đổi đuôi thành .xlsx

# old_file.rename(new_file)

# print(f"Đã đổi tên thành: {new_file}")