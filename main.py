"""
GenOS Python code-serving — 워크플로우 sample.
/chat 만 노출. 외부 LLM 의존성 없이 question 을 echo 로 응답.
requirements.txt: fastapi, uvicorn[standard]
"""
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(body: dict | None = None):
    question = (body or {}).get("question") or ""
    if question == "__verify__":
        return {"code": 0, "data": {"text": "verified"}}
    if not question:
        return {"code": 0, "data": {"text": "[ERROR] question is empty"}}
    # 외부 LLM 의존성 없이 echo. 실제 코드서빙에선 원하는 로직으로 교체.
    return {"code": 0, "data": {"text": f"echo: {question}"}}

# ── 수동 테스트 ──────────────────────────────────────────────

if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)

    def check(name: str, condition: bool, extra: str = "") -> None:
        status = "✅ PASS" if condition else "❌ FAIL"
        print(f"{status} - {name}" + (f" | {extra}" if extra else ""))

    print("=" * 60)
    print("GET /health")
    print("=" * 60)
    res = client.get("/health")
    print(f"status_code={res.status_code}, body={res.json()}")
    check("health status_code == 200", res.status_code == 200)
    check("health body == {'status': 'ok'}", res.json() == {"status": "ok"})

    print("\n" + "=" * 60)
    print("POST /chat - 정상 질문")
    print("=" * 60)
    res = client.post("/chat", json={"question": "소금빵 레시피"})
    print(f"status_code={res.status_code}, body={res.json()}")
    check("status_code == 200", res.status_code == 200)
    check("code == 0", res.json().get("code") == 0)
    check(
        "echo 응답 확인",
        res.json().get("data", {}).get("text") == "echo: 소금빵 레시피",
    )

    print("\n" + "=" * 60)
    print("POST /chat - __verify__ 특수 케이스")
    print("=" * 60)
    res = client.post("/chat", json={"question": "__verify__"})
    print(f"status_code={res.status_code}, body={res.json()}")
    check(
        "verified 응답 확인",
        res.json().get("data", {}).get("text") == "verified",
    )

    print("\n" + "=" * 60)
    print("POST /chat - question 빈 문자열")
    print("=" * 60)
    res = client.post("/chat", json={"question": ""})
    print(f"status_code={res.status_code}, body={res.json()}")
    check(
        "빈 question 에러 메시지 확인",
        res.json().get("data", {}).get("text") == "[ERROR] question is empty",
    )

    print("\n" + "=" * 60)
    print("POST /chat - question 키 자체가 없음")
    print("=" * 60)
    res = client.post("/chat", json={})
    print(f"status_code={res.status_code}, body={res.json()}")
    check(
        "question 누락 시에도 에러 메시지 확인",
        res.json().get("data", {}).get("text") == "[ERROR] question is empty",
    )

    print("\n" + "=" * 60)
    print("POST /chat - body 자체가 null (빈 요청)")
    print("=" * 60)
    res = client.post("/chat", json=None)
    print(f"status_code={res.status_code}, body={res.json()}")
    check(
        "body가 없어도 에러 메시지 확인",
        res.json().get("data", {}).get("text") == "[ERROR] question is empty",
    )

    print("\n모든 테스트 완료.")