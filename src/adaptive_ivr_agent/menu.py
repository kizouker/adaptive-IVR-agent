"""Holdmate menu as an object-oriented Python app (#201).

Rich tables/panels, real i18n dict (en default, sv toggle), same files
as the shell menu (.talk-volume, .talk-output, .menu-lang, .talk-quiet)
so both launchers interoperate. Actions shell out to the existing
sh/*.sh workers; the server stops on exit when started here.

Run: ./sh/menu.sh   (needs rich: .venv, uv run, or pip install rich)
"""
from __future__ import annotations

import atexit
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from adaptive_ivr_agent.menu_devices import (
    INPUT_FILE,
    VOLUME_FILE,
    clamp_volume,
    read_input_name,
    read_volume,
    system_inputs,
    system_outputs,
)
from adaptive_ivr_agent.menu_music import menu_music_path

ROOT = Path(__file__).resolve().parent.parent.parent
SH = ROOT / "sh"
BOARD_DIR = ROOT / "ui" / "board"
BOARD_LOG = Path("/tmp/holdmate-board.log")
OUTPUT_FILE = ROOT / ".talk-output"
LANG_FILE = ROOT / ".menu-lang"
QUIET_FILE = ROOT / ".talk-quiet"
PORT = os.environ.get("PORT", "5173")

