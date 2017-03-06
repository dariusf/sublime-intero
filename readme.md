
# Installation

```
git clone git@github.com:dariusf/sublime-intero.git $PACKAGES
```

# Getting Started

- Install intero with `stack build intero`
- Open a stack project (with `subl $DIRECTORY` or by dragging it into a new window)
- Command Palette > Start intero
- Errors will show up on save

# TODO

- Proper process management
    + The plugin loses its reference to the intero process if it's reloaded
    + Manage multiple projects without conflicts
    + Start and stop intero automatically
- Better understanding of stack project structure
    + Search upwards from the current file to find the project root
    + Handle files properly
- More robust handling of process I/O
- Generalise input parsing
- Ergonomics
    + Improve phantom appearance
    + Highlight the entire error range

# License

MIT