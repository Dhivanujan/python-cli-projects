tasks = []

def addTask():
    task = input("Please enter a task:")
    tasks.append(task)
    print(f"Task '{task}' added to the list.")

def deleteTask():
 #   task = input("Please enter the task to delete:")
 #   if task in tasks:
 #       tasks.remove(task)
 #       print(f"Task '{task}' deleted successfully!")
 #   else:
 #       print("Task '{task}' not found.")
    listTasks()
    try:
        taskToDelete = int(input("Enter the # to delete: "))
        if taskToDelete >= 0 and taskToDelete < len(tasks):
            tasks.pop(taskToDelete) 
            print(f"Task {taskToDelete} is removed.")
        else:
            print(f"Task {taskToDelete} not found.")
    except:
        print("Invaild input.")

def listTasks():
    if not tasks:
        print("There are no tasks currently.")
    else:
        print("Current tasks:")
        for index,task in enumerate(tasks):
            print(f"Task #{index}. {task}")

if __name__ == "__main__":
    print("welcome to to do list app: ")
    while True:
        print()
        print("Please select one of the following options!")
        print("-------------------------------------------")
        print("1. Add a task")
        print("2. Delete a task")
        print("3. List tasks")
        print("4. Quit")

        choice = int(input("Enter your choice: "))

        if (choice == 1):
            addTask()
        elif (choice == 2):
            deleteTask()
        elif (choice == 3):
            listTasks()
        elif (choice == 4):
            break
        else:
            print("Invalid input. Please try again")

    print("Good bye👋!!!")