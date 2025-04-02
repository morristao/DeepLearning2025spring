from flask import Flask, render_template, request, jsonify
import os
import random
import copy

app = Flask(__name__)

grid_size = 5
start = None
end = None
obstacles = set()
value_map = []
policy_map = []

gamma = 0.9  # discount factor
threshold = 1e-4
reward_step = -0.04
reward_goal = 1.0
reward_obstacle = -1.0

actions = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1)
}
action_symbols = {
    'U': '↑',
    'D': '↓',
    'L': '←',
    'R': '→'
}

def initialize_maps():
    global value_map, policy_map
    value_map = [[0.0 for _ in range(grid_size)] for _ in range(grid_size)]
    policy_map = [[random.choice(list(actions.keys())) for _ in range(grid_size)] for _ in range(grid_size)]

def in_bounds(r, c):
    return 0 <= r < grid_size and 0 <= c < grid_size

def is_terminal(r, c):
    return (r, c) == end

def is_obstacle(r, c):
    return (r, c) in obstacles

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
    initialize_maps()
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
    visual_policy = [[action_symbols.get(policy_map[i][j], '') for j in range(grid_size)] for i in range(grid_size)]
    return jsonify({
        'start': start,
        'end': end,
        'obstacles': list(obstacles),
        'size': grid_size,
        'policy': visual_policy,
        'value': value_map
    })

@app.route('/compute_policy', methods=['POST'])
def compute_policy():
    global value_map, policy_map

    def get_reward(r, c):
        if is_terminal(r, c):
            return reward_goal
        elif is_obstacle(r, c):
            return reward_obstacle
        return reward_step

    converged = False
    while not converged:
        delta = 0
        new_values = copy.deepcopy(value_map)
        for i in range(grid_size):
            for j in range(grid_size):
                if is_terminal(i, j) or is_obstacle(i, j):
                    continue

                best_value = float('-inf')
                best_action = None
                for a, (dr, dc) in actions.items():
                    ni, nj = i + dr, j + dc
                    if in_bounds(ni, nj) and not is_obstacle(ni, nj):
                        reward = get_reward(i, j)
                        value = reward + gamma * value_map[ni][nj]
                    else:
                        value = reward_step + gamma * value_map[i][j]  # stay in place if hitting wall/obstacle
                    if value > best_value:
                        best_value = value
                        best_action = a

                new_values[i][j] = best_value
                policy_map[i][j] = best_action
                delta = max(delta, abs(value_map[i][j] - best_value))

        value_map = new_values
        if delta < threshold:
            converged = True

    return jsonify({'status': 'policy updated'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    app.run(host='0.0.0.0', port=port, debug=True)

