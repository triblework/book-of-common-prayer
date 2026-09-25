import Foundation
import AppKit

// Wave 20: stack several crops into ONE image, top to bottom, each with a
// thin rule under it, so a set of cells can be read by eye in one look.
//   w20_strip out.png a.png b.png ...
let a = CommandLine.arguments
let imgs = a.dropFirst(2).compactMap { NSImage(contentsOfFile: $0)?.cgImage(forProposedRect: nil, context: nil, hints: nil) }
let W = imgs.map { $0.width }.max() ?? 1
let H = imgs.map { $0.height + 6 }.reduce(0, +)
let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0,
                    space: CGColorSpaceCreateDeviceGray(), bitmapInfo: CGImageAlphaInfo.none.rawValue)!
ctx.setFillColor(gray: 1, alpha: 1); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
var y = H
for im in imgs {
    y -= im.height
    ctx.draw(im, in: CGRect(x: 0, y: y, width: im.width, height: im.height))
    y -= 6
    ctx.setFillColor(gray: 0.5, alpha: 1); ctx.fill(CGRect(x: 0, y: y + 2, width: W, height: 2))
}
let rep = NSBitmapImageRep(cgImage: ctx.makeImage()!)
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[1]))
