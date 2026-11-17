// Une los cuadros PNG y el WAV de Movie Maker en un MP4 (H.264 + AAC) con
// AVFoundation, sin ffmpeg. Amplía por vecino más cercano (escala entera),
// igual que el juego.
//
//   swift tools/frames_to_mp4.swift <carpeta_cuadros> <audio.wav> <salida.mp4> [paso=2] [escala=2] [saltar=6]
//
// paso:   usa uno de cada N cuadros (60 fps / 2 = 30 fps).
// escala: 2 = 1280x720.
// saltar: cuadros iniciales que se omiten (antes de que cargue la sala).

import AVFoundation
import CoreGraphics
import Foundation
import ImageIO

let args = CommandLine.arguments
guard args.count >= 4 else {
    print("uso: swift frames_to_mp4.swift <cuadros> <audio.wav> <salida.mp4> [paso] [escala] [saltar]")
    exit(2)
}
let framesDir = URL(fileURLWithPath: args[1])
let wavURL = URL(fileURLWithPath: args[2])
let outURL = URL(fileURLWithPath: args[3])
let step = args.count > 4 ? Int(args[4])! : 2
let scale = args.count > 5 ? Int(args[5])! : 2
let skip = args.count > 6 ? Int(args[6])! : 6
let sourceFps = 60

let names = try FileManager.default.contentsOfDirectory(atPath: framesDir.path)
    .filter { $0.hasSuffix(".png") }.sorted()
let width = 640 * scale, height = 360 * scale
let fps = Int32(sourceFps / step)
try? FileManager.default.removeItem(at: outURL)

let writer = try AVAssetWriter(outputURL: outURL, fileType: .mp4)
let video = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 3_000_000],
])
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: video, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
    kCVPixelBufferWidthKey as String: width,
    kCVPixelBufferHeightKey as String: height,
])
writer.add(video)

let wavFile = try AVAudioFile(forReading: wavURL)
let audio = AVAssetWriterInput(mediaType: .audio, outputSettings: [
    AVFormatIDKey: kAudioFormatMPEG4AAC,
    AVSampleRateKey: wavFile.fileFormat.sampleRate,
    AVNumberOfChannelsKey: wavFile.fileFormat.channelCount,
    AVEncoderBitRateKey: 128_000,
])
writer.add(audio)

// Audio desde el mismo instante que el primer cuadro usado.
let asset = AVURLAsset(url: wavURL)
let track = asset.tracks(withMediaType: .audio).first!
let reader = try AVAssetReader(asset: asset)
reader.timeRange = CMTimeRange(start: CMTime(value: CMTimeValue(skip), timescale: CMTimeScale(sourceFps)),
                               duration: .positiveInfinity)
let output = AVAssetReaderTrackOutput(track: track, outputSettings: [AVFormatIDKey: kAudioFormatLinearPCM])
reader.add(output)
reader.startReading()

writer.startWriting()
writer.startSession(atSourceTime: .zero)

// El escritor intercala pistas: vídeo y audio se alimentan a la vez, cada uno
// en su cola, o se bloquea esperando a la otra pista.
let selected = names.enumerated().filter { $0.offset >= skip && ($0.offset - skip) % step == 0 }.map { $0.element }
var frames = selected.makeIterator()
var written: Int64 = 0
var audioStart: CMTime?
let group = DispatchGroup()

group.enter()
video.requestMediaDataWhenReady(on: DispatchQueue(label: "video")) {
    while video.isReadyForMoreMediaData {
        guard let name = frames.next() else {
            video.markAsFinished()
            group.leave()
            return
        }
        guard let source = CGImageSourceCreateWithURL(framesDir.appendingPathComponent(name) as CFURL, nil),
              let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else { continue }
        var buffer: CVPixelBuffer?
        CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &buffer)
        guard let pixels = buffer else { continue }
        CVPixelBufferLockBaseAddress(pixels, [])
        let context = CGContext(data: CVPixelBufferGetBaseAddress(pixels), width: width, height: height,
                                bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(pixels),
                                space: CGColorSpaceCreateDeviceRGB(),
                                bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
        context.interpolationQuality = .none
        context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
        CVPixelBufferUnlockBaseAddress(pixels, [])
        adaptor.append(pixels, withPresentationTime: CMTime(value: written, timescale: fps))
        written += 1
    }
}

group.enter()
audio.requestMediaDataWhenReady(on: DispatchQueue(label: "audio")) {
    while audio.isReadyForMoreMediaData {
        guard let sample = output.copyNextSampleBuffer() else {
            audio.markAsFinished()
            group.leave()
            return
        }
        // Desplaza el audio para que empiece en 0 junto al vídeo.
        let time = CMSampleBufferGetPresentationTimeStamp(sample)
        if audioStart == nil { audioStart = time }
        var timing = CMSampleTimingInfo(duration: CMSampleBufferGetDuration(sample),
                                        presentationTimeStamp: CMTimeSubtract(time, audioStart!),
                                        decodeTimeStamp: .invalid)
        var shifted: CMSampleBuffer?
        CMSampleBufferCreateCopyWithNewTiming(allocator: nil, sampleBuffer: sample, sampleTimingEntryCount: 1,
                                              sampleTimingArray: &timing, sampleBufferOut: &shifted)
        audio.append(shifted ?? sample)
    }
}
group.wait()

let done = DispatchSemaphore(value: 0)
writer.finishWriting { done.signal() }
done.wait()
if writer.status == .completed {
    print(String(format: "ok: %@ · %d cuadros a %d fps · %.1f s", outURL.path, written, fps, Double(written) / Double(fps)))
} else {
    print("error: \(String(describing: writer.error))")
    exit(1)
}
