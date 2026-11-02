import SwiftUI
import Combine
import WatchConnectivity
import WatchKit

struct BoardTurn: Decodable, Sendable {
    var queue_place: Int?
}

struct BoardCall: Decodable, Sendable {
    var position: String?
    var turns: [BoardTurn]?
}

struct BoardState: Decodable, Sendable {
    var generated: String?
    var calls: [BoardCall]?
}

final class PhoneLink: NSObject, ObservableObject, WCSessionDelegate {
    @Published var active = false
    @Published var reachable = false

    override init() {
        super.init()
        guard WCSession.isSupported() else { return }
        let session = WCSession.default
        session.delegate = self
        session.activate()
    }

    func session(
        _ session: WCSession,
        activationDidCompleteWith state: WCSessionActivationState,
        error: Error?
    ) {
        update(session)
    }

    func sessionReachabilityDidChange(_ session: WCSession) {
        update(session)
    }

    private func update(_ session: WCSession) {
        DispatchQueue.main.async {
            self.active = session.activationState == .activated
            self.reachable = session.isReachable
        }
    }
}

struct ContentView: View {
    @AppStorage("boardHost") private var host =
        "192.168.68.53"
    @State private var place = "N/A"
    @State private var sub = "starting…"
    @State private var diag = ""
    @State private var showSettings = false
    @State private var flash = false
    @StateObject private var phone = PhoneLink()

    private let timer = Timer.publish(
        every: 5, on: .main, in: .common
    ).autoconnect()
    private let blinkTimer = Timer.publish(
        every: 0.6, on: .main, in: .common
    ).autoconnect()

    private var isYourTurn: Bool {
        place == "0"
    }

    private var boardURL: URL? {
        URL(string: "http://\(host):5173/board-state.json")
    }

    private var phoneStatus: String {
        let link = phone.active ? "active" : "inactive"
        let reach = phone.reachable ? "reachable" : "unreachable"
        return "phone: \(link) · \(reach)"
    }

    var body: some View {
        VStack {
            Text(place)
                .font(.system(size: 64, weight: .bold))
                .opacity(isYourTurn ? (flash ? 1.0 : 0.3) : 1.0)
            Text(sub)
                .font(.footnote)
                .foregroundColor(.secondary)
            if !diag.isEmpty {
                Text(diag)
                    .font(.caption2)
                    .foregroundColor(.gray)
            }
            HStack {
                Button("server") { showSettings = true }
                Button("test") { testConnection() }
            }
            .font(.footnote)
        }
        .sheet(isPresented: $showSettings) {
            VStack {
                Text("Board host")
                    .font(.headline)
                TextField("host", text: $host)
                Text("Debug")
                    .font(.headline)
                Text(boardURL?.absoluteString ?? "bad URL")
                    .font(.caption2)
                    .foregroundColor(.gray)
                Text(diag.isEmpty ? "no test yet" : diag)
                    .font(.caption2)
                    .foregroundColor(.gray)
                Text("poll every 5s")
                    .font(.caption2)
                    .foregroundColor(.gray)
                Text(phoneStatus)
                    .font(.caption2)
                    .foregroundColor(.gray)
                Button("Done") { showSettings = false }
            }
            .padding()
        }
        .onReceive(timer) { _ in refresh() }
        .onReceive(blinkTimer) { _ in flash.toggle() }
        .onAppear { refresh() }
    }

    private nonisolated func reason(_ error: Error?) -> String {
        guard
            let urlError = error as? URLError
        else {
            return "bad data"
        }
        switch urlError.code {
        case .timedOut:
            return "timeout"
        case .cannotFindHost:
            return "no host"
        case .cannotConnectToHost:
            return "no server"
        case .networkConnectionLost:
            return "lost"
        default:
            return "error \(urlError.code.rawValue)"
        }
    }

    private func testConnection() {
        guard let url = boardURL else {
            diag = "FAIL · bad URL"
            return
        }
        diag = "testing \(host)…"
        let config = URLSessionConfiguration.ephemeral
        config.timeoutIntervalForRequest = 5
        let started = Date()
        URLSession(configuration: config).dataTask(
            with: url
        ) { data, _, error in
            let ms = Int(Date().timeIntervalSince(started) * 1000)
            let why = reason(error)
            Task { @MainActor in
                guard
                    let data = data,
                    let board = try? JSONDecoder().decode(
                        BoardState.self, from: data
                    )
                else {
                    self.diag = "FAIL · \(self.host) · \(why)"
                    return
                }
                let n = board.calls?.count ?? 0
                self.diag = "OK · \(self.host) · \(ms)ms · \(n)calls"
            }
        }.resume()
    }

    private func refresh() {
        guard let url = boardURL else { return }
        URLSession.shared.dataTask(with: url) { data, _, _ in
            Task { @MainActor in
                guard
                    let data = data,
                    let board = try? JSONDecoder().decode(
                        BoardState.self, from: data
                    ),
                    let live = board.calls?.last
                else {
                    self.place = "N/A"
                    self.sub = "board unreachable"
                    return
                }
                let turn = live.turns?.reversed().first {
                    $0.queue_place != nil
                }
                if let p = turn?.queue_place {
                    let was = self.isYourTurn
                    self.place = String(p)
                    self.sub = p == 0 ? "YOUR TURN" : "in queue"
                    if !was && self.isYourTurn {
                        WKInterfaceDevice.current().play(.success)
                    }
                } else {
                    self.place = "N/A"
                    self.sub = "\(live.position ?? "")"
                }
            }
        }.resume()
    }
}
