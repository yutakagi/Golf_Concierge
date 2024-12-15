import streamlit as st
from datetime import date, timedelta
import requests
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv # type: ignore
import os

# ファビコン画像のパスを指定
favicon_path = "Golf_Concierge_Favicon_32x32.png"

# ページの設定（タイトルとファビコンを指定）
st.set_page_config(
    page_title="Golf Concierge",  # ページのタイトル
    page_icon=favicon_path       # ファビコン画像のパス
)

load_dotenv()  # .envファイルを読み込む
# 定数
REQUEST_URL_TRAVEL = os.getenv("REQUEST_URL_TRAVEL")
REQUEST_URL_GORA = os.getenv("REQUEST_URL_GORA")
APP_ID = os.getenv("APP_ID")

# OpenAIクライアントのインスタンスを作成
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# サイドバーにカスタムスタイルを適用
st.sidebar.markdown(
    """
    <style>
    .css-1d391kg {
        background-color: #28a745;  /* 緑色の背景色 */
        color: black;  /* 文字色を白に設定 */
    }
    .sidebar-title {
        font-size: 30px;  /* タイトルサイズ */
        font-weight: bold;
        color: #f39c18;  /* オレンジ色 */
    }
    .sidebar-description {
        font-size: 16px;  /* 説明文のフォントサイズ */
        color: black;  /* 説明文の文字色 */
    }
    </style>
    """, unsafe_allow_html=True
)

# サイドバーにタイトルと説明文を表示
# 画像のパスまたはURLを指定
image_path = "ロゴ.svg"  # ここに画像のパスまたはURLを指定

# サイドバーに画像を表示
st.sidebar.image(image_path, caption="最高のゴルフ旅をご提案します", use_column_width=True)

# メインコンテンツにも装飾を加える
# 下記コードを<div style="text-align: center;">の後ろに追加すると画像が入る
#<img src="Golf _Concierge" alt="Golf Image" style="width: 80%; max-width: 600px; border-radius: 10px;"/>
    # </div>
st.markdown(
    """
    <h1 style="color: #28a745; text-align: center;">Welcome to Golf Concierge!</h1>
    <p style="font-size: 18px; text-align: center;">We offer the best golf plans tailored for you.</p>
    <div style="text-align: center;">
    """, 
    unsafe_allow_html=True
)

