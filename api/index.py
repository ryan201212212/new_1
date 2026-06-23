from flask import Flask, Response
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def index():
    # Vercel Serverless Function이 호출되면 백그라운드로 streamlit을 띄우거나 안내 메시지를 반환합니다.
    return Response(
        "✨ JUDAAN B2B Sales Dashboard (Vercel Node) is active.<br>"
        "Vercel은 정적 페이지에 최적화되어 있어, 실시간 Streamlit 대시보드를 구동하기 위해 아래 웹 어드레스를 추천합니다.<br>"
        "👉 <a href='https://share.streamlit.io' target='_blank'>Streamlit Community Cloud 공식 호스팅</a>",
        mimetype="text/html"
    )
