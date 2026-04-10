from flask import Blueprint, request
from app import db
from app.models import Task, Category
from app.schemas import TaskCreateSchema, TaskUpdateSchema
#task 34 new 

from datetime import datetime, timedelta, timezone
from marshmallow import ValidationError
from redis import Redis
from rq import Queue
from app.jobs import send_due_soon_notification
from flask import current_app

tasks_bp = Blueprint("tasks", __name__)

#changed tasl 3 separate schemas for create vs update 
task_create_schema = TaskCreateSchema()
task_update_schema = TaskUpdateSchema()

# task 3new 
# 1. task must have due_date
# 2. due_date must be in future
# 3. due_date must be within next 24 hours
def should_queue_notification(due_date):
    if not due_date:
        return False

    cur = datetime.now(timezone.utc)

    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)

    return cur < due_date <= cur + timedelta(hours=24)

def format_datetime(dt): #compell with the date time format 
    if not dt:
        return None
    return dt.replace(microsecond=0).isoformat() + "Z"
#serialize logic 
def serialize_task(task):
    
    category_data = None

    if task.category:
        category_data = {
            "id": task.category.id,
            "name": task.category.name,
            "color": task.category.color
        }

    return {
        "id": task.id,
        "title":task.title,
        "description":task.description,
        "completed": task.completed,
        "due_date":format_datetime(task.due_date),
        "category_id": task.category_id,
        "category":category_data,
        "created_at":format_datetime(task.created_at),
        "updated_at":format_datetime(task.updated_at)
    }


# get 
@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    completed_param = request.args.get("completed")
    q = Task.query
    # simple filtering based on completion status
    if completed_param is not None:
        if completed_param.lower() == "true":
            q = q.filter_by(completed=True)
        elif completed_param.lower() == "false":
            q = q.filter_by(completed=False)

    tasks = q.all()
    return {"tasks": [serialize_task(task) for task in tasks]}, 200


#get id 
@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    
    get_t = db.session.get(Task, task_id)

    if not get_t:
        return {"error": "Task not found"}, 404
    return serialize_task(get_t), 200


# post 
#changed task 4 create a new task and queue reminder if due date is soon 
@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json() or {}

    try:
        loaded_data = task_create_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    category_id = loaded_data.get("category_id")
    if category_id is not None:
        catg = db.session.get(Category, category_id)
        if not catg:
            return {"errors": {"category_id": ["Category does not exist."]}}, 400

    task = Task(
        title=loaded_data["title"],
        description=loaded_data.get("description"),
        completed=False,
        due_date=loaded_data.get("due_date"),
        category_id=category_id
    )

    db.session.add(task)
    db.session.commit()

    notification_queued = False

    if should_queue_notification(task.due_date):

        red = Redis.from_url(current_app.config["REDIS_URL"])

        queue = Queue(connection=red)
        queue.enqueue(send_due_soon_notification, task.title)
        notification_queued = True

    return {"task": serialize_task(task),"notification_queued": notification_queued }, 201


#put 
@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    t = db.session.get(Task, task_id)

    if not t:
        return {"error": "Task not found"}, 404

    data = request.get_json() or {}

    errors = task_update_schema.validate(data)
    if errors:
        return {"errors": errors}, 400

    if "category_id" in data:
        category_id = data["category_id"]
        if category_id is not None:
            category = db.session.get(Category, category_id)
            if not category:
                return {"errors": {"category_id": ["Category does not exist."]}}, 400
        t.category_id = category_id

    if "title" in data:
        t.title = data["title"]

    if "description" in data:
        t.description = data["description"]

    if "completed" in data:
        t.completed = data["completed"]

    if "due_date" in data:
        t.due_date = data["due_date"]

    db.session.commit()

    return serialize_task(t), 200


# delete
@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    t = db.session.get(Task, task_id)

    if not t:
        return {"error": "Task not found"}, 404

    db.session.delete(t)
    
    db.session.commit()

    return {"message": "Task deleted"}, 200