from flask import Flask, render_template, request, redirect, url_for, jsonify, json
from flask import Response
import cv2

from sql import conn
from yolo import detect

PATH = './static'

app = Flask(__name__)

@app.route('/upload', methods=['POST', 'GET'])
def upload_image():
    if 'Img' not in request.files:
        return Response('No image provided', 400)
    
    image = request.files['Img']
    filename = image.filename

    try:
        user_id = int(request.form['EmpId'])
    except:
        return Response('No user id provided', 400)

    save_path = f'{PATH}/upload/{filename}'
    result_path = f'{PATH}/result/{filename}'

    image.save(save_path)
    
    result, labels = detect(save_path)

    cv2.imwrite(result_path, result)

    with conn.cursor() as cursor:
        for cls_name, acc in labels:
            command = f"INSERT INTO contraband (EmpEntryID, Classification, accuracy) VALUES ({user_id}, '{cls_name}', {acc});"
            cursor.execute(command)

        command = f"INSERT INTO EmpEntry (EmpID, DateTime, ToolScanTime, Img) VALUES \
            ({user_id}, '{request.form['DateTime']}', {float(request.form['ToolScanTime'])}, '{result_path}');"
        cursor.execute(command)
        conn.commit()   

    print(labels)

    ret_val = {
        'labels': labels,
        'path': result_path
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
    # if 'message' not in request.form:
    #     return Response('No message provided', 400)
    
    # prompt = request.form['message']

    command = """
    SELECT EmpEntry.EmpID, EmpEntry.DateTime, Emp.EmpShift, Emp.DeptId, Emp.Zone, EmpHost.Host, EmpHost.HostEmail
        FROM EmpEntry LEFT JOIN Emp ON EmpEntry.EmpID = Emp.id
        LEFT JOIN EmpHost ON EmpEntry.EmpID = EmpHost.id;
    """
    with conn.cursor() as cursor:
        cursor.execute(command)
        # conn.commit()
        results = cursor.fetchall()

    ret_val = { 'data': [] }

    for result in results: 
        ret_val['data'].append({
            'empID': result[0],
            # 'empEmail': result[6],
            'onTime': '',
            'area': result[4],
            'hostID': result[5],
            'hostEmail': result[6]
        })
    
    return jsonify(ret_val)

if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)