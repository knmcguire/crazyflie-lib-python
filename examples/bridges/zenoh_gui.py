from nicegui import ui
import sys
import time
import argparse
import json
import zenoh
from zenoh import  config, QueryTarget, Selector, Reliability, Sample


class ZenohGui:
    def __init__(self):
        self.label = ui.label('Zenoh Gui')
        ui.button('Scout', on_click= self._button_cb_scout)  
        ui.button('Setup Logging', on_click= self._button_cb_setup_logging)
        ui.button('Start Logging', on_click= self._button_cb_start_logging)
        ui.button('Stop Logging', on_click= self._button_cb_stop_logging)

        self.log = ui.log(max_lines=10).classes('w-full h-20')
        zenoh.init_logger()
        self._zenoh_session = zenoh.open(zenoh.Config())
        self.sub = self._zenoh_session.declare_subscriber("cf/logging", self._zenoh_cb_logging,reliability=Reliability.RELIABLE())


    def _zenoh_cb_logging(self, sample: Sample):
        self.log.push(f">> [Subscriber] Received {sample.kind} ('{sample.key_expr}': '{sample.payload.decode('utf-8')}')")


    def _button_cb_scout(self):

        responses = self._zenoh_session.get(Selector("*"), zenoh.Queue())
        print(responses)
        for response in responses:
            try:
                print(f"Received '{response.ok.key_expr}': '{response.ok.payload.decode('utf-8')}'")
            except:
                print(f"Received ERROR: '{response.err.payload.decode('utf-8')}'")

    def _button_cb_setup_logging(self):
        value_json= '{"name":"state", "logs":[{"name":"stateEstimate.x", "type":"float"},{"name":"stateEstimate.y", "type":"float"}]}'
        replies = self._zenoh_session.get(Selector("cf/setup_logging"), zenoh.Queue(),value=value_json)
        for reply in replies.receiver:
            try:
                print(">> Received ('{}': '{}')"
                    .format(reply.ok.key_expr, reply.ok.payload.decode("utf-8")))
            except:
                print(">> Received (ERROR: '{}')"
                    .format(reply.err.payload.decode("utf-8")))
                
    def _button_cb_start_logging(self):
        value_json= '{"name":"state"}'
        replies = self._zenoh_session.get(Selector("cf/start_logging"), zenoh.Queue(),value=value_json)
        for reply in replies.receiver:
            try:
                print(">> Received ('{}': '{}')"
                    .format(reply.ok.key_expr, reply.ok.payload.decode("utf-8")))
            except:
                print(">> Received (ERROR: '{}')"
                    .format(reply.err.payload.decode("utf-8")))

    def _button_cb_stop_logging(self):
        value_json= '{"name":"state"}'
        replies = self._zenoh_session.get(Selector("cf/stop_logging"), zenoh.Queue(),value=value_json)
        for reply in replies.receiver:
            try:
                print(">> Received ('{}': '{}')"
                    .format(reply.ok.key_expr, reply.ok.payload.decode("utf-8")))
            except:
                print(">> Received (ERROR: '{}')"
                    .format(reply.err.payload.decode("utf-8")))
     
    def run(self):
        ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    print('starting zenoh gui')

    zenoh_gui = ZenohGui()
    zenoh_gui.run()