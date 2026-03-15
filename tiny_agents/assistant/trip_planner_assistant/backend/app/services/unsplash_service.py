"""Unsplash图片服务 - 优化版"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
import time
from typing import List, Optional, Dict, Tuple
from difflib import SequenceMatcher
from ..config import get_settings


# ========== 景点类型 → 搜索关键词映射 ==========
TYPE_KEYWORDS: Dict[str, List[str]] = {
    "自然风光": ["nature landscape scenic", "natural scenery", "landscape photography"],
    "历史文化": ["ancient historical heritage", "historical site", "cultural heritage"],
    "现代建筑": ["modern architecture skyline", "contemporary building", "cityscape"],
    "古镇": ["ancient town water village", "traditional village", "old town China"],
    "海滩": ["tropical beach coastline", "seaside beach", "coastal scenery"],
    "山水": ["mountain lake landscape", "mountain scenery", "river landscape"],
    "寺庙": ["Buddhist temple Chinese", "ancient temple", "temple architecture"],
    "园林": ["Chinese garden classical", "traditional garden", "Suzhou garden"],
    "博物馆": ["museum exhibition", "art gallery", "cultural museum"],
    "公园": ["public park Chinese", "urban park", "garden landscape"],
    "美食": ["Chinese food cuisine", "local delicacies", "food street"],
    "夜景": ["night view cityscape", "night lights", "illumination"],
}

# ========== 旅行图片备用源 ==========
FALLBACK_SOURCES = [
    "https://source.unsplash.com/1600x900/?{query},travel,china",
    "https://loremflickr.com/1600/900/{query},travel,tourism",
]

# ========== 图片缓存机制 ==========
_image_cache: Dict[Tuple[str, str], Tuple[str, float]] = {}  # {(name, city): (url, timestamp)}
CACHE_EXPIRE_HOURS = 24


# ========== 城市名称映射 ==========
CITY_NAME_MAPPING: Dict[str, str] = {
    "北京": "Beijing",
    "上海": "Shanghai",
    "广州": "Guangzhou",
    "深圳": "Shenzhen",
    "成都": "Chengdu",
    "杭州": "Hangzhou",
    "西安": "Xi'an",
    "南京": "Nanjing",
    "苏州": "Suzhou",
    "重庆": "Chongqing",
    "武汉": "Wuhan",
    "厦门": "Xiamen",
    "青岛": "Qingdao",
    "大连": "Dalian",
    "三亚": "Sanya",
    "丽江": "Lijiang",
    "拉萨": "Lhasa",
    "桂林": "Guilin",
    "张家界": "Zhangjiajie",
    "黄山": "Huangshan",
    "九寨沟": "Jiuzhaigou",
    "乌鲁木齐": "Urumqi",
    "哈尔滨": "Harbin",
    "沈阳": "Shenyang",
    "天津": "Tianjin",
    "郑州": "Zhengzhou",
    "长沙": "Changsha",
    "昆明": "Kunming",
    "贵阳": "Guiyang",
    "兰州": "Lanzhou",
    "西宁": "Xining",
    "银川": "Yinchuan",
    "呼和浩特": "Hohhot",
    "太原": "Taiyuan",
    "石家庄": "Shijiazhuang",
    "济南": "Jinan",
    "合肥": "Hefei",
    "南昌": "Nanchang",
    "福州": "Fuzhou",
    "南宁": "Nanning",
    "海口": "Haikou",
    "澳门": "Macau",
    "香港": "Hong Kong",
    "台北": "Taipei",
}

# ========== 景点名称映射（扩展版）==========
ATTRACTION_NAME_MAPPING: Dict[str, str] = {
    # 北京景点
    "故宫": "Forbidden City",
    "故宫博物院": "Forbidden City",
    "天安门": "Tiananmen Square",
    "天安门广场": "Tiananmen Square",
    "颐和园": "Summer Palace Beijing",
    "天坛": "Temple of Heaven Beijing",
    "天坛公园": "Temple of Heaven Beijing",
    "长城": "Great Wall of China",
    "八达岭长城": "Great Wall Badaling",
    "慕田峪长城": "Great Wall Mutianyu",
    "居庸关长城": "Great Wall Juyongguan",
    "十三陵": "Ming Tombs",
    "明十三陵": "Ming Tombs",
    "圆明园": "Old Summer Palace",
    "圆明园遗址": "Old Summer Palace",
    "北海公园": "Beihai Park Beijing",
    "景山公园": "Jingshan Park Beijing",
    "雍和宫": "Yonghe Temple Beijing",
    "雍和宫喇嘛庙": "Yonghe Temple Beijing",
    "国子监": "Confucius Temple Beijing",
    "孔庙": "Confucius Temple",
    "798艺术区": "798 Art Zone Beijing",
    "798": "798 Art Zone",
    "鸟巢": "Bird's Nest Stadium",
    "国家体育场": "Bird's Nest Stadium",
    "水立方": "Water Cube",
    "国家游泳中心": "Water Cube",
    "国家大剧院": "National Centre for the Performing Arts Beijing",
    "恭王府": "Prince Kung's Mansion",
    "什刹海": "Shichahai Lake Beijing",
    "什刹海风景区": "Shichahai",
    "南锣鼓巷": "Nanluoguxiang Alley",
    "南锣鼓巷": "Nanluoguxiang",
    "王府井": "Wangfujing Street",
    "王府井步行街": "Wangfujing Street",
    "三里屯": "Sanlitun Beijing",
    "五道口": "Wudaokou Beijing",
    "香山": "Fragrant Hills Beijing",
    "香山公园": "Fragrant Hills Beijing",
    "植物园": "Beijing Botanical Garden",

    # 上海景点
    "外滩": "The Bund Shanghai",
    "外滩风景区": "The Bund",
    "东方明珠": "Oriental Pearl Tower",
    "东方明珠塔": "Oriental Pearl Tower Shanghai",
    "上海中心": "Shanghai Tower",
    "上海中心大厦": "Shanghai Tower",
    "金茂大厦": "Jin Mao Tower Shanghai",
    "环球金融中心": "Shanghai World Financial Center",
    "上海环球金融中心": "Shanghai World Financial Center",
    "豫园": "Yu Garden Shanghai",
    "城隍庙": "City God Temple Shanghai",
    "老城隍庙": "City God Temple",
    "南京路": "Nanjing Road Shanghai",
    "南京路步行街": "Nanjing Road",
    "田子坊": "Tianzifang Shanghai",
    "新天地": "Xintiandi Shanghai",
    "迪士尼": "Shanghai Disney Resort",
    "上海迪士尼": "Disneyland Shanghai",
    "上海迪士尼乐园": "Shanghai Disney",
    "武康路": "Wukang Road Shanghai",
    "思南公馆": "Sinan Mansions Shanghai",
    "多伦路": "Duolun Road Shanghai",
    "淮海路": "Huaihai Road Shanghai",
    "静安寺": "Jing'an Temple Shanghai",

    # 西安景点
    "兵马俑": "Terracotta Warriors",
    "秦始皇兵马俑": "Terracotta Army",
    "兵马俑博物馆": "Terracotta Warriors Museum",
    "大雁塔": "Big Wild Goose Pagoda",
    "大雁塔景区": "Big Wild Goose Pagoda Xi'an",
    "小雁塔": "Small Wild Goose Pagoda",
    "古城墙": "Xi'an City Wall",
    "西安城墙": "Ancient City Wall Xi'an",
    "钟楼": "Bell Tower Xi'an",
    "西安钟楼": "Xi'an Bell Tower",
    "鼓楼": "Drum Tower Xi'an",
    "西安鼓楼": "Xi'an Drum Tower",
    "华清宫": "Huaqing Palace Xi'an",
    "大唐芙蓉园": "Tang Paradise Xi'an",
    "回民街": "Muslim Quarter Xi'an",
    "回民街美食街": "Muslim Quarter",
    "大唐不夜城": "Great Tang All Day Mall",
    "华清池": "Huaqing Hot Springs",

    # 成都景点
    "大熊猫基地": "Chengdu Panda Base",
    "熊猫基地": "Chengdu Research Base of Giant Panda Breeding",
    "成都大熊猫繁育研究基地": "Chengdu Panda Base",
    "都江堰": "Dujiangyan Irrigation System",
    "都江堰景区": "Dujiangyan",
    "青城山": "Mount Qingcheng",
    "青城山景区": "Qingcheng Mountain",
    "武侯祠": "Wuhou Shrine Chengdu",
    "锦里": "Jinli Ancient Street",
    "锦里古街": "Jinli Street Chengdu",
    "宽窄巷子": "Kuanzhai Alleys Chengdu",
    "春熙路": "Chunxi Road Chengdu",
    "杜甫草堂": "Du Fu Thatched Cottage",
    "杜甫草堂博物馆": "Du Fu Cottage",
    "青羊宫": "Qingyang Taoist Temple",
    "文殊院": "Wenshu Monastery Chengdu",

    # 杭州景点
    "西湖": "West Lake Hangzhou",
    "西湖风景区": "West Lake",
    "断桥": "Broken Bridge West Lake",
    "断桥残雪": "Broken Bridge",
    "雷峰塔": "Leifeng Pagoda Hangzhou",
    "灵隐寺": "Lingyin Temple Hangzhou",
    "飞来峰": "Feilai Peak Hangzhou",
    "三潭印月": "Three Pools Mirroring the Moon",
    "苏堤": "Su Causeway West Lake",
    "苏堤春晓": "Su Causeway",
    "白堤": "Bai Causeway West Lake",
    "宋城": "Song Dynasty Town Hangzhou",
    "杭州宋城": "Songcheng",
    "西溪湿地": "Xixi Wetland Hangzhou",
    "千岛湖": "Qiandao Lake Hangzhou",
    "六和塔": "Six Harmonies Pagoda",

    # 苏州景点
    "拙政园": "Humble Administrator's Garden",
    "拙政园": "Humble Administrator's Garden Suzhou",
    "狮子林": "Lion Grove Garden Suzhou",
    "虎丘": "Tiger Hill Suzhou",
    "虎丘塔": "Huqiu Tower",
    "寒山寺": "Hanshan Temple Suzhou",
    "留园": "Lingering Garden Suzhou",
    "网师园": "Master of Nets Garden",
    "沧浪亭": "Canglang Pavilion Suzhou",
    "耦园": "Couple's Garden Suzhou",
    "艺圃": "Garden of Cultivation Suzhou",
    "周庄": "Zhouzhuang Water Town",
    "同里": "Tongli Water Town Suzhou",
    "甪直": "Luzhi Ancient Town",

    # 南京景点
    "中山陵": "Sun Yat-sen Mausoleum",
    "中山陵风景区": "Sun Yat-sen Mausoleum Nanjing",
    "明孝陵": "Ming Xiaoling Tomb",
    "明孝陵博物馆": "Ming Tomb",
    "夫子庙": "Confucius Temple Nanjing",
    "夫子庙秦淮风光带": "Confucius Temple",
    "秦淮河": "Qinhuai River Nanjing",
    "秦淮风光带": "Qinhuai River",
    "总统府": "Nanjing Presidential Palace",
    "南京总统府": "Presidential Palace",
    "玄武湖": "Xuanwu Lake Nanjing",
    "鸡鸣寺": "Jiming Temple Nanjing",
    "南京长江大桥": "Nanjing Yangtze River Bridge",
    "雨花台": "Yuhuatai Memorial Park",
    "夫子庙": "Fuzimiao Nanjing",

    # 厦门景点
    "鼓浪屿": "Gulangyu Island",
    "鼓浪屿风景区": "Gulangyu",
    "南普陀寺": "Nanputuo Temple Xiamen",
    "厦门大学": "Xiamen University",
    "环岛路": "Island Ring Road Xiamen",
    "曾厝垵": "Zengcuoan Xiamen",
    "沙坡尾": "Shapowei Art Zone Xiamen",
    "中山路": "Zhongshan Road Xiamen",

    # 青岛景点
    "栈桥": "Zhanqiao Pier Qingdao",
    "青岛栈桥": "Zhanqiao Pier",
    "八大关": "Badaguan Scenic Area Qingdao",
    "八大关风景区": "Badaguan",
    "崂山": "Mount Lao Qingdao",
    "崂山风景区": "Laoshan Mountain",
    "五四广场": "May Fourth Square Qingdao",
    "金沙滩": "Golden Beach Qingdao",

    # 大连景点
    "星海广场": "Xinghai Square Dalian",
    "星海公园": "Xinghai Park",
    "老虎滩": "Laohutan Ocean Park Dalian",
    "老虎滩海洋公园": "Tiger Beach",
    "金石滩": "Golden Pebble Beach Dalian",
    "金石滩度假区": "Jinshitan",

    # 桂林景点
    "漓江": "Li River Guilin",
    "漓江风景区": "Li River",
    "象鼻山": "Elephant Trunk Hill Guilin",
    "阳朔": "Yangshuo Guilin",
    "阳朔西街": "West Street Yangshuo",
    "龙脊梯田": "Longji Rice Terraces",
    "龙脊梯田景区": "Dragon's Backbone Rice Terraces",
    "芦笛岩": "Reed Flute Cave Guilin",

    # 丽江景点
    "丽江古城": "Lijiang Old Town",
    "丽江": "Lijiang Ancient City",
    "玉龙雪山": "Jade Dragon Snow Mountain",
    "玉龙雪山景区": "Yulong Snow Mountain",
    "蓝月谷": "Blue Moon Valley Lijiang",
    "泸沽湖": "Lugu Lake",
    "束河古镇": "Shuhe Ancient Town Lijiang",

    # 三亚景点
    "亚龙湾": "Yalong Bay Sanya",
    "亚龙湾海滩": "Yalong Bay",
    "天涯海角": "Tianya Haijiao Sanya",
    "蜈支洲岛": "Wuzhizhou Island Sanya",
    "南山寺": "Nanshan Temple Sanya",
    "南山文化旅游区": "Nanshan Cultural Tourism Zone",
    "大东海": "Dadonghai Beach Sanya",
    "三亚湾": "Sanya Bay Beach",

    # 广州景点
    "广州塔": "Canton Tower",
    "小蛮腰": "Canton Tower Guangzhou",
    "陈家祠": "Chen Clan Ancestral Hall",
    "陈氏书院": "Chen Clan Academy",
    "沙面": "Shamian Island Guangzhou",
    "沙面岛": "Shamian Island",
    "白云山": "Baiyun Mountain Guangzhou",
    "越秀公园": "Yuexiu Park Guangzhou",
    "珠江夜游": "Pearl River Night Cruise",
    "长隆": "Chimelong Guangzhou",

    # 深圳景点
    "世界之窗": "Window of the World Shenzhen",
    "欢乐谷": "Happy Valley Shenzhen",
    "锦绣中华": "Splendid China Shenzhen",
    "大梅沙": "Dameisha Beach Shenzhen",
    "小梅沙": "Xiaomeisha Beach",
    "东部华侨城": "OCT East Shenzhen",
    "华侨城": "OCT Shenzhen",
    "大鹏所城": "Dapeng Fortress",
    "莲花山": "Lianhuashan Park Shenzhen",

    # 重庆景点
    "洪崖洞": "Hongya Cave Chongqing",
    "洪崖洞民俗风貌区": "Hongya Cave",
    "解放碑": "Jiefangbei Chongqing",
    "解放碑步行街": "Liberation Monument",
    "朝天门": "Chaotianmen Chongqing",
    "朝天门码头": "Chaotianmen Wharf",
    "磁器口": "Ciqikou Ancient Town",
    "磁器口古镇": "Ciqikou",
    "大足石刻": "Dazu Rock Carvings",
    "武隆天坑": "Wulong Karst",
    "南山": "Nanshan Mountain Chongqing",

    # 拉萨景点
    "布达拉宫": "Potala Palace Lhasa",
    "大昭寺": "Jokhang Temple Lhasa",
    "八廓街": "Barkhor Street Lhasa",
    "纳木错": "Namtso Lake Tibet",
    "色拉寺": "Sera Monastery Lhasa",
    "哲蚌寺": "Drepung Monastery",
    "罗布林卡": "Norbulingka Palace",

    # 黄山景点
    "黄山": "Huangshan Mountain",
    "黄山风景区": "Yellow Mountain",
    "迎客松": "Guest-Greeting Pine Huangshan",
    "西递宏村": "Xidi and Hongcun Villages",
    "西递": "Xidi Village Anhui",
    "宏村": "Hongcun Village",

    # 张家界景点
    "张家界": "Zhangjiajie National Forest Park",
    "张家界国家森林公园": "Zhangjiajie",
    "天门山": "Tianmen Mountain Zhangjiajie",
    "黄龙洞": "Yellow Dragon Cave Zhangjiajie",
    "玻璃栈道": "Glass Bridge Zhangjiajie",

    # 九寨沟景点
    "九寨沟": "Jiuzhaigou Valley",
    "九寨沟风景区": "Jiuzhaigou National Park",
    "黄龙": "Huanglong Scenic Valley",
    "黄龙风景区": "Huanglong Sichuan",

    # 乌鲁木齐景点
    "天山天池": "Heavenly Lake of Tianshan",
    "天池": "Tianchi Urumqi",
    "大巴扎": "Grand Bazaar Urumqi",
    "国际大巴扎": "Xinjiang International Grand Bazaar",

    # 哈尔滨景点
    "冰雪大世界": "Harbin Ice and Snow World",
    "圣索菲亚教堂": "Saint Sophia Cathedral Harbin",
    "中央大街": "Central Street Harbin",
    "太阳岛": "Sun Island Harbin",
    "松花江": "Songhua River Harbin",

    # 天津景点
    "天津之眼": "Tianjin Eye",
    "天津之眼摩天轮": "Tianjin Eye Ferris Wheel",
    "古文化街": "Ancient Culture Street Tianjin",
    "五大道": "Five Great Avenues Tianjin",
    "意大利风情区": "Italian Style Town Tianjin",
    "海河": "Haihe River Tianjin",
    "盘山": "Mount Pan Tianjin",
    "天津站": "Tianjin Railway Station",
    "津湾广场": "Jinwan Plaza Tianjin",
    "瓷房子": "Porcelain House Tianjin",
    "天津博物馆": "Tianjin Museum",
    "天津美术馆": "Tianjin Art Museum",
    "西开教堂": "Xikai Church Tianjin",
    "天津水上公园": "Water Park Tianjin",
    "劝业场": "Quanyechang Tianjin",
    "望海楼教堂": "Wanghailou Church Tianjin",
    "天津自然博物馆": "Tianjin Natural History Museum",
    "天津图书馆": "Tianjin Library",
    "天津大剧院": "Tianjin Grand Theatre",
    "滨海航母": "Binhai Aircraft Carrier Tianjin",
    "泰达航母主题公园": "Tianjin Aircraft Carrier Theme Park",
    "天津之眼夜景": "Tianjin Eye at Night",
    "意式风情街": "Italian Style Street Tianjin",
    "天津德式风琴区": "German Quarter Tianjin",

    # 武汉景点
    "黄鹤楼": "Yellow Crane Tower Wuhan",
    "东湖": "East Lake Wuhan",
    "户部巷": "Hubu Alley Wuhan",
    "武汉长江大桥": "Wuhan Yangtze River Bridge",
    "汉口江滩": "Hankou Riverfront",
    "晴川阁": "Qingchuan Pavilion",
    "归元寺": "Guiyuan Temple Wuhan",
    "武汉大学": "Wuhan University",
    "湖北省博物馆": "Hubei Provincial Museum",
    "木兰天池": "Mulan Tianchi Wuhan",
    "木兰草原": "Mulan Prairie Wuhan",
    "古琴台": "Guqin Tai Wuhan",
    "汉秀剧场": "Han Show Theater Wuhan",
    "武汉科技馆": "Wuhan Science Museum",
    "江汉路": "Jianghan Road Wuhan",
    "光谷": "Optics Valley Wuhan",
    "楚河汉街": "Chuhe Han Street Wuhan",
    "武汉园博园": "Wuhan Garden Expo Park",
    "武汉海昌极地海洋世界": "Wuhan Haichang Polar Ocean World",
    "东湖绿道": "East Lake Greenway Wuhan",
    "武汉植物园": "Wuhan Botanical Garden",
    "辛亥革命武昌起义纪念馆": "Wuhan 1911 Revolution Museum",
    "汉正街": "Hanzheng Street Wuhan",
    "武汉琴台大剧院": "Wuhan Qintai Grand Theatre",
    "昙华林": "Tan Hualin Wuhan",
    "武汉欢乐谷": "Wuhan Happy Valley",

    # 长沙景点
    "橘子洲": "Orange Isle Changsha",
    "岳麓山": "Mount Yuelu Changsha",
    "太平老街": "Taiping Old Street",
    "湖南省博物馆": "Hunan Museum",
    "马王堆汉墓": "Mawangdui Han Tombs",
    "天心阁": "Tianxin Pavilion Changsha",
    "火宫殿": "Huogongdian Changsha",
    "湘江": "Xiangjiang River Changsha",
    "岳麓书院": "Yuelu Academy Changsha",
    "爱晚亭": "Aiwan Pavilion Changsha",
    "湖南省立第一师范": "Hunan First Normal University",
    "长沙世界之窗": "Window of the World Changsha",
    "长沙海底世界": "Changsha Ocean World",
    "橘子洲头": "Orange Isle Head Changsha",
    "烈士公园": "Martyr Park Changsha",
    "石燕湖": "Shiyan Lake Changsha",
    "湖南省科技馆": "Hunan Science Museum",
    "长沙生态动物园": "Changsha Ecological Zoo",
    "湖南省植物园": "Hunan Botanical Garden",
    "洋湖湿地": "Yanghu Wetland Changsha",
    "长沙滨江文化园": "Changsha Riverside Cultural Park",
    "李自健美术馆": "Li Zijian Art Museum",
    "谢子龙影像艺术馆": "Xie Zilong Photography Art Museum",
    "长沙铜官窑": "Changsha Tongguan Kiln",
    "大围山": "Dawei Mountain Changsha",
    "沩山": "Weishan Mountain Changsha",

    # 昆明景点
    "石林": "Stone Forest Kunming",
    "滇池": "Dianchi Lake Kunming",
    "翠湖": "Green Lake Kunming",
    "云南民族村": "Yunnan Nationalities Village",
    "西山": "Western Hills Kunming",
    "大观楼": "Daguan Pavilion Kunming",
    "官渡古镇": "Guandu Ancient Town",
    "九乡溶洞": "Jiuxiang Caves Kunming",
    "金马碧鸡坊": "Jinma Biji Archway Kunming",
    "云南大学": "Yunnan University",
    "陆军讲武堂": "Military Academy Kunming",
    "圆通山": "Yuantong Mountain Kunming",
    "圆通寺": "Yuantong Temple Kunming",
    "昆明世博园": "World Expo Park Kunming",
    "轿子雪山": "Jiaozi Snow Mountain Kunming",
    "抚仙湖": "Fuxian Lake Kunming",
    "云南陆军讲武堂": "Yunnan Military Academy",
    "昆明动物研究所": "Kunming Institute of Zoology",
    "昆明植物研究所": "Kunming Institute of Botany",
    "斗南花市": "Dounan Flower Market Kunming",
    "昆明老街": "Kunming Old Street",
    "南屏街": "Nanping Street Kunming",
    "云南师范大学": "Yunnan Normal University",
    "西南联大旧址": "Former Site of Southwest Associated University",
    "阳宗海": "Yangzonghai Lake Kunming",
    "普者黑": "Puzhehei Kunming",

    # 郑州景点
    "少林寺": "Shaolin Temple",
    "嵩山": "Mount Song Dengfeng",
    "黄河风景区": "Yellow River Scenic Area",
    "河南博物院": "Henan Museum",
    "二七纪念塔": "Erqi Memorial Tower",
    "黄帝故里": "Yellow Emperor's Hometown",
    "嵩阳书院": "Songyang Academy",
    "中岳庙": "Zhongyue Temple",
    "郑州黄河游览区": "Yellow River Tourist Area Zhengzhou",
    "郑州动物园": "Zhengzhou Zoo",
    "人民公园": "People's Park Zhengzhou",
    "碧沙岗公园": "Bishagang Park Zhengzhou",
    "绿博园": "Green Expo Park Zhengzhou",
    "郑州植物园": "Zhengzhou Botanical Garden",
    "中原福塔": "Zhongyuan Tower Zhengzhou",
    "郑州方特": "Zhengzhou Fantawild",
    "郑州黄河大桥": "Zhengzhou Yellow River Bridge",
    "郑州商城遗址": "Zhengzhou Shang City Ruins",
    "郑州城隍庙": "Zhengzhou City God Temple",
    "郑州文庙": "Zhengzhou Confucius Temple",
    "郑州大河村遗址": "Zhengzhou Dahucun Ruins",
    "郑州世纪欢乐园": "Zhengzhou Century Park",
    "郑州树木园": "Zhengzhou Arboretum",
    "郑州洞林湖": "Zhengzhou Donglin Lake",
    "郑州黄帝故里拜祖大典": "Zhengzhou Yellow Emperor Ceremony",

    # 沈阳景点
    "沈阳故宫": "Shenyang Imperial Palace",
    "张氏帅府": "Marshal Zhang's Mansion",
    "昭陵": "Zhaoling Tomb Shenyang",
    "福陵": "Fuling Tomb Shenyang",
    "北陵公园": "Beiling Park Shenyang",
    "中街": "Zhongjie Street Shenyang",
    "沈阳世博园": "Shenyang Expo Garden",
    "棋盘山": "Qipan Mountain Shenyang",
    "沈阳森林动物园": "Shenyang Forest Zoo",
    "沈阳科学宫": "Shenyang Science Center",
    "辽宁省博物馆": "Liaoning Provincial Museum",
    "九一八历史博物馆": "September 18th History Museum",
    "浑河": "Hun River Shenyang",
    "南湖公园": "Nanhu Park Shenyang",
    "青年公园": "Qingnian Park Shenyang",
    "沈阳科技馆": "Shenyang Science Museum",
    "沈阳方特": "Shenyang Fantawild",
    "沈阳森林野生动物园": "Shenyang Forest Wildlife Park",
    "沈阳奥体中心": "Shenyang Olympic Center",
    "沈阳南湖公园": "Nanhu Park Shenyang",
    "沈阳万柳塘公园": "Wanliutang Park Shenyang",
    "沈阳北市场": "Beishi Market Shenyang",
    "沈阳太原街": "Taiyuan Street Shenyang",
    "沈阳中兴街": "Zhongxing Street Shenyang",
    "沈阳盛京大剧院": "Shengjing Grand Theatre Shenyang",

    # 南昌景点
    "滕王阁": "Tengwang Pavilion Nanchang",
    "八一起义纪念馆": "Bayi Uprising Memorial",
    "绳金塔": "Shengjin Pagoda Nanchang",
    "八大山人纪念馆": "Badashanren Memorial",
    "艾溪湖": "Aixi Lake Nanchang",
    "梅岭": "Meiling Mountain Nanchang",
    "秋水广场": "Qiushui Square",
    "南昌起义纪念馆": "Nanchang Uprising Memorial",
    "江西省博物馆": "Jiangxi Provincial Museum",
    "瑶湖": "Yao Lake Nanchang",
    "天香园": "Tianxiang Garden Nanchang",
    "厚田沙漠": "Houtian Desert Nanchang",
    "安义古村": "Anyi Ancient Village Nanchang",
    "凤凰沟": "Fenghuang Gou Nanchang",
    "南昌动物园": "Nanchang Zoo",
    "南昌之星": "Star of Nanchang",
    "南昌摩天轮": "Nanchang Ferris Wheel",
    "八一广场": "Bayi Square Nanchang",
    "南昌市博物馆": "Nanchang Museum",
    "南昌军事主题公园": "Nanchang Military Theme Park",    "象湖公园": "Xianghu Park Nanchang",
    "贤士湖": "Xianshi Lake Nanchang",
    "南昌瑶湖国家森林公园": "Nanchang Yaohu Forest Park",
    "南昌环球公园": "Nanchang Global Park",
    "南昌麦园": "Nanchang Wheat Garden",

    # 福州景点
    "三坊七巷": "Three Lanes and Seven Alleys",
    "鼓山": "Mount Drum Fuzhou",
    "西禅寺": "West Chan Temple Fuzhou",
    "福州森林公园": "Fuzhou Forest Park",
    "上下杭": "Shangxiahang Fuzhou",
    "乌塔": "Black Pagoda Fuzhou",
    "白塔": "White Pagoda Fuzhou",
    "闽江": "Minjiang River Fuzhou",
    "西湖公园": "West Lake Park Fuzhou",
    "福州西湖": "Fuzhou West Lake",
    "左海公园": "Zuohai Park Fuzhou",
    "金山寺": "Jinshan Temple Fuzhou",
    "马尾船政": "Mawei Shipyard Fuzhou",
    "福州国家森林公园": "Fuzhou National Forest Park",
    "青云山": "Qingyun Mountain Fuzhou",
    "十八重溪": "Shibachongxi Fuzhou",
    "福州三宝寺": "Fuzhou Sanbao Temple",
    "福州文庙": "Fuzhou Confucius Temple",
    "福州孔庙": "Fuzhou Confucian Temple",
    "福州旗山": "Fuzhou Qishan Mountain",
    "福州永泰云顶": "Fuzhou Yongtai Cloud Top",
    "福州鼓岭": "Fuzhou Guling Mountain Resort",
    "福州闽侯": "Fuzhou Minhou",
    "福州长乐": "Fuzhou Changle",
    "福州琅岐岛": "Fuzhou Langqi Island",
    "福州连江": "Fuzhou Lianjiang",

    # 贵阳景点
    "甲秀楼": "Jiaxiu Pavilion Guiyang",
    "黔灵山": "Qianlingshan Park Guiyang",
    "青岩古镇": "Qingyan Ancient Town",
    "花溪公园": "Huaxi Park Guiyang",
    "天河潭": "Tianhetan Guiyang",
    "贵阳森林公园": "Guiyang Forest Park",
    "香火岩": "Xianghuoyan Guiyang",
    "红枫湖": "Hongfeng Lake Guiyang",
    "百花湖": "Baihua Lake Guiyang",
    "南江大峡谷": "Nanjiang Grand Canyon Guiyang",
    "贵阳野生动物园": "Guiyang Wildlife Park",
    "河滨公园": "Riverside Park Guiyang",
    "观山湖公园": "Guanshan Lake Park Guiyang",
    "小车河湿地公园": "Xiaoche River Wetland Guiyang",
    "贵州博物馆": "Guizhou Museum",
    "贵州大学": "Guizhou University",
    "贵州民族大学": "Guizhou Minzu University",
    "贵阳孔学堂": "Guiyang Confucius Academy",
    "贵阳大剧院": "Guiyang Grand Theatre",
    "贵阳奥林匹克中心": "Guiyang Olympic Center",
    "贵阳阿哈湖": "Guiyang Aha Lake",
    "贵阳鱼洞峡": "Guiyang Yudong Gorge",
    "贵阳开阳": "Guiyang Kaiyang",
    "贵阳修文": "Guiyang Xiuwen",
    "贵阳息烽": "Guiyang Xifeng",

    # 南宁景点
    "青秀山": "Qingxiu Mountain Nanning",
    "南宁人民公园": "Nanning People's Park",
    "中国-东盟博览园": "China-ASEAN Expo Park",
    "扬美古镇": "Yangmei Ancient Town Nanning",
    "大龙湖": "Dalong Lake Nanning",
    "南宁邕江": "Yongjiang River Nanning",
    "南宁大桥": "Nanning Bridge",
    "广西民族博物馆": "Guangxi Nationalities Museum",
    "南湖公园": "Nanhu Park Nanning",
    "金花茶公园": "Jinhuacha Park Nanning",
    "狮子山公园": "Lion Mountain Park Nanning",
    "良凤江": "Liangfeng River Nanning",
    "伊岭岩": "Yiling Rock Nanning",
    "大明山": "Daming Mountain Nanning",
    "九龙瀑布": "Jiulong Waterfall Nanning",
    "南宁明月湖": "Nanning Mingyue Lake",
    "南宁相思湖": "Nanning Xiangsi Lake",
    "南宁心圩江": "Nanning Xinxu River",
    "南宁大唐天城": "Nanning Datang Tiancheng",
    "南宁民歌湖": "Nanning Folk Song Lake",
    "南宁国际会展中心": "Nanning International Convention Center",
    "南宁体育中心": "Nanning Sports Center",
    "南宁东盟商务区": "Nanning ASEAN Business District",
    "南宁五象新区": "Nanning Wuxiang New District",
    "南宁邕宁区": "Nanning Yongning District",

    # 合肥景点
    "三河古镇": "Sanhe Ancient Town",
    "巢湖": "Chaohu Lake Hefei",
    "包公园": "Bao Park Hefei",
    "李鸿章故居": "Li Hongzhang's Former Residence",
    "逍遥津公园": "Xiaoyaojin Park Hefei",
    "合肥野生动物园": "Hefei Wildlife Park",
    "大蜀山": "Dashu Mountain Hefei",
    "合肥植物园": "Hefei Botanical Garden",
    "合肥滨湖国家森林公园": "Hefei Binhu Forest Park",
    "安徽科技馆": "Anhui Science Museum",
    "合肥美术馆": "Hefei Art Museum",
    "天鹅湖": "Swan Lake Hefei",
    "紫蓬山": "Zipeng Mountain Hefei",
    "三河古镇风景区": "Sanhe Ancient Town Scenic Area",
    "合肥政务区": "Hefei Government Affairs District",
    "合肥滨湖新区": "Hefei Binhu New District",
    "合肥万达乐园": "Hefei Wanda Theme Park",
    "合肥海洋世界": "Hefei Ocean World",
    "合肥欢乐岛": "Hefei Happy Island",
    "合肥非遗园": "Hefei Intangible Cultural Heritage Park",
    "合肥野生动物园": "Hefei Wildlife Park",
    "合肥董铺水库": "Hefei Dongpu Reservoir",
    "合肥大房郢水库": "Hefei Dafangying Reservoir",
    "合肥三十岗": "Hefei Sanshigang",
    "安徽博物院": "Anhui Museum",

    # 海口景点
    "骑楼老街": "Qilou Old Street Haikou",
    "假日海滩": "Holiday Beach Haikou",
    "万绿园": "Wannvly Garden Haikou",
    "五公祠": "Five Officials Memorial Haikou",
    "海瑞墓": "Hairui Tomb Haikou",
    "海口湾": "Haikou Bay",
    "火山口公园": "Volcanic Cluster Park Haikou",
    "海南热带野生动植物园": "Hainan Tropical Wildlife Park",
    "海口钟楼": "Haikou Clock Tower",
    "世纪大桥": "Century Bridge Haikou",
    "海口观澜湖": "Mission Hills Haikou",
    "东寨港红树林": "Dongzhai Harbor Mangrove",
    "海口桂林洋": "Guilinyang Beach Haikou",
    "海口骑楼": "Haikou Qilou Architecture",
    "海口滨海公园": "Binhai Park Haikou",
    "海口白沙门公园": "Baishamen Park Haikou",
    "海口人民公园": "Haikou People's Park",
    "海口万绿园": "Haikou Wunlv Garden",
    "海口金牛岭公园": "Jinniuling Park Haikou",
    "海口西海岸": "Haikou West Coast",
    "海口东寨港": "Haikou Dongzhai Port",
    "海口桂林洋经济开发区": "Haikou Guilinyang Development Zone",
    "海口观澜湖度假区": "Haikou Mission Hills Resort",
    "海口南海大道": "Haikou Nanhai Avenue",
    "海口国贸": "Haikou International Trade Zone",

    # 西宁景点
    "塔尔寺": "Ta'er Monastery Xining",
    "青海湖": "Qinghai Lake",
    "日月山": "Riyue Mountain Xining",
    "东关清真大寺": "Dongguan Mosque Xining",
    "塔尔寺景区": "Kumbum Monastery",
    "北禅寺": "Beichan Temple Xining",
    "马步芳公馆": "Ma Bufang Mansion Xining",
    "西宁植物园": "Xining Botanical Garden",
    "西宁人民公园": "Xining People's Park",
    "湟水河": "Huangshui River Xining",
    "大通老爷山": "Laoye Mountain Datong",
    "贵德黄河": "Yellow River Guide",
    "循化撒拉族": "Xunhua Salar Ethnic Town",
    "西宁中心广场": "Xining Central Square",
    "西宁新宁广场": "Xining Xinning Square",
    "西宁麒麟湾": "Xining Qilin Bay",
    "西宁南川公园": "Xining Nanchuan Park",
    "西宁北川河": "Xining Beichuan River",
    "西宁湟中": "Xining Huangzhong",
    "西宁大通": "Xining Datong",
    "西宁湟源": "Xining Huangyuan",
    "西宁塔尔寺广场": "Xining Kumbum Monastery Square",
    "西宁南山公园": "Xining Nanshan Park",

    # 银川景点
    "西夏王陵": "Western Xia Tombs",
    "沙湖": "Sand Lake Yinchuan",
    "贺兰山": "Helan Mountains",
    "镇北堡影视城": "Zhenbeipu Film City",
    "青铜峡": "Qingtong Gxia Yinchuan",
    "银川鼓楼": "Yinchuan Drum Tower",
    "海宝塔": "Haibao Pagoda Yinchuan",
    "承天寺": "Chengtian Temple Yinchuan",
    "南关清真大寺": "Nanguan Mosque Yinchuan",
    "银川中山公园": "Zhongshan Park Yinchuan",
    "览山公园": "Lanshan Park Yinchuan",
    "鸣翠湖": "Mingcui Lake Yinchuan",
    "黄河军事文化博览园": "Yellow River Military Museum",
    "银川植物园": "Yinchuan Botanical Garden",
    "银川阅海公园": "Yinchuan Yuehai Park",
    "银川丽景湖": "Yinchuan Lijing Lake",
    "银川宝湖": "Yinchuan Bao Lake",
    "银川唐徕渠": "Yinchuan Tanglai Canal",
    "银川艾依河": "Yinchuan Aiyi River",
    "银川文化城": "Yinchuan Cultural City",
    "银川大阅城": "Yinchuan Dayue City",
    "银川金凤区": "Yinchuan Jinfeng District",
    "银川兴庆区": "Yinchuan Xingqing District",
    "银川贺兰县": "Yinchuan Helan County",

    # 呼和浩特景点
    "大召寺": "Dazhao Temple Hohhot",
    "内蒙古博物院": "Inner Mongolia Museum",
    "席力图召": "Xiletuzhao Temple",
    "哈素海": "Hasuhai Lake Hohhot",
    "蛮汗山": "Manhan Mountain",
    "昭君墓": "Wang Zhaojun Tomb",
    "大召无量寺": "Dazhao Temple Hohhot",
    "小召寺": "Xiaozhao Temple Hohhot",
    "呼和浩特市博物馆": "Hohhot Museum",
    "将军衙署": "General's Office Hohhot",
    "乌素图森林公园": "Wusutu Forest Park Hohhot",
    "哈达门": "Hadamen Mountain Hohhot",
    "老牛湾": "Laoniuwan Yellow River Bend",
    "辉腾锡勒草原": "Huitengxile Grassland",
    "呼和浩特大青山": "Hohhot Daqing Mountain",
    "呼和浩特哈拉沁": "Hohhot Halaqin",
    "呼和浩特和林格尔": "Hohhot Horinger",
    "呼和浩特清水河": "Hohhot Qingshui River",
    "呼和浩特武川": "Hohhot Wuchuan",
    "呼和浩特土默特": "Hohhot Tumed",
    "呼和浩特伊利草原": "Hohhot Yili Grassland",
    "呼和浩特蒙牛工业园": "Hohhot Mengniu Industrial Park",
    "呼和浩特如意开发区": "Hohhot Ruyi Development Zone",
    "呼和浩特金桥开发区": "Hohhot Jinqiao Development Zone",

    # 普通景点类别
    "寺庙": "Chinese Buddhist temple",
    "古寺": "ancient Chinese temple",
    "佛寺": "Buddhist temple China",
    "公园": "Chinese park garden",
    "森林公园": "forest park China",
    "国家公园": "national park China",
    "博物馆": "Chinese museum",
    "美术馆": "art museum China",
    "展览馆": "exhibition hall",
    "古镇": "ancient Chinese water town",
    "古村落": "traditional Chinese village",
    "古建筑": "ancient Chinese architecture",
    "山": "Chinese mountain landscape",
    "名山": "famous Chinese mountain",
    "山风景区": "Chinese scenic mountain",
    "湖": "Chinese lake scenery",
    "湖泊": "lake China",
    "江": "Chinese river scenery",
    "河流": "river landscape China",
    "海": "Chinese coastal scenery",
    "海滩": "beach China",
    "海滨": "seaside China",
    "景区": "Chinese scenic area",
    "景点": "Chinese landmark attraction",
    "风景区": "Chinese tourist attraction",
    "历史": "Chinese historical site",
    "文化": "Chinese cultural heritage",
    "历史文化": "Chinese history culture",
    "历史古迹": "ancient Chinese monument",
    "自然": "Chinese natural scenery",
    "自然风光": "China nature landscape",
    "现代建筑": "modern Chinese architecture",
    "地标": "Chinese landmark building",
    "美食街": "Chinese food street market",
    "步行街": "pedestrian street China",
    "商业街": "shopping street China",
}

# ========== 景点类别关键词映射（扩展版）==========
CATEGORY_TO_KEYWORDS: Dict[str, List[str]] = {
    "寺庙": ["Chinese Buddhist temple", "ancient Chinese temple", "Buddhist monastery", "traditional temple"],
    "古建筑": ["ancient Chinese architecture", "traditional Chinese building", "Chinese palace", "historic Chinese building"],
    "公园": ["Chinese garden", "traditional park", "landscape garden China", "classical Chinese garden"],
    "博物馆": ["Chinese museum", "art museum China", "history museum", "national museum China"],
    "美术馆": ["art gallery China", "Chinese art museum", "modern art museum"],
    "古镇": ["ancient Chinese water town", "traditional village", "old town China", "historic Chinese town"],
    "古村落": ["traditional Chinese village", "ancient village China", "rural China"],
    "山": ["Chinese mountain", "scenic mountain", "mountain landscape", "Chinese peak"],
    "名山": ["famous Chinese mountain", "sacred mountain China", "Chinese landmark mountain"],
    "湖": ["Chinese lake", "scenic lake", "traditional lake", "lake China"],
    "江": ["Chinese river", "scenic river", "river landscape China"],
    "海": ["Chinese beach", "coastal scenery", "ocean view China", "seaside China"],
    "海滩": ["tropical beach", "Chinese coastal beach", "sandy beach China"],
    "景点": ["Chinese landmark", "China scenery", "Chinese attraction", "famous Chinese site"],
    "历史文化": ["Chinese historical site", "ancient China", "Chinese heritage", "Chinese cultural site"],
    "自然风光": ["Chinese natural scenery", "China landscape", "nature China", "Chinese countryside"],
    "现代建筑": ["modern Chinese architecture", "China skyline", "modern building", "contemporary architecture China"],
    "美食街": ["Chinese food street", "night market China", "food market", "street food China"],
    "商业街": ["shopping street China", "commercial district", "Chinese shopping area"],
    "步行街": ["pedestrian street China", "walking street", "Chinese pedestrian mall"],
    "园林": ["Chinese garden", "classical garden", "traditional Chinese garden design"],
    "皇宫": ["Chinese imperial palace", "ancient palace China", "royal Chinese palace"],
    "陵墓": ["Chinese tomb", "ancient Chinese mausoleum", "imperial tomb China"],
    "塔": ["Chinese pagoda", "ancient Chinese tower", "Buddhist pagoda"],
    "桥": ["Chinese bridge", "ancient Chinese bridge", "traditional bridge China"],
}

# ========== 热门景点白名单（提高搜索权重）==========
POPULAR_ATTRACTIONS: Dict[str, float] = {
    # 北京
    "Forbidden City": 5.0,
    "Great Wall": 5.0,
    "Summer Palace": 4.5,
    "Temple of Heaven": 4.5,
    "Tiananmen Square": 4.0,
    "Bird's Nest": 4.0,
    # 西安
    "Terracotta Warriors": 5.0,
    "Terracotta Army": 5.0,
    "Big Wild Goose Pagoda": 4.5,
    "Xi'an City Wall": 4.0,
    # 上海
    "The Bund": 4.5,
    "Oriental Pearl Tower": 4.5,
    "Yu Garden": 4.0,
    # 杭州
    "West Lake": 4.5,
    "Lingyin Temple": 4.0,
    # 成都
    "Chengdu Panda Base": 5.0,
    "Dujiangyan": 4.5,
    "Mount Qingcheng": 4.5,
    # 桂林
    "Li River": 4.5,
    "Elephant Trunk Hill": 4.5,
    "Yangshuo": 4.0,
    # 丽江
    "Lijiang Old Town": 4.5,
    "Jade Dragon Snow Mountain": 5.0,
    # 拉萨
    "Potala Palace": 5.0,
    "Jokhang Temple": 4.5,
    # 三亚
    "Yalong Bay": 4.0,
    # 苏州
    "Humble Administrator's Garden": 4.5,
    "Lion Grove Garden": 4.0,
    # 张家界
    "Zhangjiajie": 5.0,
    "Tianmen Mountain": 4.5,
    # 黄山
    "Yellow Mountain": 5.0,
    # 九寨沟
    "Jiuzhaigou": 5.0,
    # 厦门
    "Gulangyu": 4.0,
    # 青岛
    "Zhanqiao Pier": 3.5,
    # 重庆
    "Hongya Cave": 4.0,
}

# 全局已使用图片URL记录（用于去重）
_used_image_urls: set = set()


class UnsplashService:
    """Unsplash图片服务类 - 优化版"""

    def __init__(self):
        """初始化服务"""
        settings = get_settings()
        self.access_key = settings.unsplash_access_key
        self.base_url = "https://api.unsplash.com"

        # 创建带有重试机制的 session
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _get_fallback_image(self, query: str, category: str = None) -> Optional[str]:
        """获取备用图片（当 Unsplash API 不可用时）- 使用旅行相关图源"""
        try:
            # 清理查询关键词
            clean_query = query.replace(" ", ",").replace("'", "")
            if category and category in TYPE_KEYWORDS:
                # 添加类别关键词
                type_kw = TYPE_KEYWORDS[category][0] if TYPE_KEYWORDS[category] else ""
                clean_query = f"{clean_query},{type_kw}"
            
            # 尝试使用 source.unsplash.com（更专业的旅行图源）
            url = f"https://source.unsplash.com/1600x900/?{clean_query}"
            
            # 验证 URL 是否可访问（简单检查）
            # 返回 URL，实际加载由前端处理
            return url
        except Exception:
            # 最后备用：使用 picsum 但带上旅行相关的 seed
            seed = hashlib.md5(query.encode()).hexdigest()[:8]
            return f"https://picsum.photos/seed/{seed}/800/600"

    def _translate_city_name(self, city: str) -> str:
        """翻译城市名称为英文"""
        if city in CITY_NAME_MAPPING:
            return CITY_NAME_MAPPING[city]

        # 尝试部分匹配
        for cn_city, en_city in CITY_NAME_MAPPING.items():
            if cn_city in city:
                return en_city

        return city  # 返回原名称（可能是英文或已翻译）

    def _translate_attraction_name(self, name: str) -> str:
        """翻译景点名称为英文搜索关键词"""
        # 首先尝试精确匹配
        if name in ATTRACTION_NAME_MAPPING:
            return ATTRACTION_NAME_MAPPING[name]

        # 尝试部分匹配（处理包含完整名称的情况）
        for cn_name, en_name in ATTRACTION_NAME_MAPPING.items():
            if cn_name in name:
                return en_name

        # 如果没有匹配，返回原名称（可能是英文或已翻译）
        return name

    def _calculate_relevance_score(self, photo: dict, search_keywords: List[str], attraction_name: str = None) -> float:
        """计算图片相关性评分 - 增强版"""
        score = 0.0
        description = photo.get("description", "") or ""
        alt_desc = photo.get("alt_description", "") or ""
        combined_text = f"{description} {alt_desc}".lower()

        # 1. 关键词匹配加分
        for keyword in search_keywords:
            keyword_lower = keyword.lower()
            # 完全匹配
            if keyword_lower in combined_text:
                score += 2.0
            # 部分匹配
            for word in keyword_lower.split():
                if word in combined_text and len(word) > 3:
                    score += 0.5

        # 2. 优先选择有描述的图片
        if description or alt_desc:
            score += 1.0

        # 3. 中国相关加权（关键优化）
        if "china" in combined_text or "chinese" in combined_text:
            score += 3.0

        # 4. 图片质量评分（基于Unsplash的likes数）
        likes = photo.get("likes", 0)
        score += min(likes / 1000, 2.0)  # 最多加2分

        # 5. 热门景点白名单加权
        if attraction_name:
            translated_name = self._translate_attraction_name(attraction_name)
            if translated_name in POPULAR_ATTRACTIONS:
                score += POPULAR_ATTRACTIONS[translated_name]

        # 6. 避免重复图片（如果已使用过，降低分数）
        photo_url = photo.get("urls", {}).get("regular", "")
        if photo_url in _used_image_urls:
            score -= 10.0  # 大幅降低重复图片分数

        return score

    def _get_search_queries(self, name: str, category: str = None, city: str = None) -> List[str]:
        """获取多个搜索查询策略（按优先级排序）- 优化版"""
        queries = []
        search_keywords = []

        # 翻译景点名称
        translated_name = self._translate_attraction_name(name)
        search_keywords.append(translated_name.lower())

        # 翻译城市名称
        translated_city = None
        if city:
            translated_city = self._translate_city_name(city)
            if translated_city != city:
                search_keywords.append(translated_city.lower())

        # === 优化后的查询策略 ===

        # 策略1: 城市 + 景点 + landmark（最高优先级）
        if city and translated_city:
            queries.append(f"{translated_city} {translated_name} landmark")
            queries.append(f"{translated_city} {translated_name}")

        # 策略2: 景点 + China + UNESCO/landmark
        queries.append(f"{translated_name} China UNESCO")
        queries.append(f"{translated_name} China landmark")

        # 策略3: 景点 + travel photography
        queries.append(f"{translated_name} travel photography")

        # 策略4: 使用 TYPE_KEYWORDS 进行类型匹配
        if category and category in TYPE_KEYWORDS:
            type_keywords = TYPE_KEYWORDS[category]
            queries.append(f"{translated_name} {type_keywords[0]}")
            # 城市 + 类型
            if translated_city:
                queries.append(f"{translated_city} {type_keywords[0]}")
            search_keywords.extend([kw.lower() for kw in type_keywords])

        # 策略5: 原始的类别关键词
        if category and category in CATEGORY_TO_KEYWORDS:
            keywords = CATEGORY_TO_KEYWORDS[category]
            queries.extend(keywords[:2])
            for kw in keywords[:2]:
                search_keywords.append(kw.lower())

        # 策略6: 城市 + 类别组合
        if translated_city and category and category in CATEGORY_TO_KEYWORDS:
            category_keyword = CATEGORY_TO_KEYWORDS[category][0]
            queries.append(f"{translated_city} {category_keyword}")

        # 策略7: 通用备选（保留）
        queries.append("famous Chinese landmark")
        queries.append("China travel destination")

        # 去重
        seen = set()
        unique_queries = []
        for q in queries:
            if q.lower() not in seen:
                seen.add(q.lower())
                unique_queries.append(q)

        return unique_queries, search_keywords

    def search_photos(self, query: str, per_page: int = 10) -> List[dict]:
        """搜索图片"""
        # 如果没有配置 API Key，使用备用方案
        if not self.access_key:
            print(f"⚠️ 未配置 Unsplash API Key，使用备用图片服务")
            photo_url = self._get_fallback_image(query)
            if photo_url:
                return [{
                    "id": "fallback",
                    "url": photo_url,
                    "description": query,
                    "photographer": "Picsum",
                    "score": 0.0
                }]
            return []

        try:
            url = f"{self.base_url}/search/photos"
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape",  # 横向图片更适合景点展示
                "content_filter": "high",     # 高质量内容
                "order_by": "relevant",       # 按相关性排序
                "client_id": self.access_key
            }

            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            photos = []
            for photo in results:
                photos.append({
                    "id": photo.get("id"),
                    "url": photo.get("urls", {}).get("regular"),
                    "thumb": photo.get("urls", {}).get("thumb"),
                    "description": photo.get("description") or photo.get("alt_description"),
                    "photographer": photo.get("user", {}).get("name"),
                    "score": 0.0  # 初始分数，后续计算
                })

            return photos

        except Exception as e:
            print(f"❌ Unsplash搜索失败: query='{query}', error={str(e)}")
            # 尝试使用备用方案
            photo_url = self._get_fallback_image(query)
            if photo_url:
                return [{
                    "id": "fallback",
                    "url": photo_url,
                    "description": query,
                    "photographer": "Picsum",
                    "score": 0.0
                }]
            return []

    def get_photo_url(self, name: str, category: str = None, city: str = None) -> Optional[str]:
        """
        获取单张图片URL - 使用多策略搜索 + 增强版相关性评分 + 缓存

        Args:
            name: 景点名称
            category: 景点类别（可选）
            city: 城市名称（可选）

        Returns:
            图片URL
        """
        # === 检查缓存 ===
        cache_key = (name, city or "")
        current_time = time.time()
        
        if cache_key in _image_cache:
            cached_url, cached_time = _image_cache[cache_key]
            # 检查是否过期
            if current_time - cached_time < CACHE_EXPIRE_HOURS * 3600:
                print(f"📦 使用缓存图片: '{name}'")
                return cached_url

        # 获取搜索策略和关键词
        queries, search_keywords = self._get_search_queries(name, category, city)

        print(f"🔍 搜索景点图片: name='{name}', city='{city}', category='{category}'")

        # 尝试每个查询策略
        for query in queries:
            photos = self.search_photos(query, per_page=10)  # 增加返回数量以提高选择质量

            if photos:
                # 计算相关性评分并排序（传递景点名称以进行热门景点加权）
                for photo in photos:
                    photo["score"] = self._calculate_relevance_score(photo, search_keywords, name)

                # 按评分排序
                photos.sort(key=lambda p: p["score"], reverse=True)

                # 选择评分最高的非重复图片
                for photo in photos:
                    if photo.get("url"):
                        # 记录并返回图片URL
                        _used_image_urls.add(photo["url"])
                        
                        # 存入缓存
                        _image_cache[cache_key] = (photo["url"], current_time)
                        
                        print(f"✅ 找到图片: '{name}' | 查询: '{query}' | 评分: {photo['score']:.1f} | 摄影师: {photo.get('photographer', 'N/A')}")
                        return photo.get("url")

        # 如果所有策略都失败，尝试备用方案
        print(f"⚠️ 尝试备用图片源: '{name}'")
        fallback_url = self._get_fallback_image(name, category)
        if fallback_url:
            _image_cache[cache_key] = (fallback_url, current_time)
            return fallback_url

        print(f"❌ 未找到 '{name}' 的图片（已尝试 {len(queries)} 个查询）")
        return None


# 全局服务实例
_unsplash_service = None


def get_unsplash_service() -> UnsplashService:
    """获取Unsplash服务实例(单例模式)"""
    global _unsplash_service

    if _unsplash_service is None:
        _unsplash_service = UnsplashService()

    return _unsplash_service
