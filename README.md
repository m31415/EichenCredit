# EichenCredit

# Set up:
1. Open a new virtualenv (Python 3.6)
2. ```pip install -r requirements.txt```
3. ```python run.py```


# Create a Process [POST]
```http://0.0.0.0:5000/process```
With Body

```nodes=[(<string:TaskName>,<int:NumberOfRepeats>), ...]``` </br>
```edges=[(<string:FromNode>, <string:ToNode>, <["sub_task","condition","next_task", "result"]:EdgeType>, <string:Result>), ...]```

<b>Rules</b> : 
1. A result/next_task edge has always a counter condition edge (see example graph)
2. If a task has result edges it can not have next_task edges vice versa

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
Will create this internal Graph:
![Process](https://i.imgur.com/twLI7YQ.png)

# Open Tasks [GET]

Receive open task with 
```
curl -X GET \
http://127.0.0.1:5000/process/tasks/<StartTask>
 ```
  
 <b> Rule </b> Always use the StartTask of your process (Example A1)
 Example:
 
 ```
curl -X GET \
http://127.0.0.1:5000/process/tasks/A1
  ```
  
When using the example process it should return:
```
Please conduct one of following tasks : 
{'A2 []'}
```
Closed Brackets can contain possible results:
```
Please conduct one of following tasks : 
{"A4 ['B', 'A']"}
```

# Conduct Task [PUT]

Conduct an open task with 
```
curl -X PUT \
http://127.0.0.1:5000/process/tasks/A2 \
-F done=True
```
When conducting a task with a result:
```
curl -X PUT \
http://127.0.0.1:5000/process/tasks/A4 \
-F done=True \
-F result=A
````
When conducting a repeat use ```done=False```

# Conduct Example Process
1. POST like above
2. 
````
curl -X PUT \
  http://127.0.0.1:5000/process/tasks/A2 \
  -F done=True
 ````
 3.
````
curl -X PUT \
  http://127.0.0.1:5000/process/tasks/A3 \
  -F done=True
 ````
4.
```
curl -X PUT \
http://127.0.0.1:5000/process/tasks/A4 \
-F done=True \
-F result=A
````
5.
````
curl -X PUT \
  http://127.0.0.1:5000/process/tasks/A5 \
  -F done=True
 ````
 
=> Process ended with conducting Task A5,  GET ```http://127.0.0.1:5000/process/tasks/A1``` will return an empty set
 ````
 ````
