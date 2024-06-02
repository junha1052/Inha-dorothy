from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# 엑셀 파일에서 5번째 열 데이터 읽기
df = pd.read_excel('강의시간표 보정.xlsx')
classroom_suggestions = df.iloc[:, 4].dropna().astype(str).tolist()  # 5번째 열 (0부터 시작하므로 인덱스는 4)

@app.route('/')
def home():
    return render_template('도로시 길찾기test.html')

@app.route('/건물도면')
def 건물도면():
    return render_template('건물 도면.html')

@app.route('/강의실 검색', methods=['GET', 'POST'])
def search_classroom():
    if request.method == 'POST':
        building_name = request.form['search']
        time_table = pd.read_excel('강의시간표 보정.xlsx')

        # NaN/NA 값을 제거하고 필터링
        filtered_rows = time_table.loc[
            time_table.iloc[:, 4].notna() & time_table.iloc[:, 4].str.contains(building_name, case=False), ['과목명', '시간']]

        return render_template('검색 결과.html', building_name=building_name, results=filtered_rows)
    return render_template('강의실 검색.html')

@app.route('/get_suggestions')
def get_suggestions():
    query = request.args.get('q', '').lower()
    if query:
        filtered_suggestions = [s for s in classroom_suggestions if query in s.lower()]
    else:
        filtered_suggestions = []
    return jsonify({'suggestions': filtered_suggestions})

@app.route('/내비게이션')
def 내비게이션():
    return render_template('내비게이션.html')

@app.route('/편의시설')
def 편의시설():
    return render_template('편의 시설.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
