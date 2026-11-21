# -*- coding: utf-8 -*-
"""
Script to build comprehensive Red Chamber dataset (honglou_data.json and honglou_data.js)
"""
import os
import json
import urllib.request

# Ensure directories
os.makedirs('data', exist_ok=True)

# Read raw honglou.json
url = 'https://raw.githubusercontent.com/bluejoe2008/InteractiveGraph/master/dist/examples/honglou.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    raw_data = json.loads(resp.read().decode('utf-8'))

raw_nodes = raw_data['data']['nodes']
raw_edges = raw_data['data']['edges']

raw_node_by_label = {}
for n in raw_nodes:
    if 'label' in n:
        raw_node_by_label[n['label'].strip()] = n

# Available avatars
available_avatars = set(os.listdir('assets/avatars'))
print(f"Total available avatars: {len(available_avatars)}")

# Clan categories
CLANS = [
    {"id": "rongguo", "name": "荣国府", "color": "#c53030", "bg": "#fff5f5", "border": "#feb2b2", "desc": "以贾母、贾政、贾赦为核心的国公勋贵府邸"},
    {"id": "ningguo", "name": "宁国府", "color": "#9b2c2c", "bg": "#fff5f5", "border": "#feb2b2", "desc": "贾氏宗族祖祠所在地，贾珍、贾蓉居所"},
    {"id": "shi", "name": "史家", "color": "#c05621", "bg": "#fffaf0", "border": "#fbd38d", "desc": "阿房宫三百里，住不下金陵一个史"},
    {"id": "wang", "name": "王家", "color": "#b7791f", "bg": "#fffff0", "border": "#fefcbf", "desc": "东海缺少白玉床，龙王来请江南王"},
    {"id": "xue", "name": "薛家", "color": "#2c7a7b", "bg": "#e6fffa", "border": "#81e6d9", "desc": "丰年好大雪，珍珠如土金如铁"},
    {"id": "lin", "name": "姑苏林家", "color": "#2b6cb0", "bg": "#ebf8ff", "border": "#90cdf4", "desc": "钟鼎之家，书香之族，黛玉之母族"},
    {"id": "servant", "name": "大观园丫鬟侍从", "color": "#2f855a", "bg": "#f0fff4", "border": "#9ae6b4", "desc": "心比天高、灵秀聪慧的大观园群芳与仆从"},
    {"id": "external", "name": "故旧亲友与方外", "color": "#6b46c1", "bg": "#faf5ff", "border": "#d6bcfa", "desc": "皇亲王侯、世交知己、引路仙师与乡野恩人"}
]

# Relation types
RELATION_TYPES = [
    {"id": "blood", "name": "宗族血亲", "color": "#e53e3e", "stroke": "solid", "desc": "父子、母子、兄妹、姐弟、祖孙等骨肉至亲"},
    {"id": "marriage", "name": "结发姻亲", "color": "#d53f8c", "stroke": "solid", "desc": "夫妻、妾室、妯娌、连襟、亲家等婚姻纽带"},
    {"id": "love", "name": "情缘至交", "color": "#ed64a6", "stroke": "dashed", "desc": "木石前盟、金玉良缘、痴情暗恋、宿世情缘"},
    {"id": "master_servant", "name": "主仆侍奉", "color": "#3182ce", "stroke": "solid", "desc": "贴身大丫鬟、乳母、随从书童、总管执事"},
    {"id": "friendship", "name": "知己交好", "color": "#38a169", "stroke": "solid", "desc": "结拜结义、金石之交、诗社同人、同僚契友"},
    {"id": "conflict", "name": "恩怨对立", "color": "#718096", "stroke": "dotted", "desc": "家族倾轧、抗婚争斗、嫌隙逐杀、宿世怨怼"}
]

