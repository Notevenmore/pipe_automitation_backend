from flask import Flask, jsonify, request
from flask_cors import CORS
from lib import DE_Best_1, DE_Best_2, DE_Current_Best_1


app = Flask(__name__) 
CORS(app)

@app.route("/automated", methods=["POST"])
def automated():
  ps = request.form.get("pipe_initial_pressure")
  length_b1_b2 = request.form.get("distance_to_consumer_l1")
  length_b1_b3 = request.form.get("distance_to_consumer_l2")
  ps1 = request.form.get("required_output_pressures_p1")
  ps2 = request.form.get("required_output_pressures_p2")
  requested = request.form.get('selected_algorithm')

  try:
    if(requested == "de_best_1"):
        result = DE_Best_1(ps, length_b1_b2, length_b1_b3, ps1, ps2)
    elif(requested == "de_best_2"):
        result = DE_Best_2(ps, length_b1_b2, length_b1_b3, ps1, ps2)
    elif(requested == "de_current_best_1"):
        result = DE_Current_Best_1(ps, length_b1_b2, length_b1_b3, ps1, ps2)
    else:
        return jsonify({"status": 400, "message": "Your request method has not accepted!"}), 400
    return jsonify({"status": 200, "result": result, "message": "Successfuly!"}), 200
  except Exception as e:
    return jsonify({"error": str(e), "status": 500, "message": "Data failed to automated!"}), 500

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5000)