"""
UDS (Unified Diagnostic Services) Güvenlik Test Modülü
Kvaser Memorator 2xHS - Windows

ISO 14229 UDS protokolü güvenlik testleri
ECU güvenlik açıklarını tespit etmek için
"""

import logging
import time
import threading
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from can_pentest_core import CANPentestCore, CANMessage, PentestMode


class UDSService(Enum):
    """UDS Servisleri (ISO 14229)"""
    DIAGNOSTIC_SESSION_CONTROL = 0x10
    ECU_RESET = 0x11
    SECURITY_ACCESS = 0x27
    COMMUNICATION_CONTROL = 0x28
    TESTER_PRESENT = 0x3E
    ACCESS_TIMING_PARAMETER = 0x83
    SECURED_DATA_TRANSMISSION = 0x84
    CONTROL_DTC_SETTING = 0x85
    RESPONSE_ON_EVENT = 0x86
    LINK_CONTROL = 0x87
    READ_DATA_BY_IDENTIFIER = 0x22
    READ_MEMORY_BY_ADDRESS = 0x23
    READ_SCALING_DATA_BY_IDENTIFIER = 0x24
    READ_DATA_BY_PERIODIC_IDENTIFIER = 0x2A
    DYNAMICALLY_DEFINE_DATA_IDENTIFIER = 0x2C
    WRITE_DATA_BY_IDENTIFIER = 0x2E
    WRITE_MEMORY_BY_ADDRESS = 0x3D
    CLEAR_DIAGNOSTIC_INFORMATION = 0x14
    READ_DTC_INFORMATION = 0x19
    INPUT_OUTPUT_CONTROL_BY_IDENTIFIER = 0x2F
    ROUTINE_CONTROL = 0x31
    REQUEST_DOWNLOAD = 0x34
    REQUEST_UPLOAD = 0x35
    TRANSFER_DATA = 0x36
    REQUEST_TRANSFER_EXIT = 0x37


class SessionType(Enum):
    """UDS Session tipleri"""
    DEFAULT = 0x01
    PROGRAMMING = 0x02
    EXTENDED_DIAGNOSTIC = 0x03
    SAFETY_SYSTEM_DIAGNOSTIC = 0x04


@dataclass
class UDSTestConfig:
    """UDS test konfigürasyonu"""
    # Hedef ECU
    target_ecu_id: int = 0x7E0  # Request ID
    response_id: int = 0x7E8    # Response ID

    # Test tipleri
    test_security_access: bool = True
    test_session_control: bool = True
    test_write_operations: bool = False  # Tehlikeli!
    test_routine_control: bool = False   # Tehlikeli!

    # Timeout
    response_timeout: float = 1.0  # saniye

    # Safety
    safe_mode: bool = True


@dataclass
class UDSTestResult:
    """UDS test sonucu"""
    config: UDSTestConfig
    start_time: datetime
    end_time: datetime
    tests_performed: int
    vulnerabilities_found: List[Dict[str, Any]]
    ecu_responses: List[Dict[str, Any]]
    success: bool


