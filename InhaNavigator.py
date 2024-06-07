import folium
from folium import plugins
import pandas as pd
import ipywidgets
import os
import json

# 초기 지도 설정
UMMlocation = (37.44933418489706, 126.65433805399361)
map_UMM = folium.Map(location=UMMlocation, width="80%", zoom_start=16)
map_UMM

# GeoJSON 파일 경로
hauseOutline = '/path/to/your/haus1.geojson'  # 실제 경로로 변경 필요
display(folium.GeoJson(hauseOutline, name="haus1").add_to(map_UMM))
display(map_UMM)

# 경로 좌표 변환 함수
def switchPosition(coordinate):
    return [coordinate[1], coordinate[0]]

# 경로 데이터를 불러와서 좌표 변환
testGeoJson = '/path/to/your/f2b.geojson'  # 실제 경로로 변경 필요
with open(testGeoJson) as f:
    testWay = json.load(f)

for feature in testWay['features']:
    path = feature['geometry']['coordinates']

finalPath = list(map(switchPosition, path))
print(finalPath)

# 경로를 지도에 추가
folium.plugins.AntPath(finalPath).add_to(map_UMM)
map_UMM

# 선택 위젯 정의
select_widget = ipywidgets.Select(
    options=['Option A', 'Option B'],
    value='Option A',
    description='Select',
    disabled=False
)

def selectOption(opt):
    if opt == 'Option A':
        print('A')
    elif opt == 'Option B':
        print('B')

ipywidgets.interact(selectOption, opt=select_widget)

# Navigator 클래스 정의
class Navigator:
    def __init__(self):
        self.geoResources = {}
        self.inhaLocation = (37.44933418489706, 126.65433805399361)
        self.position = 'f'
        self.destination = 'haus1'

        # 실제 파일 경로로 변경 필요
        for root, dirs, files in os.walk('/path/to/your/GeoResources'):
            for file in files:
                self.geoResources[file.split('.')[0]] = os.path.join(root, file)

    def changeDestination(self, newDestination):
        self.destination = newDestination
        self.redrawMap()

    def changeStartPoint(self, newStartPoint):
        self.position = newStartPoint
        print(f'Selected Start: {newStartPoint}; Selected Target: {self.destination}')
        self.redrawMap()

    def drawPathWay(self, inhaMap):
        searchString = self.position + self.destination.split('haus')[1]
        with open(self.geoResources[searchString]) as f:
            testWay = json.load(f)

        for feature in testWay['features']:
            path = feature['geometry']['coordinates']

        finalPath = list(map(switchPosition, path))
        folium.plugins.AntPath(finalPath).add_to(inhaMap)

    def drawBuilding(self, inhaMap):
        hauseOutline = self.geoResources[self.destination]
        folium.GeoJson(hauseOutline, name="geojson").add_to(inhaMap)

    def redrawMap(self):
        inhaMap = folium.Map(location=self.inhaLocation, width="75%", zoom_start=17)
        self.drawPathWay(inhaMap)
        self.drawBuilding(inhaMap)
        display(inhaMap)

myNavigator = Navigator()

def displayWay(whereTo):
    myNavigator.changeDestination(whereTo)

def changePosition(whereFrom):
    myNavigator.changeStartPoint(whereFrom)

# 도착점 선택 위젯
selectHouse_widget = ipywidgets.Select(
    options=['haus1', 'haus2', 'haus2n', 'haus2s', 'haus4', 'haus5', 'haus6', 'haus7', 'haus9', 'haus10', 'haus11', 'haus12', 'haus13', 'haus15', 'haus60', 'jungseok'],
    value='haus1',
    description='Target',
    disabled=False
)

def selectHouse(way):
    displayWay(way)

# 시작점 선택 위젯
selectPosition_widget = ipywidgets.Select(
    options=['Front gate', 'Back gate'],
    value='Front gate',
    description='Start',
    disabled=False
)

def selectPosition(position):
    if position == 'Front gate':
        changePosition('f')
    elif position == 'Back gate':
        changePosition('b')

# 위젯 초기화
ipywidgets.interact(selectPosition, position=selectPosition_widget)
ipywidgets.interact(selectHouse, way=selectHouse_widget)