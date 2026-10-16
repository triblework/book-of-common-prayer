import Foundation
import AppKit

// Workstream C: a LABELLED strip of crops for reading pointing by eye.
//   w22_strip out.png spec.json [scale=1] [cols=1]
// spec.json: [{"label": "2:5 p358\nwrath | and", "png": "<page render>",
//              "rect": [x,y,w,h], "caret": x (optional)}, ...]
// Each item is cut out of its page render at `rect` (pixels, origin top-left),
// drawn at `scale`, with its label (one or more lines) set in a left gutter.
// The label names the two words the mark to be read falls BETWEEN (never the
// cell's mark itself). `caret` (a page x-coordinate) draws a small grey caret
// in a band BELOW the crop; it is optional because Vision's word boxes are
// estimated within a line and can be 30-70px off, so a caret can mislead.
// `cols` lays the items out in that many columns, top to bottom then left to
// right, so a strip stays near square and is shown at a larger scale.
// Wave 20's w20_strip stacks crops with a rule between them and no label;
// this adds the labels and the columns, nothing else.
let a = CommandLine.arguments
let spec = try! JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: a[2]))) as! [[String: Any]]
let S = a.count > 3 ? Double(a[3])! : 1.0
let C = a.count > 4 ? max(1, Int(a[4])!) : 1
let gutter = 360.0, gap = 12.0, colgap = 40.0
let band = spec.contains(where: { $0["caret"] != nil }) ? 26.0 : 0.0
var cache: [String: CGImage] = [:]
func page(_ p: String) -> CGImage? {
    if let c = cache[p] { return c }
    guard let im = NSImage(contentsOfFile: p)?.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return nil }
    cache[p] = im; return im
}
var items: [(String, CGImage?, Double, Double, Double?)] = []
for it in spec {
    let r = it["rect"] as! [Int]
    let sub = page(it["png"] as! String)?.cropping(to: CGRect(x: r[0], y: r[1], width: r[2], height: r[3]))
    let caret = (it["caret"] as? Int).map { Double($0 - r[0]) * S }
    items.append((it["label"] as? String ?? "", sub, Double(r[2]) * S, Double(r[3]) * S, caret))
}
let per = (items.count + C - 1) / C
var columns: [[(String, CGImage?, Double, Double, Double?)]] = []
for c in 0..<C {
    let lo = c * per, hi = min(items.count, lo + per)
    if lo < hi { columns.append(Array(items[lo..<hi])) }
}
let colW = columns.map { gutter + ($0.map { $0.2 }.max() ?? 1) }
let colH = columns.map { $0.map { $0.3 + band + gap }.reduce(0, +) }
let W = Int(colW.reduce(0, +) + colgap * Double(max(0, columns.count - 1)))
let H = Int(colH.max() ?? 1)
let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0,
                    space: CGColorSpaceCreateDeviceGray(), bitmapInfo: CGImageAlphaInfo.none.rawValue)!
ctx.setFillColor(gray: 1, alpha: 1); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
ctx.interpolationQuality = .high
NSGraphicsContext.current = NSGraphicsContext(cgContext: ctx, flipped: false)
let font = NSFont(name: "Helvetica-Bold", size: 30) ?? NSFont.boldSystemFont(ofSize: 30)
let font2 = NSFont(name: "Helvetica", size: 26) ?? NSFont.systemFont(ofSize: 26)
var x0 = 0.0
for (ci, col) in columns.enumerated() {
    var y = Double(H)
    for (label, im, w, h, caret) in col {
        y -= h
        if let im = im { ctx.draw(im, in: CGRect(x: x0 + gutter, y: y, width: w, height: h)) }
        let parts = label.components(separatedBy: "\n")
        var ly = y + h / 2 + Double(parts.count - 1) * 16 - 15
        for (k, part) in parts.enumerated() {
            let attrs: [NSAttributedString.Key: Any] = [.font: k == 0 ? font : font2,
                                                        .foregroundColor: NSColor.black]
            (part as NSString).draw(at: NSPoint(x: x0 + 12, y: ly), withAttributes: attrs)
            ly -= 34
        }
        y -= band
        if let cx = caret {
            ctx.setFillColor(gray: 0.45, alpha: 1)
            ctx.beginPath()
            ctx.move(to: CGPoint(x: x0 + gutter + cx, y: y + band - 3))
            ctx.addLine(to: CGPoint(x: x0 + gutter + cx - 14, y: y + 3))
            ctx.addLine(to: CGPoint(x: x0 + gutter + cx + 14, y: y + 3))
            ctx.closePath(); ctx.fillPath()
        }
        y -= gap
        ctx.setFillColor(gray: 0.6, alpha: 1)
        ctx.fill(CGRect(x: x0, y: y + 3, width: colW[ci], height: 2))
    }
    x0 += colW[ci] + colgap
}
let rep = NSBitmapImageRep(cgImage: ctx.makeImage()!)
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[1]))
