import smbus2
import sys
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)

@time_trigger("cron(* * * * *)")
def update():
    log.warning("Starting BME")
    calibration_params = task.executor(bme280.load_calibration_params, bus, address)

    # the sample method will take a single reading and return a
    # compensated_reading object
    data = task.executor(bme280.sample, bus, address, calibration_params)

    temperature = round(data.temperature * 9.0 / 5.0, 1) + 32.0
    log.warning("Temperature: {}".format(temperature))
    service.call("input_number", "set_value", entity_id="input_number.server_temperature", value=temperature)
    service.call("input_number", "set_value", entity_id="input_number.server_humidity", value=data.humidity)