STRINGS: dict[str, dict[str, str]] = {
    "tagline": {"en": "waits on hold, so you don't have to",
                "sv": "väntar i kö, så du slipper"},
    "menu_title": {"en": "Holdmate menu", "sv": "Holdmate-meny"},
    "m_board": {"en": "Board + talk (server, page, call)",
                "sv": "Tavla + samtal (server, sida, samtal)"},
    "m_talk": {"en": "Talk options (server runs already)",
               "sv": "Samtalsval (servern kör redan)"},
    "m_misc": {"en": "Misc...", "sv": "Övrigt..."},
    "m_lessons": {"en": "Holdmate phones Roksolana alone (BFS)",
                  "sv": "Holdmate ringer Roksolana själv (BFS)"},
    "m_sound": {"en": "Sound", "sv": "Ljud"},
    "m_change": {"en": "(change...)", "sv": "(ändra...)"},
    "m_github": {"en": "GitHub (repo, site, pulls...)",
                 "sv": "GitHub (repo, sajt, pulls...)"},
    "m_diesel": {"en": "Diesel walk", "sv": "Dieselpromenad"},
    "m_lang": {"en": "Language: English (change)",
               "sv": "Språk: svenska (ändra)"},
    "m_quit": {"en": "Quit", "sv": "Avsluta"},
    "back": {"en": "Back", "sv": "Tillbaka"},
    "bye": {"en": "Bye", "sv": "Hej då"},
    "pick": {"en": "Pick", "sv": "Välj"},
    "invalid": {"en": "pick a number from the list (q quits)",
                "sv": "välj ett nummer i listan (q avslutar)"},
    "gh_title": {"en": "GitHub", "sv": "GitHub"},
    "gh_repo": {"en": "Open repo", "sv": "Öppna repo"},
    "gh_site": {"en": "Open live site (Pages)", "sv": "Öppna sajten (Pages)"},
    "gh_pulls": {"en": "Open pull requests", "sv": "Öppna pull requests"},
    "gh_issues": {"en": "Open issues", "sv": "Öppna issues"},
    "gh_actions": {"en": "Open Actions", "sv": "Öppna Actions"},
    "out_title": {"en": "Output (now:", "sv": "Utdata (nu:"},
    "speakers": {"en": "Speakers", "sv": "Högtalare"},
    "vol_title": {"en": "Volume (now:", "sv": "Volym (nu:"},
    "louder": {"en": "Louder (+)", "sv": "Högre (+)"},
    "quieter": {"en": "Quieter (-)", "sv": "Lägre (-)"},
    "snd_title": {"en": "Sound (now:", "sv": "Ljud (nu:"},
    "snd_output": {"en": "Output:", "sv": "Utdata:"},
    "snd_volume": {"en": "Volume:", "sv": "Volym:"},
    "snd_quiet": {"en": "Quiet:", "sv": "Tyst:"},
    "quiet_word": {"en": "Quiet", "sv": "Tyst"},
    "on": {"en": "on", "sv": "på"},
    "off": {"en": "off", "sv": "av"},
    "talk_title": {"en": "Talk options", "sv": "Samtalsval"},
    "t_talk": {"en": "Talk to Roksolana", "sv": "Prata med Roksolana"},
    "t_airpods": {"en": "Talk with AirPods", "sv": "Prata med AirPods"},
    "t_check": {"en": "Sound check only", "sv": "Endast ljudkoll"},
    "t_persona": {"en": "Talk as persona", "sv": "Prata som persona"},
    "t_quiet": {"en": "Talk quietly (type + read)",
                "sv": "Prata tyst (skriv + läs)"},
    "lsn_title": {"en": "Holdmate phones Roksolana alone",
                  "sv": "Holdmate ringer Roksolana själv"},
    "lsn_silent": {"en": "All personas, silent",
                   "sv": "Alla personas, tyst"},
    "lsn_spoken": {"en": "All personas, spoken (Oskar + Alva)",
                   "sv": "Alla personas, tal (Oskar + Alva)"},
    "lsn_one": {"en": "One persona, spoken (pick...)",
                "sv": "En persona, tal (välj...)"},
    "stopped": {"en": "stopped early, partial knowledge saved",
                "sv": "stoppade tidigt, delkunskap sparad"},
    "misc_title": {"en": "Misc", "sv": "Övrigt"},
    "teach": {"en": "Teach Roksolana new words (disabled)",
              "sv": "Lär Roksolana nya ord (avstängt)"},
    "teach_off": {"en": "Teaching is disabled (Roksolana stays dumb; Holdmate learns)",
                  "sv": "Inlärning avstängd (Roksolana förblir dum; Holdmate lär)"},
    "step_board": {"en": "Board + talk", "sv": "Tavla + samtal"},
    "opened": {"en": "opened", "sv": "öppnade"},
    "in_browser": {"en": "in your browser", "sv": "i webbläsaren"},
    "open_this": {"en": "open this", "sv": "öppna detta"},
    "vol_word": {"en": "volume", "sv": "volym"},
    "vol_used": {"en": "(used by the next talk)",
                 "sv": "(används av nästa samtal)"},
    "snd_word": {"en": "sound", "sv": "ljud"},
    "auto_pick": {"en": "Auto-follow (AirPods when worn)",
                  "sv": "Autofölj (AirPods när de bärs)"},
    "auto_on": {"en": "output: auto-follow on", "sv": "utdata: autofölj på"},
    "srv_up": {"en": "board up:", "sv": "tavlan uppe:"},
    "srv_reuse": {"en": "reusing running server:",
                  "sv": "återanvänder server:"},
    "srv_stop": {"en": "board server stopped", "sv": "boardservern stoppad"},
    "persona_title": {"en": "Pick a persona", "sv": "Välj en persona"},
    "in_title": {"en": "Input (now:", "sv": "Indata (nu:"},
    "snd_input": {"en": "Input:", "sv": "Indata:"},
    "in_auto": {"en": "Auto (default mic)", "sv": "Auto (standardmic)"},
    "in_on": {"en": "input: default mic", "sv": "indata: standardmic"},
    "snd_check": {"en": "Sound check", "sv": "Ljudkoll"},
    "t_self": {"en": "I practice myself", "sv": "Jag tränar själv"},
    "t_holdmate": {"en": "Holdmate trains itself", "sv": "Holdmate tränar själv"},
}

