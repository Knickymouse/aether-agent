import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from agent_engine import run_autonomous_thinking_loop, load_memory
from notifier import dispatch_notifications

load_dotenv()

def scheduled_autonomous_job():
    print("⏰ 定期自律思考タスクを開始します...")
    result = run_autonomous_thinking_loop(max_iterations=3)
    dispatch_notifications(result)
    print("🎉 自律思考＆通知が完了しました！")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # サーバー起動時にスケジューラを開始（毎日 日本時間 朝7:00 に自動実行）
    scheduler = BackgroundScheduler(timezone="Asia/Tokyo")
    scheduler.add_job(scheduled_autonomous_job, CronTrigger(hour=7, minute=0))
    scheduler.start()
    print("🚀 AETHER-AUTONOMOUS スケジューラ稼働開始（毎日 07:00 JST 実行）")
    yield
    scheduler.shutdown()

app = FastAPI(title="AETHER-AUTONOMOUS API", lifespan=lifespan)

@app.get("/")
def health_check():
    return {"status": "running", "agent": "AETHER-AUTONOMOUS"}

@app.post("/run-now")
def trigger_now(background_tasks: BackgroundTasks):
    """今すぐ自律思考ループをバックグラウンドで起動し、完了後に通知を送る"""
    background_tasks.add_task(scheduled_autonomous_job)
    return {"message": "自律思考ループをバックグラウンドで開始しました。完了次第通知されます。"}

@app.get("/ideas/history")
def get_idea_history():
    """過去にAIが考え抜いたアイデアの履歴をJSONで取得（自作アプリ連携用）"""
    return {"history": load_memory()}