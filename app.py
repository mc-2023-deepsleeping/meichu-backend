from flask import Flask, render_template, request, redirect, url_for, jsonify, json
from flask import Response
import cv2
import re
from datetime import datetime, timedelta

from sql import conn
from yolo import detect

PATH = './static'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return Response('Hello World!', 200)

@app.route('/upload', methods=['POST', 'GET'])
def upload_image():
    if 'Img' not in request.files:
        return Response('No image provided', 400)
    
    image = request.files['Img']
    filename = image.filename

    try:
        emp_id = int(request.form['EmpId'])
    except:
        return Response('No user id provided', 400)

    save_path = f'{PATH}/upload/{filename}'
    result_path = f'{PATH}/result/{filename}'

    image.save(save_path)
    
    result, labels = detect(save_path)

    cv2.imwrite(result_path, result)

    with conn.cursor() as cursor:
        for cls_name, acc in labels:
            command = f"INSERT INTO contraband (EmpEntryID, Classification, accuracy) VALUES ({emp_id}, '{cls_name}', {acc});"
            cursor.execute(command)

        command = f"INSERT INTO EmpEntry (EmpID, DateTime, ToolScanTime, Img) VALUES \
            ({emp_id}, '{request.form['DateTime']}', {float(request.form['ToolScanTime'])}, '{result_path}');"
        cursor.execute(command)
        conn.commit()   

    # print(labels)

    with conn.cursor() as cursor:
        command = f"SELECT EmpHost.Host, EmpHost.HostEmail FROM EmpHost WHERE id={emp_id}"
        cursor.execute(command)
        host_name, host_email = cursor.fetchone()
    
    # print(result)

    with conn.cursor() as cursor:
        cursor.execute(f"SELECT Emp.EmpShift, Emp.Zone FROM Emp WHERE id={emp_id}")
        emp_shift, area = cursor.fetchone()

    arrival_time = datetime.strptime(request.form['DateTime'], '%m/%d/%Y %H:%M')
    target_time = datetime.strptime(emp_shift, '%H:%M')
    half_an_hour = timedelta(minutes=30)
        
    if arrival_time.time() < (target_time - half_an_hour).time():
        arrival_status = 'early'
    elif arrival_time.time() > (target_time + half_an_hour).time():
        arrival_status = 'late'
    else:
        arrival_status = 'normal'

    ret_val = {
        'empID': emp_id,
        'status': arrival_status,
        'area': area,
        'hostID': host_name,
        'hostEmail': host_email,
        'labels': labels,
        'imageLink': result_path
    }
    
    return jsonify(ret_val)

# @app.route('/chat', methods=['POST', 'GET'])
# def chat():
#     if 'message' not in request.form:
#         return Response('No message provided', 400)
    
#     prompt = request.form['message']

#     response = ''

#     return Response(response, 200)

@app.route('/attd_rec', methods=['GET'])
def attd_rec():
    command = """
    SELECT EmpEntry.EmpID, EmpEntry.DateTime, Emp.EmpShift, Emp.DeptId, Emp.Zone, EmpHost.Host, EmpHost.HostEmail
        FROM EmpEntry LEFT JOIN Emp ON EmpEntry.EmpID = Emp.id
        LEFT JOIN EmpHost ON EmpEntry.EmpID = EmpHost.id;
    """
    with conn.cursor() as cursor:
        cursor.execute(command)
        results = cursor.fetchall()

    ret_val = { 'data': [] }

    print(results[0])

    for result in results:       
        arrival_time = datetime.strptime(result[1], '%m/%d/%Y %H:%M')
        target_time = datetime.strptime(result[2], '%H:%M')
        half_an_hour = timedelta(minutes=30)
        
        if arrival_time.time() < (target_time - half_an_hour).time():
            arrival_status = 'early'
        elif arrival_time.time() > (target_time + half_an_hour).time():
            arrival_status = 'late'
        else:
            arrival_status = 'normal'

        ret_val['data'].append({
            'empID': result[0],
            'status': arrival_status,
            'area': result[4],
            'hostID': result[5],
            'hostEmail': result[6]
        })
    
    return jsonify(ret_val)

@app.route('/sec_stat', methods=['GET'])
def sec_stat():
    command = """
        SELECT subquery.EmpEntryID, subquery.Classification, 
            subquery.Zone, subquery.Host, subquery.HostEmail, 
            COUNT(*) as CountOfDuplicates
        FROM (
            SELECT contraband.EmpEntryID, contraband.Classification, 
                Emp.Zone, EmpHost.Host, EmpHost.HostEmail
            FROM contraband
            LEFT JOIN Emp ON contraband.EmpEntryID = Emp.id
            LEFT JOIN EmpHost ON contraband.EmpEntryID = EmpHost.id
        ) subquery
        GROUP BY subquery.EmpEntryID, subquery.Classification, subquery.Zone, subquery.Host, subquery.HostEmail
        HAVING COUNT(*) > 1;
    """

    #     SELECT contraband.EmpEntryID, contraband.Classification, 
    #     Emp.Zone, EmpHost.Host, EmpHost.HostEmail
    # FROM contraband
    # LEFT JOIN Emp ON contraband.EmpEntryID = Emp.id
    # LEFT JOIN EmpHost ON contraband.EmpEntryID = EmpHost.id
    with conn.cursor() as cursor:
        cursor.execute(command)
        results = cursor.fetchall()
    
    ret_val = { 'data': [] }

    for result in results:
        emp_id, cls_name, area, host_name, host_email, count = result

        if emp_id not in ret_val['data']:
            ret_val['data'].append({
                'empID': emp_id,
                'item': [{
                    'type': cls_name,
                    'number': count
                }],
                'area': area,
                'hostID': host_name,
                'hostEmail': host_email
            })
        else:
            # ret_val['data']
            ...

            
        #     if emp_id not in ret_val['data']:
        #         ret_val['data'].append({
        #             'empID': emp_id,
        #             'item': [],
        #             'area': area,
        #             'hostID': host_name,
        #             'hostEmail': host_email
        #         })
        #     else:
        #         for entry in ret_val['data']:
        #             if entry['empID'] == emp_id:
        #                 entry['item'].append({'clsName': cls_name, 'count': count})

        # print(ret_val)
        # {
        #     data: [
        #         {
        #             empID: int,
        #             item: [
        #                 {
        #                     type: string,   // The type of invalid items
        #                     number: int,    // The number of invalid items
        #                 }
        #             ]
        #             area: string,   // AZ or HQ
        #             hostID: int,
        #             hostEmail: string
        #         }
        #     ]
        # }
    
    return jsonify(ret_val)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)