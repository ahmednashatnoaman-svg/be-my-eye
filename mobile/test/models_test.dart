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

  test('ConversationResponse parses tts_fallback_required, defaulting to false', () {
    final withFlag = ConversationResponse.fromJson({
      'session_id': 's1',
      'text': 'hello',
      'audio_base64': '',
      'tts_fallback_required': true,
    });
    final withoutFlag = ConversationResponse.fromJson({
      'session_id': 's1',
      'text': 'hello',
      'audio_base64': 'd2F2',
    });

    expect(withFlag.ttsFallbackRequired, isTrue);
    expect(withoutFlag.ttsFallbackRequired, isFalse);
  });

  test('CurrencyLookupResponse parses a confident detection', () {
    final response = CurrencyLookupResponse.fromJson({
      'found': true,
      'denomination': '20 EGP',
      'confidence': 0.92,
      'spoken_text': 'This looks like 20 EGP.',
      'audio_base64': 'd2F2',
      'tts_fallback_required': false,
    });

    expect(response.found, isTrue);
    expect(response.denomination, '20 EGP');
    expect(response.confidence, 0.92);
  });

  test('ProductLookupResponse parses a found product', () {
    final response = ProductLookupResponse.fromJson({
      'found': true,
      'product': {
        'name': 'Sample Product',
        'brand': 'Sample Brand',
        'ingredients_text': 'water, sugar',
        'allergens': ['milk'],
      },
    });

    expect(response.found, isTrue);
    expect(response.product?.name, 'Sample Product');
    expect(response.product?.allergens, ['milk']);
  });

  test('ProductLookupResponse parses a not-found result', () {
    final response = ProductLookupResponse.fromJson({'found': false, 'product': null});

    expect(response.found, isFalse);
    expect(response.product, isNull);
  });
}

