import sublime
import sublime_plugin


class ViewCalculator(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.view = view
        self.phantom_set = sublime.PhantomSet(view)
        self.timeout_scheduled = False
        self.needs_update = False

        self.update_phantoms()

    @classmethod
    def is_applicable(cls, settings):
        syntax = settings.get('syntax')
        return syntax == 'Packages/Text/Plain text.tmLanguage'

    def update_phantoms(self):
        phantoms = []

        # Don't do any calculations on 1MB or larger files
        if self.view.size() < 2**20:
            candidates = self.view.find_all('=>')

            for r in candidates:
                line_region = self.view.line(r.a)

                line = self.view.substr(line_region)

                idx = r.a - line_region.a
                if idx != -1:
                    val = len(line[0:idx].strip())

                    op_pt = line_region.a + idx

                    phantoms.append(sublime.Phantom(
                        sublime.Region(op_pt + 2),
                        # str(val),
                        '<div>a</div><div>b</div>',
                        sublime.LAYOUT_BELOW))

        self.phantom_set.update(phantoms)

    def handle_timeout(self):
        self.timeout_scheduled = False
        if self.needs_update:
            self.needs_update = False
            self.update_phantoms()

    def on_modified(self):
        # Call update_phantoms(), but not any more than 10 times a second
        if self.timeout_scheduled:
            self.needs_update = True
        else:
            sublime.set_timeout(lambda: self.handle_timeout(), 100)
            self.update_phantoms()
