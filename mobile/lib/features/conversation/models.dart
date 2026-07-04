class ConversationRequest {
  ConversationRequest({
    required this.sessionId,
    required this.imageBase64,
    required this.audioBase64,
    this.debug = false,
  });

  final String sessionId;
  final String imageBase64;
  final String audioBase64;
  final bool debug;

  Map<String, dynamic> toJson() => {
        'session_id': sessionId,
        'image_base64': imageBase64,
        'audio_base64': audioBase64,
        'debug': debug,
      };
}

class ConversationDebug {
  ConversationDebug({
    required this.transcript,
    required this.selectedProviders,
    this.visionSummary,
    this.ocrText,
  });

  final String transcript;
  final List<String> selectedProviders;
  final String? visionSummary;
  final String? ocrText;

  factory ConversationDebug.fromJson(Map<String, dynamic> json) {
    return ConversationDebug(
      transcript: json['transcript'] as String,
      selectedProviders: List<String>.from(json['selected_providers'] as List),
      visionSummary: json['vision_summary'] as String?,
      ocrText: json['ocr_text'] as String?,
    );
  }
}

class ConversationResponse {
  ConversationResponse({
    required this.sessionId,
    required this.text,
    required this.audioBase64,
    this.ttsFallbackRequired = false,
    this.debug,
  });

  final String sessionId;
  final String text;
  final String audioBase64;
  final bool ttsFallbackRequired;
  final ConversationDebug? debug;

  factory ConversationResponse.fromJson(Map<String, dynamic> json) {
    return ConversationResponse(
      sessionId: json['session_id'] as String,
      text: json['text'] as String,
      audioBase64: json['audio_base64'] as String,
      ttsFallbackRequired: json['tts_fallback_required'] as bool? ?? false,
      debug: json['debug'] != null
          ? ConversationDebug.fromJson(json['debug'] as Map<String, dynamic>)
          : null,
    );
  }
}

class CurrencyLookupResponse {
  CurrencyLookupResponse({
    required this.found,
    this.denomination,
    this.confidence,
    required this.spokenText,
    this.audioBase64 = '',
    this.ttsFallbackRequired = false,
  });

  final bool found;
  final String? denomination;
  final double? confidence;
  final String spokenText;
  final String audioBase64;
  final bool ttsFallbackRequired;

  factory CurrencyLookupResponse.fromJson(Map<String, dynamic> json) {
    return CurrencyLookupResponse(
      found: json['found'] as bool,
      denomination: json['denomination'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble(),
      spokenText: json['spoken_text'] as String,
      audioBase64: json['audio_base64'] as String? ?? '',
      ttsFallbackRequired: json['tts_fallback_required'] as bool? ?? false,
    );
  }
}

class ProductInfo {
  ProductInfo({
    required this.name,
    this.brand,
    this.ingredientsText,
    this.allergens = const [],
  });

  final String name;
  final String? brand;
  final String? ingredientsText;
  final List<String> allergens;

  factory ProductInfo.fromJson(Map<String, dynamic> json) {
    return ProductInfo(
      name: json['name'] as String,
      brand: json['brand'] as String?,
      ingredientsText: json['ingredients_text'] as String?,
      allergens: List<String>.from(json['allergens'] as List? ?? const []),
    );
  }
}

class ProductLookupResponse {
  ProductLookupResponse({required this.found, this.product});

  final bool found;
  final ProductInfo? product;

  factory ProductLookupResponse.fromJson(Map<String, dynamic> json) {
    return ProductLookupResponse(
      found: json['found'] as bool,
      product: json['product'] != null
          ? ProductInfo.fromJson(json['product'] as Map<String, dynamic>)
          : null,
    );
  }
}
