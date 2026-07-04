import 'dart:convert';

import 'package:http/http.dart' as http;

import 'models.dart';

class BackendException implements Exception {
  BackendException(this.message);

  final String message;

  @override
  String toString() => 'BackendException: $message';
}

class BackendClient {
  BackendClient({required this.baseUrl, this.apiKey = '', http.Client? httpClient})
      : _httpClient = httpClient ?? http.Client();

  // Generous but bounded: the Egyptian TTS pipeline is genuinely slow
  // (observed 15-90s in production, since the free Gradio Space can need to
  // wake up from sleep and queue the request), but a request must still
  // fail predictably rather than hang indefinitely -- an unbounded wait is
  // exactly what silently produced "no response at all" for the user.
  static const Duration _requestTimeout = Duration(seconds: 150);

  final String baseUrl;
  final String apiKey;
  final http.Client _httpClient;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (apiKey.isNotEmpty) 'X-API-Key': apiKey,
      };

  Future<ConversationResponse> sendConversation(ConversationRequest request) async {
    final uri = Uri.parse('$baseUrl/conversation');
    final response = await _httpClient
        .post(
          uri,
          headers: _headers,
          body: jsonEncode(request.toJson()),
        )
        .timeout(_requestTimeout);

    if (response.statusCode != 200) {
      throw BackendException(
        'Backend returned ${response.statusCode}: ${response.body}',
      );
    }

    return ConversationResponse.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<CurrencyLookupResponse> lookupCurrency(String imageBase64) async {
    final uri = Uri.parse('$baseUrl/currency-lookup');
    final response = await _httpClient
        .post(
          uri,
          headers: _headers,
          body: jsonEncode({'image_base64': imageBase64}),
        )
        .timeout(_requestTimeout);

    if (response.statusCode != 200) {
      throw BackendException(
        'Backend returned ${response.statusCode}: ${response.body}',
      );
    }

    return CurrencyLookupResponse.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<ProductLookupResponse> lookupProduct(String barcode) async {
    final uri = Uri.parse('$baseUrl/product-lookup');
    final response = await _httpClient
        .post(
          uri,
          headers: _headers,
          body: jsonEncode({'barcode': barcode}),
        )
        .timeout(_requestTimeout);

    if (response.statusCode != 200) {
      throw BackendException(
        'Backend returned ${response.statusCode}: ${response.body}',
      );
    }

    return ProductLookupResponse.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }
}
