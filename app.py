from flask import Flask, request, abort
import ast, json

app = Flask(__name__)

edge_types = ['sub_task', 'result', 'next_task', 'condition']


class Edge:

    def __init__(self, task, edge_type, result=None):

        self.task = task
        self.edge_type = edge_type
        self.result = result

    def __repr__(self):
        return 'Edge to ' + self.task.name + ' From Edge_Type ' + self.edge_type

    def is_condition(self):
        return self.edge_type == 'condition'

    def is_result(self):
        return self.edge_type == 'result'

    def is_sub_task(self):
        return self.edge_type == 'sub_task'

    def is_next(self):
        return self.edge_type == 'next_task'


class Task:

    def __init__(self, name, result=None, repeats=0):

        self.name = name
        self.edges = []
        self.result = result
        self.done = False
        self.max_repeats = repeats
        self.repeats = repeats

    def __repr__(self):
        return self.name

    def is_done(self):
        if self.done:
            return True
        if any([edge.is_sub_task() for edge in self.edges]):
            return all([edge.task.is_done() for edge in self.edges if edge.is_sub_task()])
        else:
            return False

    def conduct(self, last_task, task_done):

        # 'Check if it's the first task
        if last_task is None:
            self.repeats -= 1
            self.done = task_done
            return self

        # 'Check if self-repeating'
        if last_task is self and self.repeats > 0:
            self.repeats -= 1
            self.done = task_done
            return self

        # 'If Last task was repeated and self can repeat
        if last_task.max_repeats - last_task.repeats > 1 and self.repeats > 0:
            # 'And the repeats conducted in last_task are <= current repeats - 1 => Task can be repeated once more
            if self.max_repeats - (self.repeats - 1) <= last_task.max_repeats - last_task.repeats:
                self.repeats -= 1
                self.done = task_done
                self.repeats = (last_task.max_repeats - last_task.repeats) - 1
                return self
            else:
                return False

        # 'If last_task is not repeatable or was conduct just once, must be first conduct call
        elif self.max_repeats == self.repeats:
            self.repeats -= 1
            self.done = True
            return self

        # 'Can't conduct
        else:
            return False


class Graph:

    def __init__(self):
        self.graph = {}
        self.last_task = None

    def find_open(self, task,  to_do):

        # 'Filter conditions, which are not satisfied'
        open_conditions = [edge.task for edge in task.edges if edge.is_condition() and not edge.task.is_done()]

        # 'Filter open_sub_tasks and done_sub_tasks'
        open_sub_tasks = [edge.task for edge in task.edges if edge.is_sub_task() and not edge.task.is_done()]
        sub_tasks = [edge.task for edge in task.edges if edge.is_sub_task()]

        # 'Filter result-edges'
        possible_results = [edge for edge in task.edges if edge.is_result()]

        # 'Filter next-task'
        next_tasks = [edge.task for edge in task.edges if edge.is_next()]

        # 'Open conditions => Task can not be done => Traverse to conditions'
        for open_condition in open_conditions:
            self.find_open(open_condition, to_do)

        # 'No open_conditions => Task itself or it's sub_tasks can be done'
        if len(open_conditions) == 0:
            # 'No sub_tasks => Task itself can be done'
            if len(open_sub_tasks) == 0:
                # 'Except all sub_tasks are done =>/OR Task itself is done => Traverse to all next-tasks/results'
                # 'Assumption! : A task can either have next_tasks or tasks depending on result'
                if len(sub_tasks) > 0 or task.is_done():
                    # 'If tasks has next_tasks it has no result => traverse to all next_tasks'
                    for next_task in next_tasks:
                        self.find_open(next_task, to_do)
                    # 'if task has possible_results =>  traverse to matching result'
                    for edge in possible_results:
                        if task.result == edge.result:
                            self.find_open(edge.task, to_do)

                else:
                    # Found => All Conditions are met + Task has no sub_tasks + Task is not done => Task can be done'
                    if task not in to_do:
                        to_do.append(task.name + " " + str([edge.result for edge in possible_results]))

            # 'Open sub_tasks => Traverse top open sub_tasks'
            else:
                for open_sub_task in open_sub_tasks:
                    self.find_open(open_sub_task, to_do)

    def open_tasks(self, start):

        to_do = []

        self.find_open(start, to_do)

        return set(to_do)


Graph = Graph()


@app.route('/process', methods=['POST'])
def process():

    nodes = ast.literal_eval(request.form['nodes'])
    edges = ast.literal_eval(request.form['edges'])

    for node in nodes:
        Graph.graph[node[0]] = Task(name=node[0], repeats=node[1])

    for edge in edges:
        Graph.graph[edge[0]].edges.append(Edge(task=Graph.graph[edge[1]], edge_type=edge[2], result=edge[3]))

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/process/tasks/<string:task>', methods=['GET', 'PUT'])
def tasks(task):

    if task not in Graph.graph:
        abort(404)

    if request.method == 'GET':
        response = "Please conduct one of following tasks : \n" + str(Graph.open_tasks(Graph.graph[task]))

    if request.method == 'PUT':

        if 'result' in request.form:
            result = request.form['result']
            Graph.graph[task].result = result

        # 'Check if the last task was repeated, if so set the max repeats to last_task repeats'

        task_done = ast.literal_eval(request.form['done'])
        conduct = Graph.graph[task].conduct(Graph.last_task, task_done)
        if conduct:
            Graph.last_task = conduct
            response = json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            response = json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

    return response





