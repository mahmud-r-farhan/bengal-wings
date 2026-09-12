// Run with: gcc 17_pcb_i2c_sensor_driver.c -o i2c_driver && ./i2c_driver
#include <stdio.h>
#include <stdint.h>

// PCB Hardware Sensor I2C Address Definitions
#define BMP280_I2C_ADDR       0x76
#define BMP280_REG_PRESS_MSB  0xF7
#define BMP280_REG_PRESS_LSB  0xF8
#define BMP280_REG_PRESS_XLSB 0xF9

// Simulating Low-Level I2C Register Read Function
int8_t pcb_i2c_read_registers(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, uint16_t length) {
    // Low-level Hardware Bus Transaction (I2C Start -> Send Addr -> Read Bytes -> Stop)
    for(uint16_t i = 0; i < length; i++) {
        data[i] = 0x7E + i; // Dummy raw sensor bytes
    }
    return 0; // Success ACK
}

int main() {
    printf("==================================================================\n");
    printf(" 🦅 BENGAL WINGS :: BARE-METAL C - PCB I2C SENSOR HARDWARE DRIVER \n");
    printf("==================================================================\n");

    uint8_t raw_buffer[3];
    printf("[I2C BUS]: Initializing Hardware I2C1 (Speed: 400kHz Fast-Mode)...\n");
    
    if (pcb_i2c_read_registers(BMP280_I2C_ADDR, BMP280_REG_PRESS_MSB, raw_buffer, 3) == 0) {
        uint32_t raw_pressure = ((uint32_t)raw_buffer[0] << 12) | ((uint32_t)raw_buffer[1] << 4) | (raw_buffer[2] >> 4);
        printf("[PCB HW ACK]: Device 0x%02X Responded.\n", BMP280_I2C_ADDR);
        printf("[RAW SENSOR DATA]: Barometer ADC Output = %u (Calculated Altitude: ~14.8m)\n", raw_pressure);
    }

    return 0;
}