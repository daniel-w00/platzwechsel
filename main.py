from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SeatingState:
    # Aktuelle Sitzordnung (0-11 für Personen 1-12)
    current_arrangement: List[int]
    # Für jede Person ein Integer, dessen Bits die Nachbarhistorie repräsentieren
    neighbor_history: List[int]
    # Liste der durchgeführten Tauschoperationen als Tupel (pos1, pos2)
    swap_history_of_positions: List[Tuple[int, int]]
    swap_history_of_persons: List[Tuple[int, int]]


class SeatingOptimizer:
    def __init__(self, n_per_side: int = 6):
        self.n_per_side = n_per_side
        self.total_seats = 2 * n_per_side

        # Initial arrangement: 0-5 on one side, 6-11 on other side (0-based)
        self.initial_state = SeatingState(
            current_arrangement=list(range(self.total_seats)),
            neighbor_history=[1 << i for i in range(self.total_seats)], # Jeder Int ist eine Bitmask mit sich selbst als Nachbar
            swap_history_of_positions=[],
            swap_history_of_persons=[]
        )


        # Pre-compute neighbor indices for each position
        self.neighbor_indices = self._compute_start_neighbor_indices()

        # Pre-compute required neighbors for each position as bitmasks
        self.required_neighbor_masks = self._compute_required_neighbors()

        # Initialize the initial neighbor relationships
        self._update_neighbor_history(self.initial_state)

        # Initialize state history with the initial state
        self.state_history = [self.initial_state]

    def _compute_start_neighbor_indices(self) -> List[List[int]]:
        """Berechnet die Nachbarpositionen für jede Sitzposition."""
        neighbor_indices = []
        for pos in range(self.total_seats):
            row_pos = pos % self.n_per_side
            neighbors = []

            # Check if the seat is on the edge
            if row_pos == 0:  # Left edge
                neighbors.append((pos + 1) % self.total_seats)
                neighbors.append((pos + self.n_per_side) % self.total_seats)
                neighbors.append((pos + self.n_per_side + 1) % self.total_seats)
            elif row_pos == self.n_per_side - 1:  # Right edge
                neighbors.append((pos - 1) % self.total_seats)
                neighbors.append((pos + self.n_per_side - 1) % self.total_seats)
                neighbors.append((pos + self.n_per_side) % self.total_seats)
            else:  # Middle positions
                neighbors.append((pos - 1) % self.total_seats)
                neighbors.append((pos + 1) % self.total_seats)
                neighbors.append((pos + self.n_per_side - 1) % self.total_seats)
                neighbors.append((pos + self.n_per_side) % self.total_seats)
                neighbors.append((pos + self.n_per_side + 1) % self.total_seats)

            neighbor_indices.append(neighbors)
        return neighbor_indices

    def _compute_required_neighbors(self) -> List[int]:
        """Berechnet für jede Position die Bitmask der möglichen Nachbarn."""
        masks = []
        for pos in range(self.total_seats):
            row_pos = pos % self.n_per_side
            # Mittlere Position (5 Nachbarn) vs. Randposition (3 Nachbarn)
            if 0 < row_pos < self.n_per_side - 1:
                # Beispiel: 0b11111 für 5 Nachbarn
                mask = (1 << 5) - 1
            else:
                # Beispiel: 0b111 für 3 Nachbarn
                mask = (1 << 3) - 1
            masks.append(mask)
        return masks

    def update_neighbor_history_for_swap(self, state: SeatingState, pos1: int, pos2: int) -> None:
        """Aktualisiert die Nachbarhistorie für die Personen an pos1, pos2 und deren Nachbarn."""
        positions_to_update = set([pos1, pos2])
        positions_to_update.update(self.neighbor_indices[pos1])
        positions_to_update.update(self.neighbor_indices[pos2])

        for pos in positions_to_update:
            person = state.current_arrangement[pos]
            neighbor_mask = 0
            for n_pos in self.neighbor_indices[pos]:
                neighbor = state.current_arrangement[n_pos]
                neighbor_mask |= (1 << neighbor)
            state.neighbor_history[person] |= neighbor_mask

    def update_neighbor_history_for_swap_by_person(self, state: SeatingState, person1: int, person2: int) -> None:
        """Aktualisiert die Nachbarhistorie für die Personen person1, person2 und deren Nachbarn."""
        pos1 = state.current_arrangement.index(person1)
        pos2 = state.current_arrangement.index(person2)
        self.update_neighbor_history_for_swap(state, pos1, pos2)

    def _update_neighbor_history(self, state: SeatingState) -> None:
        """Aktualisiert die Nachbarhistorie mittels Bitoperationen."""
        for pos, person in enumerate(state.current_arrangement):
            neighbor_mask = 0
            # Für jede Nachbarposition
            for n_pos in self.neighbor_indices[pos]:
                neighbor = state.current_arrangement[n_pos]
                # Setze das entsprechende Bit für diesen Nachbarn
                # Beispiel: neighbor=3 → 1 << 3 = 0b1000
                neighbor_mask |= (1 << neighbor)
            # Kombiniere neue Nachbarn mit bisheriger Historie durch OR
            state.neighbor_history[person] |= neighbor_mask

    def is_complete(self, state: SeatingState) -> bool:
        """Prüft ob alle erforderlichen Nachbarschaften erfüllt sind."""
        return sum(history.bit_count() for history in state.neighbor_history) == self.total_seats **2

    def swap_positions(self, pos1: int, pos2: int) -> SeatingState:
        """Erzeugt einen neuen Zustand mit getauschten Positionen."""

        state = self.state_history[-1]
        new_arrangement = state.current_arrangement.copy()
        new_arrangement[pos1], new_arrangement[pos2] = new_arrangement[pos2], new_arrangement[pos1]

        # Kopiere Nachbarhistorie (schnelle Integer-Liste)
        new_history = state.neighbor_history.copy()

        # Kopiere und erweitere Tauschhistorie
        new_swap_pos_history = state.swap_history_of_positions.copy()
        new_swap_pos_history.append((pos1, pos2))

        #kopiere und erweitere Tauschhistorie von Personen
        new_swap_person_history = state.swap_history_of_persons.copy()
        new_swap_person_history.append((new_arrangement[pos1], new_arrangement[pos2]))

        new_seating_state=  SeatingState(
            current_arrangement=new_arrangement,
            neighbor_history=state.neighbor_history.copy(), #not updated yet
            swap_history_of_positions=new_swap_pos_history,
            swap_history_of_persons=new_swap_person_history
        )
        self.update_neighbor_history_for_swap(new_seating_state, pos1, pos2)

        self.state_history.append(new_seating_state)

    def get_neighbor_count(self, state: SeatingState, person: int) -> int:
        """Gibt die Anzahl der bisherigen Nachbarn einer Person zurück."""
        # Zähle die gesetzten Bits in der Bitmask
        return bin(state.neighbor_history[person]).count('1')



    def find_best_swap(self, state: SeatingState) -> Tuple[int, int]:
        """Findet den besten Tausch, der die meisten neuen Nachbarschaften erzeugt."""
        best_swap = None
        max_new_connections = 0

        for pos1 in range(self.total_seats):
            for pos2 in range(pos1 + 1, self.total_seats):
                if pos2 == pos1 + self.n_per_side:
                    continue  # Skip swapping with pos1 + n_per_side

                # Simuliere den Tausch
                new_arrangement = state.current_arrangement.copy()
                new_arrangement[pos1], new_arrangement[pos2] = new_arrangement[pos2], new_arrangement[pos1]

                new_connections = 0
                # Berechne die neuen Nachbarschaften für pos1 und pos2
                for pos in [pos1, pos2]:
                    person = new_arrangement[pos]
                    for neighbor_pos in self.neighbor_indices[pos]:
                        neighbor = new_arrangement[neighbor_pos]
                        if not (state.neighbor_history[person] & (1 << neighbor)):
                            new_connections += 1

                # Überprüfe, ob dieser Tausch die meisten neuen Nachbarschaften erzeugt
                if new_connections > max_new_connections:
                    max_new_connections = new_connections
                    best_swap = (pos1, pos2)

                # Wenn 10 neue Nachbarschaften gefunden wurden, sofort zurückgeben
                if new_connections >= 10:
                    return best_swap

        return best_swap

    def print_pretty_seating_order(self, state: SeatingState, n_per_side: int) -> None:
        """Prints the current seating order in a pretty way with a new line after every n-th person."""
        print("Aktuelle Sitzordnung:")
        for i, person in enumerate(state.current_arrangement):
            print(f"{person + 1:2}", end=' ')
            if (i + 1) % self.n_per_side == 0:
                print()  # New line after every n_per_side persons
        print()  # Ensure the last line ends properly

    def print_state(self, state: SeatingState) -> None:
        """Gibt den aktuellen Zustand lesbar aus."""
        self.print_pretty_seating_order(state, self.n_per_side)
        print("Letzte Tauschoperationen:")
        if state.swap_history_of_positions:
            pos1, pos2 = state.swap_history_of_positions[-1]
            print(
                f"Personen {state.current_arrangement[pos1] + 1} ↔ {state.current_arrangement[pos2] + 1}  (Position {pos1 + 1} ↔ {pos2 + 1})")
        else:
            print("Keine Tauschoperationen durchgeführt.")

        print("Nachbarhistorie:")
        for person in range(self.total_seats):
            neighbors = []
            # Durchlaufe alle möglichen Nachbarn
            for n in range(self.total_seats):
                # Prüfe ob das entsprechende Bit gesetzt ist
                if state.neighbor_history[person] & (1 << n):
                    neighbors.append(n + 1)  # +1 für 1-basierte Ausgabe
            print(f"Person {person + 1} hatte Kontakt mit: {neighbors}")

    def print_all_states(self) -> None:
        """Prints all states in the order of the state history."""
        for i, state in enumerate(self.state_history):
            print(f"State {i }:")
            self.print_state(state)
            print("-" * 40)  # Separator between states
        print("Vollständig:", self.is_complete(self.state_history[-1]))

        #print how many swaps were needed
        print("Anzahl Tauschoperationen:", len(self.state_history[-1].swap_history_of_positions))


def test_swapping():
    optimizer = SeatingOptimizer(n_per_side=4)

    # Perform swaps
    optimizer.swap_positions(0, 3)
    optimizer.swap_positions(3, 4)
    optimizer.swap_positions(4, 7)

    # Print all states
    optimizer.print_all_states()

def optimize_seating(optimizer: SeatingOptimizer) -> None:
    """Executes the best swaps until the seating arrangement is complete."""
    while not optimizer.is_complete(optimizer.state_history[-1]):
        best_swap = optimizer.find_best_swap(optimizer.state_history[-1])
        if best_swap is None:
            raise ValueError("No more swaps can improve the seating arrangement.")
            break  # No more swaps can improve the arrangement
        optimizer.swap_positions(*best_swap)

    # Print all states after optimization
    optimizer.print_all_states()




if __name__ == "__main__":
    optimizer = SeatingOptimizer(n_per_side=6)

    optimize_seating(optimizer)