# ボタンのカスタマイズ
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #28a745;  /* 緑色のボタン */
        color: white;  /* ボタン文字色 */
        font-size: 16px;  /* ボタンの文字サイズ */
        border-radius: 8px;  /* ボタンの角を丸くする */
    }
    </style>
    """, unsafe_allow_html=True
)



# 今日と明日の日付を取得　
today = date.today()
tomorrow = today + timedelta(days=1)

# 47都道府県リストと対応するAPIコードを用意
prefecture_mapping = {
    "北海道": "hokkaido", "青森県": "aomori", "岩手県": "iwate", "宮城県": "miyagi", "秋田県": "akita", 
    "山形県": "yamagata", "福島県": "hukushima", "茨城県": "ibaragi", "栃木県": "tochigi", "群馬県": "gunma", 
    "埼玉県": "saitama", "千葉県": "tiba", "東京都": "tokyo", "神奈川県": "kanagawa", "新潟県": "niigata", 
    "富山県": "toyama", "石川県": "ishikawa", "福井県": "hukui", "山梨県": "yamanasi", "長野県": "nagano", 
    "岐阜県": "gihu", "静岡県": "shizuoka", "愛知県": "aichi", "三重県": "mie", "滋賀県": "shiga", 
    "京都府": "kyoto", "大阪府": "osaka", "兵庫県": "hyogo", "奈良県": "nara", "和歌山県": "wakayama", 
    "鳥取県": "tottori", "島根県": "simane", "岡山県": "okayama", "広島県": "hiroshima", "山口県": "yamaguchi", 
    "徳島県": "tokushima", "香川県": "kagawa", "愛媛県": "ehime", "高知県": "kouchi", "福岡県": "hukuoka", 
    "佐賀県": "saga", "長崎県": "nagasaki", "熊本県": "kumamoto", "大分県": "ooita", "宮崎県": "miyazaki", 
    "鹿児島県": "kagoshima", "沖縄県": "okinawa"
}

# small_areaの選択肢 (都道府県ごとの対応リスト)
small_area_mapping = {
    "北海道"	: {
    	"札幌"	: "sapporo",
    	"定山渓"	: "jozankei",
    	"稚内・留萌・利尻・礼文"	: "wakkanai",
    	"網走・紋別・北見・知床"	: "abashiri",
    	"釧路・阿寒・川湯・根室"	: "kushiro",
    	"帯広・十勝"	: "obihiro",
    	"日高・えりも"	: "hidaka",
    	"富良野・美瑛・トマム"	: "furano",
    	"旭川・層雲峡・旭岳"	: "asahikawa",
    	"千歳・支笏・苫小牧・滝川・夕張・空知"	: "chitose",
    	"小樽・キロロ・積丹・余市"	: "otaru",
    	"ルスツ・ニセコ・倶知安"	: "niseko",
    	"函館・湯の川・大沼・奥尻"	: "hakodate",
    	"洞爺・室蘭・登別"	: "noboribetsu",
    },
    "青森県"	: {
        "青森・浅虫温泉"	: "aomori",
        "津軽半島・五所川原"	: "tsugaru",
       	"白神山地・西津軽"	: "ntsugaru",
    	"弘前・黒石"	: "hirosaki",
    	"八甲田・十和田湖・奥入瀬"	: "towadako",
    	"八戸・三沢・七戸十和田"	: "hachinohe",
    	"下北・大間・むつ"	: "shimokita",
    },
    "岩手県"	: {
    	"盛岡"	: "morioka",
    	"雫石"	: "shizukuishi",
    	"安比高原・八幡平・二戸"	: "appi",
        "宮古・久慈・岩泉"	: "kuji",
        "釜石・大船渡・陸前高田"	: "ofunato",
        "北上・花巻・遠野"	: "kitakami",
        "奥州・平泉・一関"	: "ichinoseki",
    },
    "宮城県"	: {
        "仙台・多賀城・名取"	: "sendai",
        "秋保・作並"	: "akiu",
        "鳴子・古川・くりこま高原"	: "naruko",
        "松島・塩釜・石巻・南三陸・気仙沼"	: "matsushima",
        "白石・宮城蔵王"	: "shiroishi",
    },
    "秋田県"	: {
        "秋田"	: "akita",
        "能代・男鹿・白神"	: "noshiro",
        "大館・鹿角・十和田大湯・八幡平"	: "odate",
        "角館・大曲・田沢湖"	: "tazawa",
        "湯沢・横手"	: "yuzawa",
        "由利本荘・鳥海山"	: "honjo",
    },
    "山形県"	: {
        "山形・蔵王・天童・上山"	: "yamagata",
        "米沢・赤湯・高畠・長井"	: "yonezawa",
        "寒河江・月山"	: "sagae",
        "尾花沢・新庄・村山"	: "mogami",
        "酒田・鶴岡・湯野浜・温海"	: "shonai",
    },
    "福島県"	: {
        "福島・二本松"	: "fukushima",
        "会津若松・喜多方"	: "aizu",
        "猪苗代・表磐梯"	: "bandai",
        "磐梯高原・裏磐梯"	: "urabandai",
        "郡山・磐梯熱海"	: "koriyama",
        "南会津・下郷・只見・檜枝岐"	: "minami",
        "白河・須賀川"	: "nakadori",
        "いわき・南相馬・相馬"	: "hamadori",
    },
    "茨城県"	: {
        "水戸・笠間"	: "mito",
        "大洗・ひたちなか"	: "oarai",
        "日立・北茨城・奥久慈"	: "hitachi",
    	"つくば・土浦・取手"	: "tsukuba",
        "古河・結城・筑西・常総"	: "yuki",
        "鹿嶋・神栖・潮来・北浦"	: "kashima",
    },
    "栃木県"	: {
        "宇都宮・さくら"	: "utsunomiya",
        "日光・中禅寺湖・奥日光・今市"	: "nikko",
        "鬼怒川・川治・湯西川・川俣"	: "kinugawa",
        "那須・板室・黒磯"	: "nasu",
        "塩原・矢板・大田原・西那須野"	: "shiobara",
        "真岡・益子・茂木"	: "mashiko",
        "小山・足利・佐野・栃木"	: "koyama",
    },
    "群馬県"	: {
        "前橋・赤城"	: "maebashi",
        "伊香保温泉・渋川"	: "ikaho",
        "万座･嬬恋･北軽井沢"	: "manza",
        "草津温泉・白根"	: "kusatsu",
    	"四万温泉"	: "shimaonsen",
        "水上・猿ヶ京・沼田"	: "numata",
        "尾瀬・丸沼"	: "oze",
        "伊勢崎・太田・館林・桐生"	: "kiryu",
        "高崎"	: "takasaki",
        "富岡・藤岡・安中・磯部温泉"	: "fujioka",
    },
    "埼玉県"	: {
        "大宮・浦和・川口・上尾"	: "saitama",
        "草加・越谷・春日部・羽生"	: "kasukabe",
        "熊谷・深谷・本庄"	: "kumagaya",
        "川越・東松山・志木・和光"	: "kawagoe",
        "所沢・狭山・飯能"	: "tokorozawa",
        "秩父・長瀞"	: "chichibu",
    },
    "千葉県"	: {
        "千葉"	: "chiba",
        "舞浜・浦安・船橋・幕張"	: "keiyo",
        "松戸・柏"	: "kashiwa",
        "成田空港・佐倉"	: "narita",
        "銚子・旭・九十九里・東金・茂原"	: "choshi",
        "鴨川・勝浦・御宿・養老渓谷"	: "sotobo",
        "南房総・館山・白浜・千倉"	: "tateyama",
        "市原・木更津・君津・富津・鋸南"	: "uchibo",
    },
    "東京都"	: {
        "東京２３区内"	: "tokyo",
        "立川・八王子・町田・府中・吉祥寺"	: "nishi",
        "奥多摩・青梅・羽村"	: "okutama",
        "八丈島"	: "ritou",
        "大島"	: "oshima",
        "神津島・新島・式根島"	: "kouzu",
        "三宅島"	: "miyake",
        "小笠原諸島"	: "Ogasawara",
    },
    "神奈川県"	: {
        "横浜"	: "yokohama",
        "川崎"	: "kawasaki",
        "箱根"	: "hakone",
        "小田原"	: "odawara",
        "湯河原・真鶴"	: "yugawara",
        "相模湖・丹沢"	: "sagamiko",
        "大和・相模原・町田西部"	: "sagamihara",
        "厚木・海老名・伊勢原"	: "ebina",
        "湘南・鎌倉・江ノ島・藤沢・平塚"	: "shonan",
        "横須賀・三浦"	: "miura",
    },
    "新潟県"	: {
        "新潟"	: "niigata",
        "月岡・瀬波・咲花"	: "kaetsu",
        "長岡・燕三条・柏崎・弥彦・岩室・寺泊"	: "kita",
        "魚沼・十日町・津南・六日町・大湯"	: "minami",
        "越後湯沢・苗場"	: "yuzawa",
        "上越・糸魚川・妙高"	: "joetsu",
        "佐渡"	: "sado",
    },
    "富山県"	: {
        "富山・八尾・立山"	: "toyama",
        "滑川・魚津・朝日・黒部・宇奈月"	: "goto",
    	"高岡・氷見・砺波"	: "gosei",
    },
    "石川県"	: {
        "金沢"	: "kanazawa",
        "加賀・小松・辰口"	: "kaga",
        "能登・輪島・珠洲"	: "noto",
        "七尾・和倉・羽咋"	: "nanao",
    },
    "福井県"	: {
        "福井"	: "hukui",
        "あわら・三国"	: "awara",
        "永平寺・勝山・大野"	: "katsuyama",
        "越前・鯖江・武生"	: "echizen",
        "敦賀・美浜"	: "tsuruga",
        "若狭・小浜・高浜"	: "obama",
    },
    "山梨県"	: {
        "甲府・湯村・昇仙峡"	: "kofu",
        "山梨・石和・勝沼・塩山"	: "yamanashi",
        "大月・都留・道志渓谷"	: "otsuki",
        "山中湖・忍野"	: "yamanakako",
        "河口湖・富士吉田・本栖湖・西湖・精進湖"	: "kawaguchiko",
        "下部・身延・早川"	: "minobu",
    	"韮崎・南アルプス"	: "nirasaki",
        "八ヶ岳・小淵沢・清里・大泉"	: "kiyosato",
    },
    "長野県"	: {
        "長野・小布施・信州高山・戸隠・飯綱"	: "nagano",
    	"斑尾・飯山・信濃町・野尻湖・黒姫"	: "madara",
        "野沢温泉・木島平・秋山郷"	: "nozawa",
        "志賀高原･湯田中･渋"	: "shiga",
        "上田・別所・鹿教湯"	: "ueda",
    	"戸倉上山田・千曲"	: "chikuma",
        "菅平・峰の原"	: "sugadaira",
        "軽井沢・佐久･小諸"	: "karui",
        "八ヶ岳・野辺山・富士見・原村"	: "yatsu",
        "蓼科・白樺湖・霧ヶ峰・車山"	: "kirigamine",
        "諏訪湖"	: "suwa",
        "伊那・駒ヶ根・飯田・昼神"	: "ina",
        "木曽"	: "kiso",
        "松本・塩尻・浅間温泉・美ヶ原温泉"	: "matsumo",
        "上高地・乗鞍・白骨"	: "kamiko",
        "安曇野・穂高・大町・豊科"	: "hotaka",
        "白馬・八方尾根・栂池高原・小谷"	: "hakuba",
    },
    "岐阜県"	: {
        "岐阜・各務原"	: "gifu",
        "奥飛騨・新穂高"	: "kamitakara",
        "高山・飛騨"	: "takayama",
        "下呂温泉・濁河温泉"	: "gero",
        "中津川・多治見・恵那・美濃加茂"	: "tajimi",
        "郡上八幡・関・美濃"	: "gujo",
        "白川郷"	: "shirakawago",
        "大垣・岐阜羽島"	: "ogaki",
    },
    "静岡県"	: {
        "静岡・清水"	: "shizuoka",
        "熱海"	: "atami",
        "伊東"	: "ito",
        "伊豆高原"	: "izukogen",
        "東伊豆・河津"	: "higashi",
        "下田・南伊豆"	: "shimoda",
        "西伊豆・戸田・土肥・堂ヶ島"	: "nishi",
        "伊豆長岡・修善寺・天城湯ヶ島"	: "naka",
        "富士・富士宮"	: "fuji",
    	"御殿場・沼津・三島"	: "numazu",
        "焼津・藤枝・御前崎・寸又峡"	: "yaizu",
    	"浜松・浜名湖・天竜"	: "hamamatsu",
    	"掛川・袋井・磐田"	: "kikugawa",
    },
    "愛知県"	: {
       	"名古屋"	: "nagoyashi",
        "豊橋・豊川・蒲郡・伊良湖"	: "mikawawan",
        "奥三河・新城・湯谷温泉"	: "okumikawa",
        "豊田・刈谷・知立・安城・岡崎"	: "mikawa",
        "一宮・犬山・小牧・瀬戸・春日井"	: "owari",
        "セントレア・東海・半田・知多"	: "chita",
        "南知多・日間賀島・篠島"	: "minamichita",
    },
    "三重県"	: {
        "津･鈴鹿･亀山"	: "tsu",
        "四日市・桑名・湯の山・長島温泉"	: "yunoyama",
        "伊賀・名張"	: "iga",
        "松阪"	: "matsusaka",
        "伊勢・二見"	: "ise",
        "鳥羽"	: "toba",
        "志摩・賢島"	: "shima",
        "熊野・尾鷲・紀北"	: "kumano",
    },
    "滋賀県"	: {
        "大津・雄琴・草津・栗東"	: "ootsu",
        "湖西・高島・マキノ"	: "kosei",
        "長浜・米原"	: "kohoku",
        "彦根・近江八幡・守山・東近江"	: "kotou",
        "信楽・甲賀"	: "shigaraki",
    },
    "京都府"	: {
        "京都"	: "shi",
        "宇治・長岡京"	: "nannbu",
        "亀岡・湯の花・美山・京丹波"	: "yunohana",
        "福知山・綾部"	: "fukuchiyama",
        "丹後・久美浜"	: "hokubu",
        "天橋立・宮津・舞鶴"	: "miyazu",
    },
    "大阪府"	: {
        "大阪"	: "shi",
        "高槻・茨木・箕面・伊丹空港"	: "hokubu",
        "枚方・守口・東大阪"	: "toubu",
        "八尾・藤井寺・河内長野"	: "nantou",
        "堺・岸和田・関空・泉佐野"	: "nanbu",
    },
    "兵庫県"	: {
        "神戸・有馬温泉・六甲山"	: "kobe",
        "宝塚・西宮・甲子園・三田・篠山"	: "nantou",
        "明石・加古川・三木"	: "minamichu",
        "姫路・相生・赤穂"	: "nannansei",
        "和田山・竹田城・ハチ高原"	: "chubu",
        "城崎温泉・豊岡・出石・神鍋"	: "kita",
        "香住・浜坂・湯村"	: "kasumi",
        "淡路島"	: "awaji",
    },
    "奈良県"	: {
        "奈良・大和高原"	: "nara",
        "橿原・大和郡山・天理・生駒"	: "hokubu",
        "吉野・十津川・天川・五條"	: "nanbu",
    },
    "和歌山県"	: {
        "和歌山・加太・和歌浦"	: "wakayama",
        "高野山・橋本"	: "Kihoku",
        "御坊・有田・海南・日高"	: "gobo",
        "南紀白浜・紀伊田辺・龍神"	: "shirahama",
        "勝浦・串本・すさみ"	: "Katsuura",
        "熊野古道・新宮・本宮・中辺路"	: "hongu",
    },
    "鳥取県"	: {
        "鳥取・岩美・浜村"	: "tottori",
        "倉吉・三朝温泉"	: "chubu",
        "米子・皆生温泉・大山"	: "seibu",
    },
    "島根県"	: {
        "松江・玉造・安来・奥出雲"	: "matsue",
        "出雲・大田・石見銀山"	: "toubu",
        "津和野・益田・浜田・江津"	: "masuda",
        "隠岐諸島"	: "ritou",
    },
    "岡山県"	: {
        "岡山"	: "okayama",
        "牛窓・瀬戸内・備前"	: "bizen",
        "津山・湯郷・美作・奥津"	: "tsuyama",
        "湯原・蒜山・新見・高梁"	: "niimi",
        "倉敷・総社・玉野・笠岡"	: "kurashiki",
    },
    "広島県"	: {
        "広島"	: "hiroshima",
        "東広島・竹原・三原・広島空港"	: "higashihiroshima",
        "福山・尾道・しまなみ海道"	: "fukuyama",
        "呉・江田島"	: "kure",
        "三次・庄原・帝釈峡"	: "shohara",
        "三段峡・芸北・北広島"	: "sandankyo",
        "宮島・宮浜温泉・廿日市"	: "miyajima",
    },
    "山口県"	: {
        "山口・湯田温泉・防府"	: "yamaguchi",
        "下関・宇部"	: "shimonoseki",
        "岩国・周南・柳井"	: "iwakuni",
        "萩・長門・秋吉台"	: "hagi",
    },
    "徳島県"	: {
        "徳島・鳴門"	: "tokushima",
        "大歩危・祖谷・剣山・吉野川"	: "hokubu",
        "阿南・日和佐・宍喰"	: "nanbu",
    },
    "香川県"	: {
        "高松・さぬき・東かがわ"	: "takamatsu",
        "坂出・宇多津・丸亀"	: "sakaide",
        "琴平・観音寺"	: "kotohira",
        "小豆島・直島"	: "ritou",
    },
    "愛媛県"	: {
        "松山・道後"	: "chuuyo",
        "今治・しまなみ海道"	: "touyo",
        "西条・新居浜・四国中央"	: "saijo",
        "宇和島・八幡浜"	: "nanyo",
    },
    "高知県"	: {
        "高知・南国・香南・伊野"	: "kouchi",
        "安芸・室戸"	: "toubu",
        "足摺・四万十・宿毛・須崎"	: "seibu",
    },
    "福岡県"	: {
        "博多・キャナルシティ・海の中道・太宰府・二日市"	: "fukuoka",
        "天神・中洲・薬院・福岡ドーム・糸島"	: "seibu",
        "北九州"	: "kitakyusyu",
        "宗像・宮若・飯塚"	: "chikuzen",
        "久留米・甘木・原鶴温泉・筑後川温泉"	: "kurume",
        "北九州空港・苅田・行橋・豊前"	: "buzen",
        "大牟田・柳川・八女・筑後"	: "chikugo",
    },
    "佐賀県"	: {
        "佐賀・古湯温泉"	: "saga",
        "鳥栖"	: "tosu",
        "嬉野・武雄・伊万里・有田・太良"	: "ureshino",
        "唐津・呼子"	: "karatsu",
    },
    "長崎県"	: {
        "長崎"	: "nagasaki",
        "雲仙・島原・小浜"	: "unzen",
        "諫早・大村・長崎空港"	: "airport",
        "ハウステンボス・佐世保・平戸"	: "sasebo",
        "五島列島"	: "ritou",
        "対馬"	: "tsushima",
        "壱岐島"	: "iki",
    },
    "熊本県"	: {
        "熊本"	: "kumamoto",
        "大津・玉名・山鹿・荒尾・菊池"	: "kikuchi",
        "阿蘇"	: "aso",
        "宇土・八代・水俣"	: "yatsushiro",
        "人吉・球磨"	: "kuma",
        "天草･本渡"	: "amakusa",
        "黒川温泉・杖立"	: "kurokawa",
    },
    "大分県"	: {
        "大分"	: "oita",
    	"別府・日出"	: "beppu",
        "佐伯・臼杵・豊後大野"	: "usuki",
        "湯布院・湯平"	: "yufuin",
        "久住・竹田"	: "taketa",
        "九重・日田・天瀬"	: "hita",
        "国東・中津・宇佐・耶馬渓"	: "kunisaki",
    },
    "宮崎県"	: {
        "宮崎"	: "miyazaki",
        "高千穂・延岡・日向・高鍋"	: "hokubu",
        "都城・えびの・日南・綾"	: "nanbu",
    },
    "鹿児島県"	: {
        "鹿児島・桜島"	: "kagoshima",
        "霧島・国分・鹿児島空港"	: "oosumi",
        "鹿屋・垂水・志布志"	: "kanoya",
        "川内・出水"	: "hokusatsu",
        "指宿・枕崎・南さつま"	: "nansatsu",
        "屋久島"	: "yakushima",
        "種子島"	: "ritou",
        "奄美大島･喜界島・徳之島"	: "amami",
        "沖永良部島・与論島"	: "okinoerabu",
    },
    "沖縄県"	: {
        "那覇"	: "nahashi",
        "恩納・名護・本部・今帰仁"	: "hokubu",
        "宜野湾・北谷・読谷・沖縄市・うるま"	: "chubu",
        "糸満・豊見城・南城"	: "nanbu",
        "慶良間・渡嘉敷・座間味・阿嘉"	: "kerama",
        "久米島"	: "kumejima",
        "宮古島・伊良部島"	: "Miyako",
        "石垣・西表・小浜島"	: "ritou",
        "与那国島"	: "yonaguni",
        "大東島"	: "daito",
    },
    # 他の都道府県の対応リストも必要に応じて追加
}

# 47都道府県リスト
prefectures = list(prefecture_mapping.keys())


# ホテル検索関数
def search_hotels(middle_area, small_area, checkin_date, checkout_date, min_charge, max_charge, people):
    params = {
        "applicationId": APP_ID,
        "format": "json",
        "largeClassCode": "japan",
        "middleClassCode": middle_area,
        "smallClassCode": small_area,
        "checkinDate": checkin_date.strftime('%Y-%m-%d'),
        "checkoutDate": checkout_date.strftime('%Y-%m-%d'),
        "maxCharge": max_charge,
        "minCharge": min_charge,
        "datumType": 1,
        "adultNum": people,
    }

    try:
        res = requests.get(REQUEST_URL_TRAVEL, params=params)
        res.raise_for_status()
        results = res.json()
        if "hotels" in results:
            df = pd.DataFrame([hotel["hotel"][0]["hotelBasicInfo"] for hotel in results["hotels"]])
            return df.sort_values(by="hotelMinCharge", ascending=True)
        else:
            st.warning("条件に一致するホテルが見つかりませんでした。")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"ホテル検索中にエラーが発生しました: {e}")
    return pd.DataFrame()

# ゴルフ場検索関数
def search_golf_courses(latitude, longitude):
    params = {
        "applicationId": APP_ID,
        "format": "json",
        "latitude": latitude,
        "longitude": longitude,
        "searchRadius": 50,
        "reservation": 1,
    }

    try:
        res = requests.get(REQUEST_URL_GORA, params=params)
        res.raise_for_status()
        results = res.json()
        if "Items" in results:
            df = pd.DataFrame([item["Item"] for item in results["Items"]])
            return df.sort_values(by="evaluation", ascending=False)
        else:
            st.warning("条件に一致するゴルフ場が見つかりませんでした。")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"ゴルフ場検索中にエラーが発生しました: {e}")
    return pd.DataFrame()

# Streamlit アプリの設定
# st.title("楽天旅行APIを使用した宿泊とゴルフ場検索")

# 入力フォーム
with st.sidebar:
    # ユーザー入力を受け取る
    start_area = st.selectbox("出発する県名", prefectures, index=prefectures.index("東京都"))
    middle_area_display = st.selectbox("目的地県名", prefectures, index=prefectures.index("岐阜県"))
    
    # small_area の選択肢を動的に設定
    small_area_options = small_area_mapping.get(middle_area_display, {})
    small_area_display = st.selectbox("目的地市、地域名", list(small_area_options.keys()), index=0)

    # ユーザー入力を受け取る(続き)
    col1, col2 = st.columns(2) # 横並びにするために列を作成
    with col1:
        checkin_date = st.date_input("旅行開始日", value=today)
    with col2:
        checkout_date = st.date_input("旅行終了日", value=tomorrow)
    min_charge = st.slider("宿泊最小金額", min_value=0, max_value=100000, value=50000, step=1000)
    max_charge = st.slider("宿泊最大金額", min_value=0, max_value=200000, value=100000, step=1000)
    people = st.slider("旅行人数(大人のみ)", min_value=1, max_value=20, value=4, step=1)
    activity = st.text_input("やりたいアクティビティ", "キャンプ")
# middle_area をAPI用コードに変換
middle_area = prefecture_mapping[middle_area_display]
# small_area をAPI用コードに変換
small_area = small_area_mapping.get(middle_area_display, {}).get(small_area_display, "")


# セッション状態の初期化
if "selected_plan" not in st.session_state:
    st.session_state["selected_plan"] = None

# 既に選択されたプランが保存されている場合、その情報を表示
def display_selected_plan():
    if st.session_state["selected_plan"]:
        selected_plan = st.session_state["selected_plan"]
        st.title("選択されたプラン")
        col1, col2 = st.columns([6, 4])
        with col1:
            st.subheader(f"""ホテル名: 
                         {selected_plan['hotel_name']}""")
            st.subheader(f"""ゴルフ場名: 
                         {selected_plan['golf_course_name']}""")
        with col2:
            st.markdown(f"""
                        <style>
                            .custom-image {{
                                height: 50px;  /* 画像の高さを指定 */
                                width: 150px;   /* 幅を自動的に調整 */
                                object-fit: cover;
                                float: right;
                                margin-left: auto;
                                margin-right: auto;
                                display: block;
                            }}
                        </style>
                        <img src="{selected_plan['hotel_image_url']}" class="custom-image">
                    """, unsafe_allow_html=True)
            st.markdown(f"""
                        <style>
                            .custom-image {{
                                height: 50px;  /* 画像の高さを指定 */
                                width: 150px;   /* 幅を自動的に調整 */
                                object-fit: cover;
                                float: right;
                                margin-left: auto;
                                margin-right: auto;
                                display: block;
                            }}
                        </style>
                        <img src="{selected_plan['golf_image_url']}" class="custom-image">
                    """, unsafe_allow_html=True)
        
    else:
        st.write("選択されたプランはありません。")

# 選択ボタンがクリックされたときに実行する処理
def on_plan_select(hotel, top_golf, idx):
    # 選択されたプランをセッションに保存
    st.session_state["selected_plan"] = {
        "hotel_name": hotel["hotelName"],
        "hotel_price": hotel["hotelMinCharge"],
        "hotel_review_average": hotel.get("reviewAverage", "N/A"),
        "hotel_review_count": hotel.get("reviewCount", "N/A"),
        "golf_course_name": top_golf["golfCourseName"] if top_golf is not None else "なし",
        "golf_course_evaluation": top_golf["evaluation"] if top_golf is not None else  "なし",
        "hotel_image_url":hotel["hotelImageUrl"],
        "golf_image_url":top_golf['golfCourseImageUrl']
    }

 

# 検索ボタンを押した後の処理
def search_and_display_hotels():
    # ここでは仮のデータを使う
    df_hotels = search_hotels(middle_area, small_area, checkin_date, checkout_date, min_charge, max_charge, people)
    
    if not df_hotels.empty:  # df_hotels が空でないかを確認
        # いくつかの条件でホテルを並べ替え
        min_charge_hotel = df_hotels.iloc[0]
        max_review_hotel = df_hotels.sort_values(by="reviewAverage", ascending=False).iloc[0]
        max_review_count_hotel = df_hotels.sort_values(by="reviewCount", ascending=False).iloc[0]

        # 3つのホテルに関して、選択ボタンを作成
        for idx, hotel in enumerate([min_charge_hotel, max_review_hotel, max_review_count_hotel], start=1):
            golf_df = search_golf_courses(hotel["latitude"], hotel["longitude"])
            col1, col2 = st.columns([6, 4])
            # golf_df が空でないかを確認
            if not golf_df.empty:  # 空でない場合、top_golfを取得
                top_golf = golf_df.iloc[0]
                # 各ホテルに対して「このプランを選択」ボタンを表示
                button_id = f"select_plan_{idx}"
                st.button(f"このプランを選択", key=button_id, on_click=on_plan_select, args=(hotel, top_golf if not golf_df.empty else None, idx))
                # 左カラムにテキストを表示
                col1, col2, col3, col4 = st.columns(4)

                # ホテル情報を左上のカラムに表示 (col1)
                with col1:
                    st.markdown(f"""
                        <style>
                            .custom-link {{
                                font-size: 18px;  /* テキストサイズ */
                                font-weight: bold; /* 太字 */
                                color: blue; /* テキスト色 */
                            }}
                        </style>
                        <a href="{hotel['hotelInformationUrl']}" target="_blank" class="custom-link">{hotel['hotelName']}</a>
                    """, unsafe_allow_html=True)
                    st.write(f"最安料金: {hotel['hotelMinCharge']}円")
                    st.write(f"レビュー平均: {hotel.get('reviewAverage', 'N/A')}")

                # ホテル画像を右上のカラムに表示 (col2)
                with col2:
                    st.markdown(f"""
                        <style>
                            .custom-image {{
                                height: 1500px;  /* 画像の高さを指定 */
                                width: 300px;   /* 幅を自動的に調整 */
                                object-fit: cover;
                                float: right;
                                margin-left: auto;
                                margin-right: auto;
                                display: block;
                            }}
                        </style>
                        <img src="{hotel['hotelImageUrl']}" class="custom-image">
                    """, unsafe_allow_html=True)

                # ゴルフ場情報を左下のカラムに表示 (col3)
                with col3:
                    st.markdown(f"""
                        <style>
                            .custom-link {{
                                font-size: 18px;  /* テキストサイズ */
                                font-weight: bold; /* 太字 */
                                color: blue; /* テキスト色 */
                            }}
                        </style>
                        <a href="{top_golf['golfCourseDetailUrl']}" target="_blank" class="custom-link">{top_golf['golfCourseName']}</a>
                    """, unsafe_allow_html=True)
                    st.write(f"評価: {top_golf['evaluation']}")
                    
                    st.markdown(f"""
                        <style>
                            .custom-link_calendar {{
                                font-size: 16px;  /* テキストサイズ */
                                color: blue; /* テキスト色 */
                            }}
                        </style>
                        <a href="{top_golf['reserveCalUrl']}" target="_blank" class="custom-link_calendar">予約カレンダー</a>
                    """, unsafe_allow_html=True)

                # ゴルフ場画像を右下のカラムに表示 (col4)
                with col4:
                    st.markdown(f"""
                        <style>
                            .custom-image {{
                                height: 150px;  /* 画像の高さを指定 */
                                width: 300px;   /* 幅を自動的に調整 */
                                object-fit: cover;
                                float: right;
                                margin-left: auto;
                                margin-right: auto;
                                display: block;
                            }}
                        </style>
                        <img src="{top_golf['golfCourseImageUrl']}" class="custom-image">
                    """, unsafe_allow_html=True)
            else:
                button_id = f"select_plan_{idx}"
                st.button(f"このプランを選択", key=button_id, on_click=on_plan_select, args=(hotel, top_golf if not golf_df.empty else None, idx))
                # 左カラムにテキストを表示
                col1, col2, col3, col4 = st.columns(4)

                # ホテル情報を左上のカラムに表示 (col1)
                with col1:
                    st.markdown(f"""
                        <style>
                            .custom-link {{
                                font-size: 18px;  /* テキストサイズ */
                                font-weight: bold; /* 太字 */
                                color: blue; /* テキスト色 */
                            }}
                        </style>
                        <a href="{hotel['hotelInformationUrl']}" target="_blank" class="custom-link">{hotel['hotelName']}</a>
                    """, unsafe_allow_html=True)
                    st.write(f"最安料金: {hotel['hotelMinCharge']}円")
                    st.write(f"レビュー平均: {hotel.get('reviewAverage', 'N/A')}")

                # ホテル画像を右上のカラムに表示 (col2)
                with col2:
                    st.markdown(f"""
                        <style>
                            .custom-image {{
                                height: 1500px;  /* 画像の高さを指定 */
                                width: 300px;   /* 幅を自動的に調整 */
                                object-fit: cover;
                                float: right;
                                margin-left: auto;
                                margin-right: auto;
                                display: block;
                            }}
                        </style>
                        <img src="{hotel['hotelImageUrl']}" class="custom-image">
                    """, unsafe_allow_html=True)

                # ゴルフ場情報を左下のカラムに表示 (col3)
                with col3:
                    st.markdown(f"""
                        <style>
                            .custom-link {{
                                font-size: 18px;  /* テキストサイズ */
                                font-weight: bold; /* 太字 */
                                color: blue; /* テキスト色 */
                            }}
                        </style>
                        <a href="{top_golf['golfCourseDetailUrl']}" target="_blank" class="custom-link">{top_golf['golfCourseName']}</a>
                    """, unsafe_allow_html=True)
                    st.write(f"評価: {top_golf['evaluation']}")
                    
                    st.markdown(f"""
                        <style>
                            .custom-link_calendar {{
                                font-size: 16px;  /* テキストサイズ */
                                color: blue; /* テキスト色 */
                            }}
                        </style>
                        <a href="{top_golf['reserveCalUrl']}" target="_blank" class="custom-link_calendar">予約カレンダー</a>
                    """, unsafe_allow_html=True)

                # ゴルフ場画像を右下のカラムに表示 (col4)
                with col4:
                    st.markdown(f"""
                        <style>
                            .custom-image {{
                                height: 150px;  /* 画像の高さを指定 */
                                width: 300px;   /* 幅を自動的に調整 */
                                object-fit: cover;
                                float: right;
                                margin-left: auto;
                                margin-right: auto;
                                display: block;
                            }}
                        </style>
                        <img src="{top_golf['golfCourseImageUrl']}" class="custom-image">
                    """, unsafe_allow_html=True)


# メイン処理
def main():
    # まずは選択されたプランがあるかを確認
    display_selected_plan()

    # プランが選択されていなければ、検索ボタンを表示
    if st.session_state["selected_plan"] is None:
        if st.sidebar.button("検索"):
            search_and_display_hotels()

if __name__ == "__main__":
    main()

# システムメッセージで指示を設定
instructions = """
あなたは旅行プランを提案するプロフェッショナルアシスタントです。以下のルールに従って旅行プランを提案してください：

