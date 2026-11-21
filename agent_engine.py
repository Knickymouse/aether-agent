import os
import json
import re
import feedparser
import anthropic
from datetime import datetime

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MEMORY_FILE = "memory.json"

def load_memory() -> list:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(entry: dict):
    history = load_memory()
    history.append(entry)
    # 直近30件の記憶を保持
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-30:], f, ensure_ascii=False, indent=2)

def fetch_latest_trends() -> str:
    """
    Google News RSS（日本の最新トレンド・テクノロジー・ビジネス）から最新の世の中の動きを取得
    """
    rss_urls = [
        "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ja&gl=JP&ceid=JP:ja",
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ja&gl=JP&ceid=JP:ja",
        "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
    ]
    headlines = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:6]:
            headlines.append(f"- {entry.title}")
    
    # 重複を除去して結合
    unique_headlines = list(dict.fromkeys(headlines))
    return "\n".join(unique_headlines[:15])

def extract_json(text: str) -> dict:
    """LLMの出力から安全にJSONを抽出するヘルパー"""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {"score": 70, "critique": "JSONパース失敗のため再思考を実行"}

def run_autonomous_thinking_loop(max_iterations: int = 3) -> dict:
    """
    【自律思考エンジン】
    世間の流行・環境を読み込み、自己批判ループを経て考え抜かれた事業アイデアを出力する
    """
    trends = fetch_latest_trends()
    past_memories = load_memory()
    past_titles = [m.get("title", "") for m in past_memories]
    
    feedback = "初回思考。固定概念を完全に破壊する斬新な切り口からスタートせよ。"
    best_idea = ""
    best_score = 0
    thought_log = []

    for attempt in range(1, max_iterations + 1):
        print(f"🧠 [自律思考ループ {attempt}/{max_iterations}回目] 実行中...")
        
        # --- Step 1: アイデア生成・昇華フェーズ ---
        generator_prompt = f"""
あなたは孫正義の「タイムマシン経営・A→B→C群戦略」と、ジェンスン・フアンの「計算コストゼロ化・フィジカルAI・デジタルツイン思想」を体得した自律型起業AI『AETHER-AUTONOMOUS』です。

【現在の世間の最新トレンド・ニュース】
{trends}

【過去に考案済みのテーマ（重複禁止）】
{past_titles}

【前回の自己批判フィードバック（これを完全に克服すること）】
{feedback}

# ミッション
上記の最新トレンドや生活環境の変化を踏まえ、「人々の暮らしの一部に空気のように溶け込み、毎日当たり前のように使われるスマホアプリ（Phase A）」を起点とし、最終的に「法人インフラ（Phase B）→ フィジカルAI・空間制御（Phase C）」へと化ける画期的な事業アイデアを1つ考え抜いてください。

# 必須条件
1. ユーモアとパッションがあり、ユーザーの感情を動かす仕掛けがあること。
2. ユーザーに長文プロンプトを入力させない「ゼロ・フリクションUX（カメラ・音声・ワンタップ等）」であること。
3. 単なる既存AIのラッパーではなく、使えば使うほど個人の記憶・行動データ（デジタルツイン）が溜まり乗り換え不可能になること。

# 出力フォーマット（Markdown）
### 💡 アプリ名＆キャッチコピー
（ユーモアとインパクトのある一言）

### 🌍 捉えたトレンドと「非常識な切り口」
（どの世間の動きに目をつけ、どんな固定概念を壊したか）

### 📱 暮らしの当たり前になるUX（Phase A：最初のアプリ仕様）
（1日のどの瞬間に、ユーザーが何をして、AIがどう返すか）

### 🔄 A → B → C 進化ロードマップ
- **Phase A（個人習慣）：** 
- **Phase B（法人・現場インフラ）：** 
- **Phase C（フィジカルAI・ロボティクス連携）：** 
"""
        gen_response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": generator_prompt}]
        )
        current_idea = gen_response.content[0].text

        # --- Step 2: 冷徹な自己批判（Red-Team）フェーズ ---
        critic_prompt = f"""
あなたは世界で最も厳しいトップVC兼プロダクト責任者です。
以下の事業アイデアを100点満点で厳しく採点し、弱点を容赦なく指摘してください。

【評価基準】
1. 本当に「3日で飽きられず」毎日の習慣になるか？（25点）
2. ユーモア・パッション・非常識な面白さがあるか？（25点）
3. Big Tech（Apple/Google/OpenAI等）の標準機能に潰されない独自データ（Moat）があるか？（25点）
4. Phase A（個人アプリ）からB（法人）・C（フィジカルAI）への接続に無理がないか？（25点）

【評価対象アイデア】
{current_idea}

必ず以下のJSONフォーマットのみを出力してください（余計な文章は一切不要）：
{{
  "title": "アイデアの短いタイトル",
  "score": 82,
  "critique": "どこが甘いか、どう作り直せば90点以上になるかの具体的な改善指示"
}}
"""
        crit_response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": critic_prompt}]
        )
        
        eval_data = extract_json(crit_response.content[0].text)
        score = eval_data.get("score", 0)
        feedback = eval_data.get("critique", "")
        title = eval_data.get("title", "新規事業アイデア")
        
        thought_log.append(f"試行{attempt}回目: {score}点 - 批判: {feedback}")
        print(f"⚖️ 評価スコア: {score}点 | 批判: {feedback[:60]}...")

        if score >= best_score:
            best_score = score
            best_idea = current_idea
            best_title = title

        # 85点以上に到達したら「考え抜いた」と判断してループ完了
        if score >= 85:
            print("✅ 合格基準（85点以上）に到達！思考を確定します。")
            break

    result_payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": best_title,
        "final_score": best_score,
        "trends_referenced": trends,
        "thought_process": thought_log,
        "final_idea": best_idea
    }
    
    # 記憶に保存
    save_memory({"timestamp": result_payload["timestamp"], "title": best_title, "score": best_score})
    return result_payload
