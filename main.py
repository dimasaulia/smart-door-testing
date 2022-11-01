from urllib.request import Request
import requests
import inquirer
import xlsxwriter
import json
from concurrent.futures import ThreadPoolExecutor, thread
from time import perf_counter

# INFO: Prompt Question
questions = [
    inquirer.List(
        "test",
        message="What API testing program do you want to do?",
        choices=["Register User", "Logging In User", "Register Card", "Pairing User and Card", "User Request Room", "Admin Give Room Access", "Check In"],
    ),
]
test = inquirer.prompt(questions)
filePath = input("Testing file name: ")
outputFile = input("Output testing file name: ")
threadSize = int(input("How many thread you want to use: "))
url_ = "http://127.0.0.1:8000" #for online url please user "https://smart-door-pnj.herokuapp.com"
secret = {
    "username"  : "dimasaulia",
    "password"  : "T4np4$4nd1",
    "api_id"    : "cl9w74nuc0000o0lkbpnqol7w",
    "api_key"   : "YE6wazWUk0XcTqI9B4D3QwYuGfIjSgXz"
}
buffData = []
RUID = "yuiOB"
DUID = "Hge40"
# INFO: Open File
file = open(f'{filePath}')
jsonData = json.load(file)
file.close()

# INFO: Starting XLSX 
workbook = xlsxwriter.Workbook(f'{outputFile}.xlsx')


def fetchData(_payload, _endpoint, _no, _worksheet):
    with requests.Session() as client:
        resp = client.post(f'{url_}{_endpoint}', json=_payload)
        _worksheet.write(f"A{_no}", f"{_no-1}")
        _worksheet.write(f"B{_no}", str(_payload))
        _worksheet.write(f"C{_no}", str(resp.json()))
        _worksheet.write(f"D{_no}", round(float(resp.elapsed.total_seconds()),3)*1000)
        if(_endpoint == "/api/v1/user/register" or _endpoint == "/api/v1/user/login"):
            _payload["jwt"] = resp.cookies["jwt"]
            buffData.append(_payload)
        no+=1

def fetchDataAdmin(_payload, _endpoint, _no, _worksheet):
    with requests.Session() as client:
        resp = client.post(f'{url_}{_endpoint}', json=_payload, cookies=adminAuth)
        _worksheet.write(f"A{_no}", f"{_no-1}")
        _worksheet.write(f"B{_no}", str(_payload))
        _worksheet.write(f"C{_no}", str(resp.json()))
        _worksheet.write(f"D{_no}", round(float(resp.elapsed.total_seconds()),3)*1000)

def fetchDataAdminAcc(_payload, _endpoint, _no, _worksheet):
    with requests.Session() as client:
        resp = client.post(f'{url_}{_endpoint}?ruid={RUID}&cardNumber={_payload["cardNumber"]}', json=_payload, cookies=adminAuth)
        _worksheet.write(f"A{_no}", f"{_no-1}")
        _worksheet.write(f"B{_no}", str(_payload))
        _worksheet.write(f"C{_no}", str(resp.json()))
        _worksheet.write(f"D{_no}", round(float(resp.elapsed.total_seconds()),3)*1000)

def fetchDataWCookie(_payload, _endpoint, _no, _worksheet):
    with requests.Session() as client:
        resp = client.post(f'{url_}{_endpoint}?ruid={RUID}&cardNumber={_payload["cardNumber"]}', cookies={"jwt":_payload["jwt"]})
        _worksheet.write(f"A{_no}", f"{_no-1}")
        _worksheet.write(f"B{_no}", str(_payload))
        _worksheet.write(f"C{_no}", str(resp.json()))
        _worksheet.write(f"D{_no}", round(float(resp.elapsed.total_seconds()),3)*1000)

if test.get("test") == "Register User":
    registerWorksheet = workbook.add_worksheet("REGISTER")
    registerWorksheet.write("A1", "NO")
    registerWorksheet.write("B1", "PAYLOAD DATA")
    registerWorksheet.write("C1", "RESPONSE DATA")
    registerWorksheet.write("D1", "RESPON TIME")
    start = perf_counter()
    with ThreadPoolExecutor(threadSize) as executor:
        executor.map(fetchData, jsonData, ["/api/v1/user/register"] * len(jsonData), range(2, len(jsonData)+2), [registerWorksheet] * len(jsonData))
        executor.shutdown(wait=True)

    file = open(f'{filePath}', "w+")
    file.write(json.dumps(buffData))
    file.close()
    print("Execution time:", f"{round((perf_counter() - start),3) * 1000}ms" )