BANNER = r""" _   _  ___  _     ____  __  __    _  _____ _____
| | | |/ _ \| |   |  _ \|  \/  |  / \|_   _| ____|
| |_| | | | | |   | | | | |\/| | / _ \ | | |  _|
|  _  | |_| | |___| |_| | |  | |/ ___ \| | | |___
|_| |_|\___/|_____|____/|_|  |_/_/   \_\_| |_____|"""

CAT = "  /\\_/\\  Diesel supervises\n ( o.o )\n  > ^ <"


class I18N:
    def __init__(self, lang: str = "en") -> None:
        self.lang = lang if lang in ("en", "sv") else "en"

    def t(self, key: str) -> str:
        return STRINGS[key].get(self.lang, STRINGS[key]["en"])

    def toggle(self) -> None:
        self.lang = "sv" if self.lang == "en" else "en"
        LANG_FILE.write_text(self.lang, encoding="utf-8")


def load_lang() -> str:
    try:
        value = LANG_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return "en"
    return value if value in ("en", "sv") else "en"


def read_personas() -> list[tuple[str, str]]:
    raw = json.loads((ROOT / "data/role-phrasebooks.json").read_text())
    return [(role["id"], role["label"]) for role in raw["roles"]]


@dataclass
class MenuItem:
    label: str
    action: str = ""
    data: str = ""