# Metadata dictionary for key characters (Actors from 87 TV series, identities, residences, poems)
CHAR_META = {
    "贾宝玉": {
        "id": "baoyu",
        "actor": "欧阳奋强",
        "gender": "男",
        "clan": "rongguo",
        "generation": "草字辈（第四代）",
        "identity": "荣国府嫡公子 / 怡红公子",
        "residence": "怡红院",
        "importance": 5,
        "judgment": "无故寻愁觅恨，有时似傻如狂。纵然生得好皮囊，腹内原来草莽。潦倒不通世务，愚顽怕读文章。行为偏僻性乖张，那管世人诽谤！",
        "tags": ["核心主角", "神瑛侍者", "通灵宝玉", "大观园", "红楼梦曲"]
    },
    "林黛玉": {
        "id": "daiyu",
        "actor": "陈晓旭",
        "gender": "女",
        "clan": "lin",
        "generation": "草字辈（外孙女）",
        "identity": "巡盐御史林如海之女 / 潇湘妃子",
        "residence": "潇湘馆",
        "importance": 5,
        "judgment": "可叹停机德，堪怜咏絮才。玉带林中挂，金簪雪里埋。\n两弯似蹙非蹙罥烟眉，一双似喜非喜含情目。态生两靥之愁，娇袭一身之病。",
        "tags": ["金陵十二钗正册之首", "绛珠仙草", "木石前盟", "潇湘馆", "海棠诗社"]
    },
    "薛宝钗": {
        "id": "baochai",
        "actor": "张莉",
        "gender": "女",
        "clan": "xue",
        "generation": "草字辈（表姐妹）",
        "identity": "皇商薛家千金 / 蘅芜君",
        "residence": "蘅芜苑",
        "importance": 5,
        "judgment": "可叹停机德，堪怜咏絮才。玉带林中挂，金簪雪里埋。\n珍重芳姿昼掩门，自携手杖就空盆。",
        "tags": ["金陵十二钗正册之首", "金玉良缘", "蘅芜君", "冷香丸", "海棠诗社"]
    },
    "王熙凤": {
        "id": "wangxifeng",
        "actor": "邓婕",
        "gender": "女",
        "clan": "rongguo",
        "generation": "玉字辈正室",
        "identity": "贾琏正妻 / 凤辣子 / 荣国府大总管",
        "residence": "荣国府内堂上房",
        "importance": 5,
        "judgment": "凡鸟偏从末世来，都知爱慕此生才。一从二令三人木，哭向金陵事更哀。\n机关算尽太聪明，反算了卿卿性命！",
        "tags": ["金陵十二钗正册", "治家铁腕", "凤姐", "红楼梦曲"]
    },
    "贾母": {
        "id": "jiamu",
        "actor": "李婷",
        "gender": "女",
        "clan": "rongguo",
        "generation": "代字辈正室（第一代在世长辈）",
        "identity": "荣国公之妻 / 史老太君 / 贾府最高掌权长辈",
        "residence": "荣庆堂",
        "importance": 5,
        "judgment": "享尽人间尊荣富贵，慈爱怜弱，一生历经四代荣华，红楼末世的福寿定海神针。",
        "tags": ["贾府最高尊长", "史老太君", "定海神针", "慈母"]
    },
    "贾政": {
        "id": "jiazheng",
        "actor": "马加奇",
        "gender": "男",
        "clan": "rongguo",
        "generation": "文字辈（第二代）",
        "identity": "工部员外郎 / 贾宝玉之父",
        "residence": "梦坡斋",
        "importance": 4,
        "judgment": "为人方正严谨，崇尚程朱儒道，督责宝玉读书仕进，贾府正统正途的代表。",
        "tags": ["荣府主政", "宝玉之父", "严父", "封建卫道士"]
    },
    "王夫人": {
        "id": "wangfuren",
        "actor": "周贤珍",
        "gender": "女",
        "clan": "rongguo",
        "generation": "文字辈正室",
        "identity": "贾政正室 / 贾宝玉生母 / 荣国府掌堂夫人",
        "residence": "荣国府正堂上房",
        "importance": 4,
        "judgment": "表面宽和吃斋念佛，内里雷霆铁腕，逐晴雯、撵金钏，守护宗法秩序与宝玉前程。",
        "tags": ["当家主母", "宝玉之母", "王家血统"]
    },
    "贾赦": {
        "id": "jiashe",
        "actor": "李颉",
        "gender": "男",
        "clan": "rongguo",
        "generation": "文字辈（第二代长子）",
        "identity": "一等将军 / 贾母长子 / 贾琏之父",
        "residence": "荣国府东院",
        "importance": 3,
        "judgment": "袭爵一等将军，荒淫纵欲，强纳鸳鸯，逼娶迎春与孙绍祖，加速贾府衰亡。",
        "tags": ["袭爵世职", "贾母长子", "贾琏之父"]
    },
    "邢夫人": {
        "id": "xingfuren",
        "actor": "夏明辉",
        "gender": "女",
        "clan": "rongguo",
        "generation": "文字辈继室",
        "identity": "贾赦继室 / 荣国府大太太",
        "residence": "荣国府东院",
        "importance": 3,
        "judgment": "禀性愚劣偏狭，贪财弄权，不恤继子与迎春，常与二房王夫人、王熙凤暗生嫌隙。",
        "tags": ["大太太", "贪吝愚弱"]
    },
    "贾琏": {
        "id": "jialian",
        "actor": "高宏亮",
        "gender": "男",
        "clan": "rongguo",
        "generation": "玉字辈（第三代）",
        "identity": "琏二爷 / 荣国府同知 / 王熙凤之夫",
        "residence": "荣国府前院",
        "importance": 4,
        "judgment": "风流浪荡，处事圆滑通达，精于庶务交际，惧内却多情窃色，偷娶尤二姐。",
        "tags": ["琏二爷", "四大家族公子", "荣府管事"]
    },
    "贾元春": {
        "id": "yuanchun",
        "actor": "成梅",
        "gender": "女",
        "clan": "rongguo",
        "generation": "玉字辈嫡长女",
        "identity": "贤德妃 / 贾政长女 / 皇贵妃",
        "residence": "凤藻宫（大观园省亲）",
        "importance": 4,
        "judgment": "二十年来辨是非，榴花开处照宫闱。三春争及初春景，虎兕相逢大梦归。\n恨黄泉，夭寿韶华，红颜已断，天伦永隔。",
        "tags": ["金陵十二钗正册", "贤德妃", "元春省亲", "大观园之主"]
    },
    "贾迎春": {
        "id": "yingchun",
        "actor": "牟一",
        "gender": "女",
        "clan": "rongguo",
        "generation": "玉字辈庶女",
        "identity": "二木头 / 贾赦庶女 / 菱洲仙子",
        "residence": "紫菱洲缀锦楼",
        "importance": 4,
        "judgment": "子系中山狼，得志便猖狂。金闺花柳质，一载赴黄粱。\n懦弱不争，老实无能，误嫁中山狼孙绍祖，受尽摧残早逝。",
        "tags": ["金陵十二钗正册", "二木头", "缀锦楼", "紫菱洲"]
    },
    "贾探春": {
        "id": "tanchun",
        "actor": "东方闻樱",
        "gender": "女",
        "clan": "rongguo",
        "generation": "玉字辈庶女",
        "identity": "蕉下客 / 贾政庶女 / 大观园改革家",
        "residence": "秋爽斋",
        "importance": 5,
        "judgment": "才自精明志自高，生于末世运偏消。清香一缕谁同惜，去向秋风哭大观。\n远嫁异域，红楼群芳中最具眼界魄力与才干的奇女子。",
        "tags": ["金陵十二钗正册", "大观园改革", "秋爽斋", "蕉下客", "玫瑰花"]
    },
    "贾惜春": {
        "id": "xichun",
        "actor": "胡泽红",
        "gender": "女",
        "clan": "ningguo",
        "generation": "玉字辈胞妹",
        "identity": "藕香榭主 / 贾珍胞妹 / 缁衣皈依者",
        "residence": "暖香坞蓼风轩",
        "importance": 4,
        "judgment": "勘破三春景不长，缁衣顿改昔年妆。可怜绣户侯门女，独卧青灯古佛旁。\n孤僻冷漠，看透荣华幻灭，最终毅然出家为尼。",
        "tags": ["金陵十二钗正册", "蓼风轩", "暖香坞", "出家皈依"]
    },
    "史湘云": {
        "id": "xiangyun",
        "actor": "郭霄珍",
        "gender": "女",
        "clan": "shi",
        "generation": "草字辈（贾母内侄孙女）",
        "identity": "枕霞旧友 / 史候孤女 / 豪爽才女",
        "residence": "枕霞阁（寄住潇湘馆/秋爽斋）",
        "importance": 5,
        "judgment": "富贵又何为？襁褓之间父母违。展眼吊斜晖，湘江水逝楚云飞。\n霁月清风，醉眠芍药裀，英豪阔大宽宏量，巾帼不让须眉。",
        "tags": ["金陵十二钗正册", "醉卧芍药", "大块吃肉", "海棠诗社", "卫若兰之妻"]
    },
    "秦可卿": {
        "id": "keqing",
        "actor": "张蕾",
        "gender": "女",
        "clan": "ningguo",
        "generation": "草字辈正室",
        "identity": "贾蓉之妻 / 宁国府少奶奶 / 太虚幻境可卿仙子",
        "residence": "天香楼",
        "importance": 4,
        "judgment": "情天情海幻情身，情既相逢必主淫。漫言不肖皆荣出，造衅开端实在宁。\n生得袅娜纤巧，行事温柔平和，托梦凤姐警示贾府末路。",
        "tags": ["金陵十二钗正册", "兼美", "太虚幻境", "天香楼", "造衅开端"]
    },
    "妙玉": {
        "id": "miaoyu",
        "actor": "姬玉",
        "gender": "女",
        "clan": "external",
        "generation": "方外仙姝",
        "identity": "栊翠庵女尼 / 畸人 / 槛外人",
        "residence": "栊翠庵",
        "importance": 4,
        "judgment": "欲洁何曾洁，云空未必空。可怜金玉质，终陷淖泥中。\n气质美如兰，才华阜比仙，天生成孤僻人皆罕，与宝玉暗生知音情愫。",
        "tags": ["金陵十二钗正册", "栊翠庵", "槛外人", "雪水烹茶"]
    },
    "李纨": {
        "id": "liwan",
        "actor": "孙梦泉",
        "gender": "女",
        "clan": "rongguo",
        "generation": "玉字辈遗孀",
        "identity": "贾珠之妻 / 贾兰之母 / 稻香老农 / 大观园社长",
        "residence": "稻香村",
        "importance": 4,
        "judgment": "桃李春风结子完，到头谁似一盆兰。如冰水好空相妒，枉与他人作笑谈。\n青春守节，课子成名，大观园诗社领头人。",
        "tags": ["金陵十二钗正册", "稻香村", "课子成名", "海棠诗社社长"]
    },
    "贾巧姐": {
        "id": "qiaojie",
        "actor": "李端",
        "gender": "女",
        "clan": "rongguo",
        "generation": "草字辈嫡女",
        "identity": "贾琏与王熙凤之女",
        "residence": "荣国府大房",
        "importance": 3,
        "judgment": "势败休云贵，家亡莫论亲。偶因济刘氏，巧得遇恩人。\n生于七月初七，刘姥姥为其取名巧姐，贾府抄家后蒙刘姥姥搭救避祸。",
        "tags": ["金陵十二钗正册", "刘姥姥相救", "凤姐之女"]
    },
    "晴雯": {
        "id": "qingwen",
        "actor": "安雯",
        "gender": "女",
        "clan": "servant",
        "generation": "宝玉房侍从",
        "identity": "宝玉房第一贴身大丫鬟 / 芙蓉花神",
        "residence": "怡红院",
        "importance": 4,
        "judgment": "霁月难逢，彩云易散。心比天高，身为下贱。风流灵巧招人怨。寿夭多因诽谤生，多情公子空牵念。\n撕扇作千金一笑，抱病勇补孔雀裘，至性至烈。",
        "tags": ["金陵十二钗又副册之首", "芙蓉女儿", "撕扇千金一笑", "病补雀金裘"]
    },
    "袭人": {
        "id": "xiren",
        "actor": "袁枚",
        "gender": "女",
        "clan": "servant",
        "generation": "宝玉房侍从",
        "identity": "花袭人 / 宝玉房首席大丫鬟 / 准侍妾",
        "residence": "怡红院",
        "importance": 4,
        "judgment": "枉自温柔和顺，空云似桂如兰。堪羡优伶有福，谁知公子无缘。\n恪尽职守，温柔和顺，侍奉宝玉体贴入微，后嫁与名伶蒋玉菡。",
        "tags": ["金陵十二钗又副册", "花气袭人", "温柔和顺", "贾府首席侍女"]
    },
    "紫鹃": {
        "id": "zijuan",
        "actor": "徐丽霞",
        "gender": "女",
        "clan": "servant",
        "generation": "潇湘馆侍从",
        "identity": "鹦哥 / 林黛玉第一贴身大丫鬟 / 患难知己",
        "residence": "潇湘馆",
        "importance": 4,
        "judgment": "慧紫鹃情辞试忙玉，忠心耿耿照护林姑娘一生，黛玉泪尽夭亡后看破红尘随惜春出家。",
        "tags": ["慧紫鹃", "黛玉知己", "情试宝玉", "忠肝义胆"]
    },
    "平儿": {
        "id": "pinger",
        "actor": "沈琳",
        "gender": "女",
        "clan": "servant",
        "generation": "琏二奶奶陪房",
        "identity": "王熙凤陪房大丫鬟 / 贾琏通房侍妾 / 荣府平事掌平秤",
        "residence": "荣国府内房",
        "importance": 4,
        "judgment": "俏平儿软语温香，在凤姐之威与贾琏之浪之间周旋自处，仁慈宽厚，常暗济他人。",
        "tags": ["俏平儿", "贤德侍女", "凤姐心腹", "贾府调停人"]
    },
    "鸳鸯": {
        "id": "yuanyang",
        "actor": "郑铮",
        "gender": "女",
        "clan": "servant",
        "generation": "贾母首席大丫鬟",
        "identity": "金鸳鸯 / 贾母贴身管事姑姑 / 贾母私库掌匙人",
        "residence": "荣庆堂",
        "importance": 4,
        "judgment": "鸳鸯女誓绝鸳鸯偶，深得贾母倚重与阖府敬重，刚烈抗拒贾赦威逼强纳，后随贾母自尽。",
        "tags": ["抗婚刚烈", "贾母倚重", "大雪断发"]
    },
    "香菱": {
        "id": "xiangling",
        "actor": "陈剑月",
        "gender": "女",
        "clan": "xue",
        "generation": "薛蟠之妾",
        "identity": "甄英莲 / 甄士隐之女 / 薛蟠妾室",
        "residence": "薛家别院 / 蘅芜苑（寄居学诗）",
        "importance": 4,
        "judgment": "根并荷花一茎香，平生遭际实堪伤。自从两地生孤木，致使香魂返故乡。\n元宵被拐颠沛流离，痴心慕雅大观园苦心学诗，饱受夏金桂虐害而逝。",
        "tags": ["金陵十二钗副册之首", "甄英莲", "香菱学诗", "薄命女"]
    },
    "刘姥姥": {
        "id": "liulaolao",
        "actor": "沙玉华",
        "gender": "女",
        "clan": "external",
        "generation": "乡野长者",
        "identity": "积善之家老农妇 / 巧姐恩人",
        "residence": "京郊乡野农舍",
        "importance": 4,
        "judgment": "大智若愚，知恩图报，一进荣国府求济，二进大观园带来田园欢趣，三进贾府万难搭救巧姐。",
        "tags": ["三进大观园", "大智若愚", "巧姐恩人", "草根福星"]
    },
    "贾珍": {
        "id": "jiazhen",
        "actor": "李志新",
        "gender": "男",
        "clan": "ningguo",
        "generation": "文字辈（宁府当家人）",
        "identity": "威烈将军 / 贾氏宗族族长",
        "residence": "宁国府会芳园",
        "importance": 4,
        "judgment": "宁国府族长，骄奢淫逸，倒行逆施，与秦可卿有染，宁荣二府衰败的重要根源之一。",
        "tags": ["宁国府族长", "威烈将军", "秦可卿公公"]
    },
    "尤氏": {
        "id": "youshi",
        "actor": "王贵娥",
        "gender": "女",
        "clan": "ningguo",
        "generation": "文字辈继室",
        "identity": "贾珍继妻 / 宁国府当家主妇 / 尤大奶奶",
        "residence": "宁国府正房",
        "importance": 3,
        "judgment": "性情随和懦弱，难制贾珍之劣，虽身居大奶奶尊位，却只能顺应周旋。",
        "tags": ["宁府主母", "尤大奶奶"]
    },
    "贾蓉": {
        "id": "jiarong",
        "actor": "杨俊勇",
        "gender": "男",
        "clan": "ningguo",
        "generation": "玉字辈嫡长子",
        "identity": "贾珍之子 / 秦可卿之夫",
        "residence": "宁国府",
        "importance": 3,
        "judgment": "纨绔轻浮，受其父管束却毫无主见，在长辈淫威下唯唯诺诺，纵情酒色。",
        "tags": ["宁府公子", "秦可卿之夫"]
    },
    "薛蟠": {
        "id": "xuepan",
        "actor": "陈洪海",
        "gender": "男",
        "clan": "xue",
        "generation": "草字辈（薛家家主）",
        "identity": "薛霸王 / 宝钗之兄 / 皇商世家公子",
        "residence": "薛家大宅",
        "importance": 3,
        "judgment": "幼年丧父宠溺无度，鲁莽粗野打死冯渊，但天性未泯，敬重宝钗，后为柳湘莲痛改前非。",
        "tags": ["薛霸王", "宝钗之兄", "打死冯渊"]
    },
    "薛蝌": {
        "id": "xueke",
        "actor": "罗二羊",
        "gender": "男",
        "clan": "xue",
        "generation": "草字辈堂弟",
        "identity": "宝钗堂弟 / 薛宝琴之兄 / 邢岫烟之夫",
        "residence": "薛家别院",
        "importance": 3,
        "judgment": "为人沉稳端重，品格端庄清俊，与宝玉相得甚欢，迎娶雅澹如仙的邢岫烟。",
        "tags": ["端正公子", "岫烟良配", "宝琴之兄"]
    },
    "薛宝琴": {
        "id": "xuebaoqin",
        "actor": "王羊",
        "gender": "女",
        "clan": "xue",
        "generation": "草字辈堂妹",
        "identity": "薛蝌之妹 / 宝钗堂妹 / 贾母极宠之客",
        "residence": "随贾母居荣庆堂",
        "importance": 3,
        "judgment": "琉璃世界白雪红梅，才貌双绝，见多识广曾周游名山大川，深得贾母喜爱赐凫靥裘。",
        "tags": ["艳冠群芳", "芦雪庵踏雪", "凫靥裘"]
    },
    "薛姨妈": {
        "id": "xueyima",
        "actor": "李凤英",
        "gender": "女",
        "clan": "xue",
        "generation": "文字辈正室",
        "identity": "王夫人之胞妹 / 宝钗薛蟠之母",
        "residence": "梨香院",
        "importance": 3,
        "judgment": "慈爱宽厚，携子女寄居荣府梨香院，极力促成金玉良缘。",
        "tags": ["宝钗之母", "王夫人胞妹", "梨香院"]
    },
    "尤二姐": {
        "id": "youerjie",
        "actor": "张明明",
        "gender": "女",
        "clan": "ningguo",
        "generation": "尤氏继母之女",
        "identity": "贾琏偷娶之外室二房",
        "residence": "小花房外宅 / 荣府侧院",
        "importance": 3,
        "judgment": "花为肠肚雪作肌肤，悔悟前非专情于贾琏，入荣府后遭王熙凤软刀子借剑杀人，吞金而逝。",
        "tags": ["金陵十二钗副册", "花子二姐", "吞金自逝", "借剑杀人"]
    },
    "尤三姐": {
        "id": "yousanjie",
        "actor": "周月",
        "gender": "女",
        "clan": "ningguo",
        "generation": "尤氏继母之女",
        "identity": "烈女 / 钟情柳湘莲",
        "residence": "小花房外宅",
        "importance": 3,
        "judgment": "揉碎桃花红满地，玉山倾倒再难扶。性情刚烈绝俗，钟情柳湘莲数年，遭疑退婚愤然刎颈自尽。",
        "tags": ["金陵十二钗副册", "绝世烈女", "鸳鸯剑刎颈", "情殇"]
    },
    "贾环": {
        "id": "jiahuan",
        "actor": "王蔚",
        "gender": "男",
        "clan": "rongguo",
        "generation": "草字辈庶子",
        "identity": "贾政与赵姨娘之子 / 探春胞弟",
        "residence": "贾政内宅",
        "importance": 3,
        "judgment": "形容猥琐，心胸狭隘嫉妒，在生母赵姨娘教唆下屡屡陷害宝玉，推烛烫伤宝玉面颊。",
        "tags": ["庶出三爷", "赵姨娘之子", "推烛烫宝玉"]
    },
    "赵姨娘": {
        "id": "zhaoyiniang",
        "actor": "战爱霞",
        "gender": "女",
        "clan": "rongguo",
        "generation": "贾政之妾",
        "identity": "贾探春、贾环生母",
        "residence": "贾政侧房",
        "importance": 3,
        "judgment": "丫鬟出身，浅薄昏聩，生养一双儿女却终日与下人争短长，勾结马道婆暗害宝玉凤姐。",
        "tags": ["贾政侍妾", "探春生母", "魇魔法害宝玉"]
    },
    "贾兰": {
        "id": "jialan",
        "actor": "李玥",
        "gender": "男",
        "clan": "rongguo",
        "generation": "草字辈长孙",
        "identity": "贾珠与李纨之子",
        "residence": "稻香村",
        "importance": 3,
        "judgment": "少言寡语，敏学苦读，在母亲李纨督导下习文练箭，家族败落后中第重振门庭。",
        "tags": ["荣府嫡重孙", "李纨之子", "苦读成名"]
    },
    "贾敬": {
        "id": "jiajing",
        "actor": "韩准",
        "gender": "男",
        "clan": "ningguo",
        "generation": "代字辈（贾母同辈）",
        "identity": "宁国公世袭进士 / 贾珍、惜春之父",
        "residence": "城外玄真观",
        "importance": 2,
        "judgment": "考中进士却看破红尘，弃家不顾隐居玄真观炼丹修仙，最终误服丹砂中毒身亡。",
        "tags": ["宁府老太爷", "好道炼丹", "玄真观"]
    },
    "贾雨村": {
        "id": "jiayucun",
        "actor": "刘宗佑",
        "gender": "男",
        "clan": "external",
        "generation": "同宗附攀",
        "identity": "大司马协办大学士 / 黛玉开蒙恩师",
        "residence": "京师官邸",
        "importance": 4,
        "judgment": "乱世奸雄，投机钻营，葫芦僧乱判葫芦案背弃甄士隐恩情，攀附贾府平步青云，终遭革职。",
        "tags": ["葫芦僧乱判", "黛玉启蒙师", "官场蠹虫"]
    },
    "北静王": {
        "id": "beijingwang",
        "actor": "侯长荣",
        "gender": "男",
        "clan": "external",
        "generation": "皇朝郡王",
        "identity": "北静郡王水溶 / 四王八公之首",
        "residence": "北静王府",
        "importance": 3,
        "judgment": "年少英俊，谦逊温和，爱才惜士，在秦可卿大殡上与宝玉初见如故，赠宝玉鹡鸰香念珠。",
        "tags": ["水溶", "四王八公", "莫逆知己"]
    },
    "柳湘莲": {
        "id": "liuxianglian",
        "actor": "侯长荣",
        "gender": "男",
        "clan": "external",
        "generation": "世家侠士",
        "identity": "冷面二郎 / 游侠雅士",
        "residence": "京师客居",
        "importance": 3,
        "judgment": "面容冷艳，性格豪侠，武艺高强，尤三姐自刎后痛悔万分，削发斩断情丝随道人出家。",
        "tags": ["冷面二郎", "痛打薛蟠", "尤三姐情殇", "削发出家"]
    },
    "蒋玉菡": {
        "id": "jiangyuhan",
        "actor": "冯福生",
        "gender": "男",
        "clan": "external",
        "generation": "名伶知己",
        "identity": "琪官 / 忠顺王府红伶",
        "residence": "紫檀堡别业",
        "importance": 3,
        "judgment": "温雅柔美，与宝玉私交甚深并互赠茜香罗与松花汗巾，后逃出王府，娶袭人为妻。",
        "tags": ["琪官", "茜香罗汗巾", "袭人丈夫"]
    },
    "甄士隐": {
        "id": "zhenshiyin",
        "actor": "王忠信",
        "gender": "男",
        "clan": "external",
        "generation": "姑苏乡绅 / 引路隐士",
        "identity": "香菱之父 / 红楼开卷引路人",
        "residence": "姑苏阊门十里街葫芦庙旁",
        "importance": 3,
        "judgment": "真事隐去，资助贾雨村赴考，元宵痛失爱女英莲，家园焚毁看破红尘，随跛足道人出家解注好了歌。",
        "tags": ["真事隐", "注好了歌", "香菱之父", "开卷第一人"]
    },
    "跛足道人": {
        "id": "daoren",
        "actor": "王辉",
        "gender": "男",
        "clan": "external",
        "generation": "太虚幻境仙使",
        "identity": "大荒山无稽崖度化仙师",
        "residence": "太虚幻境 / 人间云游",
        "importance": 3,
        "judgment": "世人都晓神仙好，唯有功名忘不了！唱响《好了歌》，携通灵宝玉入红尘历劫的引路真仙。",
        "tags": ["好了歌", "警幻仙使", "度化顽石"]
    },
    "癞头和尚": {
        "id": "heshang",
        "actor": "王小东",
        "gender": "男",
        "clan": "external",
        "generation": "太虚幻境仙使",
        "identity": "茫茫大士化身 / 赠金锁海上方",
        "residence": "太虚幻境 / 人间云游",
        "importance": 3,
        "judgment": "赐宝钗冷香丸药方与金锁吉谶“不离不弃，芳龄永继”，与跛足道人一同度尽有缘人。",
        "tags": ["茫茫大士", "赠金锁吉谶", "冷香丸仙方"]
    },
    "邢岫烟": {
        "id": "xingxiuyan",
        "actor": "李伊",
        "gender": "女",
        "clan": "rongguo",
        "generation": "草字辈（邢夫人侄女）",
        "identity": "邢夫人贫家侄女 / 薛蝌之妻",
        "residence": "大观园紫菱洲（寄住迎春处）",
        "importance": 3,
        "judgment": "风髻雾鬓端凝清丽，家贫却超然物外，如闲云野鹤淡泊明志，大观园群芳皆深敬其高洁。",
        "tags": ["金陵十二钗副册", "淡雅脱俗", "薛蝌之妻"]
    },
    "夏金桂": {
        "id": "xiajingui",
        "actor": "杨晓玲",
        "gender": "女",
        "clan": "xue",
        "generation": "草字辈正室",
        "identity": "桂花夏家千金 / 薛蟠正妻",
        "residence": "薛府内宅",
        "importance": 2,
        "judgment": "骄横跋扈，悍妒狠毒，虐待香菱，栽赃宝蟾，闹得薛家鸡犬不宁，自食恶果服毒暴毙。",
        "tags": ["河东狮吼", "薛蟠悍妻", "虐害香菱"]
    },
    "金钏": {
        "id": "jinchuan",
        "actor": "张迎玖",
        "gender": "女",
        "clan": "servant",
        "generation": "王夫人大丫鬟",
        "identity": "白金钏 / 王夫人首席贴身侍女",
        "residence": "王夫人正院",
        "importance": 3,
        "judgment": "因与宝玉说笑被王夫人痛扇耳光撵出，含羞受辱投井自尽，引发宝玉被贾政痛笞大难。",
        "tags": ["投井殉节", "王夫人侍女", "宝玉挨打导火索"]
    },
    "玉钏": {
        "id": "yuchuan",
        "actor": "于洁",
        "gender": "女",
        "clan": "servant",
        "generation": "王夫人大丫鬟",
        "identity": "白玉钏 / 金钏之胞妹",
        "residence": "王夫人正院",
        "importance": 2,
        "judgment": "姐姐金钏自尽后继升大丫鬟，王夫人赐其双份月钱，宝玉情切尝莲叶羹为其解怨。",
        "tags": ["金钏之妹", "尝羹释嫌"]
    },
    "司棋": {
        "id": "siqi",
        "actor": "谷童",
        "gender": "女",
        "clan": "servant",
        "generation": "迎春房大丫鬟",
        "identity": "贾迎春首席大丫鬟 / 潘又安表姐与爱人",
        "residence": "紫菱洲缀锦楼",
        "importance": 3,
        "judgment": "性情刚烈如火，怒砸大观园小厨房，在大观园私会表弟潘又安遗落香囊，抄检大观园后撞墙自尽。",
        "tags": ["大闹厨房", "绣春囊风波", "殉情烈女"]
    },
    "侍书": {
        "id": "shishu",
        "actor": "张卫郑",
        "gender": "女",
        "clan": "servant",
        "generation": "探春房大丫鬟",
        "identity": "贾探春首席大丫鬟",
        "residence": "秋爽斋",
        "importance": 2,
        "judgment": "口齿伶俐，颇有探春之风骨，在抄检大观园时舌战王善保家的，严守主仆尊严。",
        "tags": ["探春心腹", "舌战王善保家的"]
    },
    "入画": {
        "id": "ruhua",
        "actor": "李文玲",
        "gender": "女",
        "clan": "servant",
        "generation": "惜春房大丫鬟",
        "identity": "贾惜春贴身大丫鬟",
        "residence": "蓼风轩",
        "importance": 2,
        "judgment": "因私藏哥哥寄存在此的贾珍赏赐之物，在抄检大观园中被搜出，虽无私弊仍遭惜春绝情撵走。",
        "tags": ["惜春侍女", "抄检被逐"]
    },
    "莺儿": {
        "id": "yingr",
        "actor": "刘继红",
        "gender": "女",
        "clan": "servant",
        "generation": "宝钗房大丫鬟",
        "identity": "黄金莺 / 薛宝钗贴身首席大丫鬟",
        "residence": "蘅芜苑",
        "importance": 3,
        "judgment": "心巧手灵，精通编织各种络子，打花线精妙绝伦，常向宝玉与众人宣扬宝钗之金锁吉谶。",
        "tags": ["宝钗心腹", "打络子巧手", "宣传金玉良缘"]
    },
    "小红": {
        "id": "xiaohong",
        "actor": "刘继红",
        "gender": "女",
        "clan": "servant",
        "generation": "贾府管事之女",
        "identity": "林红玉 / 林之孝之女 / 凤姐心腹丫鬟 / 贾芸意中人",
        "residence": "怡红院 -> 凤姐房",
        "importance": 3,
        "judgment": "心思灵动极具谋略，四五门利落回话得凤姐激赏提拔，与贾芸遗帕传情，贾府破败后与贾芸施救狱中凤姐。",
        "tags": ["林红玉", "遗帕定情", "利落回话", "凤姐得力助手"]
    },
    "麝月": {
        "id": "sheyue",
        "actor": "韩流流",
        "gender": "女",
        "clan": "servant",
        "generation": "宝玉房大丫鬟",
        "identity": "怡红院大丫鬟 / 袭人之副手",
        "residence": "怡红院",
        "importance": 3,
        "judgment": "温厚安详，言语犀利有理有据，宝玉房中群芳散尽后唯一陪伴宝玉到最后的红颜大丫鬟。",
        "tags": ["金陵十二钗又副册", "怡红院留守", "开到荼蘼花事了"]
    },
    "焦大": {
        "id": "jiaoda",
        "actor": "孔芮",
        "gender": "男",
        "clan": "servant",
        "generation": "宁府老仆功臣",
        "identity": "救过宁国公性命的老奴",
        "residence": "宁国府马棚",
        "importance": 3,
        "judgment": "曾从死人堆里背出主子，饮马尿救主，仗着老功醉酒痛骂宁国府“每日家偷狗戏鸡，爬灰的爬灰，养小叔子的养小叔子”。",
        "tags": ["饮马尿救主", "痛骂宁国府", "扒灰丑闻揭露者"]
    },
    "茗烟": {
        "id": "mingyan",
        "actor": "李楠",
        "gender": "男",
        "clan": "servant",
        "generation": "宝玉书童",
        "identity": "焙茗 / 贾宝玉第一贴身小厮",
        "residence": "怡红院外房",
        "importance": 3,
        "judgment": "最知宝玉心意，为宝玉搜罗《西厢记》《牡丹亭》等传奇杂书，助宝玉大闹家塾，带宝玉出府祭金钏。",
        "tags": ["宝玉第一贴身小厮", "大闹学堂", "搜罗传奇杂书"]
    },
    "孙绍祖": {
        "id": "sunshaozu",
        "actor": "王振荣",
        "gender": "男",
        "clan": "external",
        "generation": "世家武职",
        "identity": "大同府指挥使 / 贾迎春之夫",
        "residence": "大同孙府",
        "importance": 2,
        "judgment": "中山狼，借贾赦五千两银子抵债强娶迎春，婚后禽兽不如肆意虐打，致迎春一载夭亡赴黄粱。",
        "tags": ["中山狼", "迎春之夫", "家暴残害者"]
    },
    "贾芸": {
        "id": "jiayun",
        "actor": "吴晓东",
        "gender": "男",
        "clan": "rongguo",
        "generation": "草字辈（西廊下五嫂子之子）",
        "identity": "西廊下二爷 / 认宝玉为父 / 小红之夫",
        "residence": "贾府西廊下住宅",
        "importance": 3,
        "judgment": "精明能干，孝顺坚毅，借冰片麝香奉承凤姐求得大观园栽树美差，与小红情投意合，狱神庙探监济难。",
        "tags": ["孝子贤侄", "认宝玉为义父", "小红夫婿", "大观园栽树"]
    },
    "贾瑞": {
        "id": "jiarui",
        "actor": "马广儒",
        "gender": "男",
        "clan": "rongguo",
        "generation": "草字辈（贾代儒之孙）",
        "identity": "贾家义学督学长孙",
        "residence": "贾代儒宅",
        "importance": 2,
        "judgment": "图谋凤姐美色起淫心，反中凤姐“相思毒设相思局”，屡遭捉弄冻饿惊恐，照风月宝鉴正照精竭而亡。",
        "tags": ["风月宝鉴", "相思局", "痴妄色诫"]
    },
    "林如海": {
        "id": "linruhai",
        "actor": "郑乾龙",
        "gender": "男",
        "clan": "lin",
        "generation": "前科探花 / 巡盐御史",
        "identity": "林黛玉之父 / 贾母之婿",
        "residence": "扬州巡盐御史衙门",
        "importance": 3,
        "judgment": "列侯之第，前科探花，官居兰台寺大夫钦点巡盐御史，夫人贾敏过世后送黛玉进贾府，病逝扬州。",
        "tags": ["黛玉之父", "巡盐御史", "贾母爱婿"]
    },
    "贾代儒": {
        "id": "jiadairu",
        "actor": "郅友",
        "gender": "男",
        "clan": "rongguo",
        "generation": "代字辈老塾师",
        "identity": "贾府家塾主理塾师",
        "residence": "贾府家塾",
        "importance": 2,
        "judgment": "贾氏宗族最长之代字辈族人，严管家塾却难整风纪，痛失长孙贾瑞后凄凉老去。",
        "tags": ["家塾老塾师", "代字辈宗老"]
    },
    "芳官": {
        "id": "fangguan",
        "actor": "孔繁洁",
        "gender": "女",
        "clan": "servant",
        "generation": "戏班伶人 -> 宝玉丫鬟",
        "identity": "大观园十二小戏子正生 / 怡红院丫鬟",
        "residence": "怡红院",
        "importance": 2,
        "judgment": "伶俐俏皮，常着男装改称耶律雄奴，在大观园用蔷薇硝替茉莉粉，后被王夫人逐出大观园出家。",
        "tags": ["大观园戏子", "耶律雄奴", "蔷薇硝风波"]
    },
    "龄官": {
        "id": "lingguan",
        "actor": "程荣",
        "gender": "女",
        "clan": "servant",
        "generation": "戏班当红花旦",
        "identity": "大观园十二戏子台柱 / 贾蔷挚爱",
        "residence": "梨香院戏班",
        "importance": 2,
        "judgment": "眉目神情酷似林黛玉，傲骨嶙峋不附权贵，痴情贾蔷在大观园蔷薇架下画“蔷”字，令宝玉悟情。",
        "tags": ["画蔷痴情", "似林黛玉", "贾蔷之恋"]
    },
    "贾蔷": {
        "id": "jiaqiang",
        "actor": "罗立平",
        "gender": "男",
        "clan": "ningguo",
        "generation": "草字辈（宁府嫡派）",
        "identity": "贾珍养育侄儿 / 梨香院戏班总管",
        "residence": "宁国府别所",
        "importance": 2,
        "judgment": "风流俊俏，管理采买姑苏小戏子与乐器行头，深爱龄官，为她买雀放生至纯相爱。",
        "tags": ["管理戏班", "龄官恋人", "宁府俊秀"]
    },
    "冷子兴": {
        "id": "lengzixing",
        "actor": "关长珠",
        "gender": "男",
        "clan": "external",
        "generation": "古董行家",
        "identity": "都中古董商人 / 周瑞女婿",
        "residence": "都中古玩街",
        "importance": 2,
        "judgment": "红楼开篇演说荣国府，向贾雨村详细剖析贾府庞大家族脉络与百年兴衰气象。",
        "tags": ["演说荣国府", "周瑞女婿", "红楼引路人"]
    },
    "冯紫英": {
        "id": "fengziying",
        "actor": "黄实",
        "gender": "男",
        "clan": "external",
        "generation": "神武将军之子",
        "identity": "京师贵胄侠客 / 宝玉挚友",
        "residence": "神武将军府",
        "importance": 2,
        "judgment": "豪爽洒脱，牵线结识薛蟠、柳湘莲、蒋玉菡与宝玉，并在秦可卿重病时荐名医张友士。",
        "tags": ["神武将军子", "豪饮行令", "荐名医张友士"]
    },
    "赖大": {
        "id": "laida",
        "actor": "程增奎",
        "gender": "男",
        "clan": "servant",
        "generation": "荣府总管",
        "identity": "荣国府第一大管家",
        "residence": "赖家私宅府邸",
        "importance": 2,
        "judgment": "贾府家生奴才，凭借总管荣府家财万贯，自起齐整花园大宅，儿子赖尚荣甚至放外任知县。",
        "tags": ["荣府大管家", "赖尚荣之父"]
    },
    "赖嬷嬷": {
        "id": "laimama",
        "actor": "梁寿萱",
        "gender": "女",
        "clan": "servant",
        "generation": "贾府极尊老嬷嬷",
        "identity": "侍奉过贾母的老保姆 / 赖大之母",
        "residence": "赖宅",
        "importance": 2,
        "judgment": "贾府最具体面的家生老奴，可在贾母堂前赐坐，训诫孙儿不可恃宠而骄忘本。",
        "tags": ["贾府体面老嬷嬷", "训诫子孙"]
    },
    "周瑞家的": {
        "id": "zhouruijiade",
        "actor": "孙彩虹",
        "gender": "女",
        "clan": "servant",
        "generation": "王夫人陪房",
        "identity": "王夫人贴身心腹陪房大管家",
        "residence": "贾府周宅",
        "importance": 2,
        "judgment": "替薛姨妈送宫花串引大观园十二钗群芳出场，抄检大观园得力随从，势利圆滑。",
        "tags": ["送宫花", "王夫人心腹", "冷子兴岳母"]
    },
    "板儿": {
        "id": "baner",
        "actor": "李玥",
        "gender": "男",
        "clan": "external",
        "generation": "乡村孩童",
        "identity": "刘姥姥外孙 / 贾巧姐夫婿（后四十回/红学索隐）",
        "residence": "京郊农家",
        "importance": 2,
        "judgment": "随刘姥姥进荣国府大观园，与巧姐互换佛手与大柚子，伏下日后两家姻缘拯救巧姐之伏笔。",
        "tags": ["柚佛伏线", "刘姥姥外孙", "巧姐良配"]
    },
    "卫若兰": {
        "id": "weiruolan",
        "actor": "孙琦",
        "gender": "男",
        "clan": "external",
        "generation": "王孙公子",
        "identity": "王孙公子 / 史湘云之夫",
        "residence": "都中卫府",
        "importance": 2,
        "judgment": "佩金麒麟的豪门公子，与宝玉交好，后娶史湘云为妻，不久得暴病身亡，留下湘云守寡。",
        "tags": ["金麒麟姻缘", "湘云夫婿"]
    },
    "马道婆": {
        "id": "madaopo",
        "actor": "李白",
        "gender": "女",
        "clan": "external",
        "generation": "江湖三姑六婆",
        "identity": "宝玉寄名干娘 / 巫婆",
        "residence": "京中庵堂",
        "importance": 2,
        "judgment": "贪婪阴狠，受赵姨娘贿银指使，用剪纸魇魔法暗害宝玉与王熙凤，致二人发狂几濒于死。",
        "tags": ["魇魔法害宝玉", "贪婪巫婆"]
    }
}

