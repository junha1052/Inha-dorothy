rom flask import Flask, render_template, request
import pandas as pd
import re 

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/건물도면')
def 건물도면():
    return render_template('건물도면.html')

@app.route('/강의실 검색', methods=['GET', 'POST'])
def search_classroom():
    if request.method == 'POST':
        building_name = request.form['search']
        time_table = pd.read_excel('강의시간표 보정.xlsx')
        
        # NaN/NA 값을 제거하고 필터링
        filtered_rows = time_table.loc[time_table['강의실'].notna() & time_table['강의실'].str.contains(building_name, case=False), ['과목명', '시간']]
        
        # 시간표 초기화 (가정: 월~금, 1~25교시)
        timetable = {day: ['' for _ in range(25)] for day in ['월', '화', '수', '목', '금']}
        
        # 정규 표현식 패턴 정의
        pattern = re.compile(r'(월|화|수|목|금|토|일)(\d+(?:,\d+)*)')
        
        for index, row in filtered_rows.iterrows():
            subject = row['과목명']
            cell_value = row['시간']
            matches = pattern.findall(cell_value)
            
            for match in matches:
                day, numbers = match
                numbers_list = numbers.split(',')
                for number in numbers_list:
                    period = int(number)
                    if period <= 25:  # 교시가 25 이하인 경우만 처리
                        timetable[day][period - 1] = subject  # 0부터 시작하므로 -1
        
        return render_template('시간표.html', timetable=timetable)
    
    return render_template('강의실 검색.html')
@app.route('/네비게이션')
def 네비게이션():
    return render_template('네비게이션.html')

@app.route('/편의시설')
def 편의시설():
    return render_template('편의시설.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
