import streamlit as st  # 웹 대시보드 UI 라이브러리
import folium  # 지도 및 마커 생성 라이브러리
from streamlit_folium import st_folium  # 포리움 지도를 스트림릿 웹 화면에 출력
from geopy.distance import geodesic  # 두 좌표 사이의 직선 거리 계산

# ==============================================================================
# 1. 웹사이트 타이틀 및 환경 세팅
# ==============================================================================
st.set_page_config(page_title="천안터미널 킬링타임 지도", layout="wide")
st.title("🚌 천안고속터미널 킬링타임(시간 때우기) 스팟 지도")
st.write("버스 대기 시간에 가볍게 혹은 편안하게 시간을 때울 수 있는 터미널 근처 맞춤형 지도입니다.")

# 고정 기준점: 천안고속터미널 좌표 설정
TERMINAL_LAT = 36.8197
TERMINAL_LNG = 127.1565

# ==============================================================================
# 2. 세션 상태(st.session_state) 데이터 초기화 (78개 전체 데이터 통합 및 일관화 완료 ⭐)
# ==============================================================================
if "killing_data" not in st.session_state:
    st.session_state["killing_data"] = [
        # === 카페 카테고리 데이터 (29개) ===
        {"name": "room816", "type": "카페", "time": "1시간 내외", "lat": 36.8181, "lng": 127.1585, "runtime": "12:00~22:00",
         "comment": "도보 3분 거리! 비주얼 대박인 딸기 케이크와 디저트 맛집입니다."},
        {"name": "치프 (CHIEF)", "type": "카페", "time": "1시간 내외", "lat": 36.8189, "lng": 127.1558,
         "runtime": "13:00~21:00", "comment": "지하 1층의 아늑하고 어두운 감성 인테리어에서 조용히 시간 때우기 좋습니다."},
        {"name": "세나클 신부점", "type": "카페", "time": "1시간 내외", "lat": 36.8188, "lng": 127.1556, "runtime": "14:00~01:00",
         "comment": "1, 2층으로 넓게 구성되어 있어 눈치 안 보고 편하게 대기할 수 있습니다."},
        {"name": "카페베니스", "type": "카페", "time": "30분 미만", "lat": 36.8186, "lng": 127.1559, "runtime": "12:00~21:00",
         "comment": "상하이 버터떡 등 독특하고 맛있는 베이커리 디저트가 가득합니다."},
        {"name": "커피센트", "type": "카페", "time": "1시간 내외", "lat": 36.8193, "lng": 127.1542, "runtime": "12:00~22:00",
         "comment": "소림원룸 1층에 위치한 차분한 분위기의 디저트 카페입니다."},
        {"name": "안다미로팬케이크 천안", "type": "카페", "time": "1시간 내외", "lat": 36.8175, "lng": 127.1568,
         "runtime": "12:00~21:30", "comment": "2층의 탁 트인 통창 뷰를 보며 퐁신퐁신한 수플레 팬케이크를 즐겨보세요."},
        {"name": "카페문", "type": "카페", "time": "1시간 내외", "lat": 36.8168, "lng": 127.1575, "runtime": "11:00~23:00",
         "comment": "12층 고층 스카이뷰! 천안 시내를 한눈에 내려다보며 힐링할 수 있는 스팟입니다."},
        {"name": "달콤한윤", "type": "카페", "time": "1시간 내외", "lat": 36.8162, "lng": 127.1581, "runtime": "12:00~22:00",
         "comment": "귀염뽀짝한 캐릭터 디저트와 음료가 있어 사진 찍으며 시간 보내기 좋습니다."},
        {"name": "아인스커피피자", "type": "카페", "time": "1시간 내외", "lat": 36.8169, "lng": 127.1572, "runtime": "11:00~23:00",
         "comment": "프라이빗한 룸 카페 스타일 공간이 있어 편하게 누워서 혹은 앉아서 쉴 수 있습니다."},
        {"name": "카페라고", "type": "카페", "time": "1시간 내외", "lat": 36.8170, "lng": 127.1569, "runtime": "12:00~22:00",
         "comment": "지하 1층에 숨겨진 아지트 같은 공간, 달달한 초코와 딸기 디저트가 맛있습니다."},
        {"name": "카페어젠", "type": "카페", "time": "1시간 내외", "lat": 36.8191, "lng": 127.1550, "runtime": "12:00~22:00",
         "comment": "두툼하고 부드러운 수플레와 말차 디저트 비주얼이 환상적입니다."},
        {"name": "달과 토끼", "type": "카페", "time": "1시간 내외", "lat": 36.8194, "lng": 127.1545, "runtime": "12:00~22:00",
         "comment": "화이트 톤의 깔끔하고 모던한 인테리어로 감성 충전하기 딱 좋은 공간입니다."},
        {"name": "눌 (NUL)", "type": "카페", "time": "30분 미만", "lat": 36.8186, "lng": 127.1559, "runtime": "12:00~22:00",
         "comment": "감각적인 로고와 힙한 무드의 붉은 벽돌 외관이 매력적인 카페입니다."},
        {"name": "엔457 (N457)", "type": "카페", "time": "30분 미만", "lat": 36.8186, "lng": 127.1559,
         "runtime": "12:00~22:00", "comment": "신부동 골목길 감성을 가득 담아 가볍게 커피 한잔 마시기 좋은 곳입니다."},
        {"name": "석정시", "type": "카페", "time": "1시간 내외", "lat": 36.8202, "lng": 127.1538, "runtime": "12:00~22:00",
         "comment": "정갈하고 고급스러운 인테리어 속에서 딸기 초코 산도 케이크를 즐길 수 있습니다."},
        {"name": "프로바이드 신부동카페", "type": "카페", "time": "1시간 내외", "lat": 36.8182, "lng": 127.1565,
         "runtime": "12:00~22:00", "comment": "꾸덕한 말차 바스크 치즈케이크와 크림 커피 조합이 일품인 2층 카페입니다."},
        {"name": "솔티당", "type": "카페", "time": "30분 미만", "lat": 36.8166, "lng": 127.1579, "runtime": "11:00~21:00",
         "comment": "빵순이·빵돌이 필수 코스! 고소한 베이커리 냄새 가득한 디저트 맛집입니다."},
        {"name": "브루어스커피 천안신부점", "type": "카페", "time": "30분 미만", "lat": 36.8181, "lng": 127.1566,
         "runtime": "12:00~21:00", "comment": "겉바속촉 까눌레와 휘낭시에 등 구움과자 러버들의 성지입니다."},
        {"name": "설빙 천안 신부점", "type": "카페", "time": "1시간 내외", "lat": 36.8175, "lng": 127.1568, "runtime": "11:30~22:30",
         "comment": "여럿이서 버스 기다릴 때 시원한 빙수 한 그릇 비우면서 수다 떨기 최고입니다."},
        {"name": "사오", "type": "카페", "time": "30분 미만", "lat": 36.8176, "lng": 127.1567, "runtime": "11:00~22:00",
         "comment": "전국 크로칸슈 맛집! 버스 타기 전 테이크아웃해서 가볍게 먹기 좋습니다."},
        {"name": "소셜스낵 신부점", "type": "카페", "time": "1시간 내외", "lat": 36.8202, "lng": 127.1538, "runtime": "11:30~21:30",
         "comment": "독일식 팬케이크 더치베이비와 폭신한 수플레가 유명한 디저트 카페입니다."},
        {"name": "나오트커피", "type": "카페", "time": "1시간 내외", "lat": 36.8188, "lng": 127.1557, "runtime": "12:00~22:00",
         "comment": "미니멀하고 깔끔한 화이트 인테리어에 포인트 디저트가 귀여운 인스타 감성 맛집입니다."},
        {"name": "코르크베이크바 천안", "type": "카페", "time": "1시간 내외", "lat": 36.8184, "lng": 127.1560,
         "runtime": "12:00~22:00", "comment": "야외 테라스 감성을 느끼며 달콤한 베이커리를 즐길 수 있는 힐링 스팟입니다."},
        {"name": "프럼브릿지 천안신부점", "type": "카페", "time": "1시간 내외", "lat": 36.8189, "lng": 127.1555,
         "runtime": "12:00~22:00", "comment": "이국적인 유럽풍 주택 개조 인테리어로, 어디서 찍어도 인생샷이 나오는 핫플입니다."},
        {"name": "머든 천안신부점", "type": "카페", "time": "2시간 이상", "lat": 36.8170, "lng": 127.1568, "runtime": "10:00~23:00",
         "comment": "조용하고 아늑한 분위기의 북카페 스타일로, 장시간 독서하며 대기하기 좋습니다."},
        {"name": "에이바우트커피 천안터미널점", "type": "카페", "time": "2시간 이상", "lat": 36.8167, "lng": 127.1571,
         "runtime": "07:00~23:00", "comment": "자리마다 콘센트가 잘 되어 있어 노트북 하거나 폰 충전하며 버스 기다리기 좋습니다."},
        {"name": "냥이싸롱", "type": "카페", "time": "2시간 이상", "lat": 36.8173, "lng": 127.1566, "runtime": "12:00~22:00",
         "comment": "귀여운 고양이들이 가득한 고양이 카페! 냥이들과 놀다 보면 시간 뚝딱입니다."},
        {"name": "카페 파비에", "type": "카페", "time": "1시간 내외", "lat": 36.8231, "lng": 127.1559, "runtime": "11:00~22:00",
         "comment": "벽면 가득 책이 꽂혀 있는 클래식한 서재 분위기에서 따뜻한 타르트를 맛볼 수 있습니다."},
        {"name": "카페보니", "type": "카페", "time": "1시간 내외", "lat": 36.8235, "lng": 127.1563, "runtime": "11:00~21:00",
         "comment": "조용하고 편안한 동네 카페 분위기에서 아늑하게 휴식을 취할 수 있습니다."},

        # === 굿즈 카테고리 데이터 (31개) ===
        {"name": "콩그레츄", "type": "굿즈", "time": "30분 미만", "lat": 36.8185, "lng": 127.1561, "runtime": "10:00~19:00",
         "comment": "이쁜 꽃다발과 케이크 전문점! 유인 10:00~19:00 / 무인 08:00~23:00 운영합니다."},
        {"name": "코브라피어싱 천안점", "type": "굿즈", "time": "30분 미만", "lat": 36.8191, "lng": 127.1553,
         "runtime": "09:30~21:30", "comment": "다양한 액세서리와 피어싱 종류를 구경하기 좋습니다."},
        {"name": "천안명문카메라수리센터", "type": "굿즈", "time": "30분 미만", "lat": 36.8195, "lng": 127.1542,
         "runtime": "09:00~19:00", "comment": "카메라 기기나 소품에 관심이 많다면 가볍게 둘러보기 좋습니다."},
        {"name": "고이비토 중고명품 천안신세계점", "type": "굿즈", "time": "30분 미만", "lat": 36.8203, "lng": 127.1550,
         "runtime": "11:00~19:00 (일 휴무)", "comment": "다양한 중고 명품 의류와 잡화를 구경하는 재미가 있습니다."},
        {"name": "아웃핏 남자옷가게 천안본점", "type": "굿즈", "time": "30분 미만", "lat": 36.8194, "lng": 127.1545,
         "runtime": "11:00~22:00", "comment": "트렌디한 남성의류가 가득한 옷가게로 가볍게 아이쇼핑하기 좋은 곳입니다."},
        {"name": "피어싱갤러리 신부점", "type": "굿즈", "time": "30분 미만", "lat": 36.8189, "lng": 127.1558,
         "runtime": "11:00~22:00", "comment": "예쁜 액세서리와 귀걸이, 피어싱 잡화가 깔끔하게 진열되어 있습니다."},
        {"name": "메이크온유", "type": "굿즈", "time": "30분 미만", "lat": 36.8192, "lng": 127.1552, "runtime": "12:00~20:00",
         "comment": "2층에 위치한 감성 인테리어 소품샵으로 아기자기한 방 꾸미기 소품이 가득합니다."},
        {"name": "을지문구", "type": "굿즈", "time": "30분 미만", "lat": 36.8215, "lng": 127.1530, "runtime": "09:00~21:00",
         "comment": "추억의 문구, 팬시용품점 분위기 속에서 다양한 필기구와 소품을 구경해 보세요."},
        {"name": "하우스 오브 하우스", "type": "굿즈", "time": "30분 미만", "lat": 36.8185, "lng": 127.1560,
         "runtime": "13:00~21:00", "comment": "반짝이는 주얼리, 목걸이, 귀걸이 등 패션 잡화를 전문으로 다루는 매장입니다."},
        {"name": "알파 천안법원점", "type": "굿즈", "time": "30분 미만", "lat": 36.8155, "lng": 127.1610, "runtime": "09:00~20:00",
         "comment": "대형 문구·팬시 전문점으로 시간 때우기용 노트나 필기구 구경에 딱입니다."},
        {"name": "하우스오브프룻", "type": "굿즈", "time": "30분 미만", "lat": 36.8152, "lng": 127.1615, "runtime": "10:00~20:00",
         "comment": "감성 가득한 프리미엄 과일 및 선물 기프트숍으로 패키지 디자인 구경하는 맛이 있습니다."},
        {"name": "파충류샵 반모리", "type": "굿즈", "time": "1시간 내외", "lat": 36.8151, "lng": 127.1618, "runtime": "12:00~21:00",
         "comment": "지하 1층 이색 스팟! 독특한 파충류와 관련 소품들을 볼 수 있는 신기한 공간입니다."},
        {"name": "타이거하우스", "type": "굿즈", "time": "1시간 내외", "lat": 36.8220, "lng": 127.1515, "runtime": "13:00~21:00",
         "comment": "유니크한 수입 구제 의류와 빈티지 소품들이 숨어있는 보물창고 같은 매장입니다."},
        {"name": "업리프팅빈티지 무인샵", "type": "굿즈", "time": "30분 미만", "lat": 36.8170, "lng": 127.1568, "runtime": "24시간 영업",
         "comment": "지하 1층에 위치한 무인 빈티지 옷가게로, 눈치 안 보고 편하게 옷 구경하기 좋습니다."},
        {"name": "더피빈티지", "type": "굿즈", "time": "30분 미만", "lat": 36.8172, "lng": 127.1567, "runtime": "13:00~20:00",
         "comment": "독특한 캐릭터 컵, 안경, 레트로한 인테리어 소품이 가득해 눈이 즐겁습니다."},
        {"name": "하이에이치알 (high HR)", "type": "굿즈", "time": "30분 미만", "lat": 36.8173, "lng": 127.1566,
         "runtime": "13:00~21:00", "comment": "감성적인 리빙 소품과 유니크한 인테리어 잡화를 셀렉해 놓은 소품샵입니다."},
        {"name": "브라운도그빈티지", "type": "굿즈", "time": "1시간 내외", "lat": 36.8171, "lng": 127.1569, "runtime": "12:00~21:00",
         "comment": "지하 1층에 위치한 힙한 분위기의 스트릿 빈티지 구제의류 전문점입니다."},
        {"name": "칼하트WIP 천안점", "type": "굿즈", "time": "30분 미만", "lat": 36.8174, "lng": 127.1565,
         "runtime": "12:00~21:00", "comment": "스트릿 패션의 정석 칼하트 매장으로 깔끔한 워크웨어 의류를 쇼핑할 수 있습니다."},
        {"name": "제티하우스", "type": "굿즈", "time": "30분 미만", "lat": 36.8166, "lng": 127.1579, "runtime": "12:30~20:30",
         "comment": "2층 소품샵! 귀여운 인형들과 굿즈들이 가득해서 힐링되는 킬링타임 스팟입니다."},
        {"name": "윈트 천안점 (WANTT)", "type": "굿즈", "time": "30분 미만", "lat": 36.8168, "lng": 127.1577,
         "runtime": "11:00~22:00", "comment": "가성비 좋고 트렌디한 보세 의류들이 넓은 매장에 꽉 차 있습니다."},
        {"name": "토이 하루 (TOY HARU)", "type": "굿즈", "time": "1시간 내외", "lat": 36.8193, "lng": 127.1551,
         "runtime": "13:00~21:00", "comment": "지하 1층 피규어 전문점! 각종 애니메이션 굿즈와 피규어 덕질하기 최고의 장소입니다."},
        {"name": "착한필름 천안신부점", "type": "굿즈", "time": "30분 미만", "lat": 36.8172, "lng": 127.1564,
         "runtime": "10:00~22:00", "comment": "다양하고 귀여운 스마트폰 케이스와 그립톡 등 폰 액세서리를 판매합니다."},
        {"name": "렌즈미 천안점", "type": "굿즈", "time": "30분 미만", "lat": 36.8171, "lng": 127.1563, "runtime": "10:30~21:30",
         "comment": "컬러 렌즈 및 관련 뷰티 소품들을 한눈에 비교하고 쇼핑하기 좋습니다."},
        {"name": "캐롤하우스", "type": "굿즈", "time": "30분 미만", "lat": 36.8185, "lng": 127.1553, "runtime": "11:30~22:00",
         "comment": "세련된 무드의 외관과 감각적인 남성 패션 의류들이 진열되어 있습니다."},
        {"name": "다이소 천안본점", "type": "굿즈", "time": "1시간 내외", "lat": 36.8193, "lng": 127.1566, "runtime": "10:00~22:00",
         "comment": "설명이 필요 없는 최고의 킬링타임 스팟! 백화점 바로 뒤라 접근성도 최고입니다."},
        {"name": "오렌즈 천안점", "type": "굿즈", "time": "30분 미만", "lat": 36.8191, "lng": 127.1567, "runtime": "10:00~22:00",
         "comment": "신부동 먹자골목 초입 GS25 건물 1층에 위치한 트렌디한 아이뷰티 매장입니다."},
        {"name": "ABC마트 ST 천안신부점", "type": "굿즈", "time": "30분 미만", "lat": 36.8190, "lng": 127.1568,
         "runtime": "10:30~22:00", "comment": "아트박스 바로 옆! 신상 신발이나 스니커즈 잡화들을 가볍게 구경하기 좋습니다."},
        {"name": "스비스 안경원 천안본점", "type": "굿즈", "time": "30분 미만", "lat": 36.8167, "lng": 127.1571,
         "runtime": "09:30~21:00", "comment": "엔틱한 벽돌 외관이 멋진 안경원으로 선글라스나 안경 소품 패션을 살펴볼 수 있습니다."},
        {"name": "윙크렌즈스토어 천안점", "type": "굿즈", "time": "30분 미만", "lat": 36.8169, "lng": 127.1570,
         "runtime": "10:00~21:30", "comment": "하파크리스틴 등 요즘 핫한 브랜드의 렌즈와 뷰티 잡화가 모여있습니다."},
        {"name": "스파오 천안신부점", "type": "굿즈", "time": "30분 미만", "lat": 36.8168, "lng": 127.1569, "runtime": "11:00~22:00",
         "comment": "유행하는 캐주얼웨어 의류와 캐릭터 콜라보 굿즈들을 편하게 둘러보기 좋은 대형 매장입니다."},
        {"name": "원더플레이스 천안신부점", "type": "굿즈", "time": "30분 미만", "lat": 36.8169, "lng": 127.1575,
         "runtime": "11:00~22:00", "comment": "다양한 브랜드의 트렌디한 스트릿 의류와 패션 잡화들을 한눈에 구경하기 좋습니다."},
        {"name": "가챠노리", "type": "굿즈", "time": "30분 미만", "lat": 36.8175, "lng": 127.1568, "runtime": "11:00~21:00",
         "comment": "1층에 위치한 뽑기(가챠) 및 장난감 피규어 전문점으로 시간 때우기 최고입니다."},

        # === 피시방 카테고리 데이터 (11개) ===
        {"name": "신세계PC방", "type": "피시방", "time": "1시간 내외", "lat": 36.8172, "lng": 127.1564, "runtime": "24시간 영업",
         "comment": "터미널 도보 3분 거리 최고 접근성! 대기 시간이 애매할 때 빠르게 들어가기 좋습니다."},
        {"name": "더와라와라 천안신부점", "type": "피시방", "time": "1시간 내외", "lat": 36.8170, "lng": 127.1568, "runtime": "24시간 영업",
         "comment": "도보 4분 거리이며, 연중무휴 24시간이라 늦은 밤 버스 대기에도 걱정 없습니다."},
        {"name": "에이드PC방", "type": "피시방", "time": "1시간 내외", "lat": 36.8205, "lng": 127.1580, "runtime": "24시간 영업",
         "comment": "조용하고 쾌적하게 컴퓨터하면서 킬링타임하기 좋은 PC방입니다."},
        {"name": "익스펜션PC방 천안점", "type": "피시방", "time": "1시간 내외", "lat": 36.8142, "lng": 127.1550, "runtime": "24시간 영업",
         "comment": "정도떡집 인근에 위치해 있으며, 컴퓨터 사양이 좋아 게임 즐기기에 딱입니다."},
        {"name": "라이또PC방 천안신부점", "type": "피시방", "time": "1시간 내외", "lat": 36.8198, "lng": 127.1538, "runtime": "24시간 영업",
         "comment": "3층에 위치해 있으며 깔끔한 인테리어와 다양한 먹거리 메뉴가 준비되어 있습니다."},
        {"name": "아레나PC 천안터미널점", "type": "피시방", "time": "1시간 내외", "lat": 36.8170, "lng": 127.1568, "runtime": "24시간 영업",
         "comment": "지하 1층에 넓게 자리 잡고 있어 친구들과 버스 기다리며 한판 하기 좋습니다."},
        {"name": "옵티멈존PC카페 천안터미널점", "type": "피시방", "time": "1시간 내외", "lat": 36.8171, "lng": 127.1570,
         "runtime": "24시간 영업", "comment": "노란색 간판이 눈에 띄는 핫플! 쾌적한 좌석과 맛있는 먹거리가 많습니다."},
        {"name": "옵티멈존PC카페 천안신부점", "type": "피시방", "time": "1시간 내외", "lat": 36.8169, "lng": 127.1575,
         "runtime": "24시간 영업", "comment": "지하 1층에 위치한 대형 매장으로 최신 프리미엄 게이밍 기어들이 세팅되어 있습니다."},
        {"name": "메카PC카페", "type": "피시방", "time": "1시간 내외", "lat": 36.8168, "lng": 127.1577, "runtime": "24시간 영업",
         "comment": "넓고 편안한 의자에서 게임하거나 유튜브 보며 쉬어가기 좋은 공간입니다."},
        {"name": "아이센스리그PC방 천안터미널점", "type": "피시방", "time": "1시간 내외", "lat": 36.8169, "lng": 127.1572,
         "runtime": "24시간 영업", "comment": "3층에 위치한 인기 프랜차이즈 PC방으로 커플석 및 팀전 자리가 잘 되어 있습니다."},
        {"name": "뉴몬PC", "type": "피시방", "time": "1시간 내외", "lat": 36.8167, "lng": 127.1573, "runtime": "24시간 영업",
         "comment": "깔끔하게 관리된 시설 덕분에 장시간 대기에도 피로감이 덜합니다."},

        # === 찜질방과 스파 카테고리 데이터 (7개) ===
        {"name": "굿모닝스파", "type": "찜질방과 스파", "time": "2시간 이상", "lat": 36.8165, "lng": 127.1610, "runtime": "24시간 영업",
         "comment": "터미널 도보 9분 거리! 24시간 운영이라 버스 대기 시간이 아주 길 때 누워서 쉬기 최고입니다."},
        {"name": "청담사우나", "type": "찜질방과 스파", "time": "2시간 이상", "lat": 36.8340, "lng": 127.1495, "runtime": "24시간 영업",
         "comment": "개운하게 목욕하고 피로를 풀며 편안하게 장시간 대기하기 좋습니다."},
        {"name": "세신샵결 천안점", "type": "찜질방과 스파", "time": "2시간 이상", "lat": 36.8270, "lng": 127.1378,
         "runtime": "08:00~22:00", "comment": "프라이빗 1인 세신샵으로, 대기 시간 동안 나만을 위한 프리미엄 힐링 타임을 보낼 수 있습니다."},
        {"name": "주식회사제이케이티개발 (하이렉스파)", "type": "찜질방과 스파", "time": "2시간 이상", "lat": 36.8225, "lng": 127.1365,
         "runtime": "24시간 영업", "comment": "대형 목욕·찜질 시설로, 넓고 쾌적한 찜질방 공간에서 휴식을 취할 수 있습니다."},
        {"name": "힐링찜질 족욕카페 천안점", "type": "찜질방과 스파", "time": "2시간 이상", "lat": 36.8295, "lng": 127.1340,
         "runtime": "10:00~21:00", "comment": "따뜻하게 족욕과 스파를 즐기며 차 한잔의 여유를 가질 수 있는 이색 스팟입니다."},
        {"name": "맥스스파휘트니스", "type": "찜질방과 스파", "time": "2시간 이상", "lat": 36.8315, "lng": 127.1425, "runtime": "24시간 영업",
         "comment": "두정동 코리타운 8층에 위치해 있으며, 사우나 시설이 잘 갖춰져 있어 길게 시간 때우기 적합합니다."},
        {"name": "뉴모닝스파", "type": "찜질방과 스파", "time": "2시간 이상", "lat": 36.8310, "lng": 127.1432, "runtime": "24시간 영업",
         "comment": "24시 목욕·찜질 스팟으로, 아늑하게 한숨 자거나 몸을 녹이며 쉬어가기 좋습니다."}
    ]