class UDSSecurity:
    """
    UDS Güvenlik Tester

    ISO 14229 UDS protokolü güvenlik testleri
    """

    # Negative Response Codes (NRC)
    NRC_CODES = {
        0x10: "General Reject",
        0x11: "Service Not Supported",
        0x12: "Sub-Function Not Supported",
        0x13: "Incorrect Message Length",
        0x22: "Conditions Not Correct",
        0x24: "Request Sequence Error",
        0x31: "Request Out Of Range",
        0x33: "Security Access Denied",
        0x35: "Invalid Key",
        0x36: "Exceed Number Of Attempts",
        0x37: "Required Time Delay Not Expired",
        0x78: "Request Correctly Received - Response Pending"
    }

    def __init__(self, pentest_core: CANPentestCore):
        """
        Args:
            pentest_core: CAN pentest core instance
        """
        self.core = pentest_core
        self.config = UDSTestConfig()

        # State
        self.is_testing = False
        self.test_thread = None

        # Results
        self.vulnerabilities: List[Dict[str, Any]] = []
        self.ecu_responses: List[Dict[str, Any]] = []
        self.tests_performed = 0

        # Response handling
        self.waiting_for_response = False
        self.last_request = None
        self.last_response = None
        self.response_event = threading.Event()

        # Callbacks
        self.progress_callback: Optional[Callable[[str], None]] = None
        self.vulnerability_callback: Optional[Callable[[Dict], None]] = None

        self.logger = logging.getLogger(__name__)

    def start_test(self, config: Optional[UDSTestConfig] = None) -> bool:
        """
        UDS güvenlik testi başlat

        Args:
            config: Test konfigürasyonu

        Returns:
            Başarı durumu
        """
        if self.is_testing:
            self.logger.warning("UDS testi zaten çalışıyor!")
            return False

        if not self.core.is_connected:
            self.logger.error("CAN bağlantısı yok!")
            return False

        if config:
            self.config = config

        # Core'a response callback ekle
        self.core.message_callback = self._on_can_message

        # Core'u ACTIVE moda al
        self.core.set_mode(PentestMode.ACTIVE)

        # Reset
        self.vulnerabilities.clear()
        self.ecu_responses.clear()
        self.tests_performed = 0

        # Thread başlat
        self.is_testing = True
        self.test_thread = threading.Thread(
            target=self._test_loop,
            daemon=True,
            name="UDS_Test"
        )
        self.test_thread.start()

        self.logger.info("UDS güvenlik testi başlatıldı")
        return True

    def stop_test(self):
        """Testi durdur"""
        self.is_testing = False

        if self.test_thread:
            self.test_thread.join(timeout=2.0)

        self.core.message_callback = None
        self.core.set_mode(PentestMode.PASSIVE)

        self.logger.info("UDS testi durduruldu")

    def _test_loop(self):
        """Test ana döngüsü"""
        self._report_progress("UDS güvenlik testi başlatılıyor...")

        # 1. Session Control testleri
        if self.config.test_session_control:
            self._test_session_control()

        # 2. Security Access testleri
        if self.config.test_security_access:
            self._test_security_access()

        # 3. Write operations (tehlikeli!)
        if self.config.test_write_operations and not self.config.safe_mode:
            self._test_write_operations()

        # 4. Routine Control (tehlikeli!)
        if self.config.test_routine_control and not self.config.safe_mode:
            self._test_routine_control()

        self.is_testing = False
        self._report_progress("UDS güvenlik testi tamamlandı")

    def _test_session_control(self):
        """Session Control testleri"""
        self._report_progress("Session Control testleri...")

        # Test 1: Default session'a geçiş
        self._send_uds_request(
            UDSService.DIAGNOSTIC_SESSION_CONTROL,
            [SessionType.DEFAULT.value],
            "Default Session"
        )

        # Test 2: Extended Diagnostic session
        self._send_uds_request(
            UDSService.DIAGNOSTIC_SESSION_CONTROL,
            [SessionType.EXTENDED_DIAGNOSTIC.value],
            "Extended Diagnostic Session"
        )

        # Test 3: Programming session (çok hassas!)
        if not self.config.safe_mode:
            self._send_uds_request(
                UDSService.DIAGNOSTIC_SESSION_CONTROL,
                [SessionType.PROGRAMMING.value],
                "Programming Session"
            )

    def _test_security_access(self):
        """Security Access testleri"""
        self._report_progress("Security Access testleri...")

        # Test 1: Seed Request (Level 1)
        response = self._send_uds_request(
            UDSService.SECURITY_ACCESS,
            [0x01],  # Request Seed - Level 1
            "Security Access - Request Seed Level 1"
        )

        if response and len(response) > 2:
            # Seed alındı
            seed = response[2:]
            self.logger.info(f"Seed alındı: {seed.hex()}")

            # Test 2: Brute force key deneme (basit örnek)
            self._test_security_brute_force(seed)

        # Test 3: Seed Request (Level 3)
        self._send_uds_request(
            UDSService.SECURITY_ACCESS,
            [0x03],  # Request Seed - Level 3
            "Security Access - Request Seed Level 3"
        )

    def _test_security_brute_force(self, seed: bytes):
        """Security access brute force (basit örnek)"""
        self._report_progress("Security Access brute force testi...")

        # UYARI: Bu gerçek bir brute force değil, sadece örnek
        # Gerçek implementasyonda seed-key algoritması analiz edilir

        test_keys = [
            bytes([0x00, 0x00, 0x00, 0x00]),
            bytes([0xFF, 0xFF, 0xFF, 0xFF]),
            bytes([0x12, 0x34, 0x56, 0x78]),
            seed,  # Seed'i key olarak gönder (hatalı ama test için)
        ]

        for key in test_keys:
            response = self._send_uds_request(
                UDSService.SECURITY_ACCESS,
                [0x02] + list(key),  # Send Key - Level 1
                f"Security Access - Send Key: {key.hex()}"
            )

            if response and response[0] == 0x67:  # Positive response
                # Güvenlik açığı! Key kabul edildi!
                self._report_vulnerability({
                    'type': 'SECURITY_ACCESS_WEAK',
                    'description': 'Security access weak key accepted',
                    'key': key.hex(),
                    'severity': 'CRITICAL'
                })
                break

            # Attempt counter kontrolü
            time.sleep(0.5)  # Rate limiting

    def _test_write_operations(self):
        """Write operation testleri (TEHLİKELİ!)"""
        self._report_progress("Write operation testleri (SAFE MODE disabled)...")

        # Test: Write Data By Identifier
        # NOT: Gerçek bir DID kullanmıyoruz, sadece test
        self._send_uds_request(
            UDSService.WRITE_DATA_BY_IDENTIFIER,
            [0xFF, 0xFF, 0x00, 0x00],  # Invalid DID
            "Write Data By Identifier Test"
        )

    def _test_routine_control(self):
        """Routine Control testleri (TEHLİKELİ!)"""
        self._report_progress("Routine Control testleri (SAFE MODE disabled)...")

        # Test: Invalid routine
        self._send_uds_request(
            UDSService.ROUTINE_CONTROL,
            [0x01, 0xFF, 0xFF],  # Start Routine, Invalid ID
            "Routine Control Test"
        )

    def _send_uds_request(self, service: UDSService, data: List[int], description: str) -> Optional[bytes]:
        """
        UDS request gönder ve response bekle

        Args:
            service: UDS service
            data: Service data
            description: Test açıklaması

        Returns:
            Response data veya None
        """
        self.tests_performed += 1

        # Request oluştur
        request_data = bytes([service.value] + data)

        # Gönder
        self.waiting_for_response = True
        self.last_request = request_data
        self.last_response = None
        self.response_event.clear()

        if not self.core.send_message(self.config.target_ecu_id, request_data, len(request_data)):
            self.logger.error(f"UDS request gönderilemedi: {description}")
            return None

        self.logger.debug(f"UDS Request: {description} - {request_data.hex()}")

        # Response bekle
        if self.response_event.wait(timeout=self.config.response_timeout):
            response = self.last_response
            self._log_response(description, request_data, response)
            return response
        else:
            self.logger.warning(f"UDS Response timeout: {description}")
            return None

    def _on_can_message(self, msg: CANMessage):
        """CAN mesajı alındığında"""
        # Response ID kontrolü
        if msg.can_id == self.config.response_id and self.waiting_for_response:
            self.last_response = msg.data
            self.waiting_for_response = False
            self.response_event.set()

    def _log_response(self, description: str, request: bytes, response: bytes):
        """Response'u logla ve analiz et"""
        # Response kaydet
        self.ecu_responses.append({
            'description': description,
            'request': request.hex(),
            'response': response.hex(),
            'timestamp': time.time()
        })

        # Positive response
        if len(response) > 0 and response[0] >= 0x40:
            self.logger.info(f"UDS Positive Response: {description}")

        # Negative response
        elif len(response) >= 3 and response[0] == 0x7F:
            service_id = response[1]
            nrc = response[2]
            nrc_desc = self.NRC_CODES.get(nrc, f"Unknown (0x{nrc:02X})")
            self.logger.info(f"UDS Negative Response: {description} - NRC: {nrc_desc}")

        # Unexpected response
        else:
            self.logger.warning(f"UDS Unexpected Response: {description} - {response.hex()}")

    def _report_vulnerability(self, vuln: Dict[str, Any]):
        """Güvenlik açığı raporla"""
        self.vulnerabilities.append(vuln)
        self.logger.critical(f"VULNERABILITY FOUND: {vuln['type']} - {vuln['description']}")

        if self.vulnerability_callback:
            self.vulnerability_callback(vuln)

    def _report_progress(self, message: str):
        """Progress raporla"""
        self.logger.info(message)

        if self.progress_callback:
            self.progress_callback(message)

    def get_result(self) -> UDSTestResult:
        """Test sonucunu al"""
        return UDSTestResult(
            config=self.config,
            start_time=datetime.now(),  # TODO: Başlangıç zamanını sakla
            end_time=datetime.now(),
            tests_performed=self.tests_performed,
            vulnerabilities_found=self.vulnerabilities.copy(),
            ecu_responses=self.ecu_responses.copy(),
            success=len(self.vulnerabilities) == 0
        )

    def print_report(self):
        """Test raporunu yazdır"""
        print("\n" + "=" * 60)
        print("UDS SECURITY TEST REPORT")
        print("=" * 60)
        print(f"Tests Performed: {self.tests_performed}")
        print(f"ECU Responses: {len(self.ecu_responses)}")
        print(f"Vulnerabilities Found: {len(self.vulnerabilities)}")

        if self.vulnerabilities:
            print("\nVULNERABILITIES:")
            print("-" * 60)
            for vuln in self.vulnerabilities:
                print(f"  [{vuln['severity']}] {vuln['type']}")
                print(f"    {vuln['description']}")

        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Core
    core = CANPentestCore(channel=0, bitrate=500000)

    if core.connect():
        # UDS tester
        uds = UDSSecurity(core)

        # Config
        config = UDSTestConfig(
            target_ecu_id=0x7E0,
            response_id=0x7E8,
            test_security_access=True,
            test_session_control=True,
            test_write_operations=False,  # Güvenli mod
            safe_mode=True
        )

        # Callbacks
        def on_progress(msg):
            print(f"[Progress] {msg}")

        def on_vulnerability(vuln):
            print(f"[VULN] {vuln['type']}: {vuln['description']}")

        uds.progress_callback = on_progress
        uds.vulnerability_callback = on_vulnerability

        # Test başlat
        print("UDS güvenlik testi başlatılıyor...")
        uds.start_test(config)

        try:
            while uds.is_testing:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nDuruyor...")

        uds.stop_test()

        # Rapor
        uds.print_report()

        core.disconnect()
