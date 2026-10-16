import Foundation
import Vision
import AppKit
import CoreML

// Workstream C: OCR with LINE and WORD geometry in one pass.
//   w22_ocr page.png [page2.png ...]
// One JSON object per image on stdout:
//   {"path":…, "w":…, "h":…,
//    "lines":[{"t":…, "x":…, "y":…, "w":…, "h":…,
//              "words":[[t, x, y, w, h], …]}]}
// Settings are Wave 17's (accurate, language correction OFF, en-US), so the
// page's own spelling survives. Word boxes come from Vision's own
// boundingBox(for:) over each whitespace-separated token of the line, as in
// w20_ocrword.swift. Pixels, origin TOP-LEFT.
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        FileHandle.standardError.write("cannot read \(path)\n".data(using: .utf8)!)
        continue
    }
    let W = Double(cg.width), H = Double(cg.height)
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    req.recognitionLanguages = ["en-US"]
    // W22_CPU=1 runs the model on the CPU, off the shared Neural Engine queue
    // (other sessions' OCR runs serialize there). Same model, same settings.
    if ProcessInfo.processInfo.environment["W22_CPU"] == "1" {
        if let devs = try? req.supportedComputeStageDevices[.main],
           let cpu = devs.first(where: { if case .cpu = $0 { return true }; return false }) {
            req.setComputeDevice(cpu, for: .main)
        }
    }
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    var lines: [[String: Any]] = []
    for obs in (req.results ?? []) {
        guard let c = obs.topCandidates(1).first else { continue }
        let s = c.string
        let b = obs.boundingBox
        var words: [[Any]] = []
        var i = s.startIndex
        while i < s.endIndex {
            while i < s.endIndex && s[i] == " " { i = s.index(after: i) }
            if i >= s.endIndex { break }
            var j = i
            while j < s.endIndex && s[j] != " " { j = s.index(after: j) }
            if let rb = try? c.boundingBox(for: i..<j) {
                let wb = rb.boundingBox
                words.append([String(s[i..<j]), Int(wb.minX * W), Int((1 - wb.maxY) * H),
                              Int(wb.width * W), Int(wb.height * H)])
            }
            i = j
        }
        lines.append(["t": s,
                      "x": Int(b.minX * W), "w": Int(b.width * W),
                      "y": Int((1 - b.maxY) * H), "h": Int(b.height * H),
                      "words": words])
    }
    lines.sort { ($0["y"] as! Int) < ($1["y"] as! Int) }
    let obj: [String: Any] = ["path": path, "w": Int(W), "h": Int(H), "lines": lines]
    let data = try! JSONSerialization.data(withJSONObject: obj)
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write("\n".data(using: .utf8)!)
}
