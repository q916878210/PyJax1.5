"""
Created on Oct 1, 2014

@author: Sean Mead
"""


import os
import time
import inspect
import platform
import subprocess


class File(object):
    def __init__(self, filename):
        self.__filename = filename

    def delete(self):
        if self.__filename:
            if os.path.exists(self.__filename):
                os.remove(self.__filename)


class PlatformHolder(type):
    PLATFORM_NAME = platform.system()

    @staticmethod
    def is_windows():
        return 'Windows' in PlatformHolder.PLATFORM_NAME

    @staticmethod
    def is_mac():
        return 'Darwin' in PlatformHolder.PLATFORM_NAME

    @staticmethod
    def is_linux():
        return 'Linux' in PlatformHolder.PLATFORM_NAME


def set_title(title):
    if PlatformHolder.is_mac():
        os.system("osascript -e 'tell application \"Terminal\" to set custom title of front window to \"%s\"'" % title)


def get_title():
    if PlatformHolder.is_mac():
        name = call("osascript -e 'tell application \"Terminal\" to get custom title of front window'")
        if len(name) > 0:
            name = str(name[0]).strip()
        return name


def close_terminal_window(title):
    if PlatformHolder.is_mac():
        os.system("osascript -e 'tell application \"Terminal\" to close (every window whose custom title is \"%s\")'" % title)


def close_process(pid):
    if PlatformHolder.is_windows():
        pass
    else:
        os.system('kill -9 %s' % pid)


def call_terminal(arg):
    if PlatformHolder.is_windows():
        subprocess.call('start cmd /K %s' % arg, shell=True)
    else:
        os.system('open -a /Applications/Utilities/Terminal.app %s' % arg)


def call(*args):
    try:
        return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    except Exception as exc:
        return exc


def get_parent_id(pid):
    if not PlatformHolder.is_windows():
        result = call('ps -p %s -o ppid=' % pid)
        if len(result) > 0:
            return str(result[0]).strip()


def get_terminal_id():
    if not PlatformHolder.is_windows():
        return get_parent_id(get_parent_id(get_parent_id(os.getppid())))


def get_address_local():
    for interface_name in get_interfaces():
        interface = get_interface(interface_name)
        if PlatformHolder.is_windows():
            net = interface.get('IP Address')
        elif PlatformHolder.is_mac():
            net = interface.get('inet')
        elif PlatformHolder.is_linux():
            net = interface.get('inet addr')
        if net and net.startswith('127.'):
            return net


def get_address():
    net = None
    for interface_name in get_interfaces():
        interface = get_interface(interface_name)
        if PlatformHolder.is_windows():
            net = interface.get('IP Address')
        elif PlatformHolder.is_mac() and interface.get('status') == 'active':
            net = interface.get('inet')
        elif PlatformHolder.is_linux() and not interface.get('inet addr').startswith('127.'):
            net = interface.get('inet addr')
        if net:
            return net


def get_interfaces():
    if PlatformHolder.is_windows():
        interfaces = subprocess.check_output('netsh interface show interface', shell=True).split('\n')[3:]
        return [item.split('     ')[-1].strip() for item in interfaces if item.strip() != '']
    elif PlatformHolder.is_mac():
        return subprocess.check_output('ifconfig -lu', shell=True).split(' ')
    elif PlatformHolder.is_linux():
        interfaces = subprocess.check_output('ifconfig -s', shell=True).split('\n')[1:]
        return [item.split(' ')[0].strip() for item in interfaces]


def get_interface(interface_name):
    interface = {'name': interface_name}
    if PlatformHolder.is_windows():
        items = subprocess.check_output('netsh interface ip show addresses "%s"' % interface_name, shell=True).split('\n')
        items = [item.strip().split(':') for item in items[2:] if item.strip() != '']
        for item in items:
            try:
                interface.update({item[0].strip(): item[1].strip()})
            except IndexError:
                pass
    elif PlatformHolder.is_mac():
        for line in subprocess.check_output('ifconfig %s' % interface_name, shell=True).split('\n'):
            if '\t' in line:
                line = line.replace('\t', '')
                line = line.split(' ', 1)
                if len(line) > 1:
                    items = str(line[1]).split(' ')
                    interface.update({line[0].replace(':', '').strip(): items[0].strip()})
                    count = 0
                    for index in range(0, len(items)):
                        try:
                            interface.update({items[count].strip(): items[count + 1].strip()})
                        except IndexError:
                            pass
                        count += 2
    elif PlatformHolder.is_linux():
        items = subprocess.check_output('ifconfig %s | grep "Link\|inet"' % interface_name, shell=True).split('\n')
        items = [item.strip().split(':', 1) for item in items]
        for item in items:
            if item[0] and item[-1]:
                interface[item[0]] = item[-1].split(' ')[0].strip()
    return interface


def route_path():
    """
    Change the os directory to the current site.
    """
    os.chdir(up_path(get_path()))


def new_window_path():
    return '%s/new-window.command' % up_path(up_path(get_path()))


def up_path(path):
    return os.path.abspath(os.path.join(path, os.pardir))


def get_path():
    return os.path.realpath(inspect.getfile(inspect.currentframe()))


def clear_screen():
    """
    Clear the terminal/cmd screen.
    """
    if PlatformHolder.is_windows():
        os.system('cls')
    else:
        os.system('clear')


def terminate():
    """
    Destroy all pythons.
    """
    if PlatformHolder.is_windows():
        os.system('taskkill -f -im python.exe')
    else:
        os.system('sudo pkill -9 Python')


def get_epoch(date):
    return int(time.mktime(time.strptime(str(date), '%Y-%m-%d %H:%M:%S')))


def human_time(epoch=time.time()):
    """
    Return a human readable epoch.
    :param epoch:
    """
    return time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime(epoch))


def human_gmt_time(epoch=time.time()):
    """
    Return a human readable epoch.
    :param epoch:
    """
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(epoch))


def split_extension(filename):
    """
    Returns the name, ext of the given filename.
    :param filename: filename to split
    """
    name, ext = os.path.splitext(filename)
    ext = ext.replace(".", "")
    return name, ext


def get_files(path):
    """
    Parses through a directory and finds all files.
    :rtype : list
    :param path: path to parent of the files
    """
    try:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.startswith('.')]
    except OSError:
        return []


def applications():
    if os.path.isdir("/Applications"):
        return os.listdir("/Applications")
    return []


def open_in_browser(browser, url):
    if PlatformHolder.is_mac():
        if not browser:
            browser = 'Safari'
        for app in applications():
            if app.lower().find(browser.lower()) != -1:
                subprocess.call(["open", "-a", app, url])
    elif PlatformHolder.is_windows():
        if not browser:
            browser = 'iexplore'
        subprocess.call([browser, url])