1. 情報を入力したら、おすすめの旅行プランを1日ごとに提案してください。
<入力情報>
- 出発地
- 目的地
- 旅行日程
- 人数
- ゴルフ場
- 宿泊するホテル
- ゴルフ以外にやりたいアクティビティ
2. 旅行がスムーズに行くためのアドバイスや、目的地や旅行の季節に合わせたアドバイスをしてください。
3. ホテルやゴルフ場の場所を調べ、やりたいアクティビティがしやすいプランを提案してください。
4. 具体的なお店や施設を提案するときはURLをつけてリンクできるようにしてください。
5. やりたいアクティビティが全て完了してしまった場合でも、旅行日程の最後まで楽しめるように全日程のプランを考えてください。"""

# 入力情報の例
if "selected_plan" in st.session_state and st.session_state["selected_plan"]:
    selected_plan = st.session_state["selected_plan"]

    user_input = f"""
    出発地: {start_area}
    目的地: {small_area}
    旅行日程: {checkin_date}〜{checkout_date}
    人数: {people}人
    ゴルフ場: {selected_plan['golf_course_name']}
    宿泊するホテル: {selected_plan['hotel_name']}
    ゴルフ以外にやりたいアクティビティ: {activity}
    """

    # ChatGPT APIにリクエストを送信
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_input}
        ]
    )

    # 応答を取得して表示
    st.write(completion.choices[0].message.content)

