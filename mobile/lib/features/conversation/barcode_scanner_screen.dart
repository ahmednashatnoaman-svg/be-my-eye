import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

/// Scans a single barcode and pops back with its raw value. All lookup and
/// speech logic lives in ConversationState.lookupProductByBarcode -- this
/// screen only wraps the camera hardware, matching this app's established
/// pattern for hardware-facing code (verified via flutter analyze, not
/// full behavioral tests, since it can't run meaningfully without a device).
class BarcodeScannerScreen extends StatefulWidget {
  const BarcodeScannerScreen({super.key});

  @override
  State<BarcodeScannerScreen> createState() => _BarcodeScannerScreenState();
}

class _BarcodeScannerScreenState extends State<BarcodeScannerScreen> {
  bool _handled = false;

  void _onDetect(BarcodeCapture capture) {
    if (_handled || capture.barcodes.isEmpty) {
      return;
    }
    final rawValue = capture.barcodes.first.rawValue;
    if (rawValue == null) {
      return;
    }
    _handled = true;
    Navigator.of(context).pop(rawValue);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan barcode')),
      body: MobileScanner(
        // Restricted to numeric retail barcode formats only. Without this,
        // scanning a stray QR code or any other non-retail symbology in
        // view (easy to do by accident when you can't see the camera
        // framing) sends non-numeric text to the backend, which rejects it
        // with a 422 since ProductLookupRequest.barcode requires digits
        // only -- surfacing as a generic "something went wrong" error
        // instead of just not matching that stray code in the first place.
        controller: MobileScannerController(
          formats: const [
            BarcodeFormat.ean13,
            BarcodeFormat.ean8,
            BarcodeFormat.upcA,
            BarcodeFormat.upcE,
          ],
        ),
        onDetect: _onDetect,
      ),
    );
  }
}
