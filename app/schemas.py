from marshmallow import Schema, fields, validate

# Schema for Category
class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
     # required,  1-50 chars, uniqueness is checked separately 
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    #optional, must be valid hex like #FFFFFF
    color = fields.Str( required=False, allow_none=True, validate=validate.Regexp(r"^#([A-Fa-f0-9]{6})$"))


# schema for creating a new task
class TaskCreateSchema(Schema):
    #required + length check
    title = fields.Str(required=True,validate=validate.Length(min=1, max=100))
    # option  + max 500 chars
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500) )
    #string
    due_date = fields.DateTime(required=False, allow_none=True)
    #optional
    category_id = fields.Int(required=False, allow_none=True)

# schema for updating task
class TaskUpdateSchema(Schema):
    #optional 
    title = fields.Str(required=False,validate=validate.Length(min=1, max=100))
    #optional 
    description = fields.Str(required=False, allow_none=True,validate=validate.Length(max=500) )
    #optional 
    completed = fields.Bool(required=False)
    # allow updating due date
    due_date = fields.DateTime(required=False, allow_none=True)
    #allow changing category
    category_id = fields.Int(required=False, allow_none=True)