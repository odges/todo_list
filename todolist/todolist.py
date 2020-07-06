# Write your code here
import calendar
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

Base = declarative_base()
engine = create_engine('sqlite:///todo.db?check_same_thread=False')


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.string_field


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


class TodoList:
    list_days = list(calendar.day_name)
    list_months = list(calendar.month_abbr)
    users_action = [
        "1) Today's tasks",
        "2) Week's tasks",
        "3) All tasks",
        "4) Missed tasks",
        "5) Add task",
        "6) Delete task",
        "0) Exit"
    ]

    def handle_action(self, users_action):
        actions = {
            "1": self.today_tasks,
            "2": self.weeks_task,
            "3": self.all_tasks,
            "4": self.missed_task,
            "5": self.add_task,
            "6": self.delete_task,
        }
        actions[users_action]()
        return None

    def delete_task(self):
        print("Chose the number of the task you want to delete:")
        tasks = session.query(Task).group_by(Task.deadline)
        for index, task in enumerate(tasks):
            print(f'{index + 1}. {task.task}. {task.deadline.day} {self.list_months[task.deadline.month]}')
        delete_task = int(input())
        session.delete(tasks[delete_task - 1])
        session.commit()
        print("The task has been deleted!")

    def missed_task(self):
        print("Missed tasks:")
        tasks = session.query(Task).filter(Task.deadline < datetime.today()).all()
        if len(tasks) == 0:
            print("Nothing is missed!")
        for index, task in enumerate(tasks):
            print(f'{index + 1}. {task.task}. {task.deadline.day} {self.list_months[task.deadline.month]}')

    def today_tasks(self):
        print("Today:")
        tasks = session.query(Task).filter(Task.deadline == datetime.today()).all()
        self.show_today_tasks(tasks)

    def weeks_task(self):
        yesterday = datetime.today() - timedelta(days=1)
        week_forward = datetime.today() + timedelta(days=7)
        tasks = session.query(Task).filter(
            Task.deadline > yesterday,
            Task.deadline <= week_forward
        )
        self.show_weeks_task(tasks)

    def all_tasks(self):
        tasks = session.query(Task).all()
        self.show_all_tasks(tasks)

    def show_today_tasks(self, tasks):
        today = datetime.today()
        print(f'Today {today.day} {self.list_months[today.month]}:')
        if len(tasks) == 0:
            print("Nothing to do!")
        else:
            for index, task in enumerate(tasks):
                print(f'{index + 1}. {task.task}')

    def show_all_tasks(self, tasks):
        print("All tasks:")
        for index, task in enumerate(tasks):
            print(f'{index + 1}. {task.task}. {task.deadline.day} {self.list_months[task.deadline.month]}')

    def show_weeks_task(self, tasks):
        today = datetime.today()
        for day in range(0, 7):
            print('')
            current_day = today + timedelta(days=day)
            task_for_current_day = list(filter(lambda task: task.deadline.day == current_day.day, tasks))
            print(self.list_days[current_day.weekday()], current_day.day, self.list_months[current_day.month] + ":")
            if len(task_for_current_day) > 0:
                for index, task in enumerate(task_for_current_day):
                    print(f'{index + 1}. {task.task}')
            else:
                print("Nothing to do!")

    @staticmethod
    def add_task():
        print("Enter task")
        task = input()
        print("Enter deadline")
        deadline = input()
        created_task = Task(
            task=task,
            deadline=datetime.strptime(deadline, '%Y-%m-%d')
        )
        session.add(created_task)
        session.commit()
        print("The task has been added!")


user_choice = None
while user_choice != "0":
    todo = TodoList()
    for action in todo.users_action:
        print(action)

    user_choice = input()

    if user_choice == "0":
        break

    todo.handle_action(user_choice)
    print('')

print("Bye!")
