"""Behavior checks without a TV, Sonos, keys, or configuration writes."""
import asyncio
import unittest
from unittest.mock import patch
from reader_under_test import VolumeReader


class ReaderTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.sent = []
        async def send(direction):
            self.sent.append(direction)
        self.reader = VolumeReader("test",5555,None,"Xiaomi RC Consumer Control",send,lambda value: None)

    async def asyncTearDown(self):
        await self.reader.stop()

    async def test_short_press_once_and_ignore_other_keys(self):
        await self.reader.handle_line("EV_KEY KEY_VOLUMEUP DOWN")
        await self.reader.handle_line("EV_KEY KEY_VOLUMEUP UP")
        await self.reader.handle_line("EV_KEY KEY_WWW DOWN")
        await asyncio.sleep(0.5)
        self.assertEqual(self.sent,["up"])

    async def test_hold_repeats_and_release_stops(self):
        await self.reader.handle_line("EV_KEY KEY_VOLUMEDOWN DOWN")
        await asyncio.sleep(0.5)
        await self.reader.handle_line("EV_KEY KEY_VOLUMEDOWN UP")
        count=len(self.sent)
        self.assertGreaterEqual(count,2)
        await asyncio.sleep(0.3)
        self.assertEqual(len(self.sent),count)

    async def test_failed_action_does_not_start_repeat(self):
        async def fail(_direction):
            raise ConnectionError()
        self.reader.send=fail
        with self.assertRaises(ConnectionError):
            await self.reader.handle_line("EV_KEY KEY_VOLUMEUP DOWN")
        self.assertIsNone(self.reader._repeat_task)

    async def test_colors_once_per_press_without_volume(self):
        colors=[]
        async def button(color):
            colors.append(color)
        self.reader.button=button
        for key in ("KEY_EJECTCD","KEY_SHUFFLE","KEY_SEARCH"):
            await self.reader.handle_line("EV_KEY "+key+" DOWN")
            await self.reader.handle_line("EV_KEY "+key+" DOWN")
            await self.reader.handle_line("EV_KEY "+key+" REPEAT")
            await self.reader.handle_line("EV_KEY "+key+" UP")
        await self.reader.handle_line("EV_KEY KEY_STOPCD DOWN")
        self.assertEqual(colors,["green","yellow","blue"])
        self.assertEqual(self.sent,[])
        await self.reader.handle_line("EV_KEY KEY_SEARCH DOWN")
        await self.reader.handle_line("EV_KEY KEY_SEARCH UP")
        self.assertEqual(colors,["green","yellow","blue","blue"])

    async def test_shutdown_closes_idle_connection(self):
        closed=[]
        statuses=[]
        class FakeDevice:
            def __init__(self,*args,**kwargs): pass
            async def connect(self,**kwargs): return True
            async def shell(self,*args,**kwargs):
                return 'add device 1: /dev/input/event99\n name: "Xiaomi RC Consumer Control"\n'
            async def streaming_shell(self,*args,**kwargs):
                await asyncio.Event().wait()
                yield ""
            async def close(self): closed.append(True)
        self.reader.status=statuses.append
        with patch('reader_under_test.AdbDeviceTcpAsync',FakeDevice):
            self.reader.start()
            await asyncio.sleep(0.02)
            await asyncio.wait_for(self.reader.stop(),timeout=1)
        self.assertIn("listening",statuses)
        self.assertTrue(closed)
        self.assertEqual(statuses[-1],"stopped")

    async def test_tv_plus_once_per_press_and_no_volume(self):
        buttons=[]
        async def button(value): buttons.append(value)
        self.reader.button=button
        for action in ("DOWN","DOWN","REPEAT","UP","DOWN","UP"):
            await self.reader.handle_line("EV_KEY KEY_WWW " + action)
        self.assertEqual(buttons,["tv_plus","tv_plus"])
        self.assertEqual(self.sent,[])
