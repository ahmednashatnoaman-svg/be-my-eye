import 'package:flutter_test/flutter_test.dart';

import 'package:be_my_eye/features/conversation/models.dart';

void main() {
  test('ConversationRequest serializes to backend payload keys', () {
    final request = ConversationRequest(
      sessionId: 'session-1',
      imageBase64: 'image',
      audioBase64: 'audio',
      debug: true,
    );

    expect(request.toJson(), {
      'session_id': 'session-1',
      'image_base64': 'image',
      'audio_base64': 'audio',
      'debug': true,
    });
  });

  test('ConversationResponse parses backend response shape', () {
    final response = ConversationResponse.fromJson({
      'session_id': 'session-1',
      'text': 'hello',
      'audio_base64': 'abcd',
      'debug': {
        'transcript': 'what is this',
        'selected_providers': ['vision'],
        'vision_summary': 'a desk',
        'ocr_text': null,
      },
    });

    expect(response.sessionId, 'session-1');
    expect(response.text, 'hello');
    expect(response.audioBase64, 'abcd');
    expect(response.debug?.selectedProviders, ['vision']);
  });
}

