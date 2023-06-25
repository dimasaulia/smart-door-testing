import serial
import serial.tools.list_ports
import time
import json
import xlsxwriter
from datetime import datetime
ports = serial.tools.list_ports.comports()
portsList = []
for port in ports:
    portsList.append(str(port))
    print(str(port))
selectedPort = input("Plase select available port. COM:")
filePath = input("Please input testing file path: ")
monitoringString = input("Please input text to monitor: ")
fileName = input("Please input output file name: ")
serialDebug = serial.Serial(port = f'COM{selectedPort}', baudrate=9600, bytesize=8, parity="N", stopbits=serial.STOPBITS_TWO, timeout=1)
serialString = ""
startTime = None
endTime = None

workbook = xlsxwriter.Workbook(f'{fileName}.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write("A1", "ID")
worksheet.write("B1", "PAYLOAD")
worksheet.write("C1", "RESPONSE")
worksheet.write("D1", "HTTP CODE")
worksheet.write("E1", "INTERNAL ESP TIME(ms)")
worksheet.write("F1", "RESPON TIME(ms)")

file = open(filePath)
jsonData = json.load(file)
file.close()

print("\t\tMONITORING TASK\t")
print("-------------------------------------------------")
print("|\tSELECTED PORT\t|\tMONITORING TEXT\t|")
print(f"|\tCOM{selectedPort}\t\t|\t{monitoringString}\t|")
print("-------------------------------------------------\n")
pointer = 0;
newDataArrive = True
successRespon = 0

startTimes = time.time()

while True and selectedPort != "" and pointer < (len(jsonData)):
    if(newDataArrive):
        serialDebug.write(bytes(f"DATA#{pointer}#{jsonData[pointer]['cardNumber']}#{jsonData[pointer]['pin']}!", 'utf-8'))
    
    # print(f"DATA#{pointer}#{jsonData[pointer]}!")
    time.sleep(0.2)
    try:
        if serialDebug.in_waiting:
            try:
                serialString = serialDebug.readline().decode('utf').rstrip("\n").replace("!","")
                stringArray = serialString.rstrip('\r').split("#")
                print(serialString)
                if(stringArray[1] == monitoringString):
                    if(stringArray[6] == "START"):
                        worksheet.write(f"B{pointer+2}", f"[{datetime.now().time()}]{serialString}")
                        startTime = time.time()
                        newDataArrive = False
                    if(stringArray[6] == "END"):
                        newDataArrive = True
                        endTime = time.time()
                        print(f"SERIAL EXECUTION TIME = {round((endTime-startTime), 3)}s")
                        worksheet.write(f"A{pointer+2}", f"{pointer}")
                        worksheet.write(f"C{pointer+2}", f"[{datetime.now().time()}]{serialString}")
                        worksheet.write(f"D{pointer+2}", f"{stringArray[5]}")
                        worksheet.write(f"E{pointer+2}", f"{stringArray[4]}")
                        worksheet.write(f"F{pointer+2}", f"{round((endTime-startTime), 3)*1000}")
                        if(stringArray[5] == "200"):
                            successRespon+=1
                        pointer+=1
            except:
                pass
    except KeyboardInterrupt:
        break

finalDuration = round((time.time() - startTime),3)
resultString = f"Process done! {successRespon} request successfuly done from {len(jsonData)} total request in {finalDuration}s"
print(resultString)
worksheet.write(f"A{int(len(jsonData))+5}", resultString)
workbook.close()