# Scan all avatar files to build character dictionary
all_characters = {}

# Process all files in assets/avatars
for filename in sorted(list(available_avatars)):
    if not filename.endswith('.jpg'):
        continue
    name = filename.replace('.jpg', '')
    
    # Check if we have pre-defined metadata
    meta = CHAR_META.get(name, {})
    raw_node = raw_node_by_label.get(name, {})
    
    cid = meta.get('id') or f"char_{name}"
    actor = meta.get('actor', '')
    gender = meta.get('gender', '女' if any(w in name for w in ['姐', '娘', '妃', '妻', '姨', '姑', '妈', '女', '婢', '春', '玉', '钗', '云', '黛', '纨', '凤', '卿']) else '男')
    clan = meta.get('clan')
    if not clan:
        # deduce clan
        if name.startswith('贾') or '贾' in name:
            clan = 'rongguo'
        elif name.startswith('薛') or '薛' in name:
            clan = 'xue'
        elif name.startswith('史') or '史' in name:
            clan = 'shi'
        elif name.startswith('王') or '王' in name:
            clan = 'wang'
        elif name.startswith('林') or '林' in name:
            clan = 'lin'
        elif any(w in name for w in ['儿', '官', '丫', '婆', '瑞家的', '管', '小', '珠', '痕', '纹', '缕', '书', '橘', '画']):
            clan = 'servant'
        else:
            clan = 'external'
            
    clan_info = next((c for c in CLANS if c['id'] == clan), CLANS[0])
    
    info_text = meta.get('description') or raw_node.get('info') or f"87版《红楼梦》电视剧出场人物，由{actor or '特邀演员'}饰演。"
    
    # Determine tier hierarchy
    tier1_names = {'贾母', '贾宝玉', '林黛玉', '薛宝钗', '王熙凤', '贾政', '王夫人', '贾琏', '贾珍', '尤氏', '贾赦', '邢夫人'}
    tier2_names = {'贾元春', '贾迎春', '贾探春', '贾惜春', '史湘云', '妙玉', '李纨', '秦可卿', '贾巧姐', '香菱', '贾蓉', '贾兰', '贾环', '赵姨娘', '贾敬', '薛姨妈', '薛蟠', '薛蝌', '薛宝琴', '尤二姐', '尤三姐', '邢岫烟', '林如海', '刘姥姥'}
    tier3_names = {'晴雯', '袭人', '紫鹃', '平儿', '鸳鸯', '金钏', '玉钏', '司棋', '侍书', '入画', '莺儿', '小红', '麝月', '芳官', '龄官', '藕官', '蕊官', '翠缕', '彩云', '碧痕', '秋纹', '茗烟', '焦大', '贾蔷', '贾芸', '贾瑞', '北静王', '柳湘莲', '蒋玉菡', '冯紫英', '板儿', '卫若兰'}
    if name in tier1_names:
        char_tier = 1
    elif name in tier2_names:
        char_tier = 2
    elif name in tier3_names:
        char_tier = 3
    else:
        char_tier = 4

    all_characters[name] = {
        "tier": char_tier,
        "id": name, # using Chinese name as stable ID for seamless matching
        "name": name,
        "avatar": f"assets/avatars/{filename}",
        "actor": actor,
        "gender": gender,
        "clan": clan,
        "clanName": clan_info['name'],
        "identity": meta.get('identity', f"{clan_info['name']}相关人物"),
        "generation": meta.get('generation', "—"),
        "residence": meta.get('residence', "—"),
        "judgment": meta.get('judgment', ""),
        "importance": meta.get('importance', 2),
        "description": info_text,
        "tags": meta.get('tags', [clan_info['name']])
    }