if "dynamic_times" not in st.session_state:
    st.session_state["dynamic_times"] = ["전체", "30분 미만", "1시간 내외", "2시간 이상"]

# ==============================================================================
# 3. 사이드바 필터 UI 및 제보창 구성 구역
# ==============================================================================
st.sidebar.header("🔍 필터 설정")

# 1) 남은 시간별 필터
selected_time = st.sidebar.selectbox("⏱️ 버스 출발까지 남은 시간", st.session_state["dynamic_times"])

st.sidebar.markdown("---")

# 2) 개별 체크박스 형태의 카테고리 필터
st.sidebar.subheader("🗂️ 카테고리 선택")
show_cafe = st.sidebar.checkbox("☕ 카페 보기", value=True)
show_goods = st.sidebar.checkbox("🛍️ 굿즈숍 보기", value=True)
show_pc = st.sidebar.checkbox("🎮 피시방 보기", value=True)
show_spa = st.sidebar.checkbox("♨️ 찜질방과 스파 보기", value=True)

st.sidebar.markdown("---")

# 3) 상시 노출형 제보 양식 구역
st.sidebar.subheader("📋 나만 아는 킬링타임 스팟 제보")
st.sidebar.caption("확정된 카테고리에 맞는 터미널 근처 꿀스팟을 제보해 주세요.")

