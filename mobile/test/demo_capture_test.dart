import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';

import 'package:be_my_eye/features/conversation/demo_capture.dart';

void main() {
  test('demo capture image is base64 encoded PNG', () {
    final imageBytes = base64Decode(DemoCapture.imageBase64());

    expect(imageBytes.sublist(0, 8), [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]);
  });

  test('demo capture audio is a WAV file', () {
    final audioBytes = base64Decode(DemoCapture.audioBase64());

    expect(String.fromCharCodes(audioBytes.sublist(0, 4)), 'RIFF');
    expect(String.fromCharCodes(audioBytes.sublist(8, 12)), 'WAVE');
  });
}

