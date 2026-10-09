// OCR local con el framework Vision de macOS (no usa internet).
// Uso: swift ocr_vision.swift imagen.jpg  -> imprime líneas "y|x|texto"
import Foundation
import Vision
import AppKit

let path = CommandLine.arguments[1]
guard let img = NSImage(contentsOfFile: path),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.recognitionLanguages = ["es-ES"]
req.usesLanguageCorrection = false
let handler = VNImageRequestHandler(cgImage: cg, options: [:])
try handler.perform([req])
for obs in (req.results ?? []) {
    if let t = obs.topCandidates(1).first {
        let b = obs.boundingBox
        print(String(format: "%.3f|%.3f|%@", 1 - b.origin.y - b.height, b.origin.x, t.string))
    }
}