new_name = st.sidebar.text_input("📍 스팟 명칭", placeholder="예: 짱구 피시방", key="in_rep_name")
new_type = st.sidebar.selectbox("⚙️ 시설 종류 선택", ["카페", "굿즈", "피시방", "찜질방과 스파"], key="in_rep_type")
new_time = st.sidebar.selectbox("⏳ 추천 대기 시간", ["30분 미만", "1시간 내외", "2시간 이상"], key="in_rep_time_select")
new_runtime = st.sidebar.text_input("🕒 운영 시간 입력", placeholder="예: 11:00~22:00", key="in_rep_runtime")

new_lat = st.sidebar.number_input("위도(Latitude)", value=36.819000, format="%.6f", key="in_rep_lat")
new_lng = st.sidebar.number_input("경도(Longitude)", value=127.157000, format="%.6f", key="in_rep_lng")
new_comment = st.sidebar.text_area("💬 한줄 추천 이유", placeholder="예: 구경거리가 많아요.", key="in_rep_comment")

if st.sidebar.button("✅ 제보 완료", use_container_width=True, key="btn_rep_submit"):
    if new_name and new_comment:
        runtime_val = new_runtime if new_runtime else "정보 없음"
        st.session_state["killing_data"].append({
            "name": f"[제보] {new_name}", "type": new_type, "time": new_time, "lat": new_lat, "lng": new_lng,
            "runtime": runtime_val, "comment": new_comment
        })
        st.sidebar.success("🎉 제보가 지도에 즉시 반영되었습니다!")
        st.rerun()
    else:
        st.sidebar.error("장소 이름과 추천 이유를 모두 입력해 주세요!")

