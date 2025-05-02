from bot_1 import Bot_1
from bot_2 import Bot_2
from time import sleep
import os

basedir = os.path.abspath(os.path.dirname(__file__))
in_path = os.path.join(basedir, "input.csv")
out_path = os.path.join(basedir, "output.csv")

bot_1 = Bot_1(in_path)
uri = bot_1.run()

sleep(1)

bot_2 = Bot_2(uri, out_path)
bot_2.run()