print(f"Total processed characters: {len(all_characters)}")

# Core Relationships Compilation
core_relationships = [
    # 宝玉核心
    {"source": "贾宝玉", "target": "林黛玉", "relation": "木石前盟 / 表兄妹", "type": "love", "desc": "绛珠仙草还泪神瑛侍者，两小无猜，知己深情，红楼至情至圣之绝恋。"},
    {"source": "贾宝玉", "target": "薛宝钗", "relation": "金玉良缘 / 结发夫妻", "type": "marriage", "desc": "和合吉谶通灵配金锁，举案齐眉到底意难平，封建宿命之悲剧结合。"},
    {"source": "贾宝玉", "target": "王熙凤", "relation": "堂姐弟 / 婶侄莫逆", "type": "blood", "desc": "荣国府最受宠的一对儿女，凤姐极尽照拂庇护，宝玉真性情信任。"},
    {"source": "贾宝玉", "target": "贾母", "relation": "祖孙至亲 / 掌上明珠", "type": "blood", "desc": "贾母心肝宝贝、命根子，百般溺爱庇护，宝玉的终极保护伞。"},
    {"source": "贾宝玉", "target": "贾政", "relation": "父子骨肉 / 严督畏惧", "type": "blood", "desc": "封建正统严父与性灵叛逆赤子之尖锐对立，爱之深责之切，大笞宝玉。"},
    {"source": "贾宝玉", "target": "王夫人", "relation": "母子至亲 / 慈母溺爱", "type": "blood", "desc": "王夫人仅存之嫡子，倾注全部母爱与家族荣光希望。"},
    {"source": "贾宝玉", "target": "贾元春", "relation": "同胞姐弟 / 贵妃庇佑", "type": "blood", "desc": "长姐如母，元春幼时亲自抚育发蒙，封妃后特赐宝玉进大观园与姊妹同住。"},
    {"source": "贾宝玉", "target": "贾探春", "relation": "兄妹 / 同人知己", "type": "blood", "desc": "虽为庶出却品格极投契，发起海棠诗社，兄妹情笃。"},
    {"source": "贾宝玉", "target": "贾迎春", "relation": "堂兄妹", "type": "blood", "desc": "紫菱洲同人，痛惜二姐懦弱误嫁中山狼。"},
    {"source": "贾宝玉", "target": "贾惜春", "relation": "堂兄妹", "type": "blood", "desc": "大观园手足，见证惜春勘破红尘缁衣皈依。"},
    {"source": "贾宝玉", "target": "史湘云", "relation": "表兄妹 / 诗酒知己", "type": "friendship", "desc": "青梅竹马自幼一同在贾母膝下长大，大块吃肉大碗喝酒，赠金麒麟。"},
    {"source": "贾宝玉", "target": "妙玉", "relation": "灵犀知己 / 槛外知交", "type": "love", "desc": "孤傲高洁的槛外尼僧独对宝玉另眼相看，赠红梅、品雪水茶。"},
    {"source": "贾宝玉", "target": "秦可卿", "relation": "重孙媳 / 幻境引路", "type": "love", "desc": "梦游太虚幻境授以云雨之事，秦氏托梦亦念及宝玉。"},
    {"source": "贾宝玉", "target": "晴雯", "relation": "主仆深情 / 撕扇知音", "type": "master_servant", "desc": "心比天高风流灵巧，千金一笑撕扇，抱病勇补孔雀裘，诀别赠指甲旧袄，诔芙蓉花神。"},
    {"source": "贾宝玉", "target": "袭人", "relation": "主仆温存 / 准侍妾", "type": "master_servant", "desc": "初试云雨情，温柔和顺体贴入微，苦劝宝玉走正途。"},
    {"source": "贾宝玉", "target": "麝月", "relation": "主仆忠守 / 终局相伴", "type": "master_servant", "desc": "大观园群芳散尽后唯一常伴宝玉身侧的怡红院知心侍女。"},
    {"source": "贾宝玉", "target": "茗烟", "relation": "主仆心腹 / 书童至交", "type": "master_servant", "desc": "最体贴宝玉心意的小厮，搜罗传奇秘本，随宝玉郊外偷祭金钏。"},
    {"source": "贾宝玉", "target": "北静王", "relation": "莫逆知己 / 赠鹡鸰珠", "type": "friendship", "desc": "水溶王爷折节下交，一见如故，赠宝玉皇室御赐鹡鸰香念珠。"},
    {"source": "贾宝玉", "target": "秦钟", "relation": "结义知己 / 同窗好友", "type": "friendship", "desc": "情投意合惺惺相惜，共读家塾，秦钟夭亡令宝玉恸哭伤神。"},
    {"source": "贾宝玉", "target": "柳湘莲", "relation": "结义兄弟 / 侠骨豪情", "type": "friendship", "desc": "冷面二郎侠骨柔肠，宝玉极尽推崇赞誉之江湖至交。"},
    {"source": "贾宝玉", "target": "蒋玉菡", "relation": "莫逆之交 / 赠汗巾定盟", "type": "friendship", "desc": "神交已久初见倾心，互赠大红茜香罗汗巾与松花汗巾。"},
    {"source": "贾宝玉", "target": "贾环", "relation": "庶弟 / 嫉恨毒害", "type": "conflict", "desc": "贾环嫉恨宝玉受宠，恶意推翻热油烛台烫伤宝玉面容。"},

    # 黛玉核心
    {"source": "林黛玉", "target": "贾母", "relation": "外祖孙至亲 / 慈爱倍至", "type": "blood", "desc": "贾母爱女贾敏之唯一骨肉，贾母接来身边视为心肝，与宝玉同日寝食。"},
    {"source": "林黛玉", "target": "林如海", "relation": "父女骨肉", "type": "blood", "desc": "巡盐御史如海深爱独女，临终托孤于荣国府贾母。"},
    {"source": "林黛玉", "target": "紫鹃", "relation": "主仆知己 / 患难相依", "type": "master_servant", "desc": "贾母所赐大丫鬟，与黛玉相依为命胜似亲姐妹，情辞试忙玉护卫黛玉终生。"},
    {"source": "林黛玉", "target": "薛宝钗", "relation": "金兰契友 / 互解心结", "type": "friendship", "desc": "由最初的金玉芥蒂到秋雨长夜促膝长谈，互赠燕窝互为金兰知己。"},
    {"source": "林黛玉", "target": "贾雨村", "relation": "师生 / 启蒙恩师", "type": "friendship", "desc": "贾雨村落魄时在扬州任林府西宾，为黛玉发蒙启蒙。"},
    {"source": "林黛玉", "target": "王熙凤", "relation": "表姑嫂 / 谐谑调笑", "type": "blood", "desc": "凤姐深爱黛玉灵动机敏，“吃了我们家茶怎么还不给我们家做媳妇”。"},
    {"source": "林黛玉", "target": "香菱", "relation": "师生知音 / 授诗之恩", "type": "friendship", "desc": "黛玉在潇湘馆悉心指导香菱研读唐诗，香菱痴心苦吟终得佳作。"},

    # 宝钗核心
    {"source": "薛宝钗", "target": "薛姨妈", "relation": "母女至亲 / 孝女依怙", "type": "blood", "desc": "薛姨妈主心骨与依靠，沉稳持家体贴母亲孤苦。"},
    {"source": "薛宝钗", "target": "薛蟠", "relation": "兄妹骨肉 / 苦口劝诫", "type": "blood", "desc": "屡次规劝鲁莽霸道的长兄，薛蟠虽劣但极敬爱信服胞妹。"},
    {"source": "薛宝钗", "target": "薛蝌", "relation": "堂姐弟", "type": "blood", "desc": "同气连枝，全力促成薛蝌与邢岫烟的天作良缘。"},
    {"source": "薛宝钗", "target": "薛宝琴", "relation": "堂姐妹 / 雅重友爱", "type": "blood", "desc": "宝琴才貌双全备受贾母宠爱，宝钗坦荡爱护毫无嫉妒之心。"},
    {"source": "薛宝钗", "target": "莺儿", "relation": "主仆相依 / 心腹大丫鬟", "type": "master_servant", "desc": "自幼相随的心腹丫鬟，打花线络子巧手，助言金玉良缘。"},
    {"source": "薛宝钗", "target": "王夫人", "relation": "姨甥骨肉 / 属意儿媳", "type": "blood", "desc": "王夫人极度满意的正统儿媳人选，金玉良缘幕后坚定推手。"},
    {"source": "薛宝钗", "target": "史湘云", "relation": "闺阁密友 / 倾心相待", "type": "friendship", "desc": "湘云最崇敬信赖宝钗姐姐，蘅芜苑夜话代拟螃蟹宴。"},

    # 熙凤贾琏核心
    {"source": "王熙凤", "target": "贾琏", "relation": "结发夫妻 / 恩怨反目", "type": "marriage", "desc": "同掌荣府家务，凤姐强势弄权，贾琏偷腥纳妾，最终一从二令三人木。"},
    {"source": "王熙凤", "target": "贾巧姐", "relation": "母女骨肉", "type": "blood", "desc": "凤姐独女，托刘姥姥起名压邪，临终托孤于刘姥姥救难。"},
    {"source": "王熙凤", "target": "平儿", "relation": "主仆心腹 / 左右膀臂", "type": "master_servant", "desc": "凤姐唯一的陪房心腹大丫鬟与贾琏侍妾，处事公正常为凤姐补偏救弊。"},
    {"source": "王熙凤", "target": "贾母", "relation": "孙媳侍奉 / 承欢膝下", "type": "blood", "desc": "言笑晏晏极擅承欢老太太膝下，贾母最离不得的开心果与治家铁腕。"},
    {"source": "王熙凤", "target": "王夫人", "relation": "姑侄至亲 / 管家授权", "type": "blood", "desc": "王夫人的亲侄女，受二房主母委托全面协理荣国府日常内政。"},
    {"source": "王熙凤", "target": "秦可卿", "relation": "叔婶至交 / 闺阁密友", "type": "friendship", "desc": "宁荣二府最说得来知心话的两位当家少奶奶，秦氏临终托梦警示。"},
    {"source": "王熙凤", "target": "尤二姐", "relation": "妻妾死敌 / 借剑杀人", "type": "conflict", "desc": "凤姐恨贾琏偷娶外室，假意迎入荣府，暗中借秋桐与家奴折磨致其吞金。"},
    {"source": "王熙凤", "target": "刘姥姥", "relation": "济贫恩客 / 托孤之恩", "type": "friendship", "desc": "一进荣府赐银二十两，二进荣府奉若座上宾，伏下巧姐万难搭救之大恩。"},
    {"source": "王熙凤", "target": "贾瑞", "relation": "族弟纠缠 / 毒设相思局", "type": "conflict", "desc": "贾瑞觊觎美色起淫心，凤姐设连环相思苦肉计将其活活惩治而亡。"},
    {"source": "贾琏", "target": "尤二姐", "relation": "偷娶外室 / 钟情爱妾", "type": "marriage", "desc": "国孝家孝中偷娶外宅二房，发誓白头偕老，二姐惨死令贾琏痛悔万分。"},
    {"source": "贾琏", "target": "秋桐", "relation": "贾赦赐妾", "type": "marriage", "desc": "贾赦所赐侍妾，恃宠而骄，受凤姐挑唆百般辱骂虐待尤二姐。"},
    {"source": "贾琏", "target": "平儿", "relation": "通房侍妾 / 敬重爱惜", "type": "marriage", "desc": "贾琏对平儿又敬又爱，常感叹平儿仁善体贴远胜凤姐。"},
    {"source": "贾琏", "target": "贾赦", "relation": "父子骨肉 / 威逼杖打", "type": "blood", "desc": "贾赦因石呆子古扇之事将贾琏打得皮开肉绽，父子关系冷漠严酷。"},

    # 贾母与两房
    {"source": "贾母", "target": "贾政", "relation": "母子至亲 / 偏爱二房", "type": "blood", "desc": "母子敦厚敬顺，贾母多依二房而居，政公至孝恪守晨昏定省。"},
    {"source": "贾母", "target": "贾赦", "relation": "母子生隙 / 纳鸳鸯嫌隙", "type": "blood", "desc": "贾赦荒唐妄图强纳鸳鸯为妾，惹得贾母大怒痛斥其居心不良。"},
    {"source": "贾母", "target": "鸳鸯", "relation": "主仆至信 / 左右膀臂", "type": "master_servant", "desc": "贾母最信赖倚重的第一贴身大丫鬟，管钥匙掌钱箱，誓死相随。"},
    {"source": "贾母", "target": "刘姥姥", "relation": "贵贱同欢 / 宴游大观园", "type": "friendship", "desc": "同为高寿老妪，贾母喜其真诚朴实，携手同游大观园畅饮行令。"},

    # 贾政王夫人房
    {"source": "贾政", "target": "王夫人", "relation": "结发夫妻 / 荣府正席", "type": "marriage", "desc": "相敬如宾，共同主理荣国府二房宗祠与后院大局。"},
    {"source": "贾政", "target": "赵姨娘", "relation": "侍妾宠侍", "type": "marriage", "desc": "生下探春与贾环，贾政常宿其房，虽鄙其浅陋却颇多眷顾。"},
    {"source": "贾政", "target": "贾探春", "relation": "父女骨肉 / 赏识器重", "type": "blood", "desc": "贾政深爱探春才学气度，探春远嫁和亲政公万般不舍。"},
    {"source": "贾政", "target": "贾兰", "relation": "祖孙骨肉 / 科举希望", "type": "blood", "desc": "对长孙贾兰勤学苦读寄予厚望，贾府败落后兰儿金榜题名。"},
    {"source": "王夫人", "target": "赵姨娘", "relation": "主奴正庶 / 宿怨暗防", "type": "conflict", "desc": "尊卑森严，王夫人对赵姨娘的狭隘挑唆深恶痛绝。"},
    {"source": "王夫人", "target": "金钏", "relation": "主仆嫌隙 / 撵逐致死", "type": "conflict", "desc": "见金钏与宝玉耳语调笑，盛怒之下掌掴并逐出，酿成投井大悲剧。"},
    {"source": "王夫人", "target": "晴雯", "relation": "主奴嫌恶 / 抄检逐亡", "type": "conflict", "desc": "恶其眉眼像黛玉且风流灵巧，病中强行从炕上拖出撵走，致晴雯冤逝。"},
    {"source": "李纨", "target": "贾兰", "relation": "母子相依 / 课子成才", "type": "blood", "desc": "孀居稻香村茹苦含辛，一心课子读书，终得爵禄诰命。"},

    # 宁国府系统
    {"source": "贾敬", "target": "贾珍", "relation": "父子骨肉 / 放任不管", "type": "blood", "desc": "贾敬弃家外宿玄真观修道炼丹，放任贾珍在宁国府胡作非为。"},
    {"source": "贾敬", "target": "贾惜春", "relation": "父女骨肉 / 弃女自修", "type": "blood", "desc": "自幼对胞女不闻不问，促成惜春孤僻冷漠看破尘世的心境。"},
    {"source": "贾珍", "target": "尤氏", "relation": "结发夫妻 / 尊卑从顺", "type": "marriage", "desc": "贾珍专横跋扈纵情声色，尤氏性格懦弱无能管束。"},
    {"source": "贾珍", "target": "贾蓉", "relation": "父子骨肉 / 严苛纵虐", "type": "blood", "desc": "贾珍动辄命家奴唾面辱骂贾蓉，父子同流合污声色犬马。"},
    {"source": "贾珍", "target": "秦可卿", "relation": "翁媳逆伦 / 爬灰遗恨", "type": "conflict", "desc": "宁国府最不可言说的造衅根源，天香楼孽情致秦氏悬梁自缢。"},
    {"source": "贾蓉", "target": "秦可卿", "relation": "结发夫妻 / 同床异梦", "type": "marriage", "desc": "门当户对貌合神离，秦氏重病早逝贾蓉毫无悲戚之色。"},
    {"source": "贾珍", "target": "焦大", "relation": "主奴恩怨 / 醉骂揭丑", "type": "conflict", "desc": "老奴焦大仗功醉骂爬灰养小叔子，贾珍命人塞马粪捆绑折磨。"},
    {"source": "贾蔷", "target": "龄官", "relation": "知心情侣 / 画蔷相守", "type": "love", "desc": "大观园中最纯粹真挚的爱情之一，买雀放生，至情至性相伴相知。"},

    # 尤氏姐妹与情仇
    {"source": "尤三姐", "target": "柳湘莲", "relation": "金石痴情 / 刎颈殉道", "type": "love", "desc": "苦恋柳湘莲五年甘守清白，因退婚索剑伤心欲绝，拔鸳鸯剑自刎明志。"},
    {"source": "柳湘莲", "target": "薛蟠", "relation": "不打不相识 / 结拜兄弟", "type": "friendship", "desc": "芦苇塘痛打调戏自己的呆霸王，后在途中搭救薛蟠脱险，结为生死兄弟。"},

    # 迎春探春侍女及其他
    {"source": "贾迎春", "target": "孙绍祖", "relation": "夫妻婚姻 / 羊入虎口", "type": "marriage", "desc": "贾赦为抵五千两银强嫁迎春，孙绍祖百般凌虐家暴，迎春一年夭折。"},
    {"source": "贾迎春", "target": "司棋", "relation": "主仆相随 / 懦弱不保", "type": "master_servant", "desc": "司棋性格刚烈敢爱敢恨，犯事后迎春虽惜之却懦弱不敢开口求情。"},
    {"source": "贾探春", "target": "赵姨娘", "relation": "母女至亲 / 宗法裂隙", "type": "blood", "desc": "探春恪守宗法只认王夫人为母，屡遭赵姨娘无理胡闹，痛心疾首。"},
    {"source": "贾探春", "target": "侍书", "relation": "主仆同心 / 舌战群仆", "type": "master_servant", "desc": "探春调教得力之贴身侍女，大观园抄检时忠勇护主反唇相讥。"},
    {"source": "贾惜春", "target": "入画", "relation": "主仆绝义 / 冷心逐撵", "type": "master_servant", "desc": "入画私藏兄长之赏赐物遭搜出，惜春为自保冰清决绝命人撵出。"},
    {"source": "香菱", "target": "薛蟠", "relation": "强占为妾 / 饱受凌虐", "type": "marriage", "desc": "冯渊被薛蟠打死后强占香菱为妾，薛蟠喜新厌旧后任由夏金桂残害。"},
    {"source": "香菱", "target": "夏金桂", "relation": "妻妾天敌 / 栽赃鸩杀", "type": "conflict", "desc": "夏金桂狠毒霸道改其名为秋菱，百般毒打栽赃，反遭天谴暴毙。"},
    {"source": "薛蝌", "target": "邢岫烟", "relation": "天作之合 / 结发夫妻", "type": "marriage", "desc": "大观园中品貌最端重登对的一对佳偶，薛宝钗与贾母鼎力促成。"},
    {"source": "贾芸", "target": "小红", "relation": "遗帕定情 / 患难夫妻", "type": "love", "desc": "手帕传情私定终身，凤姐落难时二人义薄云天往狱神庙相救。"},
    {"source": "贾雨村", "target": "甄士隐", "relation": "受恩背恩 / 葫芦断案", "type": "conflict", "desc": "当年受士隐赠银考中进士，后审薛蟠打死冯渊案见英莲却不救。"},
    {"source": "甄士隐", "target": "香菱", "relation": "父女骨肉 / 元宵相失", "type": "blood", "desc": "士隐独生爱女英莲，元宵观灯遭拐子拐走，自此骨肉永诀。"},
    {"source": "跛足道人", "target": "甄士隐", "relation": "度化仙缘 / 顿悟解歌", "type": "friendship", "desc": "唱《好了歌》引渡看破红尘的甄士隐，士隐大彻大悟作注随之羽化。"},
    {"source": "刘姥姥", "target": "贾巧姐", "relation": "赐名结缘 / 舍命搭救", "type": "friendship", "desc": "当年取名巧姐，贾府抄家巧姐被狠舅奸兄拐卖入烟花，刘姥姥倾家荡产赎回。"}
]

