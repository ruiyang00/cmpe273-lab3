from ariadne import QueryType, MutationType, graphql_sync, make_executable_schema
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify


type_defs = """

    type Query {
        students(id:ID!): studentPayload!
        courses(id:ID!): coursesPayload!
    }

    input Student {
        name: String!
    }

    input Course {
        name: String!
    }

    type Mutation {
        createStudent(newStudent: Student!, id:ID!): String
        createCourse(newCourse:Course!, id:ID!): String
        enrollCourse(student_id:ID!, course_id:ID!): String
    }

    type studentPayload{
        name: String!
    }
    
    type coursesPayload{
        name: String!
        students:[studentPayload]!
    }
    


    
"""

query = QueryType()
mutation = MutationType()


database = {
    "students": {

    },
    "classes": {

    }
}


@query.field("students")
def resolve_students(_, info, id):

    return database["students"][id]


@query.field("courses")
def resolve_courses(_, info, id):

    return database["classes"][id]


@mutation.field("createStudent")
def resolve_createStudent(_, info, newStudent, id):

    database["students"][id] = newStudent
    print(newStudent)
    return "Student created"


@mutation.field("createCourse")
def resolve_createCourse(_, info, newCourse, id):
    addCourse = {
        "name": newCourse["name"],
        "enrollStudents": []
    }

    database["classes"][id] = addCourse
    print(addCourse)
    return "Course created"


@mutation.field("enrollCourse")
def resolve_enrollCourse(_, info, student_id, course_id):
    database["classes"][course_id]["enrollStudents"].append(
        database['students'][student_id])

    return "enroll succesfully"


schema = make_executable_schema(type_defs, [query, mutation])

app = Flask(__name__)


@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)
