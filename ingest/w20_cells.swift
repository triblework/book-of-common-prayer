import Foundation
import Vision
import AppKit

// Wave 20: OCR many small rectangles of one page image, each on its own.
//   w20_cells <png> <rects.json> [scale=3]
// rects.json: [[x,y,w,h], ...] in pixels, origin top-left.
// Each rect is cut out, scaled up, set on a white margin (Vision reads an
// isolated short token -- "ii", "x" -- far better with space around it), and
// read with the Wave-17 settings (accurate, language correction OFF).
// stdout: JSON list, one entry per rect: {"t": all lines joined by " / ",
// "lines": [{"t","y"}]} with y relative to the rect, in page pixels.
let a = CommandLine.arguments
guard let img = NSImage(contentsOfFile: a[1]),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let rects = try! JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: a[2]))) as! [[Int]]
let S = a.count > 3 ? Double(a[3])! : 3.0
var out: [[String: Any]] = []
for r in rects {
    let rc = CGRect(x: r[0], y: r[1], width: r[2], height: r[3])
    guard let sub = cg.cropping(to: rc) else { out.append(["t": "", "lines": []]); continue }
    let m = 40.0
    let W = Int(Double(r[2]) * S + 2 * m), H = Int(Double(r[3]) * S + 2 * m)
    let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0,
                        space: CGColorSpaceCreateDeviceGray(), bitmapInfo: CGImageAlphaInfo.none.rawValue)!
    ctx.setFillColor(gray: 1, alpha: 1); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    ctx.interpolationQuality = .high
    ctx.draw(sub, in: CGRect(x: m, y: m, width: Double(r[2]) * S, height: Double(r[3]) * S))
    let im = ctx.makeImage()!
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    req.recognitionLanguages = ["en-US"]
    req.minimumTextHeight = 0
    try? VNImageRequestHandler(cgImage: im, options: [:]).perform([req])
    var lines: [[String: Any]] = []
    for obs in (req.results ?? []) {
        guard let c = obs.topCandidates(1).first else { continue }
        let yy = ((1 - obs.boundingBox.maxY) * Double(H) - m) / S
        lines.append(["t": c.string, "y": Int(yy)])
    }
    lines.sort { ($0["y"] as! Int) < ($1["y"] as! Int) }
    out.append(["t": lines.map { $0["t"] as! String }.joined(separator: " / "), "lines": lines])
}
FileHandle.standardOutput.write(try! JSONSerialization.data(withJSONObject: out))
FileHandle.standardOutput.write("\n".data(using: .utf8)!)
