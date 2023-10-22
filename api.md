### 員工進場
```json
/upload: POST
{
    'Img': <object>
    'EmpId': int,
    'DateTime': '%m/%d/%Y %H:%M',
    'ToolScanTime': float, 
}
```
returns:
```json
{
    empID: int,
    status: string,   // early, normal or late
    area: string,     // AZ or HQ
    hostID: int,
    hostEmail: string,
    imageLink: string,
}
```

### 出勤紀錄
```json
/attd_rec: GET
```
returns:
```json
{
data: [
    {
        empID: int,
        status: string,   // early, normal or late
        area: string,     // AZ or HQ
        date: string,
        hostID: int,
        hostEmail: string
    }
    ...
]
}
```

### 安檢狀況
```json
/sec_stat: GET
```
returns:
```json
{
    data: [
        {
            empID: int,
            item: [
                {
                    type: string,   // The type of invalid items
                    number: int,    // The number of invalid items
                }
                ...
            ]
            area: string,   // AZ or HQ
            hostID: int,
            hostEmail: string
        }
    ]
}
```

### 預測掃描時間
```json
/scan_time: POST
{
    date: '%m/%d/%Y' // start date
}
```
returns:
```json
{
    data: [int...],
    date: '%m/%d/%Y' // the predicted day when the machine will broke
}
```

### Bard AI
```json
/ask_bard: POST
{
    Question: str // start date
}
```
returns:
```json
{
    answer: str
}
```

### Ask db query 
```json
/ask_bard: POST
{
    query: str // start date
}
```
returns:
```json
{
    answer: str
}
```