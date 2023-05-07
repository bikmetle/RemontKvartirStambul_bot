# RemontKvartirStambul_bot
##### systemd

1. Create a venv (virtual environment): `python3 -m venv venv` (or any other Python 3.9+ version);
2. `source venv/bin/activate && pip install -r requirements.txt`;
3. Move `supportbot.service` to `/etc/systemd/system`;
4. Open that file and change values for `WorkingDirectory`, `ExecStart` and `EnvironmentFile` providing the correct path values;
5. Start your bot and enable its autostart: `sudo systemctl enable supportbot.service --now`;  
6. Check your bots status and logs: `systemctl status supportbot.service`.