# Merge with person-to-person edges from original honglou.json
# Map raw edges
print(f"Adding raw edges from honglou.json...")
raw_nodes_map = {n['id']: n for n in raw_nodes}
added_pairs = set((r['source'], r['target']) for r in core_relationships)
for r in core_relationships:
    added_pairs.add((r['target'], r['source']))

raw_added_count = 0
for e in raw_edges:
    fn = raw_nodes_map.get(e['from'])
    tn = raw_nodes_map.get(e['to'])
    if not fn or not tn:
        continue
    fl = fn.get('label', '').strip()
    tl = tn.get('label', '').strip()
    if fl in all_characters and tl in all_characters and fl != tl:
        if (fl, tl) not in added_pairs:
            el = e.get('label', '关联')
            
            # Map type
            rtype = "friendship"
            if el in ['父亲', '母亲', '儿子', '女儿', '哥哥', '姐姐', '弟弟', '妹妹', '祖父', '祖母', '孙子', '外孙女', '姑侄', '叔侄', '同宗']:
                rtype = "blood"
            elif el in ['丈夫', '妻子', '姬妾', '继室', '岳父', '女婿']:
                rtype = "marriage"
            elif el in ['仆人', '跟班', '奶妈', '贴身丫鬟']:
                rtype = "master_servant"
            elif el in ['喜欢', '暗恋', '情人', '前世']:
                rtype = "love"
            
            core_relationships.append({
                "source": fl,
                "target": tl,
                "relation": el,
                "type": rtype,
                "desc": f"{fl} 与 {tl} 在小说及87版电视剧中的《{el}》人物关系链。"
            })
            added_pairs.add((fl, tl))
            added_pairs.add((tl, fl))
            raw_added_count += 1

