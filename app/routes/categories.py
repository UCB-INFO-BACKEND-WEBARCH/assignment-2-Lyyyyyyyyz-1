from flask import Blueprint, request
from app import db
from app.models import Category
from app.schemas import CategorySchema

categories_bp = Blueprint("categories", __name__)

category_schema = CategorySchema()

#get
#return all categories with task_count 
@categories_bp.route("/categories", methods=["GET"])
def get_categories():

    categories = Category.query.all()

    result = []

    for c in categories:
        #include task_count
        result.append({"id": c.id,"name": c.name, "color": c.color, "task_count": len(c.tasks)})

    return {"categories": result}, 200


#get with id
@categories_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):

    category = Category.query.get(category_id)

    if not category:
        return {"error": "Category not found"}, 404

    tasks_data = []
    # only return min task info
    for task in category.tasks:
        tasks_data.append({"id": task.id,"title": task.title,"completed": task.completed })

    return {"id": category.id, "name": category.name,"color": category.color,"tasks": tasks_data}, 200


# post
@categories_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.json

    errors = category_schema.validate(data)
    if errors:
        return {"errors": errors}, 400
    #uniqueness check
    existing = Category.query.filter_by(name=data["name"]).first()
   
    if existing:
        return {"errors": {"name": ["Category with this name already exists."]}}, 400

    category = Category(name=data["name"], color=data.get("color") )

    db.session.add(category)
    db.session.commit()

    return { "id": category.id,"name": category.name,"color": category.color }, 201


# delete ##only if no task attached 
@categories_bp.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = Category.query.get(category_id)

    if not category:
        return {"error": "Category not found"}, 404

    if len(category.tasks) > 0:
        return {"error": "Cannot delete category with existing tasks. Move or delete tasks first."}, 400

    db.session.delete(category)
    db.session.commit()

    return {"message": "Category deleted"}, 200