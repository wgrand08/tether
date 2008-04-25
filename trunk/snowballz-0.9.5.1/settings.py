import pygame
import os
from ConfigParser import ConfigParser, NoOptionError

config = ConfigParser()
pygame.init()

def toggle(option, options):
    options = list(options)
    qm = config.get('display',option)
    i = options.index(qm)
    if i == len(options)-1:
        i = 0
    else:
        i += 1

    config.set('display', option, options[i])
    save_config()
    return options[i]

def get_res():
    try:
        qm = config.get('display','resolution')
    except NoOptionError:
        config.set('display', 'resolution', '0')
        save_config()
        qm = 0
    return get_res_available()[int(qm)]

def get_option(option):
    try:
        qm = config.get('display',option)
    except NoOptionError:
        config.set('display', option, '1')
        save_config()
        qm = "1"
    return qm

def get_res_available():
    res_available = pygame.display.list_modes()
    res_available.reverse()
    res_available_new = []
    for r in res_available:
        if r[0] >= 640 and r[1] >= 480:
            res_available_new.append(r)
    return res_available_new


def get_config_path():
    pathname = ""
    try:
        pathname = os.path.join(os.environ["HOME"], ".snowballz")
    except:
        try:
            pathname = os.path.join(os.environ["APPDATA"], "SnowballZ")
        except:
            print "Couldn't get environment variable for home directory"
            pathname = "."
    return pathname+".ini"


def load_config():
    path = get_config_path()
    r = config.read(path)
    if not r:
        # Setup settings.
        config.add_section('display')
        config.add_section('player')
        res_available = get_res_available()
        config.set('display', 'resolution', str(len(res_available)-1))
        config.set('display', 'snowballdetail', '3')
        config.set('player', 'name', 'Snowballer')
        file = open(path, 'w')
        config.write(file)


def save_config():
    path = get_config_path()
    file = open(path, 'w')
    config.write(file)

load_config()