# ==============================================================================
# 4. 지도 생성 및 기준점 마커 설정
# ==============================================================================
m = folium.Map(location=[TERMINAL_LAT, TERMINAL_LNG], zoom_start=16)

# 고정 터미널 마커 찍기 (빨간색 버스 핀)
folium.Marker(
    location=[TERMINAL_LAT, TERMINAL_LNG],
    popup=folium.Popup("<div style='width:150px;'><b>📍 천안고속터미널</b><br>출발/도착 기준점</div>", max_width=200),
    tooltip="천안고속터미널",
    icon=folium.Icon(color="red", icon="bus", prefix="fa")
).add_to(m)

# ==============================================================================
# 5. 데이터 매핑 및 복합 필터링 로직 (시간 + 체크박스)
# ==============================================================================
for item in st.session_state["killing_data"]:
    # 🚨 카테고리 매칭 에러 방지용 공백 전처리
    item_type = item["type"].strip()

    # ① 시간 조건 검사
    match_time = (selected_time == "전체") or (item["time"] == selected_time)

    # ② 체크박스 상태에 따른 카테고리 매칭 검사
    match_category = False
    if item_type == "카페" and show_cafe:
        match_category = True
    elif item_type == "굿즈" and show_goods:
        match_category = True
    elif item_type == "피시방" and show_pc:
        match_category = True
    elif item_type == "찜질방과 스파" and show_spa:
        match_category = True

    # 모든 필터 조건을 만족할 때만 지도에 핀 생성
    if match_time and match_category:
        # 두 좌표 간 실시간 도보 거리 및 소요 시간 계산
        start_pos = (TERMINAL_LAT, TERMINAL_LNG)
        end_pos = (item["lat"], item["lng"])
        distance_m = int(geodesic(start_pos, end_pos).meters)
        walk_time = max(1, round(distance_m / 67))

        # 카테고리별 개별 마커 스타일 매핑
        if item_type == "카페":
            icon_color = "orange"; icon_name = "coffee"
        elif item_type == "굿즈":
            icon_color = "purple"; icon_name = "shopping-bag"
        elif item_type == "피시방":
            icon_color = "green"; icon_name = "gamepad"
        elif item_type == "찜질방과 스파":
            icon_color = "blue"; icon_name = "hotcell"
        else:
            icon_color = "cadetblue"; icon_name = "info-circle"

        # 시민 제보 스팟 디자인 차별화
        if "[제보]" in item["name"]:
            border_style = "border: 2px solid #e06666; padding: 5px; border-radius: 5px;"
            title_color = "#e06666"
        else:
            border_style = ""
            title_color = "#1e88e5"

        # 반응형 풍선 팝업 디자인
        my_popup = folium.Popup(
            f"<link rel='stylesheet' href='https://use.fontawesome.com/releases/v5.15.4/css/all.css'>"
            f"<div style='width:240px; font-family:sans-serif; {border_style}'>"
            f"<b style='color:{title_color}; font-size:14px;'>{item['name']}</b><br>"
            f"<hr style='margin:5px 0; border:0; border-top:1px solid #eee'>"
            f"<i class='fas fa-tag' style='color:#777; width:18px;'></i> {item_type} ({item['time']})<br>"
            f"<i class='fas fa-clock' style='color:#777; width:18px;'></i> {item.get('runtime', '정보 없음')}<br>"
            f"🎯 <b style='color:#d9534f;'>터미널에서 도보 약 {distance_m}m (🏃 {walk_time}분)</b><br>"
            f"<hr style='margin:5px 0; border:0; border-top:1px solid #eee'>"
            f"<p style='font-size:12px; color:#555; margin:0;'>{item['comment']}</p>"
            f"</div>", max_width=300
        )

        # 최종 맵 위에 핀 등록
        folium.Marker(
            location=[item["lat"], item["lng"]],
            popup=my_popup,
            tooltip=item["name"],
            icon=folium.Icon(color=icon_color, icon=icon_name, prefix="fa")
        ).add_to(m)

# ==============================================================================
# 6. 웹 화면에 지도 출력
# ==============================================================================
st_folium(m, width=1100, height=650, key="killing_time_map_master_final_fixed")