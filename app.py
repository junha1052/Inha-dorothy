
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

        # 입력된 시간 문자열을 datetime.time 객체로 변환
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        file_path = '강의시간표.xlsx'
        df = pd.read_excel(file_path)

        def check_classroom_availability(time_str,start_time,end_time):
            pattern = re.compile(r'(월|화|수|목|금|토|일)(\d+(?:,\d+)*)')
            matches = pattern.findall(time_str)
            for match in matches:
                day_match, numbers = match
                if day == day_match:
                    periods = list(map(int, numbers.split(',')))
                    for period in periods:
                        class_start_time = datetime.strptime(period_to_time(period), "%H:%M").time()
                        class_end_time = (datetime.combine(datetime.min, class_start_time) + timedelta(minutes=30)).time()
                        print(f"Checking time: {class_start_time} - {class_end_time}, Start time: {start_time}, End time: {end_time}")
                        if class_start_time >= start_time and class_end_time <= end_time:
                            return False
            return True 

        # 빈 강의실 검색
        empty_classrooms = {}
        classrooms = df['강의실'].dropna().unique()
        
        buildings = {'60주년 기념관': '60', '본관 1호관': '1', '2호관(남)': '2S', '2호관(북)': '2N', '2호관(동)': '2E', '2호관(서)': '2W',
                     '4호관': '4', '5호관(남)': '5S', '5호관(북)': '5N', '5호관(동)': '5E', '5호관(서)': '5W', '6호관': '6', '7호관': '7', '9호관': '9',
                     '하이테크': '하', '서호관': '서'}
        
        for classroom in classrooms:
            if building_name and not classroom.startswith(building_name):
                continue

            building_found = False
            for building, prefix in buildings.items():
                if classroom.startswith(prefix):
                    building_found = True
                    empty_classrooms.setdefault(building, []).append(classroom)
                    break
            if not building_found:
                print(f"Building not found for classroom: {classroom}")

        print("Empty classrooms:", empty_classrooms)  # 디버깅을 위한 출력

        # 강의실 분류
        sorted_classrooms = []

        classrooms= empty_classrooms.get(building)
        for classroom in classrooms:
            classroom_timetable = df[df['강의실'] == classroom][['과목명', '시간']]
            is_empty = True
            for index, row in classroom_timetable.iterrows():
                if not check_classroom_availability(row['시간'],start_time,end_time):
                    is_empty = False
                    break
            if is_empty:
                sorted_classrooms.append(classroom)

        print("Sorted classrooms:", sorted_classrooms)  # 디버깅을 위한 출력
       
        return render_template('빈강의실.html', sorted_classrooms=sorted_classrooms)

    return render_template('강의실 검색.html')

