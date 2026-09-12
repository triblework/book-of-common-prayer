import Foundation
import Vision
import AppKit

// OCR one or more image files with the Vision framework; prints
//   <path>\t<text with newlines as \n>
// Accurate recognition, English, no language correction (we want the page's
// own spelling, not autocorrect to modern forms).
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        FileHandle.standardError.write("cannot load \(path)\n".data(using: .utf8)!)
        continue
    }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    req.recognitionLanguages = ["en-US"]
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    try? handler.perform([req])
    let lines = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }
    let out = path + "\t" + lines.joined(separator: "\\n") + "\n"
    FileHandle.standardOutput.write(out.data(using: .utf8)!)
}