@dataclass
class App:
    i18n: I18N
    verbose: bool = False
    url: str = f"http://localhost:{PORT}"
    server_proc: object = None
    music_proc: object = None
    sound: str = "speakers"
    sound_dirty: bool = False

    def __post_init__(self) -> None:
        from rich.console import Console
        self.console = Console()
        self._sync_sound()
        try:
            if QUIET_FILE.read_text(encoding="utf-8").strip() == "1":
                self.sound = "quiet"
                self.sound_dirty = True
        except OSError:
            pass
        atexit.register(self.stop_server)
        atexit.register(self.stop_music)

    # -- display ------------------------------------------------------
    def banner(self) -> None:
        from rich.panel import Panel
        self.console.print(Panel(
            f"[bold cyan]{BANNER}[/]\n[dim]{self.i18n.t('tagline')}\n"
            f"board: {self.url}[/]\n[yellow]{CAT}[/]",
            border_style="cyan"))

    def show(self, title: str, items: list[MenuItem]) -> str:
        self.console.clear()
        self.banner()
        if sys.stdin.isatty():
            from simple_term_menu import TerminalMenu
            entries: list[str] = []
            for number, item in enumerate(items, 1):
                entries.append(f"[{number}]  {item.label}")
                entries.append("")
            entries.pop()
            picked = TerminalMenu(
                entries,
                title=f"  {title}",
                menu_cursor="→ ",
                menu_cursor_style=("fg_cyan", "bold"),
                cycle_cursor=True,
                clear_screen=False,
                skip_empty_entries=True,
                status_bar="↑↓ + Enter, q",
            ).show()
            if picked is None:
                return "q"
            return str(picked // 2 + 1)
        from rich.table import Table
        table = Table(title=f"[bold]{title}[/]", show_header=False,
                      box=None, padding=(0, 2))
        for number, item in enumerate(items, 1):
            table.add_row(f"[cyan][{number}][/]", item.label)
        self.console.print(table)
        picked = self.console.input(
            f"[dim]{self.i18n.t('pick')} 1-{len(items)}, "
            f"0={self.i18n.t('back').lower()} "
            f"(q={self.i18n.t('m_quit').lower()}): [/]").strip()
        if picked == "0":
            return str(len(items))  # Back/Quit is always last
        return picked

    # -- sound state --------------------------------------------------
    def _sync_sound(self) -> None:
        if self.sound_dirty:
            return
        for dev in system_outputs():
            if "airpods" in dev.lower():
                self.sound = "airpods"
                return
        current = self._current_output()
        if current and "airpods" in current.lower():
            self.sound = "airpods"
            return
        self.sound = "speakers"

    @staticmethod
    def _current_output() -> str:
        exe = shutil.which("SwitchAudioSource")
        if not exe:
            return ""
        proc = subprocess.run([exe, "-c", "-t", "output"], capture_output=True,
                              text=True, timeout=10)
        return proc.stdout.strip()

    def sound_label(self) -> str:
        if self.sound == "airpods":
            return "AirPods"
        if self.sound == "quiet":
            return self.i18n.t("quiet_word")
        return self.i18n.t("speakers")

    # -- workers ------------------------------------------------------
    def run_sh(self, *args: str) -> int:
        self.stop_music()
        env = dict(os.environ)
        if self.i18n.lang == "sv":
            args = (*args, "--lang=sv")
        proc = subprocess.run([str(SH / args[0]), *args[1:]], cwd=ROOT)
        return proc.returncode

    def server_up(self) -> bool:
        try:
            with urllib.request.urlopen(self.url, timeout=2):  # nosec B310: localhost only
                return True
        except OSError:
            return False

    def refresh_url(self) -> None:
        try:
            text = BOARD_LOG.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        import re
        match = re.search(r"http://localhost:\d+", text)
        if match:
            self.url = match.group(0)

    def start_server(self) -> None:
        if self.server_up():
            self.console.print(f"[green]✔ {self.i18n.t('srv_reuse')} "
                               f"{self.url}[/]")
            return
        log = BOARD_LOG.open("w", encoding="utf-8")
        self.server_proc = subprocess.Popen(
            ["npm", "run", "dev", "--prefix", str(BOARD_DIR)],
            stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
        for _ in range(25):
            self.refresh_url()
            if self.server_up():
                self.console.print(f"[green]✔ {self.i18n.t('srv_up')} "
                                   f"{self.url}[/]")
                return
            time.sleep(1)
        self.console.print("[red]board did not answer "
                           f"(see {BOARD_LOG})[/]")
        raise SystemExit(1)

    def stop_server(self) -> None:
        proc = self.server_proc
        self.server_proc = None
        if proc is not None:
            proc.terminate()
            self.console.print(f"[dim]{self.i18n.t('srv_stop')}[/]")

    def start_music(self) -> None:
        if self.music_proc is not None:
            if self.music_proc.poll() is None:
                return
            self.music_proc = None
        if self.sound == "quiet":
            return
        if shutil.which("afplay") is None:
            return
        try:
            path = menu_music_path()
        except OSError:
            return
        self.music_proc = subprocess.Popen(
            ["afplay", path], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

    def stop_music(self) -> None:
        proc = self.music_proc
        self.music_proc = None
        if proc is not None:
            proc.terminate()

    def open_url(self, url: str) -> None:
        if shutil.which("open"):
            subprocess.run(["open", url], check=False)
            self.console.print(f"[green]✔ {self.i18n.t('opened')} {url} "
                               f"{self.i18n.t('in_browser')}[/]")
        else:
            self.console.print(f"[dim]{self.i18n.t('open_this')} "
                               f"{self.i18n.t('in_browser')}: {url}[/]")

    # -- menus --------------------------------------------------------
    def menu_main(self) -> None:
        i = self.i18n
        while True:
            self._sync_sound()
            self.start_music()
            items = [
                MenuItem(i.t("m_board"), "board"),
                MenuItem(i.t("m_talk"), "talk"),
                MenuItem(i.t("m_misc"), "misc"),
                MenuItem(i.t("m_lessons"), "lessons"),
                MenuItem(f"{i.t('m_sound')}: {self.sound_label()} "
                         f"{i.t('m_change')}", "sound"),
                MenuItem(i.t("m_github"), "github"),
                MenuItem(i.t("m_diesel"), "diesel"),
                MenuItem(i.t("m_lang"), "lang"),
                MenuItem(i.t("m_quit"), "quit"),
            ]
            choice = self.show(i.t("menu_title"), items)
            if choice in ("q", "Q", "9"):
                self.console.print(f"[bold]{i.t('bye')}[/]")
                if sys.stdin.isatty():
                    subprocess.run([str(SH / "diesel.sh"), "12"], cwd=ROOT)
                return
            action = {"1": "board", "2": "talk", "3": "misc", "4": "lessons",
                      "5": "sound", "6": "github", "7": "diesel",
                      "8": "lang"}.get(choice, "")
            if action == "board":
                self.start_server()
                self.open_url(self.url)
                self.run_sh("talk.sh")
            elif action == "talk":
                self.menu_talk()
            elif action == "misc":
                self.menu_misc()
            elif action == "lessons":
                self.menu_lessons()
            elif action == "sound":
                self.menu_sound()
            elif action == "github":
                self.menu_github()
            elif action == "diesel":
                subprocess.run([str(SH / "diesel.sh"), "30"], cwd=ROOT)
            elif action == "lang":
                i.toggle()
            else:
                self.console.print(f"[yellow]{i.t('invalid')}[/]")
                time.sleep(1)

    def menu_github(self) -> None:
        i = self.i18n
        gh = "https://github.com/kizouker/adaptive-IVR-agent"
        links = [i.t("gh_repo"), i.t("gh_site"), i.t("gh_pulls"),
                 i.t("gh_issues"), i.t("gh_actions"), i.t("back")]
        urls = [gh, "https://kizouker.github.io/adaptive-IVR-agent/",
                gh + "/pulls", gh + "/issues", gh + "/actions"]
        while True:
            choice = self.show(i.t("gh_title"),
                               [MenuItem(label) for label in links])
            if choice in ("q", "Q", "6", "b", "B"):
                return
            if choice in ("1", "2", "3", "4", "5"):
                self.open_url(urls[int(choice) - 1])
                time.sleep(1)
            else:
                self.console.print(f"[yellow]{i.t('invalid')}[/]")
                time.sleep(1)

    def menu_sound(self) -> None:
        i = self.i18n
        while True:
            volume = read_volume()
            quiet_state = (i.t("on") if self.sound == "quiet"
                           else i.t("off"))
            mic = read_input_name() or "MacBook Pro-mikrofon"
            items = [
                MenuItem(f"{i.t('snd_output')} {self.sound_label()} "
                         f"{i.t('m_change')}", "output"),
                MenuItem(f"{i.t('snd_input')} {mic} {i.t('m_change')}",
                         "input"),
                MenuItem(f"{i.t('snd_volume')} {volume} {i.t('m_change')}",
                         "volume"),
                MenuItem(f"{i.t('snd_quiet')} {quiet_state} "
                         f"{i.t('m_change')}", "quiet"),
                MenuItem(i.t("snd_check"), "check"),
                MenuItem(i.t("back"), "back"),
            ]
            title = (f"{i.t('snd_title')} {self.sound_label()}, "
                     f"{i.t('vol_word')} {volume})")
            choice = self.show(title, items)
            if choice in ("q", "Q", "6", "b", "B"):
                return
            if choice == "1":
                self.menu_output()
            elif choice == "2":
                self.menu_input()
            elif choice == "3":
                self.menu_volume()
            elif choice == "4":
                self.sound = ("speakers" if self.sound == "quiet"
                              else "quiet")
                self.sound_dirty = True
                QUIET_FILE.write_text(
                    "1" if self.sound == "quiet" else "0",
                    encoding="utf-8")
                if self.sound == "quiet":
                    self.stop_music()
                else:
                    self.start_music()
            elif choice == "5":
                self.run_sh("talk.sh", "check")
                self.console.input("[dim](Enter) [/]")
            else:
                self.console.print(f"[yellow]{i.t('invalid')}[/]")
                time.sleep(1)

    def menu_input(self) -> None:
        i = self.i18n
        devs = system_inputs()
        if not devs:
            self.console.print(f"[yellow]{i.t('invalid')}[/]")
            time.sleep(1)
            return
        labels = [*devs, i.t("in_auto"), i.t("back")]
        current = read_input_name()
        choice = self.show(f"{i.t('in_title')} {current or 'auto'})",
                           [MenuItem(label) for label in labels])
        if not choice.isdigit():
            return
        picked = labels[int(choice) - 1] if 1 <= int(choice) <= len(labels) \
            else ""
        if picked == i.t("back") or not picked:
            return
        if picked == i.t("in_auto"):
            INPUT_FILE.unlink(missing_ok=True)
            self.console.print(f"[dim]{i.t('in_on')}[/]")
        else:
            INPUT_FILE.write_text(picked, encoding="utf-8")
            self.console.print(f"[dim]{i.t('snd_input')} {picked}[/]")
            if "blackhole" in picked.lower():
                self.console.print("[yellow]BlackHole captures system "
                                   "audio, not your voice[/]")
        time.sleep(1)

    def menu_output(self) -> None:
        i = self.i18n
        devs = system_outputs()
        if not devs:
            devs = [i.t("speakers"), "AirPods"]
        labels = [*devs, i.t("auto_pick"), i.t("back")]
        choice = self.show(f"{i.t('out_title')} {self.sound_label()})",
                           [MenuItem(label) for label in labels])
        if not choice.isdigit():
            return
        picked = labels[int(choice) - 1] if 1 <= int(choice) <= len(labels) \
            else ""
        if picked == i.t("back") or not picked:
            return
        if picked == i.t("auto_pick"):
            OUTPUT_FILE.unlink(missing_ok=True)
            self.sound_dirty = False
            self.console.print(f"[dim]{i.t('auto_on')}[/]")
        else:
            OUTPUT_FILE.write_text(picked, encoding="utf-8")
            self.sound_dirty = True
            self.sound = ("airpods" if "airpods" in picked.lower()
                          else "speakers")
            self.console.print(f"[dim]{i.t('snd_word')}: {picked}[/]")
        time.sleep(1)

    def menu_volume(self) -> None:
        i = self.i18n
        while True:
            volume = read_volume()
            items = [MenuItem(i.t("louder"), "+"),
                     MenuItem(i.t("quieter"), "-"),
                     MenuItem(i.t("back"), "back")]
            choice = self.show(f"{i.t('vol_title')} {volume}, 0.1-4.0)",
                               items)
            if choice in ("q", "Q", "3", "b", "B"):
                return
            if choice == "1":
                VOLUME_FILE.write_text(str(clamp_volume(volume + 0.2)),
                                       encoding="utf-8")
            elif choice == "2":
                VOLUME_FILE.write_text(str(clamp_volume(volume - 0.2)),
                                       encoding="utf-8")

    def menu_talk(self) -> None:
        i = self.i18n
        while True:
            items = [MenuItem(i.t("t_self")), MenuItem(i.t("t_persona")),
                     MenuItem(i.t("t_holdmate")), MenuItem(i.t("back"))]
            choice = self.show(i.t("talk_title"), items)
            if choice in ("q", "Q", "4", "b", "B"):
                return
            if choice == "1":
                self.run_sh("talk.sh")
                return
            if choice == "2":
                persona = self.pick_persona()
                if persona:
                    self.run_sh("talk.sh", "--as", persona)
                    return
            elif choice == "3":
                self.menu_lessons()
                return
            else:
                self.console.print(f"[yellow]{i.t('invalid')}[/]")
                time.sleep(1)

    def pick_persona(self) -> str:
        i = self.i18n
        personas = read_personas()
        labels = [label for _, label in personas] + [i.t("back")]
        choice = self.show(i.t("persona_title"),
                           [MenuItem(label) for label in labels])
        if choice.isdigit() and 1 <= int(choice) <= len(personas):
            return personas[int(choice) - 1][0]
        return ""

    def menu_lessons(self) -> None:
        i = self.i18n
        while True:
            items = [MenuItem(i.t("lsn_silent")), MenuItem(i.t("lsn_spoken")),
                     MenuItem(i.t("lsn_one")), MenuItem(i.t("back"))]
            choice = self.show(i.t("lsn_title"), items)
            if choice in ("q", "Q", "4", "b", "B"):
                return
            if choice == "1":
                self.run_sh("holdmate-call.sh", "--all")
                self.console.print(f"[dim]{i.t('stopped')}[/]")
                return
            if choice == "2":
                self.run_sh("holdmate-call.sh", "--all", "--speak")
                self.console.print(f"[dim]{i.t('stopped')}[/]")
                return
            if choice == "3":
                persona = self.pick_persona()
                if persona:
                    self.run_sh("holdmate-call.sh", "--as", persona,
                                "--speak")
                    self.console.print(f"[dim]{i.t('stopped')}[/]")
                    return
            else:
                self.console.print(f"[yellow]{i.t('invalid')}[/]")
                time.sleep(1)

    def menu_misc(self) -> None:
        i = self.i18n
        while True:
            items = [MenuItem(i.t("teach")), MenuItem(i.t("back"))]
            choice = self.show(i.t("misc_title"), items)
            if choice in ("q", "Q", "2", "b", "B"):
                return
            if choice == "1":
                self.console.print(f"[dim]{i.t('teach_off')}[/]")
                time.sleep(2)
            else:
                self.console.print(f"[yellow]{i.t('invalid')}[/]")
                time.sleep(1)


def preflight(console, verbose: bool) -> None:
    for tool in ("node", "npm", "curl"):
        if not shutil.which(tool):
            console.print(f"[red]{tool} is missing "
                          f"(brew install {tool})[/]")
            raise SystemExit(1)
    if not (BOARD_DIR / "package.json").exists():
        console.print(f"[red]Board not found: {BOARD_DIR}[/]")
        raise SystemExit(1)
    if not (BOARD_DIR / "node_modules").exists():
        console.print("[yellow]installing board deps...[/]")
        proc = subprocess.run(["npm", "ci", "--prefix", str(BOARD_DIR)],
                              cwd=ROOT)
        if proc.returncode != 0:
            console.print("[red]Could not install board deps[/]")
            raise SystemExit(1)
    if verbose:
        console.print("[green]✔ preflight ok[/]")


def main(argv: list[str] | None = None) -> int:
    from rich.console import Console
    args = list(argv) if argv is not None else sys.argv[1:]
    verbose = False
    lang = load_lang()
    mode = "menu"
    for arg in args:
        if arg in ("check", "--check"):
            mode = "check"
        elif arg in ("-v", "--verbose"):
            verbose = True
        elif arg.startswith("--lang="):
            lang = arg.split("=", 1)[1]
        elif arg in ("1", "2", "3", "4"):
            mode = "direct-" + arg
        else:
            print(f"Unknown argument: {arg} "
                  "(use: check, -v, --lang=en|sv, 1, 2, 3, 4)")
            return 1
    if lang not in ("en", "sv"):
        print("--lang must be en or sv")
        return 1
    console = Console()
    preflight(console, verbose)
    if mode == "check":
        console.print("[bold]Check only: nothing changed[/]")
        return 0
    app = App(I18N(lang), verbose)
    if mode == "direct-1":
        app.start_server()
        app.open_url(app.url)
        app.run_sh("talk.sh")
    elif mode == "direct-2":
        app.run_sh("talk.sh")
    elif mode == "direct-3":
        app.console.print(f"[dim]{app.i18n.t('teach_off')}[/]")
    elif mode == "direct-4":
        app.menu_lessons()
    else:
        if sys.stdin.isatty():
            subprocess.run([str(SH / "diesel.sh"), "12"], cwd=ROOT)
        app.menu_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
