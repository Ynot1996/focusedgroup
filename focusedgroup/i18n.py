"""Tiny i18n layer: English is the default, Chinese is the toggle.

A translation is looked up by key for the active language; missing keys fall
back to English, then to the key itself. The active language lives in the
session and is switched via the /lang/<code> route (see routes).
"""

from flask import session

DEFAULT_LANG = "en"
SUPPORTED_LANGS = ("en", "zh")

TRANSLATIONS = {
    "en": {
        # --- navigation / common chrome ---
        "nav.finance": "Finance",
        "nav.team": "Team",
        "nav.showcase": "Showcase",
        "nav.fg_finance": "FG Finance",
        "common.continue": "Continue",
        "common.full_news": "Full story",
        "account.profile": "My Profile",
        "account.account": "My Account",
        "account.logout": "Logout",
        "lang.toggle": "中文",  # label that switches TO the other language
        # --- homepage ---
        "home.tagline": "Invest in the future, enjoy life",
        "home.featured_title": "Stock Forecast",
        "home.featured_body": (
            "Learning to invest has become an essential skill in recent years, and "
            "maximizing returns in the shortest time is a hard problem. We use an LSTM "
            "model to forecast market trends, wrapped in a clean, simple interface that "
            "anyone can use. Accurate forecasts mean an edge: position earlier and avoid "
            "unnecessary losses."
        ),
        "home.post1_title": "ChatGPT can predict stock prices!",
        "home.post1_body": (
            "Since ChatGPT arrived, many roles face the risk of being replaced. A finance "
            "professor at the University of Florida, Alejandro Lopez-Lira, found that "
            "ChatGPT can predict next-day stock movements better than random guessing."
        ),
        "home.post2_title": "Quantum breakthrough brings a computing revolution",
        "home.post2_body": (
            "Researchers are a step closer to multi-purpose 'quantum' computers far more "
            "powerful than today's best supercomputers. A team at the University of Sussex "
            "transmitted quantum information between chips at unprecedented speed and "
            "precision."
        ),
        "home.post3_title": "A screen-free, voice-controlled AI experience",
        "home.post3_body": (
            "Is the screen really our only interface to technology? To break that limit, "
            "Humane — founded by former Apple staff Imran Chaudhri and Bethany Bongiorno — "
            "unveiled an AI projection wearable for a seamless, screen-free experience."
        ),
        "home.post4_title": "How does AI combine with blockchain?",
        "home.post4_body": (
            "Through panels and roundtables, this summit explored ecosystem integration, AI "
            "applications, blockchain in healthcare and the VR metaverse, and how to bring "
            "these to Taiwan — with a focus on economic value, policy, and sustainability."
        ),
        # --- footer ---
        "footer.name": "Name",
        "footer.email": "Email",
        "footer.message": "Message",
        "footer.contact_us": "Contact us",
        "footer.address_label": "Address",
        "footer.address_value": "4F, No. 237, Sec. 2, Fuxing S. Rd., Taipei",
        "footer.phone_label": "Phone",
        "footer.social": "Social",
        # --- team ---
        "team.title": "Elite Team",
        "team.subtitle": "Meet the people behind Focused Group",
        "team.intro": (
            "We are a team passionate about technology, spanning frontend design, backend "
            "development, LSTM modeling, and web crawling. We believe the best results come "
            "from great collaboration, and we combine our experience to deliver solid "
            "technical solutions."
        ),
        "team.maintainer_role": "Lead Maintainer · Full-Stack",
        "team.maintainer_note": "Maintaining and developing this project going forward.",
        "team.role_leader": "Team Lead",
        "team.role_model": "Model Development",
        "team.role_frontend": "Frontend Design",
        "team.role_crawler": "Data Crawling",
        # member names (romanized for the English view)
        "team.name_tony": "Wen-Teng Kang",
        "team.name_jason": "Yuan-Zhi Zhang",
        "team.name_rondolph": "Tang-Yao Zhang",
        "team.name_ted": "Yi-Chen Wu",
        "team.name_leg": "Kan-Yu Xu",
        # --- stock pages ---
        "stock.global_markets": "Global Markets",
        "stock.recent_events": "Recent Events",
        "stock.market_trends": "Market Trends",
        "stock.intro": "Overview",
        "idx.sp500": "S&P 500 Index",
        "idx.dow": "Dow Jones Industrial Average",
        "idx.nasdaq": "NASDAQ Composite",
        "idx.nikkei": "Nikkei 225",
        "idx.taiex": "TAIEX",
        "trend.halfyear": "Half-year trend",
        "trend.weekly": "Weekly forecast",
        "trend.monthly": "Monthly forecast",
        "trend.quarterly": "Quarterly forecast",
        "tag.metaverse": "Metaverse",
        "tag.ai_data": "AI Data",
        "tag.crypto": "Crypto",
        # --- ML forecast card ---
        "forecast.title": "AI Forecast — Next Session",
        "forecast.prob_up": "Probability of rise",
        "forecast.direction": "Direction",
        "forecast.up": "Up",
        "forecast.down": "Down",
        "forecast.confidence": "Confidence",
        "forecast.range": "Predicted range (80%)",
        "forecast.last_close": "Last close",
        "forecast.as_of": "Based on close of",
        "forecast.backtest": "Backtest accuracy",
        "forecast.vs_baseline": "always-up baseline",
        "forecast.sharpe": "Strategy Sharpe",
        "forecast.buyhold": "buy & hold",
        "forecast.none": "Forecast not generated yet — run the ML pipeline.",
        "forecast.disclaimer": (
            "Educational only, not investment advice. Daily index direction is "
            "largely unpredictable; we show honest walk-forward backtests against "
            "naive baselines, not guarantees."
        ),
    },
    "zh": {
        "nav.finance": "聚焦金融",
        "nav.team": "專業團隊",
        "nav.showcase": "成果展示",
        "nav.fg_finance": "FG 財經",
        "common.continue": "繼續",
        "common.full_news": "完整新聞",
        "account.profile": "個人資料",
        "account.account": "我的帳戶",
        "account.logout": "登出",
        "lang.toggle": "EN",
        "home.tagline": "投資未來，享受人生",
        "home.featured_title": "未來的股市?",
        "home.featured_body": (
            "近年來學會如何投資理財已經變成大家必備的能力。如何在最短時間內，將自己的利益最大化成了一個艱難的問題。"
            "而我們想利用 LSTM 演算法搭配模型來預測股票的走勢，並希望以簡單、明瞭的操作介面讓各個年齡層的人都能輕鬆使用。"
            "若是能準確預測，那便可在投資方面占得先機、提前部署，減少不必要的虧損。"
        ),
        "home.post1_title": "ChatGPT竟能預測股價！AI秒精準給出隔天走勢",
        "home.post1_body": (
            "ChatGPT出現後，不少產業出現了被取代的危機，尤其攸關計算的職務甚至更加的焦慮。近期佛羅里達大學金融學教授"
            "Alejandro Lopez-Lira就表示，ChatGPT竟然能預測隔日股價走勢，甚至比隨機預測來得好。"
        ),
        "home.post2_title": "量子技術突破帶來計算機革命",
        "home.post2_body": (
            "研究人員離實現製造多任務的「量子」計算機又近了一步，那將是比現有的最先進的超級計算機更強大的計算機。"
            "英國蘇塞克斯大學（Sussex University）的研究團隊實現了在電腦芯片之間以前所未有的速度和精度傳送量子信息。"
        ),
        "home.post3_title": "無螢幕全聲控的 AI 應用體驗",
        "home.post3_body": (
            "當前人類正透過各式各樣的螢幕與各種科技接觸，但螢幕真的是人類使用科技的唯一管道與介面嗎？為了打破這樣的侷限，"
            "由蘋果前員工 Imran Chaudhri 和 Bethany Bongiorno 創立的 Humane 新創公司推出了基於 AI 投影的穿戴式裝置，"
            "進而讓使用者享受免螢幕、無縫式及感應式應用體驗。"
        ),
        "home.post4_title": "AI如何跟區塊鏈技術結合？",
        "home.post4_body": (
            "本高峰會活動以專場與圓桌論壇進行交流，探討產業生態系整合、AI人工智能的應用、區塊鏈在健康長照、VR元宇宙等領域"
            "的應用，以及如何落地台灣場域的應用。此外，更關注於其經濟價值和法律政策，幫助產業各方更深了解未來走向。"
        ),
        "footer.name": "姓名",
        "footer.email": "電子郵件",
        "footer.message": "訊息",
        "footer.contact_us": "聯絡我們",
        "footer.address_label": "地址",
        "footer.address_value": "台北市復興南路二段237號4樓",
        "footer.phone_label": "電話",
        "footer.social": "社群",
        "team.title": "菁英團隊",
        "team.subtitle": "認識 Focused Group 背後的團隊",
        "team.intro": (
            "我們是一個對技術領域充滿熱忱的團隊，涵蓋前端設計、後端開發、LSTM 模型開發與網路爬蟲。"
            "我們相信最好的成果來自優秀的團隊合作，因此融合彼此的技術經驗與知識，提供最佳的技術服務。"
        ),
        "team.maintainer_role": "專案維護者 · 前後端整合",
        "team.maintainer_note": "本專案後續由本人持續維護與開發。",
        "team.role_leader": "小組組長",
        "team.role_model": "模型製作",
        "team.role_frontend": "前端設計",
        "team.role_crawler": "數據爬蟲",
        "team.name_tony": "康文騰",
        "team.name_jason": "張源智",
        "team.name_rondolph": "張堂垚",
        "team.name_ted": "吳奕辰",
        "team.name_leg": "許堪佑",
        "stock.global_markets": "全球市場",
        "stock.recent_events": "近期事件",
        "stock.market_trends": "市場趨勢",
        "stock.intro": "簡介",
        "idx.sp500": "標準普爾500指數",
        "idx.dow": "道瓊工業平均指數",
        "idx.nasdaq": "那斯達克綜合指數",
        "idx.nikkei": "日經平均指數",
        "idx.taiex": "台灣加權股價指數",
        "trend.halfyear": "半年走勢圖",
        "trend.weekly": "周線-預測圖",
        "trend.monthly": "月線-預測圖",
        "trend.quarterly": "季線-預測圖",
        "tag.metaverse": "元宇宙",
        "tag.ai_data": "AI數據",
        "tag.crypto": "加密貨幣",
        # --- ML forecast card ---
        "forecast.title": "AI 預測 — 下一交易日",
        "forecast.prob_up": "上漲機率",
        "forecast.direction": "預測方向",
        "forecast.up": "看漲",
        "forecast.down": "看跌",
        "forecast.confidence": "信心度",
        "forecast.range": "預測區間（80%）",
        "forecast.last_close": "前收盤",
        "forecast.as_of": "基準收盤日",
        "forecast.backtest": "回測準確率",
        "forecast.vs_baseline": "永遠看漲基準",
        "forecast.sharpe": "策略 Sharpe",
        "forecast.buyhold": "買進持有",
        "forecast.none": "預測尚未產生——請先執行 ML pipeline。",
        "forecast.disclaimer": (
            "僅供學習，非投資建議。每日指數方向大致不可預測；我們呈現對照基準線的"
            "誠實 walk-forward 回測，而非任何保證。"
        ),
    },
}


def get_lang() -> str:
    """The active language for this request, defaulting to English."""
    lang = session.get("lang", DEFAULT_LANG)
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def translate(key: str) -> str:
    """Look up a key in the active language, falling back to English then key."""
    lang = get_lang()
    return TRANSLATIONS[lang].get(key) or TRANSLATIONS["en"].get(key, key)
