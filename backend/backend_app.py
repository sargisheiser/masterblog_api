from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime


SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"


app = Flask(__name__)
CORS(app)


swagger_ui_blueprint = get_swaggerui_blueprint(
   SWAGGER_URL,
   API_URL,
   config={"app_name": "Masterblog API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


POSTS = [
   {
       "id": 1,
       "title": "First Post",
       "content": "This is the first post.",
       "author": "Admin",
       "date": "2025-09-30"
   },
   {
       "id": 2,
       "title": "Second Post",
       "content": "This is the second post.",
       "author": "Jane Doe",
       "date": "2025-09-29"
   },
]

@app.route("/api/posts", methods=["GET"])
def get_posts():
   sort = request.args.get("sort")
   direction = request.args.get("direction", "asc")


   posts = POSTS.copy()


   if sort:
       reverse = direction == "desc"


       if sort not in ["title", "content", "author", "date"]:
           return jsonify({"error": f"Invalid sort field: {sort}"}), 400


       try:
           if sort == "date":
               posts.sort(
                   key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"),
                   reverse=reverse
               )
           else:
               posts.sort(key=lambda x: x[sort].lower(), reverse=reverse)
       except Exception as e:
           return jsonify({"error": f"Sorting failed: {str(e)}"}), 400


   return jsonify(posts), 200


@app.route("/api/posts", methods=["POST"])
def add_post():
   data = request.get_json()

   if not data:
       return jsonify({"error": "Request body must be JSON"}), 400
   if "title" not in data or "content" not in data:
       return jsonify({"error": "Missing required fields: title and content"}), 400


   new_id = max([post["id"] for post in POSTS], default=0) + 1

   new_post = {
       "id": new_id,
       "title": data["title"],
       "content": data["content"],
       "author": data.get("author", "Anonymous"),
       "date": data.get("date", datetime.today().strftime("%Y-%m-%d"))
   }

   POSTS.append(new_post)
   return jsonify(new_post), 201

@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
   global POSTS
   post = next((p for p in POSTS if p["id"] == post_id), None)

   if post is None:
       return jsonify({"error": f"Post with id {post_id} not found"}), 404

   POSTS = [p for p in POSTS if p["id"] != post_id]
   return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200

@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
   post = next((p for p in POSTS if p["id"] == post_id), None)

   if post is None:
       return jsonify({"error": f"Post with id {post_id} not found"}), 404

   data = request.get_json()
   if not data:
       return jsonify({"error": "No input data provided"}), 400

   post["title"] = data.get("title", post["title"])
   post["content"] = data.get("content", post["content"])
   post["author"] = data.get("author", post["author"])
   post["date"] = data.get("date", post["date"])

   return jsonify(post), 200

@app.route("/api/posts/search", methods=["GET"])
def search_posts():
   title_query = request.args.get("title", "").lower()
   content_query = request.args.get("content", "").lower()
   author_query = request.args.get("author", "").lower()
   date_query = request.args.get("date", "")


   results = []
   for post in POSTS:
       matches_title = title_query in post["title"].lower() if title_query else True
       matches_content = content_query in post["content"].lower() if content_query else True
       matches_author = author_query in post["author"].lower() if author_query else True
       matches_date = date_query in post["date"] if date_query else True


       if matches_title and matches_content and matches_author and matches_date:
           results.append(post)

   return jsonify(results), 200

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5002, debug=True)

