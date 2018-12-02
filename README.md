# EichenCredit

Set up:
1. Open a new virtualenv
2.  ```pip install -r requirements.txt```
3. ```python run.py


Create a Process [POST]
```http://0.0.0.0:5000/process```
With Body

```nodes=[(<string:TaskName>,<int:NumberOfRepeats>), ...]````
```edges=[(<string:FromNode>, <string:ToNode>, "<["sub_task","condition","next_task", "result"]:EdgeType>, <string:Result>), ...]```

Example:
```
curl -X POST \
  http://0.0.0.0:5000/process \
  -F 'nodes=[("A1", 1),
("A2", 2),
( "A3", 2),
( "A4", 2),
("A5", 1),
( "A7", 1)]' \
  -F 'edges=[("A1", "A2", "sub_task", "None"),
("A1","A3", "sub_task", "None"),
("A3", "A2", "condition", "None"),
("A1", "A4", "next_task", "None"),
("A4", "A1", "condition", "None"),
("A4", "A7", "result", "B"),
("A7", "A4", "condition", "None"),
("A4", "A5", "result", "A"),
("A5", "A4", "condition", "None")]
```
