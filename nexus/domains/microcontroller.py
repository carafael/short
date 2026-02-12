"""
Microcontroller/Embedded Systems domain mode
"""

from typing import Dict, Any, List


class MicrocontrollerMode:
    """Specialized mode for embedded systems and microcontroller development"""

    def __init__(self):
        self.name = "microcontroller"
        self.description = "Embedded systems, Arduino, ESP32, STM32, and microcontroller development"

        # Common microcontroller platforms and their characteristics
        self.platforms = {
            "arduino": {
                "description": "Arduino boards (Uno, Mega, Nano, etc.)",
                "voltage": "5V/3.3V",
                "common_use": "Prototyping, education, simple projects"
            },
            "esp32": {
                "description": "ESP32 WiFi+Bluetooth microcontroller",
                "voltage": "3.3V",
                "common_use": "IoT, WiFi projects, low-power applications"
            },
            "esp8266": {
                "description": "ESP8266 WiFi microcontroller",
                "voltage": "3.3V",
                "common_use": "WiFi-enabled projects, IoT"
            },
            "stm32": {
                "description": "STM32 ARM Cortex-M microcontrollers",
                "voltage": "3.3V",
                "common_use": "Professional embedded systems, real-time applications"
            },
            "raspberry_pi_pico": {
                "description": "RP2040-based microcontroller board",
                "voltage": "3.3V",
                "common_use": "Python/C++ projects, dual-core applications"
            }
        }

        # Common protocols and interfaces
        self.protocols = [
            "I2C", "SPI", "UART", "CAN", "USB", "PWM",
            "ADC", "DAC", "GPIO", "Ethernet", "WiFi", "Bluetooth"
        ]

        # Code templates
        self.templates = {
            "arduino_blink": """
// Basic LED blink example
const int LED_PIN = 13;

void setup() {
    pinMode(LED_PIN, OUTPUT);
}

void loop() {
    digitalWrite(LED_PIN, HIGH);
    delay(1000);
    digitalWrite(LED_PIN, LOW);
    delay(1000);
}
""",
            "esp32_wifi": """
#include <WiFi.h>

const char* ssid = "your_SSID";
const char* password = "your_PASSWORD";

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\\nConnected to WiFi");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
}

void loop() {
    // Your code here
}
""",
            "i2c_scanner": """
#include <Wire.h>

void setup() {
    Wire.begin();
    Serial.begin(9600);
    Serial.println("I2C Scanner");
}

void loop() {
    byte error, address;
    int devices = 0;

    for(address = 1; address < 127; address++) {
        Wire.beginTransmission(address);
        error = Wire.endTransmission();

        if (error == 0) {
            Serial.print("Device found at 0x");
            if (address < 16) Serial.print("0");
            Serial.println(address, HEX);
            devices++;
        }
    }

    if (devices == 0) Serial.println("No I2C devices found");
    delay(5000);
}
"""
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for this domain"""
        return f"""You are now in Microcontroller/Embedded Systems mode.

Focus on:
- Embedded C/C++ programming
- Hardware interfacing and protocols ({', '.join(self.protocols)})
- Power consumption optimization
- Real-time constraints and timing
- Memory management on constrained devices
- Debugging embedded systems
- Common platforms: {', '.join(self.platforms.keys())}

Provide:
- Complete, working code examples
- Pin diagrams and connections when relevant
- Power calculations and battery life estimates
- Troubleshooting steps for hardware issues
- Best practices for embedded development

Be specific about voltage levels, current draw, and hardware limitations.
"""

    def get_context_hints(self) -> List[str]:
        """Get contextual hints for this domain"""
        return [
            "Remember to specify target platform (Arduino, ESP32, etc.)",
            "Consider power consumption in your design",
            "Check voltage levels (3.3V vs 5V compatibility)",
            "Use appropriate pull-up/pull-down resistors",
            "Consider using interrupts for time-critical tasks",
            "Monitor memory usage (RAM/Flash)",
            "Use watchdog timers for reliability"
        ]

    def get_quick_reference(self) -> Dict[str, Any]:
        """Get quick reference information"""
        return {
            "platforms": self.platforms,
            "protocols": self.protocols,
            "voltage_levels": {
                "3.3V": "ESP32, ESP8266, STM32, RPi Pico",
                "5V": "Arduino Uno/Mega",
                "mixed": "Arduino Nano 33 IoT (3.3V logic, 5V tolerant pins)"
            },
            "common_i2c_addresses": {
                "0x27": "LCD Display",
                "0x3C": "OLED Display (SSD1306)",
                "0x68": "MPU6050 (IMU)",
                "0x76/0x77": "BMP280 (Pressure sensor)"
            }
        }

    def get_template(self, template_name: str) -> str:
        """Get a code template"""
        return self.templates.get(template_name, "Template not found")

    def list_templates(self) -> List[str]:
        """List available templates"""
        return list(self.templates.keys())
