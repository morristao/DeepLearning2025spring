from flask import Flask, render_template, request, jsonify
import os
import random

app = Flask(__name__)

grid_size = 5
start = None
end = None
obstacles = set()

@app.route('/')
def index():
    return render_template('index.html', n=grid_size)

@app.route('/set_size', methods=['POST'])
def set_size():
    global grid_size, start, end, obstacles
    data = request.get_json()
    grid_size = int(data['size'])
    start = None
    end = None
    obstacles = set()
    return jsonify({'status': 'ok'})

@app.route('/click_cell', methods=['POST'])
def click_cell():
    global start, end, obstacles
    data = request.get_json()
    row, col = data['row'], data['col']
    cell = (row, col)

    if not start:
        start = cell
        return jsonify({'status': 'start'})
    elif not end and cell != start:
        end = cell
        return jsonify({'status': 'end'})
    elif len(obstacles) < grid_size - 2 and cell != start and cell != end and cell not in obstacles:
        obstacles.add(cell)
        return jsonify({'status': 'obstacle'})
    return jsonify({'status': 'none'})

@app.route('/get_state')
def get_state():
    policy_map = [[random.choice(['↑', '↓', '←', '→']) for _ in range(grid_size)] for _ in range(grid_size)]
    value_map = [[round(random.uniform(-3, 3), 2) for _ in range(grid_size)] for _ in range(grid_size)]


    return jsonify({
        'start': start,
        'end': end,
        'obstacles': list(obstacles),
        'size': grid_size,
        'policy': policy_map,
        'value': value_map
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    app.run(host='0.0.0.0', port=port, debug=True)
