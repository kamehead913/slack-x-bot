from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.post("/")
async def handle_event(request: Request):
    payload = await request.json()

    # SlackのURL検証：challengeが含まれているときだけ返す
    if "challenge" in payload:
        return JSONResponse(content={"challenge": payload["challenge"]})

    # （イベント処理ロジックはここに必要に応じて書く）
    return JSONResponse(content={"status": "ok"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
