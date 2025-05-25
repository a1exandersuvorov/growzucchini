```
docker build -t pio-builder ./arduino
docker run --rm -v $PWD/arduino:/project -v /dev:/dev --device=/dev/ttyUSB0 --privileged pio-builder platformio run --target upload
```