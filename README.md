# Seat Optimizer

Ever wondered how few seat swaps it takes for everyone at a table to have sat next to everyone else?

This tool finds out. Given `n` people seated at a rectangular table (two rows facing each other), it computes a minimal sequence of seat swaps so that every person ends up sitting next to every other person at least once.

Neighbor relationships are tracked using bitmasks for efficiency. At each step the algorithm greedily picks the swap that creates the most new neighbor connections.

A Flask web app (`app.py`) serves the optimizer at **[seatoptimizer.wilhelm-daniel.de](https://seatoptimizer.wilhelm-daniel.de)**, where you can interactively configure the table size and step through the generated swap sequence.

## Usage

**Web:** visit [seatoptimizer.wilhelm-daniel.de](https://seatoptimizer.wilhelm-daniel.de)

**CLI:**
```bash
python main.py
```

Set `n_per_side` in `main.py` to the number of seats per side (default: 9 → 18 people total).
