from fastapi import FastAPI
from pydantic import BaseModel  # 自動檢驗型別
from extract import extract_cognitive_graph
from services import process_extraction
from fastapi.middleware.cors import CORSMiddleware

"""
RUN CMD: uvicorn api:app --reload
指令中的 api (檔案名稱): api.py 是 FastAPI 的 server 端程式，提供 API 給前端或其他服務使用
指令中的 app (FastAPI 的實例名稱): 對應到程式中的 app = FastAPI()
"""

class ExtractRequest(BaseModel):
    text: str   

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 允許所有來源的請求
    allow_methods=["*"],      # 允許所有 HTTP 方法
    allow_headers=["*"]     # 允許所有標頭
)

@app.get("/")   # get: client 端獲取 server 端的資料
async def root():
    return {"message": "Hello from cognitive graph API"}

@app.post("/extract")   # post: client 端向 server 端發送資料
async def extract(request: ExtractRequest): # 使用自定義class, 檢驗傳入的資料型別
    result = extract_cognitive_graph(request.text)
    node_id_map = process_extraction(request.text, result)

    return {
        "status": "success",
        "node_count": len(result.get("nodes", [])),
        "forward_question": result.get("forward_question")
    }
