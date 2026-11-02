import SwiftUI
import Combine
import Darwin
import UIKit
import WatchConnectivity

// Minimal ticket view (PoC #146): polls the Mac board server and shows the
// latest queue place. Host is editable in-app (.local default works on
// simulator and on a real device on the same WiFi; server always listens on LAN).

struct BoardTurn: Decodable, Sendable {
    var queue_place: Int?
    var queue_total: Int?
    var state: String?
}

struct BoardCall: Decodable, Sendable {
    var position: String?
    var turns: [BoardTurn]?
}

struct BoardState: Decodable, Sendable {
    var generated: String?
    var calls: [BoardCall]?
}

final class WatchLink: NSObject, ObservableObject, WCSessionDelegate {
    @Published var paired = false
    @Published var reachable = false
    var onStatus: ((Bool, Bool, Bool) -> Void)?
    private var readyFired = false

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
        if !readyFired {
            readyFired = true
            onStatus?(
                session.isPaired,
                session.isReachable,
                session.isWatchAppInstalled
            )
        }
    }

    func sessionReachabilityDidChange(_ session: WCSession) {
        update(session)
    }

    func sessionDidBecomeInactive(_ session: WCSession) {}

    func sessionDidDeactivate(_ session: WCSession) {}

    private func update(_ session: WCSession) {
        DispatchQueue.main.async {
            self.paired = session.isPaired
            self.reachable = session.isReachable
        }
    }
}

func debuggerAttached() -> Bool {
    var info = kinfo_proc()
    var size = MemoryLayout<kinfo_proc>.stride
    var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid()]
    let status = sysctl(&mib, UInt32(mib.count), &info, &size, nil, 0)
    guard status == 0 else { return false }
    return (info.kp_proc.p_flag & P_TRACED) != 0
}

struct ContentView: View {
    @AppStorage("boardHost") private var host =
        "ricks-mbp-m4.local"
    @State private var place: String = "N/A"
    @State private var sub: String = ""
    @State private var detail: String = "waiting for board…"
    @State private var diag: String = ""
    @State private var showSettings = false
    @State private var debugOpen = false
    @State private var flash = false
    @State private var connected = false
    @StateObject private var watch = WatchLink()

    private let timer = Timer.publish(
        every: 5, on: .main, in: .common
    ).autoconnect()
    private let blinkTimer = Timer.publish(
        every: 0.6, on: .main, in: .common
    ).autoconnect()

    private var boardURL: URL? {
        URL(string: "http://\(host):5173/board-state.json")
    }

    private var watchStatus: String {
        let pair = watch.paired ? "paired" : "not paired"
        let reach = watch.reachable ? "reachable" : "unreachable"
        return "watch: \(pair) · \(reach)"
    }

    private var isYourTurn: Bool {
        place == "0" && !connected
    }

    private var inQueue: Bool {
        place != "N/A" && !isYourTurn && !connected
    }

    private var statusColor: Color {
        if connected || isYourTurn {
            return .green
        }
        if inQueue {
            return .teal
        }
        return .primary
    }

    private var statusTint: Color {
        if connected || isYourTurn {
            return .green.opacity(0.12)
        }
        if inQueue {
            return .teal.opacity(0.08)
        }
        return .gray.opacity(0.08)
    }

