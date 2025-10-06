import json
import os
from datetime import datetime
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(
    __name__,
    static_folder="../frontend/static",
    template_folder="../frontend/templates"
)
CORS(app)

# Swagger configuration
SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Masterblog API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS_FILE = os.path.join(os.path.dirname(__file__), "posts.json")


def load_posts():
    """Load posts from JSON storage."""
    if not os.path.exists(POSTS_FILE):
        return []
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_posts(posts):
    """Persist posts to JSON storage."""
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


def validate_date_format(date_str):
    """Validate date format as YYYY-MM-DD."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """Retrieve all posts, optionally sorted."""
    posts = load_posts()
    sort = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    if sort:
        valid_fields = {"title", "content", "author", "date"}
        if sort not in valid_fields:
            return jsonify({"error": f"Invalid sort field: {sort}"}), 400

        reverse = direction == "desc"
        if sort == "date":
            posts.sort(key=lambda p: datetime.strptime(p["date"], "%Y-%m-%d"), reverse=reverse)
        else:
            posts.sort(key=lambda p: p.get(sort, "").lower(), reverse=reverse)

    return jsonify(posts)


@app.route("/api/posts", methods=["POST"])
def add_post():
    """Create a new blog post with date validation."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    for field in ["title", "content", "author", "date"]:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Validate date format
    if not validate_date_format(data["date"]):
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

    posts = load_posts()
    new_id = max([post["id"] for post in posts], default=0) + 1
    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"],
        "author": data["author"],
        "date": data["date"]
    }

    posts.append(new_post)
    save_posts(posts)
    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """Update an existing blog post."""
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    if "date" in data and not validate_date_format(data["date"]):
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])
    post["author"] = data.get("author", post["author"])
    post["date"] = data.get("date", post["date"])
    save_posts(posts)
    return jsonify(post), 200


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Delete a blog post by ID."""
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    posts = [p for p in posts if p["id"] != post_id]
    save_posts(posts)
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully"}), 200


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Search posts by title, content, author, or partial date."""
    title_query = request.args.get("title", "").lower()
    content_query = request.args.get("content", "").lower()
    author_query = request.args.get("author", "").lower()
    date_query = request.args.get("date", "")

    results = []
    for post in load_posts():
        matches_title = title_query in post["title"].lower() if title_query else True
        matches_content = content_query in post["content"].lower() if content_query else True
        matches_author = author_query in post["author"].lower() if author_query else True
        matches_date = date_query in post["date"] if date_query else True  # partial match

        if all([matches_title, matches_content, matches_author, matches_date]):
            results.append(post)

    return jsonify(results), 200


@app.route("/", methods=["GET"])
def home():
    """Render frontend entry point."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
