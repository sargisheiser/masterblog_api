from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
]


@app.route("/api/posts", methods=["GET"])
def get_posts():
    return jsonify(POSTS)


@app.route("/api/posts", methods=["POST"])
def add_post():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    if "title" not in data:
        return jsonify({"error": "Missing required field: title"}), 400
    if "content" not in data:
        return jsonify({"error": "Missing required field: content"}), 400

    new_id = max([post["id"] for post in POSTS], default=0) + 1

    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
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
    global POSTS
    post = next((p for p in POSTS if p["id"] == post_id), None)

    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])

    return jsonify(post), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)