    var body: some View {
        VStack(spacing: 16) {
            VStack(spacing: 8) {
                Text(place)
                    .font(.system(size: 120, weight: .bold))
                    .foregroundColor(statusColor)
                    .opacity(isYourTurn ? (flash ? 1.0 : 0.3) : 1.0)
                if !sub.isEmpty {
                    Text(sub)
                        .font(.title3)
                        .foregroundColor(.secondary)
                }
            }
            .padding(32)
            .background(
                RoundedRectangle(cornerRadius: 24).fill(statusTint)
            )
            HStack(spacing: 24) {
                Button("server") { showSettings = true }
                Button("test") { testConnection() }
            }
            .font(.title2)
            .buttonStyle(.bordered)
        }
        .padding()
        .sheet(isPresented: $showSettings) {
            NavigationStack {
                Form {
                    Section("Server") {
                        TextField("host", text: $host)
                            .font(.system(.body, design: .monospaced))
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                    }
                    Section("Details") {
                        Text(detail)
                            .font(.system(.callout, design: .monospaced))
                            .foregroundColor(.gray)
                    }
                    DisclosureGroup("Debug", isExpanded: $debugOpen) {
                        Text(boardURL?.absoluteString ?? "bad URL")
                        Text(diag.isEmpty ? "no test yet" : diag)
                        Text(watchStatus)
                        Text("poll every 5s")
                    }
                    .font(.system(.callout, design: .monospaced))
                    .foregroundColor(.gray)
                }
                .navigationTitle("Board host")
                .toolbar {
                    Button("Done") { showSettings = false }
                }
            }
        }
        .onReceive(timer) { _ in refresh() }
        .onReceive(blinkTimer) { _ in flash.toggle() }
        .onAppear { startupDiagnostics(); refresh() }
    }

    private func reason(_ error: Error?) -> String {
        guard let urlError = error as? URLError else {
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

    private func probeBoard(completion: @escaping (String) -> Void) {
        guard let url = boardURL else {
            completion("FAIL · bad URL")
            return
        }
        let config = URLSessionConfiguration.ephemeral
        config.timeoutIntervalForRequest = 5
        let started = Date()
        let usedHost = host
        URLSession(configuration: config).dataTask(
            with: url
        ) { data, _, error in
            let ms = Int(Date().timeIntervalSince(started) * 1000)
            guard
                let data = data,
                let board = try? JSONDecoder().decode(
                    BoardState.self, from: data
                )
            else {
                completion("FAIL · \(usedHost) · \(reason(error))")
                return
            }
            let n = board.calls?.count ?? 0
            completion("OK · \(usedHost) · \(ms)ms · \(n)calls")
        }.resume()
    }

    private func testConnection() {
        guard boardURL != nil else {
            diag = "FAIL · bad URL"
            return
        }
        diag = "testing \(host)…"
        probeBoard { result in
            DispatchQueue.main.async {
                self.diag = result
            }
        }
    }

    private func startupDiagnostics() {
        let cable = debuggerAttached()
            ? "OK (debugger attached)"
            : "NO (not run via Xcode)"
        print("[Holdmate] 1. cable: \(cable)")
        watch.onStatus = { paired, reachable, installed in
            print("[Holdmate] 2. watch: paired=\(paired) reachable=\(reachable)")
            print("[Holdmate] 3. watch app installed: \(installed)")
            self.probeBoard { result in
                print("[Holdmate] 4. board: \(result)")
            }
        }
    }

    private func refresh() {
        guard let url = boardURL else { return }
        URLSession.shared.dataTask(with: url) { data, _, _ in
            guard
                let data = data,
                let board = try? JSONDecoder().decode(
                    BoardState.self, from: data
                ),
                let live = board.calls?.last
            else {
                DispatchQueue.main.async {
                    self.connected = false
                    self.place = "N/A"
                    self.sub = "board unreachable"
                    self.detail = "board unreachable"
                }
                return
            }
            let turn = live.turns?.reversed().first {
                $0.queue_place != nil
            }
            DispatchQueue.main.async {
                if live.position == "officer" {
                    self.connected = true
                    self.place = "✓"
                    self.sub = "connected to officer"
                    self.detail = "connected to officer"
                } else if let p = turn?.queue_place {
                    self.connected = false
                    let was = self.isYourTurn
                    self.place = String(p)
                    let total = turn?.queue_total.map { "/\($0)" } ?? ""
                    self.detail = "in queue\(total) · \(board.generated ?? "")"
                    self.sub = p == 0 ? "YOUR TURN — answer now" : ""
                    if !was && self.isYourTurn {
                        UINotificationFeedbackGenerator().notificationOccurred(.success)
                    }
                } else {
                    self.connected = false
                    self.place = "N/A"
                    self.sub = ""
                    self.detail = "\(live.position ?? "") · \(board.generated ?? "")"
                }
            }
        }.resume()
    }
}
