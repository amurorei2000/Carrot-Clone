from fastapi import FastAPI, UploadFile, Form, Response, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import Annotated
import sqlite3
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from jose import jwt, JWTError
from datetime import datetime, timedelta


con = sqlite3.connect('carot.db', check_same_thread=False)
cur = con.cursor()

# 테이블이 없으면 생성하기
cur.execute(f"""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                image BLOB,
                price INTEGER NOT NULL,
                description TEXT,
                place TEXT NOT NULL,
                insertAt INTEGER NOT NULL
            );
            """)

# users 테이블 생성
cur.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            );
            """)

app = FastAPI()

# 엑세스 토큰 매니저 생성
SECRET = "wsdevelop"
manager = LoginManager(SECRET, "/login")
        
@app.post("/signup")
def signup(id: Annotated[str, Form()],
           password: Annotated[str, Form()],
           name: Annotated[str, Form()],
           email: Annotated[str, Form()]):
    
    cur.execute(f"""
                INSERT INTO users(id, name, email, password)
                VALUES ('{id}', '{name}', '{email}', '{password}')
                """)
    con.commit()
    return '200'

@manager.user_loader()
def query_user(data):
    print(f"query_user 호출됨 - 타입: {type(data)}")
    print(f"query_user 호출됨 - 데이터: {data}")
    
    try:
        WHERE_STATEMENTS = f"{data}"
        if type(data) == dict:
            WHERE_STATEMENTS = f"{data['sub']['id']}"
        
        print(f"추출된 사용자 ID: {WHERE_STATEMENTS}")
        
        user = cur.execute(f"""
                    SELECT *
                    FROM users
                    WHERE id = '{WHERE_STATEMENTS}'
                    """).fetchone()
        
        print(f"DB에서 찾은 사용자: {user}")
        
        # 사용자를 딕셔너리 형태로 반환
        if user:
            return {
                "id": user[0],
                "name": user[1], 
                "email": user[2],
                "password": user[3]
            }
        return None
    except Exception as e:
        print(f"query_user 에러: {e}")
        return None

@app.post("/login")
def login(id: Annotated[str, Form()],
          password: Annotated[str, Form()]):
    user = query_user(id)
    
    # 유저 정보가 db에 없는 경우
    if not user:
        raise InvalidCredentialsException
    # 입력한 패스워드가 db와 다른 경우
    elif password != user['password']:
        raise InvalidCredentialsException
    
    # 엑세스 토큰 발급
    access_token = manager.create_access_token(data={
        "sub": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
        }
    },
        expires=timedelta(minutes=30)
    )
    
    # 리프레시 토큰 발급
    refresh_token = jwt.encode(
        {"sub": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
        },
        "exp": datetime.now() + timedelta(days=7) 
        },
        key="wsdevelop",
        algorithm="HS256"
    )
    
    # 쿠키에 저장하기
    response = Response()
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        max_age=1800,
        expires=1800
    )
    
    return JSONResponse(content={"accessToken": access_token})

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

# 인증 상태에 의존
@app.get("/items")
# async def get_item(user=Depends(manager)):
async def get_item():
    # 컬럼명 가져오기
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # 테이블 데이터 가져오기
    rows = cur.execute(f"""
                SELECT * 
                FROM items
                ORDER BY insertAt;
                """).fetchall()
    
    print(rows)
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
        
        return Response(content=bytes.fromhex(image_bytes), media_type="image/*")
    except Exception as e:
        print(e)

# 정적 파일 연결(FrontEnd 파일들)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)