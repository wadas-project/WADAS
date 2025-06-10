from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample data for testing
RECEIVERS = {
    "test_receiver": {"id": "12345", "name": "Test Receiver"},
    "another_receiver": {"id": "67890", "name": "Another Receiver"},
}


@app.route("/receiver", methods=["GET"])
def get_receiver():
    receiver_name = request.args.get("id")
    if receiver_name in RECEIVERS:
        return jsonify(RECEIVERS[receiver_name])
    else:
        return jsonify({"error": "Receiver not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