print(f"Added {raw_added_count} additional relationship edges from raw data.")
print(f"Total relationships: {len(core_relationships)}")

# Build final output dataset
final_dataset = {
    "metadata": {
        "title": "87版《红楼梦》电视剧人物关系图谱",
        "subtitle": "经典永恒 · 灵动交互 · 宗族全景",
        "version": "2.0.0",
        "description": "基于1987版电视剧《红楼梦》打造的交互式全景人物关系知识图谱，支持力导向物理弹簧拉伸、节点自由拖拽、谱系多重视图切换与人物生平手卷检索。",
        "totalCharacters": len(all_characters),
        "totalRelationships": len(core_relationships),
        "author": "Antigravity Assistant",
        "createdDate": "2026-11-20"
    },
    "clans": CLANS,
    "relationTypes": RELATION_TYPES,
    "nodes": list(all_characters.values()),
    "links": core_relationships
}

# Write to JSON
with open('data/honglou_data.json', 'w', encoding='utf-8') as f:
    json.dump(final_dataset, f, ensure_ascii=False, indent=2)

# Write to JS (window.HONGLOU_DATA) for zero-CORS file:// protocol support
with open('data/honglou_data.js', 'w', encoding='utf-8') as f:
    f.write("window.HONGLOU_DATA = ")
    json.dump(final_dataset, f, ensure_ascii=False, indent=2)
    f.write(";\n")

print("Generated data/honglou_data.json and data/honglou_data.js successfully!")
