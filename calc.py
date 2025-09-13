from flask import Flask, render_template_string, request

app = Flask(__name__)

template = """
<!doctype html>
<html>
<head>
  <title>Kisses Timer — Mrs. Shrestha</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f9fafb; color: #111; text-align: center; padding: 40px; }
    .box { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
    h1 { color: #2563eb; }
    button { padding: 10px 20px; margin: 10px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
    .start { background: #22c55e; color: white; }
    .stop { background: #ef4444; color: white; }
    .reset { background: #6b7280; color: white; }
    .time { font-size: 32px; margin: 20px 0; font-weight: bold; }
  </style>
</head>
<body>
  <div class="box">
    <h1>Kisses Timer — Mrs. Shrestha</h1>
    <div class="time" id="timer">00:00:00</div>

    <form method="post" id="stopForm">
      <input type="hidden" name="minutes" id="minutesInput">
      <button type="button" onclick="startTimer()" class="start">Start</button>
      <button type="button" onclick="stopTimer()" class="stop">Stop</button>
      <button type="button" onclick="resetTimer()" class="reset">Reset</button>
    </form>

    {% if result %}
      <h2>No. of kisses Mrs. Shrestha owes me = {{ result.total_with_tax }}</h2>
      <p>Husband Tax = 13% ({{ result.tax }} minutes)</p>
      <p>Raw Time = {{ result.minutes }} minutes</p>
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

        // send elapsed minutes to server
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

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        try:
            minutes = float(request.form.get("minutes", 0))
            tax = round(minutes * 0.13, 2)
            total_with_tax = round(minutes + tax, 2)

            result = {
                "minutes": round(minutes, 2),
                "tax": tax,
                "total_with_tax": total_with_tax
            }
        except Exception:
            pass

    return render_template_string(template, result=result)

if __name__ == "__main__":
    app.run(debug=True)
