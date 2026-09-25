import Foundation
import AppKit

// Wave 20: deskew a scanned table and find its printed RULES.
//   w20_grid <png> [out.png]
// Searches rotations in [-1.5, 1.5] degrees (step 0.05) for the one that makes
// the longest vertical dark runs longest (a printed column rule is straight),
// writes the deskewed page to out.png if given, and prints JSON
//   {"w","h","angle","vruns":[[x0,x1,len]],"hruns":[[y0,y1,len]]}
// vruns: columns whose longest vertical dark run is >= 8% of the height;
// hruns: rows whose longest horizontal dark run is >= 25% of the width.
let a = CommandLine.arguments
guard let img = NSImage(contentsOfFile: a[1]),
      let cg0 = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let W = cg0.width, H = cg0.height, thr = 128

func raster(_ deg: Double) -> [UInt8] {
    var px = [UInt8](repeating: 255, count: W * H)
    let ctx = CGContext(data: &px, width: W, height: H, bitsPerComponent: 8, bytesPerRow: W,
                        space: CGColorSpaceCreateDeviceGray(), bitmapInfo: CGImageAlphaInfo.none.rawValue)!
    ctx.setFillColor(gray: 1, alpha: 1); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    ctx.translateBy(x: CGFloat(W) / 2, y: CGFloat(H) / 2)
    ctx.rotate(by: CGFloat(deg * Double.pi / 180))
    ctx.translateBy(x: -CGFloat(W) / 2, y: -CGFloat(H) / 2)
    ctx.interpolationQuality = .high
    ctx.draw(cg0, in: CGRect(x: 0, y: 0, width: W, height: H))
    return px
}
func colBest(_ px: [UInt8]) -> [Int] {
    var out = [Int](repeating: 0, count: W)
    for x in 0..<W { var run = 0, best = 0
        for y in 0..<H { if Int(px[y * W + x]) < thr { run += 1; if run > best { best = run } } else { run = 0 } }
        out[x] = best }
    return out
}
func score(_ c: [Int]) -> Int { c.sorted(by: >).prefix(12).reduce(0, +) }

// coarse-to-fine search on a downsampled idea is unnecessary at this size
var best = 0.0, bestS = -1
var d = -1.5
while d <= 1.5001 { let s = score(colBest(raster(d))); if s > bestS { bestS = s; best = d }; d += 0.1 }
var f = best - 0.1
while f <= best + 0.1001 { let s = score(colBest(raster(f))); if s > bestS { bestS = s; best = f }; f += 0.025 }
let px = raster(best)
let cb = colBest(px)
var rowBest = [Int](repeating: 0, count: H)
for y in 0..<H { var run = 0, b = 0
    for x in 0..<W { if Int(px[y * W + x]) < thr { run += 1; if run > b { b = run } } else { run = 0 } }
    rowBest[y] = b }
func runs(_ v: [Int], _ minLen: Int) -> [[Int]] {
    var out: [[Int]] = []; var i = 0
    while i < v.count { if v[i] >= minLen { var j = i; var m = 0
            while j < v.count && v[j] >= minLen { m = max(m, v[j]); j += 1 }
            out.append([i, j - 1, m]); i = j } else { i += 1 } }
    return out }
if a.count > 2 {
    var p = px
    let ctx = CGContext(data: &p, width: W, height: H, bitsPerComponent: 8, bytesPerRow: W,
                        space: CGColorSpaceCreateDeviceGray(), bitmapInfo: CGImageAlphaInfo.none.rawValue)!
    let rep = NSBitmapImageRep(cgImage: ctx.makeImage()!)
    try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[2]))
}
let obj: [String: Any] = ["w": W, "h": H, "angle": (best * 1000).rounded() / 1000,
                          "vruns": runs(cb, H * 8 / 100), "hruns": runs(rowBest, W * 25 / 100)]
FileHandle.standardOutput.write(try! JSONSerialization.data(withJSONObject: obj))
FileHandle.standardOutput.write("\n".data(using: .utf8)!)
