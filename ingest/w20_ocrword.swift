import Foundation
import Vision
import AppKit

// Wave 20: OCR with WORD geometry. One JSON object per image on stdout,
//   {"path":…, "w":…, "h":…, "words":[{"t":…, "x":…, "y":…, "w":…, "h":…, "line":n}]}
// Same settings as w17_ocrbox (accurate, language correction OFF), but every
// whitespace-separated token gets its own box, so a table cell can be placed
// in its column by x even when Vision merges a whole table row into one
// observation. Pixels, origin TOP-LEFT.
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let W = Double(cg.width), H = Double(cg.height)
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    req.recognitionLanguages = ["en-US"]
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    var words: [[String: Any]] = []
    for (n, obs) in (req.results ?? []).enumerated() {
        guard let c = obs.topCandidates(1).first else { continue }
        let s = c.string
        var i = s.startIndex
        while i < s.endIndex {
            while i < s.endIndex && s[i] == " " { i = s.index(after: i) }
            if i >= s.endIndex { break }
            var j = i
            while j < s.endIndex && s[j] != " " { j = s.index(after: j) }
            if let rb = try? c.boundingBox(for: i..<j) {
                let b = rb.boundingBox
                words.append(["t": String(s[i..<j]), "line": n,
                               "x": Int(b.minX * W), "w": Int(b.width * W),
                               "y": Int((1 - b.maxY) * H), "h": Int(b.height * H)])
            }
            i = j
        }
    }
    let obj: [String: Any] = ["path": path, "w": Int(W), "h": Int(H), "words": words]
    let data = try! JSONSerialization.data(withJSONObject: obj)
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write("\n".data(using: .utf8)!)
}
