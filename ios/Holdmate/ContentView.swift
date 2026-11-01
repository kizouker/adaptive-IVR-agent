import SwiftUI

// Minimal ticket view (PoC #146): polls the Mac board server and shows the
// latest queue place. Board URL: same host as the simulator (localhost works).

struct BoardTurn: Decodable {
    var queue_place: Int?
    var queue_total: Int?
    var state: String?
}

struct BoardCall: Decodable {
    var position: String?
    var turns: [BoardTurn]?
}

struct BoardState: Decodable {
    var generated: String?
    var calls: [BoardCall]?
}

struct ContentView: View {
    @State private var place: String = "-"
    @State private var sub: String = "starting…"
    private let timer = Timer.publish(every: 5, on: .main, in: .common).autoconnect()

    var body: some View {
        VStack(spacing: 8) {
            Text(place)
                .font(.system(size: 120, weight: .bold))
            Text(sub)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding()
        .onReceive(timer) { _ in refresh() }
        .onAppear { refresh() }
    }

    private func refresh() {
        guard let url = URL(string: "http://localhost:5173/board-state.json") else { return }
        URLSession.shared.dataTask(with: url) { data, _, _ in
            guard let data = data,
                  let board = try? JSONDecoder().decode(BoardState.self, from: data),
                  let live = board.calls?.last else {
                DispatchQueue.main.async { self.place = "-"; self.sub = "board unreachable" }
                return
            }
            let turn = live.turns?.reversed().first { $0.queue_place != nil }
            DispatchQueue.main.async {
                if let p = turn?.queue_place {
                    self.place = String(p)
                    let total = turn?.queue_total.map { "/\($0)" } ?? ""
                    self.sub = "in queue\(total) · \(board.generated ?? "")"
                } else {
                    self.place = "-"
                    self.sub = "\(live.position ?? "") · \(board.generated ?? "")"
                }
            }
        }.resume()
    }
}
