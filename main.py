import sublime
import sublime_plugin
import os
from subprocess import Popen, PIPE, STDOUT
from . import streams
from . import parse
import re

# The One Process. Should only be modified from the main thread.
# TODO need a way to handle this across plugin reloads
# TODO use a map of projects -> processes?
the_process = None

def log(window, s):
    print(s)
    window.status_message(s)

class InstallInteroCommand(sublime_plugin.WindowCommand):
    def run(self):
        # p = Popen(['stack', 'build', 'intero'],
            # stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = False)
        log(self.window, 'not yet implemented')

def write(s):
    global the_process
    if the_process:
        the_process.stdin.write(bytes(s + '\n', 'utf-8'))
        the_process.stdin.flush()
    else:
        print('intero REPL not running')

def stop_intero(window):
    global the_process
    if the_process:
        log(window, 'intero REPL stopped')
        the_process.communicate()
        the_process = None
    else:
        log(window, 'intero REPL not running')

def highlight(views, raw_error_text):
    errors = parse.parse(raw_error_text)

    region_key = 'intero_region_errors'
    phantom_key = 'intero_phantom_errors'
    for v in views:
        v.erase_regions(region_key)
        v.erase_phantoms(phantom_key)

        # TODO a better way to match relative paths with absolute
        relevant_errors = [e for e in errors if e.file and v.file_name() and os.path.basename(e.file) == os.path.basename(v.file_name())]
        regions = [sublime.Region(v.text_point(r.line, r.col), v.text_point(r.line, r.col) + 1) for r in relevant_errors]
        scope = 'invalid'
        icon = ''
        flags = 0 # sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SOLID_UNDERLINE
        v.add_regions(region_key, regions, scope, icon, flags)
        for r in relevant_errors:
            v.add_phantom(phantom_key, sublime.Region(v.text_point(r.line, r.col), v.text_point(r.line, r.col) + 1),
                ''.join(['<div>{}</div>'.format(e.strip()) for e in r.error.split('\n')]), sublime.LAYOUT_BELOW)

def start_intero(window):
    stop_intero(window)

    log(window, 'Starting intero')

    if not window.folders():
        log(window, 'Please open your stack project')
        return

    working_directory = window.folders()[0]

    global the_process
    the_process = Popen(['stack', 'ghci', '--with-ghc', 'intero'],
        stdin = PIPE, stdout = PIPE, stderr = STDOUT, shell = False,
        cwd = working_directory)
    log(window, 'Intero REPL started')

    write(':set prompt ""')

    def really_done(items):
        nonlocal window
        highlight(window.views(), ''.join(items))

    reader = None

    def prelim_done1(_):
        # no-op to drain again
        nonlocal reader
        reader.done = really_done

    def prelim_done(_):
        # no-op to drain the queue once
        nonlocal reader
        reader.done = prelim_done1

    reader = streams.NonBlockingStreamReader(the_process, the_process.stdout, 'Collecting type info for', 'Failed', prelim_done)

class StopInteroCommand(sublime_plugin.WindowCommand):
    def run(self):
        stop_intero(self.window)

class StartInteroCommand(sublime_plugin.WindowCommand):
    def run(self):
        start_intero(self.window)

class InteroReact(sublime_plugin.EventListener):
    def on_post_save(self, view):
        global the_process
        # TODO only do this with haskell source files
        if the_process:
            # saving in quick succession does not trigger an additional save.
            # sublime must be internally throttling save rate.
            # this causes intero to think that the file hasn't changed => print different error msg
            write(':r')
        else:
            print('intero process not running, not doing anything on save')
