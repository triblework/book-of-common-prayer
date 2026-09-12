import Foundation
import Vision
import AppKit

// OCR with geometry: one JSON object per image on stdout,
//   {"path":…, "w":…, "h":…, "lines":[{"t":…, "x":…, "y":…, "w":…, "h":…}]}
// Coordinates are in PIXELS with the origin at the TOP-LEFT (Vision reports
// bottom-left normalized boxes; they are converted here).
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let W = Double(cg.width), H = Double(cg.height)
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    req.recognitionLanguages = ["en-US"]
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    var lines: [[String: Any]] = []
    for obs in (req.results ?? []) {
        guard let c = obs.topCandidates(1).first else { continue }
        let b = obs.boundingBox
        lines.append(["t": c.string,
                      "x": Int(b.minX * W), "w": Int(b.width * W),
                      "y": Int((1 - b.maxY) * H), "h": Int(b.height * H)])
    }
    let obj: [String: Any] = ["path": path, "w": Int(W), "h": Int(H), "lines": lines]
    let data = try! JSONSerialization.data(withJSONObject: obj)
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write("\n".data(using: .utf8)!)
}
