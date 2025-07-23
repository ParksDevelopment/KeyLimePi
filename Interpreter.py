def keyChange(queue):
    while True:
        event = queue.get()
        interpret(event)
        queue.task_done()

def interpret(matrix):
    print(matrix)