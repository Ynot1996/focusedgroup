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
        # --- homepage redesign ---
        "home.fc_kicker": "AI-modelled",
        "home.fc_heading": "Tomorrow's market outlook",
        "home.fc_sub": "Next-session direction and an 80% range for the major indices — from a model held to an honest walk-forward backtest, not a promise.",
        "home.fc_view": "View details",
        "home.fc_acc": "backtest acc.",
        "home.feat_heading": "What this project actually does",
        "home.feat1_t": "Probabilistic forecasts",
        "home.feat1_b": "Daily up/down probability and a price range for major indices — calibrated, not hand-waved.",
        "home.feat2_t": "Honest backtesting",
        "home.feat2_b": "Every number is earned by walk-forward testing against naive baselines. No cherry-picking.",
        "home.feat3_t": "UK & US market news",
        "home.feat3_b": "Live market headlines from the Guardian and Yahoo Finance, refreshed daily.",
        "home.insights": "Latest insights",
        "home.perf_kicker": "Proven by backtest",
        "home.perf_heading": "Model performance",
        "home.perf_sub": "Walk-forward, out-of-sample. Pick an index to inspect.",
        "home.feat_kicker": "Built honestly",
        "chart.equity": "Strategy vs buy & hold",
        "chart.equity_sub": "Cumulative return — model long/flat timing",
        "chart.accuracy": "Accuracy vs always-up baseline",
        "chart.price": "Price & next-day range",
        "chart.calibration": "Probability calibration",
        "chart.calibration_sub": "Predicted vs actual up-rate (dashed = perfect)",
        "chart.model": "Model",
        "chart.perfect": "Perfect",
        "news.heading": "Market news",
        "news.sub": "UK & US markets — updated daily",
        # --- splash + app shell ---
        "splash.tag1": "Invest now, enjoy future.",
        "splash.tag2": "Your best financial web.",
        "splash.enter": "Enter",
        "tab.overview": "Overview",
        "tab.performance": "Performance",
        "tab.model": "Model",
        "tab.news": "News",
        # --- overview + predict tool ---
        "ov.heading": "Today's market outlook",
        "predict.kicker": "On-demand inference",
        "predict.heading": "Predict any stock",
        "predict.sub": "Enter a ticker, pick a market, and run the model live.",
        "predict.ticker_ph": "e.g. AAPL, NVDA, BP",
        "predict.market": "Market",
        "predict.us": "US",
        "predict.uk": "UK",
        "predict.run": "Run forecast",
        "predict.running": "Running model",
        "predict.step1": "Fetching prices",
        "predict.step2": "Engineering features",
        "predict.step3": "Training model",
        "predict.step4": "Forecasting",
        "predict.holdout": "hold-out accuracy",
        "predict.history": "trading days",
        "predict.result": "Forecast",
        "predict.again": "Predict another",
        # --- model page ---
        "model.kicker": "How it works",
        "model.heading": "Inside the model",
        "model.intro": "Each forecast comes from a gradient-boosted tree trained on engineered price features, validated by a walk-forward backtest against naive baselines. Same code runs offline for the indices and live for any ticker you enter.",
        "model.pipeline": "The pipeline",
        "pipe.data": "Market data",
        "pipe.data_s": "Yahoo Finance OHLCV",
        "pipe.features": "Features",
        "pipe.features_s": "returns · momentum · RSI · volatility",
        "pipe.model": "Model",
        "pipe.model_s": "gradient-boosted trees + quantiles",
        "pipe.backtest": "Backtest",
        "pipe.backtest_s": "walk-forward vs baselines",
        "pipe.serve": "Serve",
        "pipe.serve_s": "JSON artifacts → web app",
        "model.stack": "Stack",
        "model.honesty": "Built honestly",
        "model.honesty_b": "We publish the full model comparison, baselines, and calibration — not a cherry-picked accuracy. Daily index direction is close to unpredictable, and the numbers say so.",
        "chart.details": "Details",
        "chart.expand": "Expand",
        "chart.equity_x": "Cumulative return if you went long only when the model predicted up (else flat), versus simply buying and holding. It shows whether the probability signal adds risk-adjusted value — not just raw accuracy.",
        "chart.accuracy_x": "Out-of-sample directional accuracy of each model and the soft-vote ensemble, against the naive “always up” baseline. Gaps within ~1 point are noise: daily index direction is close to unpredictable.",
        "chart.price_x": "The last ~6 months of closes with the model's predicted 80% range for the next session shaded. The band is a quantile forecast, not a guarantee.",
        "chart.calibration_x": "Predicted probability vs the actual up-rate, in equal-count bins. Points near the dashed diagonal mean the probabilities are well-calibrated — a 55% call really happens ~55% of the time.",
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
        "home.fc_kicker": "AI 模型",
        "home.fc_heading": "明日市場展望",
        "home.fc_sub": "主要指數的下一交易日方向與 80% 區間——來自經過誠實 walk-forward 回測的模型，而非空話。",
        "home.fc_view": "查看詳情",
        "home.fc_acc": "回測準確",
        "home.feat_heading": "這個專案實際在做什麼",
        "home.feat1_t": "機率型預測",
        "home.feat1_b": "主要指數的每日漲跌機率與價格區間——經過校準，不靠臆測。",
        "home.feat2_t": "誠實回測",
        "home.feat2_b": "每個數字都來自對照基準線的 walk-forward 測試，不挑好看的呈現。",
        "home.feat3_t": "英美市場新聞",
        "home.feat3_b": "來自 Guardian 與 Yahoo Finance 的即時市場頭條，每日自動更新。",
        "home.insights": "最新觀點",
        "home.perf_kicker": "回測實證",
        "home.perf_heading": "模型績效",
        "home.perf_sub": "Walk-forward 樣本外結果，選一個指數檢視。",
        "home.feat_kicker": "誠實打造",
        "chart.equity": "策略 vs 買進持有",
        "chart.equity_sub": "累積報酬——模型做多/空手擇時",
        "chart.accuracy": "準確率 vs 永遠看漲基準",
        "chart.price": "價格與明日區間",
        "chart.calibration": "機率校準",
        "chart.calibration_sub": "預測 vs 實際上漲率（虛線＝完美）",
        "chart.model": "模型",
        "chart.perfect": "完美校準",
        "news.heading": "市場新聞",
        "news.sub": "英美股市——每日更新",
        "splash.tag1": "Invest now, enjoy future.",
        "splash.tag2": "Your best financial web.",
        "splash.enter": "進入",
        "tab.overview": "總覽",
        "tab.performance": "模型績效",
        "tab.model": "模型",
        "tab.news": "新聞",
        "ov.heading": "今日市場展望",
        "predict.kicker": "即時運算",
        "predict.heading": "預測任意股票",
        "predict.sub": "輸入代碼、選擇市場，即時跑模型。",
        "predict.ticker_ph": "例如 AAPL、NVDA、BP",
        "predict.market": "市場",
        "predict.us": "美股",
        "predict.uk": "英股",
        "predict.run": "開始預測",
        "predict.running": "模型運算中",
        "predict.step1": "抓取價格資料",
        "predict.step2": "建立特徵",
        "predict.step3": "訓練模型",
        "predict.step4": "產生預測",
        "predict.holdout": "驗證準確率",
        "predict.history": "個交易日",
        "predict.result": "預測結果",
        "predict.again": "再預測一檔",
        "model.kicker": "運作原理",
        "model.heading": "模型內部",
        "model.intro": "每一筆預測都來自一個梯度提升樹模型，以工程化的價格特徵訓練，並經 walk-forward 回測對照基準線驗證。同一套程式碼離線跑指數、也即時跑你輸入的任意代碼。",
        "model.pipeline": "資料管線",
        "pipe.data": "市場資料",
        "pipe.data_s": "Yahoo Finance OHLCV",
        "pipe.features": "特徵工程",
        "pipe.features_s": "報酬 · 動能 · RSI · 波動",
        "pipe.model": "模型",
        "pipe.model_s": "梯度提升樹 + 分位數",
        "pipe.backtest": "回測",
        "pipe.backtest_s": "walk-forward 對照基準",
        "pipe.serve": "上線",
        "pipe.serve_s": "JSON 產物 → 網站",
        "model.stack": "技術棧",
        "model.honesty": "誠實打造",
        "model.honesty_b": "我們公開完整的模型比較、基準線與校準——而非挑好看的準確率。每日指數方向接近不可預測，數字也誠實這麼說。",
        "chart.details": "說明",
        "chart.expand": "展開",
        "chart.equity_x": "只有在模型預測上漲時才做多（否則空手）的累積報酬，對比單純買進持有。用來看「機率訊號是否帶來風險調整後的價值」，而不只是看準確率。",
        "chart.accuracy_x": "各模型與軟投票集合的樣本外方向準確率，對照「永遠看漲」基準。差距在約 1 個百分點內都算雜訊——每日指數方向接近不可預測。",
        "chart.price_x": "近約半年的收盤價，並把模型對下一交易日的 80% 預測區間以陰影標出。此區間是分位數預測，非保證。",
        "chart.calibration_x": "預測機率對實際上漲率（等量分箱）。越靠近虛線對角線，代表機率校準越好——說 55% 上漲，實際就約 55% 會發生。",
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
