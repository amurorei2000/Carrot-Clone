from fastapi import FastAPI, UploadFile, Form, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from typing import Annotated
import sqlite3
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

con = sqlite3.connect('carot.db', check_same_thread=False)
cur = con.cursor()

app = FastAPI()


@app.post("/items")
async def create_item(image: UploadFile, 
                title: Annotated[str, Form()], 
                price: Annotated[int, Form()],
                description: Annotated[str, Form()],
                place: Annotated[str, Form()],
                insertAt: Annotated[int, Form()]):
    
    # 이미지를 바이트 배열로 변환
    image_bytes = await image.read()
    
    # Hex(16진수) 데이터로 변환해서 db에 저장
    cur.execute(f"""
                INSERT INTO items (title, image, price, description, place, insertAt) 
                VALUES ('{title}', '{image_bytes.hex()}', {price}, '{description}', '{place}', {insertAt});
                """)
    con.commit()
    
    return '200'

@app.get("/items")
async def get_item():
    # 컬럼명 가져오기
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # 테이블 데이터 가져오기
    rows = cur.execute(f"""
                SELECT * FROM items;
                """).fetchall()
    
    # dict 변환  -> Json 변환
    return JSONResponse(jsonable_encoder(dict(row) for row in rows))

@app.get("/images/{item_id}")
async def get_image(item_id):
    try:
        # db에서 이미지 데이터 가져오기
        cur = con.cursor()
        image_bytes = cur.execute(f"""
                                SELECT image
                                FROM items
                                WHERE id={item_id}
                                """).fetchone()[0]
        
        return Response(content=bytes.fromhex(image_bytes))
    except Exception as e:
        print(e)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)