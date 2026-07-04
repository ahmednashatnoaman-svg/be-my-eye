import 'package:audio_session/audio_session.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'features/conversation/audio_playback.dart';
import 'features/conversation/backend_client.dart';
import 'features/conversation/conversation_screen.dart';
import 'features/conversation/conversation_state.dart';
import 'features/conversation/media_services.dart';
import 'features/conversation/os_tts_fallback.dart';

const String _backendUrl = String.fromEnvironment(
  'BACKEND_URL',
  defaultValue: 'https://backend-mu-azure-ghm6imsjg1.vercel.app',
);

// Empty by default so local/dev builds without --dart-define=BACKEND_API_KEY=...
// still work against a backend that hasn't set BE_MY_EYE_API_KEY either.
const String _backendApiKey = String.fromEnvironment('BACKEND_API_KEY');

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Without this, iOS silently drops all playback (both the cloud TTS
  // response and the on-device fallback voice) whenever the phone's mute
  // switch is on -- audio.speech() is the category for spoken-word/
  // accessibility apps and explicitly ignores it, since voice output is
  // this app's primary interface for a blind user, not a secondary alert.
  await AudioSession.instance.then((session) => session.configure(const AudioSessionConfiguration.speech()));
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<ConversationState>(
      create: (_) => ConversationState(
        backendClient: BackendClient(baseUrl: _backendUrl, apiKey: _backendApiKey),
        mediaCaptureService: CameraMediaCaptureService(),
        audioPlaybackService: JustAudioPlaybackService(),
        osTtsFallbackService: FlutterOsTtsFallbackService(),
      ),
      child: MaterialApp(
        title: 'Be My Eye',
        theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
        home: const ConversationScreen(),
      ),
    );
  }
}
