from flask import Flask, render_template, request, jsonify
from main import SeatingOptimizer  # Ihr bestehender Code

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/optimize', methods=['POST'])
def optimize():
    n_per_side = int(request.json['n_per_side'])
    optimizer = SeatingOptimizer(n_per_side=n_per_side)

    # Optimierung durchführen
    while not optimizer.is_complete(optimizer.state_history[-1]):
        best_swap = optimizer.find_best_swap(optimizer.state_history[-1])
        if best_swap is None:
            break
        optimizer.swap_positions(*best_swap)

    # Ergebnisse formatieren
    states = []
    for state in optimizer.state_history:
        states.append({
            'arrangement': state.current_arrangement,
            'swap': state.swap_history_of_persons[-1] if state.swap_history_of_persons else None
        })

    return jsonify({
        'states': states,
        'total_swaps': len(optimizer.state_history[-1].swap_history_of_positions)
    })


if __name__ == '__main__':
    app.run(debug=True)
