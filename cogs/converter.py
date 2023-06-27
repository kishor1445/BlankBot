import base64
import random
from discord.ext import commands

MORSE_TO_TEXT_DICT = {
            ".-": "a",
            "-...": "b",
            "-.-.": "c",
            "-..": "d",
            ".": "e",
            "..-.": "f",
            "--.": "g",
            "....": "h",
            "..": "i",
            ".---": "j",
            "-.-": "k",
            ".-..": "l",
            "--": "m",
            "-.": "n",
            "---": "o",
            ".--.": "p",
            "--.-": "q",
            ".-.": "r",
            "...": "s",
            "-": "t",
            "..-": "u",
            "...-": "v",
            ".--": "w",
            "-..-": "x",
            "-.--": "y",
            "--..": "z",
            "-----": "0",
            ".----": "1",
            "..---": "2",
            "...--": "3",
            "....-": "4",
            ".....": "5",
            "-....": "6",
            "--...": "7",
            "---..": "8",
            "----.": "9",
            ".-.-.-": ".",
            "--..--": ",",
            "..--..": "?",
            ".----.": "'",
            "-.-.--": "!",
            "-..-.": "/",
            "-.--.": "(",
            "-.--.-": ")",
            ".-...": "&",
            "---...": ":",
            "-.-.-.": ";",
            "-...-": "=",
            ".-.-.": "+",
            "-....-": "-",
            "..--.-": "_",
            ".-..-.": '"',
            "...-..-": "$",
            ".--.-.": "@"
        }


TEXT_TO_MORSE_DICT = {'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.', 'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..', 'm': '--', 'n': '-.', 'o': '---', 'p': '.--.', 'q': '--.-', 'r': '.-.', 's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-', 'y': '-.--', 'z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.'}


class Converter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="convert", aliases=["conv"])
    async def convert(self, ctx):
        ...

    @convert.command(name="ascii2text", aliases=["a2t"])
    async def ascii_to_text(self, ctx, *, ascii_numbers: str):
        await ctx.send(
            "".join(chr(int(ascii_number)) for ascii_number in ascii_numbers.split())
        )

    @convert.command(name="text2ascii", aliases=["t2a"])
    async def text_to_ascii(self, ctx, *, text: str):
        await ctx.send(" ".join(str(ord(char)) for char in text))

    @convert.command(name="binary2text", aliases=["b2t"])
    async def binary_to_text(self, ctx, *, binary: str):
        await ctx.send(
            "".join(chr(int(binary_number, 2)) for binary_number in binary.split())
        )

    @convert.command(name="text2binary", aliases=["t2b"])
    async def text_to_binary(self, ctx, *, text: str):
        await ctx.send(" ".join(bin(ord(char))[2:] for char in text))

    @convert.command(name="hex2text", aliases=["h2t"])
    async def hex_to_text(self, ctx, *, hex_: str):
        await ctx.send(
            "".join(chr(int(hex_number, 16)) for hex_number in hex_.split())
        )

    @convert.command(name="text2hex", aliases=["t2h"])
    async def text_to_hex(self, ctx, *, text: str):
        await ctx.send(" ".join(hex(ord(char))[2:] for char in text))

    @convert.command(name="octal2text", aliases=["o2t"])
    async def octal_to_text(self, ctx, *, octal: str):
        await ctx.send(
            "".join(chr(int(octal_number, 8)) for octal_number in octal.split())
        )

    @convert.command(name="text2octal", aliases=["t2o"])
    async def text_to_octal(self, ctx, *, text: str):
        await ctx.send(" ".join(oct(ord(char))[2:] for char in text))

    @convert.command(name="base64encode", aliases=["b64e"])
    async def base64_encode(self, ctx, *, text: str):
        await ctx.send(base64.b64encode(text.encode()).decode())

    @convert.command(name="base64decode", aliases=["b64d"])
    async def base64_decode(self, ctx, *, text: str):
        await ctx.send(base64.b64decode(text.encode()).decode())

    @convert.command(name="morse2text", aliases=["m2t"])
    async def morse_to_text(self, ctx, *, morse: str):
        morse = morse.split()
        msg = ""
        for char in morse:
            if char == '/':
                msg += ' '
            else:
                msg += MORSE_TO_TEXT_DICT.get(char, char)
        await ctx.send(msg)

    @convert.command(name="text2morse", aliases=["t2m"])
    async def text_to_morse(self, ctx, *, text: str):
        text = text.lower()
        msg = ""
        for char in text:
            if char == ' ':
                msg += '/ '
            else:
                msg += TEXT_TO_MORSE_DICT.get(char) + ' '
        await ctx.send(msg)

    @convert.command(name="revtext", aliases=["rt", "revt"])
    async def text_to_reverse(self, ctx, *, text: str):
        await ctx.send(text[::-1])

    @convert.command(name="revword", aliases=["rw", "revw"])
    async def word_to_reverse(self, ctx, *, text: str):
        await ctx.send(" ".join(text.split()[::-1]))

    @convert.command(name="shuffleWord", aliases=["sw", "shw"])
    async def word_to_shuffle(self, ctx, *, text: str):
        text = text.split()
        random.shuffle(text)
        await ctx.send(" ".join(text))


async def setup(bot):
    await bot.add_cog(Converter(bot))
