# Gas Sensor Measurement App

This is a gas sensor measurement app in python language. 

## Installation
The required package is included in requirements.txt, install packages using ```pip3 install -r requirements.txt```

## Run app
Run app by command ```python3 app.py```

## Project structure
The project is structured as follow:
```
+--config
|  +--adc.json
|  +--fs.json
|  +--measurement.json
|  +--notification.json
|  +--routine_registration.json
+--driver
|  +--ADS1256
|  +--AiO
|  +--ControlByWeb
+--runtime
+--ui
+--widget
+--app.py
+--routine_function.py
```

__config__: Files related to configurations. Configurations are read by widget when app starts up.<br/>
__driver__: Drivers to interact app with measuring devices, such as adc and network relay. Arduino board uses AiO as driver, which defines a customized protocal to send command.<br/>
__runtime__: Defines how the coming data is interpreted during runtime. The data source is defined here, which instantiates the driver and preprocess the data before send to plot.<br/>
__ui__: UI files<br/>
__widget__: Functional widgets. <br/>
__app.py__: Main entrypoint <br/>
__routine_function.py__: A set of functions to be triggered during measurement. Functions defined here can be registered through config/routine_registration.json. <br/>

## Usage with Arduino
1. check the port where Arduino is connected to, change the port in runtime/src_aio.py. The data sent by Arduino is configured simply as string splited by comma.
2. run the app.py to see if there is data coming in, data will be plotted as well displayed through terminal.
