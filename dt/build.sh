dtc -O dtb -o bass-gpio.dtbo -b 0 -@ bass-gpio.dts
mv -v bass-gpio.dtbo /lib/firmware
#echo 'dtb_overlay=/lib/firmware/bass-gpio.dtbo' >> /boot/uEnv.txt