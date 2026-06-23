import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

# Set page config for premium B2B style
st.set_page_config(
    page_title="JUDAAN B2B Sales Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom premium styling
st.markdown("""
<style>
    .reportview-container {
        background: #f9fafb;
    }
    h1 {
        color: #1e1b4b;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        text-align: center;
        margin-bottom: 25px;
    }
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    .highlight-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
        margin-bottom: 20px;
        border-left: 5px solid #4f46e5;
    }
</style>
""", unsafe_allow_html=True)

st.write("## ✨ K-Derma Brand 'JUDAAN' 글로벌 진출을 위한 B2B 세일즈 대시보드")
st.markdown("##### 본 대시보드는 선행 브랜드(일리윤)의 한·일 소비자 리뷰 데이터를 형태소 분석하여 양국의 시장 니즈 유사성과 핵심 소구점을 증명합니다.")

# Data mapping configurations
FILES = {
    "수딩젤": {
        "kr": "gel_reviews_clean.csv",
        "kr_col": "베스트 리뷰",
        "jp": "qoo10_reviews_1.csv",
        "jp_col": "review",
        "match_rate": 80.0,
        "themes": [
            "1️⃣ **여름철 진정 (夏用・鎮静 / 여름용・진정)**: 강한 햇빛과 자외선에 붉게 노출된 아기 피부를 빠르게 진정시키는 쿨링 효과 소구.",
            "2️⃣ **산뜻한 사용감 (さっぱり・ベタつき無 / 산뜻함・끈적임 없음)**: 번들거림이나 끈적임이 없어 더운 날씨에도 쾌적하게 펴 발리는 산뜻함.",
            "3️⃣ **패밀리 케어 범용성 (가족공용 / 家族で使える / 가족이 함께 쓸 수 있는)**: 순한 처방으로 온 가족이 전신에 부담 없이 바르는 데일리 젤."
        ],
        "vocs": [
            "「子供用に買いました。カサカサが治るといいな。」\n(아이용으로 샀습니다. 거친 피부가 나아지면 좋겠네요.)",
            "「家族用に購入です。全身に使えて乾燥もしないみたいです。」\n(가족용으로 구매했습니다. 전신에 쓸 수 있고 건조하지도 않은 것 같습니다.)"
        ],
        "b2b_copy": "🎯 **Jovial SE & F-Care Cosme 파트너사 전용 제안**: Loft, Plaza, @cosme의 트렌디하고 민감한 뷰티 소비자층을 공략할 수 있는, 자극 없이 가볍고 산뜻한 아기용 수분 쿨링 솔루션으로의 입점을 제안합니다."
    },
    "워시": {
        "kr": "wash_reviews_clean.csv",
        "kr_col": "베스트 리뷰",
        "jp": "qoo10_reviews_2.csv",
        "jp_col": "review",
        "match_rate": 80.0,
        "themes": [
            "1️⃣ **올인원 샤워 편의성 (全身使える・時短 / 전신 사용・시간 단축)**: 머리부터 발끝까지 샴푸와 바디워시를 한 번에 끝내 바쁜 육아 시간을 단축.",
            "2️⃣ **눈시림 없는 마일드 저자극 (저자극 / 低刺激 / 저자극)**: 샤워 중 거품이 눈에 닿아도 따갑지 않은 순수하고 매끄러운 포뮬러.",
            "3️⃣ **건조 가려움 케어 (건조하지 않음 / 乾燥しない / 건조하지 않음)**: 세정 후 가려움이나 속당김 없이 수분 밀착력을 지켜주는 고보습 마감."
        ],
        "vocs": [
            "「子供と一緒に使ってます。肌がもっちもちになります。」\n(아이와 함께 쓰고 있어요. 피부가 쫀득쫀득(모찌모찌)해져요.)",
            "「子供も肌荒れすることなく使えてお気に入りです！」\n(아이도 피부 트러블 없이 쓸 수 있어서 정말 마음에 들어요!)"
        ],
        "b2b_copy": "🎯 **Jovial SE & F-Care Cosme 파트너사 전용 제안**: Loft, Plaza, @cosme의 오프라인 안심 매대를 빛낼 유아 세정 솔루션으로, 머리부터 발끝까지 단 한 번에 자극 없이 끝낼 수 있는 초순한 올인원 탑투토 워시를 입점 제안합니다."
    },
    "선크림": {
        "kr": "sunscreen_reviews_clean.csv",
        "kr_col": "베스트 리뷰",
        "jp": "qoo10_reviews_3.csv",
        "jp_col": "review",
        "match_rate": 60.0,
        "themes": [
            "1️⃣ **이지워시 편리성 (소프오프 / 石鹸で落ちる / 비누로 지워지는)**: 전용 1차 리무버 없이 일반 폼/비누 샤워만으로 말끔히 씻기는 편안함.",
            "2️⃣ **백탁 및 뻑뻑함 제로 (白浮きしない / 백탁 현상 없는)**: 허옇게 뜨거나 모공을 막아 답답한 현상 없이 투명하고 가볍게 흡수되는 밀착력.",
            "3️⃣ **순한 패밀리 자외선 차단 (親子で使える / 부모와 아이가 함께 쓰는)**: 유아 피부의 물리 차단 보호막과 어른들의 마일드 선케어 통합 소구."
        ],
        "vocs": [
            "「赤ちゃんにも使えるということから購入してみました！」\n(아기에게도 사용할 수 있다고 해서 구매해 보았습니다!)",
            "「子供と一緒に使えるのでたくさん買いました。」\n(아이와 함께 쓸 수 있어서 많이 샀습니다.)"
        ],
        "b2b_copy": "🎯 **Jovial SE & F-Care Cosme 파트너사 전용 제안**: Loft, Plaza, @cosme의 자외선 차단제 진열 영역에 적합한 패밀리 아이템으로, 성인용 전용 세안제가 필요 없는 '이지워시' 비누 세정 유아용 선크림을 강력 추천합니다."
    },
    "로션": {
        "kr": "reviews_clean.csv",
        "kr_col": "review_text",
        "jp": "qoo10_reviews_4.csv",
        "jp_col": "review",
        "match_rate": 100.0,
        "themes": [
            "1️⃣ **24시간 장벽 보습력 (保湿力・乾燥 / 보습력・건조 고민 해결)**: 극건성 피부의 각질을 유연하게 잡고 아침부터 밤까지 지속되는 극강의 보습력.",
            "2️⃣ **사용성 강화 펌프 패키지 (使いやすい・ポンプ / 사용하기 쉬운 펌프)**: 뚜껑을 돌려 딸 필요 없는 원터치 설계로 목욕 후 한 손 스피드 육아 최적화.",
            "3️⃣ **인공 향료 무첨가 (無香料 / 무향료)**: 알레르기나 트러블을 유발하는 화장품 인공 향에 대한 거부감을 완벽히 차단한 안심 처방."
        ],
        "vocs": [
            "「家族で使うのでポンプタイプがいいなと思い買いました。肌にも優しいタイプなので使いやすい。」\n(가족이 함께 쓸 거라 펌프 타입이 좋겠다고 생각해서 샀어요. 피부에도 순한 타입이라 사용하기 편해요.)",
            "「毎日子供と使ってます。珊瑚にもいいやつなので海に行く時도安心です。」\n(매일 아이와 함께 쓰고 있어요. 산호에도 무해한 차단제(로션)라 해변에 갈 때도 안심이에요.)"
        ],
        "b2b_copy": "🎯 **Jovial SE & F-Care Cosme 파트너사 전용 제안**: Loft, Plaza, @cosme의 더마 코스메틱 대표 품목으로 자리매김할 수 있는, 신생아부터 성인까지 전 연령대 장벽 강화에 집중하는 무향료 고보습 크림 로션을 입점 제안합니다."
    }
}

# Stopwords sets
STOPWORDS_KR = {'너무', '좋아요', '좋습니다', '진짜', '구매', '사용', '피부', '제품', '일리윤', '아토', '세라마이드', '로션', '크림', '수딩젤', '워시', '선크림', '바디', '주문', '배송', '정말', '것', '수', '등', '때', '안', '추천', '만족', '발림', '쓰고', '있어요', '아직', '하고', '해서', '요거', '일리', '윤', '좋라요', '좋네요'}
STOPWORDS_JP = {'良い', 'しっとり', 'いい', '購入', '使用', 'イリユン', 'アト', 'セラミ드', 'ローション', 'クリーム', 'ボディ', 'サンプル', 'おまけ', 'メガ割', '満足', 'とても', 'Qoo10', '到着', '早い', '配送', 'リピ', 'ストック', 'リピート', '愛用', 'お気に入り', '今回', 'です', 'ます', 'ので', 'から', 'オマケ', 'とても'}

TRANSLATIONS_JA = {
    '保湿': '保湿 (보습)',
    'しっとり': 'しっとり (촉촉함)',
    '乾燥': '乾燥 (건조)',
    'うるおい': 'うるおい (윤기/수분)',
    '潤い': '潤い (윤기/수분)',
    'さっぱり': 'さっぱり (산뜻함)',
    'サラサラ': 'サラサラ (보송함)',
    'ベタつき': 'ベタつき (끈적임)',
    'ベタベタ': 'ベタベタ (끈적임)',
    'ベタつかない': 'ベタつかない (끈적임 없음)',
    '子供': '子供 (아이)',
    '子ども': '子ども (아이)',
    '赤ちゃん': '赤ちゃん (아기)',
    '家族': '家族 (가족)',
    'ベビー': 'ベビー (베이비)',
    '娘': '娘 (딸)',
    '息子': '息子 (아들)',
    'ポンプ': 'ポンプ (펌프)',
    '使いやすい': '使いやすい (사용하기 편리함)',
    '楽': '楽 (편함)',
    '大容量': '大容量 (대용량)',
    'サイズ': 'サイズ (사이즈)',
    '容量': '容量 (용량)',
    'コスパ': 'コスパ (가성비)',
    '安い': '安い (저렴함)',
    'お得': 'お得 (이득/할인)',
    '無香料': '無香料 (무향료)',
    '香料': '香料 (향료)',
    '匂い': '匂い (냄새/향)',
    '香り': '香り (향)',
    'リピ': 'リピ (재구매)',
    'リピート': 'リピート (재구매)',
    '愛用': '愛用 (애용)',
    'ストック': 'ストック (스톡)',
    '低刺激': '低刺激 (저자극)',
    '優しい': '優しい (순함)',
    '安心': '安心 (안심)',
    '刺激': '刺激 (자극)',
    '荒れ': '荒れ (트러블)',
    '肌荒れ': '肌荒れ (피부 트러블)',
    '石鹸': '石鹸 (비누)',
    '落ちる': '落ちる (지워짐)',
    '目に染みない': '目に染みない (눈시림 없음)',
    '痛くない': '痛くない (안 아픔)',
    '白浮き': '白浮き (백탁)',
    '全身': '全身 (전신)',
    '時短': '時短 (시간 단축)',
    '泡': '泡 (거품)',
    '泡立ち': '泡立ち (거품 잘 남)',
    'スッキリ': 'スッキリ (개운함)',
    'アトピー': 'アトピー (아토피)',
    '敏感肌': '敏感肌 (민감성 피부)',
    '夏': '夏 (여름)',
    '冬': '冬 (겨울)',
    '季節': '季節 (계절)',
    'ひんやり': 'ひんやり (시원함/쿨링)',
    'クール': 'クール (쿨링)',
    'おまけ': 'おまけ (사은품)',
    'サンプル': 'サンプル (샘플)',
    'ギフト': 'ギフト (선물)',
    'いい': 'いい (좋음)',
    '良い': '良い (좋음)',
    '伸び': '伸び (발림성)',
    'テクスチャー': 'テクスチャー (제형)',
    'スルスル': 'スルスル (부드럽게 발림)',
    '毎日': '毎日 (매일)',
    '普段使い': '普段使い (데일리 사용)',
    '鎮静': '鎮静 (진정)',
    'バリア': 'バリア (장벽)',
    'ソープ': 'ソープ (비누/세정제)',
    'ウォッシュ': 'ウォッシュ (워시)',
    '親子': '親子 (부모와 아이)',
    '아토': '아토 (아토)',
    '肌': '肌 (피부)',
    'ない': 'ない (없음/안 됨)',
    'ボディー': 'ボディー (바디)',
    'ボディウォッシュ': 'ボディウォッシュ (바디워시)',
    'こと': 'こと (것/일)',
    '期待': '期待 (기대)',
    '楽しみ': '楽しみ (기대됨/즐거움)',
    '感じ': '感じ (느낌/감각)',
    'やすい': 'やすい (쉬움/편함)',
    'すごい': 'すごい (대단함/매우)',
    '商品': '商品 (상품/제품)',
    'メガ': 'メガ (메가와리/할인)',
    '敏感': '敏感 (민감)',
    '洗い': '洗い (씻음/세정)',
    '上がり': '上がり (마무리/세안 후)',
    'よい': 'よい (좋음)',
    '少ない': '少ない (적음)',
    '一緒': '一緒 (함께)',
    'よう': 'よう (듯함/방식)',
    'まとめ買い': 'まとめ買い (묶음구매/대량구매)',
    'こちら': 'こちら (이 제품/이쪽)',
    '大好き': '大好き (매우 좋아함)',
    'タイプ': 'タイプ (타입/유형)',
    'そう': 'そう (그렇게/듯함)',
    '効果': '効果 (효과)',
    'みたい': 'みたい (~인 듯한)',
    '欲しい': '欲しい (원함)',
    'セラミド': 'セラミド (세라마이드)',
    '痒い': '痒い (가려움)',
    'ところ': 'ところ (점/부분)',
    '嬉しい': '嬉しい (기쁨/좋음)',
    'これ': 'これ (이것)',
    'たくさん': 'たくさん (많이/가득)',
    'ベタ': 'ベタ (끈적임)',
    'つき': 'つき (묻음/느낌)',
    'おすすめ': 'おすすめ (추천)',
    'ため': 'ため (때문/위함)',
    '好き': '好き (좋아함)',
    'もの': 'もの (것/물건)',
    'ジェル': 'ジェル (젤)',
    '暑い': '暑い (더움)',
    '日焼け': '日焼け (자외선 차단/햇볕에 탐)',
    'ケア': 'ケア (케어/관리)',
    '軽い': '軽い (가벼움)',
    '水分': '水分 (수분)',
    '스ージングジェル': 'スージングジェル (수딩젤)',
    'スージングジェル': '스ージ증젤 (수딩젤)',
    '塗り': '塗り (바름/도포)',
    '心地': '心地 (사용감/기분)',
    '時間': '時間 (시간)',
    'ビックリ': 'ビックリ (깜짝 놀람)',
    '期限': '期限 (사용기한)',
    '長い': '長い (김/오래감)',
    '一つ': '一つ (하나)',
    '強い': '強い (강함)',
    '문제': '問題 (문제)',
    '問題': '問題 (문제)',
    'スースー': 'スースー (화함/시원함)',
    '止め': '止め (방지/차단)',
    '使い': '使い (사용)',
    'ありがたい': 'ありがたい (감사함/다행임)',
    'プッシュ': 'プッシュ (펌프 누름)',
    '紫外線': '紫外線 (자외선)',
    '高い': '高い (높음/비쌈)',
    'パッケージ': 'パッケージ (패키지/포장)',
    '洗顔': '洗顔 (세안/클렌징)',
    '多い': '多い (많음)',
    'キシ': 'キシ (뻑뻑함/건조함)'
}

# Lazy load tokenizers to save resources
@st.cache_resource
def get_kiwi():
    from kiwipiepy import Kiwi
    return Kiwi()

@st.cache_resource
def get_janome():
    from janome.tokenizer import Tokenizer
    return Tokenizer()

# Token extraction helpers
@st.cache_data
def extract_keywords_ko(file_path, text_col):
    df = pd.read_csv(file_path)
    texts = df[text_col].dropna().tolist()
    kiwi = get_kiwi()
    
    words = []
    for text in texts:
        for token in kiwi.tokenize(str(text)):
            if token.tag.startswith('NN') or token.tag == 'VA':
                word = token.form
                if len(word) > 1 and word not in STOPWORDS_KR:
                    # Map synonyms
                    if '보습' in word or '촉촉' in word: word = '보습/촉촉'
                    if '자극' in word: word = '저자극/순함'
                    if '끈적' in word: word = '끈적임없음'
                    if '눈' in word or '시림' in word: word = '눈시림없음'
                    if '아기' in word or '아이' in word: word = '아기/아이용'
                    if '편하' in word or '편리' in word: word = '사용편리(펌프)'
                    words.append(word)
                    
    return Counter(words).most_common(15)

@st.cache_data
def extract_keywords_ja(file_path, text_col):
    df = pd.read_csv(file_path)
    texts = df[text_col].dropna().tolist()
    texts = [t for t in texts if t not in ["フォトレビューだけ", "動画&フォトレビューのみ"]]
    
    janome_tokenizer = get_janome()
    words = []
    for text in texts:
        for token in janome_tokenizer.tokenize(str(text)):
            pos = token.part_of_speech.split(',')[0]
            if pos in ['名詞', '形容詞']:
                word = token.base_form if token.base_form != '*' else token.surface
                if len(word) > 1 and word not in STOPWORDS_JP:
                    # Map synonyms & append Korean meanings to Japanese terms
                    if '保湿' in word or 'しっとり' in word or '潤' in word:
                        word = '保湿・うるおい (보습・촉촉)'
                    elif '刺激' in word or '優しい' in word:
                        word = '低刺激・肌에優しい (저자극・순함)'
                    elif 'ベタ' in word or 'ベた' in word:
                        word = 'ベタつかない (끈적임 없음)'
                    elif '子供' in word or '赤ちゃん' in word or 'ベビー' in word:
                        word = '子供・赤ちゃん用 (어린이・아기용)'
                    elif 'ポンプ' in word or '使いやすい' in word or '楽' in word:
                        word = '使いやすい・ポンプ (사용편리・펌프)'
                    elif '石鹸' in word or 'ソープ' in word or '落ちる' in word:
                        word = '石鹸で落とせる (비누 세정가능)'
                    elif '乾燥' in word:
                        word = '乾燥悩み解決 (건조고민 해결)'
                    elif '無香料' in word:
                        word = '無香料 (무향료)'
                    elif 'おまけ' in word or 'サンプル' in word:
                        word = 'おまけ (사은품/샘플)'
                    elif '伸び' in word:
                        word = '伸びが良い (발림성 좋음)'
                    elif '泡' in word:
                        word = '泡立ちが良い (풍부한 거품)'
                    elif '目に染みない' in word or '痛くない' in word:
                        word = '目に染みない (눈시림 없음)'
                    elif '白浮き' in word:
                        word = '白浮きしない (백탁 없음)'
                    elif 'アトピー' in word:
                        word = 'アトピー肌 (아토피 피부)'
                    else:
                        word = TRANSLATIONS_JA.get(word, f"{word} ({word})")
                    words.append(word)
                    
    return Counter(words).most_common(15)

# Create 4 tabs
tabs = st.tabs(["수딩젤", "워시", "선크림", "로션"])

for tab, (prod_name, cfg) in zip(tabs, FILES.items()):
    with tab:
        st.write(f"### 📦 {prod_name} (JUDAAN {prod_name} Lineup)")
        
        # Section A: Similarity & Highlights
        st.markdown("#### **[섹션 A] 한-일 키워드 유사도(%) 및 텍스트 마이닝 핵심 발견 (Top 3 주제)**")
        col_metric, col_hl = st.columns([1, 3])
        with col_metric:
            st.metric(label="의미 기반 니즈 일치율", value=f"{cfg['match_rate']}%")
        with col_hl:
            for theme in cfg["themes"]:
                st.info(theme)
                
        st.write("---")
        
        # Section B: Chart & WordCloud layout
        st.markdown("#### **[섹션 B] 양국 소비자 언급 빈도 Top 15 키워드 비교 (Bar Chart & Wordcloud)**")
        col_wc_kr, col_wc_jp = st.columns(2)
        
        # Retrieve keyword counts
        kr_kw = dict(extract_keywords_ko(cfg["kr"], cfg["kr_col"]))
        jp_kw = dict(extract_keywords_ja(cfg["jp"], cfg["jp_col"]))
        
        with col_wc_kr:
            st.markdown("<h5 style='text-align: center; color: #4f46e5;'>한국 (Naver Shopping VOC)</h5>", unsafe_allow_html=True)
            df_kr = pd.DataFrame(list(kr_kw.items())[:15], columns=["Keyword", "Frequency"]).sort_values(by="Frequency", ascending=True)
            fig_kr = px.bar(df_kr, x="Frequency", y="Keyword", orientation="h",
                            color_discrete_sequence=['#4f46e5'])
            fig_kr.update_layout(margin=dict(l=100, r=20, t=10, b=10), height=400)
            st.plotly_chart(fig_kr, use_container_width=True)
            
            st.write("")
            if kr_kw:
                wc_kr = WordCloud(
                    font_path="C:\\Windows\\Fonts\\malgun.ttf",
                    background_color="white",
                    width=600,
                    height=350,
                    colormap="viridis"
                ).generate_from_frequencies(kr_kw)
                st.image(wc_kr.to_array(), use_container_width=True)
                
        with col_wc_jp:
            st.markdown("<h5 style='text-align: center; color: #ec4899;'>일본 (Qoo10 VOC)</h5>", unsafe_allow_html=True)
            df_jp = pd.DataFrame(list(jp_kw.items())[:15], columns=["Keyword", "Frequency"]).sort_values(by="Frequency", ascending=True)
            fig_jp = px.bar(df_jp, x="Frequency", y="Keyword", orientation="h",
                            color_discrete_sequence=['#ec4899'])
            fig_jp.update_layout(margin=dict(l=180, r=20, t=10, b=10), height=400)
            st.plotly_chart(fig_jp, use_container_width=True)
            
            st.write("")
            if jp_kw:
                wc_jp = WordCloud(
                    font_path="C:\\Windows\\Fonts\\malgun.ttf",
                    background_color="white",
                    width=600,
                    height=350,
                    colormap="plasma"
                ).generate_from_frequencies(jp_kw)
                st.image(wc_jp.to_array(), use_container_width=True)
                
        st.write("---")
        
        # Section C: VOC & B2B Positioning Card
        st.markdown("#### **[섹션 C] 일본 시장 '찐 VOC' 및 B2B 채널 맞춤형 포지셔닝 제안**")
        
        st.write("**일본 현지 소비자 리얼 VOC (Original Reviews & Translations):**")
        for voc in cfg["vocs"]:
            st.markdown(f"> {voc}")
            
        st.markdown("##### 💡 **Jovial SE & F-Care Cosme 파트너십용 영업 카피 (Loft, Plaza, @cosme 전용):**")
        st.success(cfg["b2b_copy"])
