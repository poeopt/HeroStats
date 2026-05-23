import unittest
import json
from src.engine.message_parser import MessageParser
from src.consts import events as consts

class TestMessageParser(unittest.TestCase):
    def test_identify_event_gold(self):
        msg = {"currencyData": {"gold": 100}}
        self.assertEqual(MessageParser.identify_event(msg), consts.EvNameUpdateGold)

    def test_identify_event_xp(self):
        msg = {"totalGuildXp": 1000}
        self.assertEqual(MessageParser.identify_event(msg), consts.EvNameUpdateXP)

    def test_capture_json(self):
        msg_str = 'some garbage {"currencyData": {"gold": 100}} more garbage'
        parsed = MessageParser.capture(msg_str)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["currencyData"]["gold"], 100)

    def test_capture_special_base64(self):
        # Mocking special message start 'x' and some base64
        # PROTOCOL_SIGNATURES["special_start"] is 'x'
        import base64
        data = {"foo": "bar"}
        b64_data = base64.b64encode(json.dumps(data).encode()).decode()
        msg_str = "x" + "00" + b64_data # 3 chars prefix as per original logic message[3:]
        # Length must be > 100
        msg_str = msg_str.ljust(101, ' ')
        parsed = MessageParser.capture(msg_str)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["foo"], "bar")

if __name__ == "__main__":
    unittest.main()