if test.get("test") == "Logging In User":
    registerWorksheet = workbook.add_worksheet("REGISTER")
    registerWorksheet.write("A1", "NO")
    registerWorksheet.write("B1", "PAYLOAD DATA")
    registerWorksheet.write("C1", "RESPONSE DATA")
    registerWorksheet.write("D1", "RESPON TIME")
    start = perf_counter()
    with ThreadPoolExecutor(threadSize) as executor:
        executor.map(fetchData, jsonData, ["/api/v1/user/login"] * len(jsonData), range(2, len(jsonData)+2), [registerWorksheet] * len(jsonData))
        executor.shutdown(wait=True)

    file = open(f'{filePath}', "w+")
    file.write(json.dumps(buffData))
    file.close()
    print("Execution time:", f"{round((perf_counter() - start),3) * 1000}ms" )

if test.get("test") == "Register Card":
    registerWorksheet = workbook.add_worksheet("CARD REGISTER")
    registerWorksheet.write("A1", "NO")
    registerWorksheet.write("B1", "PAYLOAD DATA")
    registerWorksheet.write("C1", "RESPONSE DATA")
    registerWorksheet.write("D1", "RESPON TIME")
    start = perf_counter()
    with ThreadPoolExecutor(threadSize) as executor:
        executor.map(fetchData, jsonData, [f"/api/v1/card/h/register?id={secret['api_id']}&key={secret['api_key']}"] * len(jsonData), range(2, len(jsonData)+2), [registerWorksheet] * len(jsonData))
        executor.shutdown(wait=True)
    print("Execution time:", f"{round((perf_counter() - start),3) * 1000}ms" )

if test.get("test") == "Pairing User and Card":
    print("Logging in Admin first")
    login = requests.post(url =f'{url_}/api/v1/user/login', json=secret)
    adminAuth = login.cookies
    registerWorksheet = workbook.add_worksheet("PAIRING USER AND CARD")
    registerWorksheet.write("A1", "NO")
    registerWorksheet.write("B1", "PAYLOAD DATA")
    registerWorksheet.write("C1", "RESPONSE DATA")
    registerWorksheet.write("D1", "RESPON TIME")
    print("Start executing task")
    start = perf_counter()
    with ThreadPoolExecutor(threadSize) as executor:
        executor.map(fetchDataAdmin, jsonData, [f"/api/v1/user/pair"] * len(jsonData), range(2, len(jsonData)+2), [registerWorksheet] * len(jsonData))
        executor.shutdown(wait=True)
    print("Execution time:", f"{round((perf_counter() - start),3) * 1000}ms" )

if test.get("test") == "User Request Room":
    registerWorksheet = workbook.add_worksheet("REQUEST ROOM ACCESS")
    registerWorksheet.write("A1", "NO")
    registerWorksheet.write("B1", "PAYLOAD DATA")
    registerWorksheet.write("C1", "RESPONSE DATA")
    registerWorksheet.write("D1", "RESPON TIME")
    print("Start executing task")
    start = perf_counter()
    with ThreadPoolExecutor(threadSize) as executor:
        executor.map(fetchDataWCookie, jsonData, [f"/api/v1/room/u/request"] * len(jsonData), range(2, len(jsonData)+2), [registerWorksheet] * len(jsonData))
        executor.shutdown(wait=True)
    print("Execution time:", f"{round((perf_counter() - start),3) * 1000}ms" )

if test.get("test") == "Admin Give Room Access":
    print("Logging in Admin first")
    login = requests.post(url =f'{url_}/api/v1/user/login', json=secret)
    adminAuth = login.cookies
    registerWorksheet = workbook.add_worksheet("GIVE ROOM ACCESS")
    registerWorksheet.write("A1", "NO")
    registerWorksheet.write("B1", "PAYLOAD DATA")
    registerWorksheet.write("C1", "RESPONSE DATA")
    registerWorksheet.write("D1", "RESPON TIME")
    print("Start executing task")
    start = perf_counter()
    with ThreadPoolExecutor(threadSize) as executor:
        executor.map(fetchDataAdminAcc, jsonData, [f"/api/v2/room/pair"] * len(jsonData), range(2, len(jsonData)+2), [registerWorksheet] * len(jsonData))
        executor.shutdown(wait=True)
    print("Execution time:", f"{round((perf_counter() - start),3) * 1000}ms" )

if test.get("test") == "Check In":
    registerWorksheet = workbook.add_worksheet("CHECK IN")
    registerWorksheet.write("A1", "NO")
    registerWorksheet.write("B1", "PAYLOAD DATA")
    registerWorksheet.write("C1", "RESPONSE DATA")
    registerWorksheet.write("D1", "RESPON TIME")
    start = perf_counter()
    with ThreadPoolExecutor(threadSize) as executor:
        executor.map(fetchData, jsonData, [f"/api/v2/room/h/check-in/{DUID}?id={secret['api_id']}&key={secret['api_key']}"] * len(jsonData), range(2, len(jsonData)+2), [registerWorksheet] * len(jsonData))
        executor.shutdown(wait=True)
    print("Execution time:", f"{round((perf_counter() - start),3) * 1000}ms" )

workbook.close()