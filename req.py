import subprocess as sp

try:
    exec(
        """import discord, dotenv, pymongo, apscheduler, pyfiglet, rich, cv2, requests, nacl, torch, transformers"""
    )
except ModuleNotFoundError as e:
    print(f"{e.name} Not Found.\nInstalling ALl Dependencies...")
    try:
        sp.check_call(
            ["pip", "install", "-r", "requirements.txt"],
            stdout=sp.DEVNULL,
            stderr=sp.DEVNULL,
        )  # nosec: B603, B607
    except sp.CalledProcessError:
        print("[ERROR] Installation Failed!")
    print("[✓] Installation Successful!")
