from flask import Flask, render_template_string, request
import csv
from datetime import datetime
import os

app = Flask(__name__)

CSV_FILE = "records.csv"
PASSWORD = "aayushalovesayush"

template = """
<!doctype html>
<html>
<head>
  <title>Kisses Timer — Mrs. Shrestha</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f9fafb; color: #111; text-align: center; padding: 40px; }
    .box { max-width: 700px; margin: auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
    h1 { color: #2563eb; }
    button { padding: 8px 16px; margin: 4px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
    .start { background: #22c55e; color: white; }
    .stop { background: #ef4444; color: white; }
    .reset { background: #6b7280; color: white; }
    .save { background: #2563eb; color: white; }
    .delete { background: #dc2626; color: white; }
    .time { font-size: 32px; margin: 20px 0; font-weight: bold; }
    table { margin: 20px auto; border-collapse: collapse; width: 95%; }
    th, td { border: 1px solid #ccc; padding: 8px; }
    th { background: #2563eb; color: white; }
    input[type="password"] { padding: 4px; width: 120px; }
  </style>
</head>
<body>
  <div class="box">
    <h1>Kisses Timer — Mrs. Shrestha</h1>
    <div class="time" id="timer">00:00:00</div>

    <form method="post" id="stopForm">
      <input type="hidden" name="minutes" id="minutesInput" value="{{ result.minutes if result else '' }}">
      <button type="button" onclick="startTimer()" class="start">Start</button>
      <button type="button" onclick="stopTimer()" class="stop">Stop</button>
      <button type="button" onclick="resetTimer()" class="reset">Reset</button>
    </form>

    {% if result %}
      <h2>No. of kisses Mrs. Shrestha owes me = {{ result.total_with_tax }}</h2>
      <p>Husband Tax = 13% ({{ result.tax }} minutes)</p>
      <p>Raw Time = {{ result.minutes }} minutes</p>
      <form method="post">
        <input type="hidden" name="save_minutes" value="{{ result.minutes }}">
        <input type="hidden" name="save_tax" value="{{ result.tax }}">
        <input type="hidden" name="save_total" value="{{ result.total_with_tax }}">
        <button type="submit" name="action" value="save" class="save">Save Record</button>
      </form>
    {% endif %}

    {% if records %}
      <h3>Saved Records</h3>
      <table>
        <tr>
          <th>Date</th>
          <th>Raw Minutes</th>
          <th>Husband Tax</th>
          <th>Total Kisses</th>
          <th>Delete</th>
        </tr>
        {% for r in records %}
        <tr>
          <td>{{ r.date }}</td>
          <td>{{ r.minutes }}</td>
          <td>{{ r.tax }}</td>
          <td>{{ r.total }}</td>
          <td>
            <form method="post" style="display:inline;">
              <input type="hidden" name="delete_date" value="{{ r.date }}">
              <input type="password" name="password" placeholder="Password">
              <button type="submit" name="action" value="delete" class="delete">Delete</button>
            </form>
          </td>
        </tr>
        {% endfor %}
      </table>
    {% endif %}
  </div>

  <script>
    let startTime = null;
    let timerInterval = null;

    function updateTimer() {
      const now = new Date().getTime();
      const elapsed = now - startTime;
      const totalSeconds = Math.floor(elapsed / 1000);

      const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
      const minutes = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
      const seconds = String(totalSeconds % 60).padStart(2, '0');

      document.getElementById('timer').innerText = `${hours}:${minutes}:${seconds}`;
    }

    function startTimer() {
      if (!timerInterval) {
        startTime = new Date().getTime();
        timerInterval = setInterval(updateTimer, 1000);
      }
    }

    function stopTimer() {
      if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;

        const timerText = document.getElementById('timer').innerText;
        const parts = timerText.split(':');
        const totalMinutes = (parseInt(parts[0]) * 60) + parseInt(parts[1]) + (parseInt(parts[2]) / 60);

        document.getElementById('minutesInput').value = totalMinutes.toFixed(2);
        document.getElementById('stopForm').submit();
      }
    }

    function resetTimer() {
      clearInterval(timerInterval);
      timerInterval = null;
      document.getElementById('timer').innerText = "00:00:00";
    }
  </script>
</body>
</html>
"""

def read_records():
    records = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    return records

def save_record(minutes, tax, total):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date","minutes","tax","total"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "minutes": minutes,
            "tax": tax,
            "total": total
        })

def delete_record(delete_date):
    records = read_records()
    records = [r for r in records if r['date'] != delete_date]
    with open(CSV_FILE, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date","minutes","tax","total"])
        writer.writeheader()
        writer.writerows(records)

@app.route("/", methods=["GET","POST"])
def index():
    result = None
    records = read_records()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "save":
            save_record(
                request.form.get("save_minutes"),
                request.form.get("save_tax"),
                request.form.get("save_total")
            )
            records = read_records()
        elif action == "delete":
            password = request.form.get("password","")
            if password == PASSWORD:
                delete_date = request.form.get("delete_date")
                delete_record(delete_date)
                records = read_records()
        else:
            try:
                minutes = float(request.form.get("minutes", 0))
                tax = round(minutes * 0.13, 2)
                total_with_tax = round(minutes + tax)  # rounded total kisses
                result = {
                    "minutes": round(minutes,2),
                    "tax": tax,
                    "total_with_tax": total_with_tax
                }
            except:
                pass

    return render_template_string(template, result=result, records=records)

if __name__ == "__main__":
    app.run(debug=True)
