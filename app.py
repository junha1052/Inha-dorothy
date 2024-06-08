from flask import Flask, request, jsonify, render_template
import pandas as pd
import re

app = Flask(__name__)

# 엑셀 파일에서 5번째 열 데이터 읽기
df = pd.read_excel('강의시간표 보정.xlsx')
classroom_suggestions = df.iloc[:, 4].dropna().astype(str).tolist()  # 5번째 열 (0부터 시작하므로 인덱스는 4)

@app.route('/')
def home():
    return render_template('도로시 길찾기test.html')

@app.route('/건물도면')
def 건물도면():
    return render_template('건물도면.html')
@app.route('/강의실 검색', methods=['GET', 'POST'])
def search_classroom():
    if request.method == 'POST':
        building_name = request.form.get('search', '') 
        '''building_name = request.form['search']'''
        if not building_name:  # 빈 문자열인 경우 처리
            return render_template('강의실 검색.html', error='건물명을 입력해주세요.')
        time_table = pd.read_excel('강의시간표.xlsx')

        # NaN/NA 값을 제거하고 필터링
        filtered_rows = time_table.loc[time_table['강의실'].notna() & time_table['강의실'].str.contains(building_name, case=False), ['과목명', '시간']]

        # 시간표 초기화 (가정: 월~금, 1~25교시)
        timetable = {day: ['' for _ in range(25)] for day in ['월', '화', '수', '목', '금', '토']}

        # 정규 표현식 패턴 정의
        pattern = re.compile(r'(월|화|수|목|금|토|일)(\d+(?:,\d+)*)')

        for index, row in filtered_rows.iterrows():
            subject = row['과목명']
            cell_value = row['시간']
            if not isinstance(cell_value, str):
                continue
            matches = pattern.findall(cell_value)

            for match in matches:
                day, numbers = match
                numbers_list = numbers.split(',')
                for number in numbers_list:
                    period = int(number)
                    if period <= 25:  # 교시가 25 이하인 경우만 처리
                        timetable[day][period - 1] = subject  # 0부터 시작하므로 -1

        return render_template('시간표.html', timetable=timetable, building_name=building_name)
    return render_template('강의실 검색.html')

@app.route('/빈강의실 검색', methods=['GET', 'POST'])
def search_empty_classrooms():
    if request.method == 'POST':
        def time_to_period(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return (hours - 9) * 2 + (minutes // 30) + 1


        # 강의실의 시간표를 확인하여 빈 교시인지 확인
        def check_classroom_availability(time_str, day, start_period, end_period):
            pattern = re.compile(r'(월|화|수|목|금|토|일)(\d+(?:,\d+)*)')
            matches = pattern.findall(time_str)
            for match in matches:
                day_match, numbers = match
                if day == day_match:
                    numbers_list = list(map(int, numbers.split(',')))
                    for number in numbers_list:
                        if start_period <= number <= end_period:
                            return False
            return True

        building_name = request.form.get('building', None)
        day = request.form['day']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        file_path = '강의시간표.xlsx'
        df = pd.read_excel(file_path)

        # 시작 및 종료 시간의 교시 계산
        start_period = time_to_period(start_time)
        end_period = time_to_period(end_time)

        # 빈 강의실 검색
        empty_classrooms = []
        classrooms = df['강의실'].dropna().unique()

        for classroom in classrooms:
            if building_name and not classroom.startswith(building_name):
                continue

            classroom_timetable = df[df['강의실'] == classroom][['과목명', '시간']]

            is_empty = all(check_classroom_availability(row['시간'], day, start_period, end_period) for index, row in classroom_timetable.iterrows())
            if is_empty:
                empty_classrooms.append(classroom)

        # 강의실 분류
        sorted_classrooms = {}
        buildings = {'60주년 기념관': '60', '본관 1호관': '1', '2호관(남)': '2S', '2호관(북)': '2N', '2호관(동)': '2E', '2호관(서)': '2',
                     '4호관': '4', '5호관(남)': '5S', '5호관(북)': '5N', '5호관(동)': '5E', '5호관(서)': '5', '6호관': '6', '7호관': '7', '9호관': '9',
                     '하이테크': '하', '서호관': '서'}

        for classroom in empty_classrooms:
            building = next((b for b, prefix in buildings.items() if classroom.startswith(prefix)), None)
            if building:
                sorted_classrooms.setdefault(building, []).append(classroom)

        if building_name:
            sorted_classrooms = {building_name: sorted_classrooms.get(building_name, [])}

        return render_template('빈강의실.html', sorted_classrooms=sorted_classrooms)

    return render_template('강의실 검색.html')

@app.route('/네비게이션')
def 네비게이션():
    return render_template('네비게이션.html')

@app.route('/편의시설')
def 편의시설():
    return render_template('편의시설.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)



