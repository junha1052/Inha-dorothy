@app.route('/강의실 검색', methods=['GET', 'POST'])
def search_classroom():
    if request.method == 'POST':
        building_name = request.form['search']
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
# 교시를 실제 시간으로 변환하는 함수
def period_to_time(period):
    start_time = datetime.strptime("09:00", "%H:%M")
    actual_time = start_time + timedelta(minutes=30 * (period - 1))
    return actual_time.strftime("%H:%M")

@app.route('/빈강의실 검색', methods=['GET', 'POST'])
def search_empty_classrooms():
    if request.method == 'POST':
        building_name = request.form.get('building', None)
        day = request.form['day']
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']

        # 디버깅을 위한 출력
        print("Form Data: ", building_name, day, start_time_str, end_time_str)

        file_path = '강의시간표.xlsx'
        df = pd.read_excel(file_path)

        # 입력된 시간 문자열을 datetime 객체로 변환 (날짜 부분 제거)
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        # 디버깅을 위한 출력
        print("Converted Times: ", start_time, end_time)

        def check_classroom_availability(time_str, start_time, end_time):
            pattern = re.compile(r'(월|화|수|목|금|토|일)(\d+(?:,\d+)*)')
            matches = pattern.findall(time_str)
            for match in matches:
                day_match, numbers = match
                if day == day_match:
                    periods = list(map(int, numbers.split(',')))
                    for period in periods:
                        class_start_time = datetime.strptime(period_to_time(period), "%H:%M").time()
                        class_end_time = (datetime.combine(datetime.min, class_start_time) + timedelta(minutes=30)).time()

                        # datetime.combine을 사용하여 날짜를 포함한 datetime 객체로 비교
                        if not (datetime.combine(datetime.min, class_end_time) <= datetime.combine(datetime.min, start_time) or
                                datetime.combine(datetime.min, class_start_time) >= datetime.combine(datetime.min, end_time)):
                            return False
            return True

        # 빈 강의실 검색
        empty_classrooms = []
        classrooms = df['강의실'].dropna().unique()

        for classroom in classrooms:
            if building_name and not classroom.startswith(building_name):
                continue

            classroom_timetable = df[df['강의실'] == classroom][['과목명', '시간']]

            is_empty = True
            for index, row in classroom_timetable.iterrows():
                if not check_classroom_availability(row['시간'], start_time, end_time):
                    is_empty = False
                    break
            if is_empty:
                empty_classrooms.append(classroom)

        print("Empty classrooms:", empty_classrooms)  # 디버깅을 위한 출력

        sorted_classrooms = {}
        buildings = {'60주년 기념관': '60', '본관 1호관': '1', '2호관(남)': '2S', '2호관(북)': '2N', '2호관(동)': '2E', '2호관(서)': '2',
                     '4호관': '4', '5호관(남)': '5S', '5호관(북)': '5N', '5호관(동)': '5E', '5호관(서)': '5', '6호관': '6', '7호관': '7', '9호관': '9',
                     '하이테크': '하', '서호관': '서'}

        for classroom in empty_classrooms:
            building = next((b for b, prefix in buildings.items() if classroom.startswith(prefix)), None)
            if building:
                sorted_classrooms.setdefault(building, []).append(classroom)

        sorted_classrooms= {building_name: empty_classrooms}

        print("Sorted classrooms:", sorted_classrooms[building_name])  # 디버깅을 위한 출력
        

        return render_template('빈강의실.html', sorted_classrooms=sorted_classrooms)

    return render_template('강의실 검색.html')
